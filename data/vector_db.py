import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from config.settings import settings

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("警告: FAISS未安装，向量数据库功能将不可用。请运行: pip install faiss-cpu")


class VectorDB:
    """FAISS向量数据库"""
    
    def __init__(
        self,
        dimension: int = 1536,
        index_type: str = "flat",
        db_path: str = None,
        use_gpu: bool = False
    ):
        self.dimension = dimension
        self.index_type = index_type
        self.db_path = db_path or settings.vector_db_path
        self.use_gpu = use_gpu and FAISS_AVAILABLE
        
        self.index = None
        self.metadata_store: Dict[int, Dict[str, Any]] = {}
        self.id_counter: int = 0
        self.is_initialized: bool = False
        
        if FAISS_AVAILABLE:
            self._init_index()
            self._load_from_disk()
            self.is_initialized = True
    
    def _init_index(self):
        if not FAISS_AVAILABLE:
            return
        
        if self.index_type == "flat":
            self.index = faiss.IndexFlatIP(self.dimension)
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatIP(self.dimension)
            nlist = 100
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        elif self.index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
        
        if self.use_gpu and hasattr(faiss, 'StandardGpuResources'):
            try:
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
            except Exception as e:
                print(f"GPU初始化失败，使用CPU: {e}")
                self.use_gpu = False
        
        print(f"FAISS索引初始化成功 (类型: {self.index_type}, 维度: {self.dimension})")
    
    def _ensure_db_directory(self):
        if self.db_path:
            os.makedirs(self.db_path, exist_ok=True)
    
    def _get_index_path(self) -> str:
        return os.path.join(self.db_path, "index.faiss")
    
    def _get_metadata_path(self) -> str:
        return os.path.join(self.db_path, "metadata.json")
    
    def _load_from_disk(self):
        if not self.db_path:
            return
        
        index_path = self._get_index_path()
        metadata_path = self._get_metadata_path()
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata_store = {int(k): v for k, v in data.get('metadata', {}).items()}
                    self.id_counter = data.get('id_counter', 0)
                
                print(f"从磁盘加载向量数据库成功 (向量数: {self.index.ntotal})")
            except Exception as e:
                print(f"加载向量数据库失败: {e}")
                self._init_index()
    
    def save_to_disk(self) -> bool:
        if not FAISS_AVAILABLE or not self.index or not self.db_path:
            return False
        
        try:
            self._ensure_db_directory()
            
            if self.use_gpu and hasattr(faiss, 'index_gpu_to_cpu'):
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                faiss.write_index(cpu_index, self._get_index_path())
            else:
                faiss.write_index(self.index, self._get_index_path())
            
            with open(self._get_metadata_path(), 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': self.metadata_store,
                    'id_counter': self.id_counter
                }, f, ensure_ascii=False, indent=2)
            
            print(f"向量数据库保存成功 (向量数: {self.index.ntotal})")
            return True
        except Exception as e:
            print(f"保存向量数据库失败: {e}")
            return False
    
    async def insert_vectors(
        self,
        vectors: List[List[float]],
        metadata_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not FAISS_AVAILABLE or not self.index:
            return {"error": "FAISS不可用", "inserted_count": 0}
        
        if len(vectors) != len(metadata_list):
            return {"error": "向量和元数据数量不匹配", "inserted_count": 0}
        
        if not vectors:
            return {"inserted_count": 0, "ids": []}
        
        try:
            vectors_np = np.array(vectors, dtype=np.float32)
            
            if vectors_np.shape[1] != self.dimension:
                return {"error": f"向量维度不匹配，期望{self.dimension}，实际{vectors_np.shape[1]}", "inserted_count": 0}
            
            faiss.normalize_L2(vectors_np)
            
            if self.index_type == "ivf" and not self.index.is_trained:
                self.index.train(vectors_np)
            
            start_id = self.id_counter
            ids = []
            
            for i, metadata in enumerate(metadata_list):
                vector_id = self.id_counter + i
                self.metadata_store[vector_id] = metadata
                ids.append(vector_id)
            
            self.index.add(vectors_np)
            self.id_counter += len(vectors)
            
            return {
                "inserted_count": len(vectors),
                "ids": ids
            }
        except Exception as e:
            print(f"插入向量失败: {e}")
            return {"error": str(e), "inserted_count": 0}
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        if not FAISS_AVAILABLE or not self.index or self.index.ntotal == 0:
            return []
        
        try:
            query_np = np.array([query_vector], dtype=np.float32)
            
            if query_np.shape[1] != self.dimension:
                print(f"查询向量维度不匹配: {query_np.shape[1]} vs {self.dimension}")
                return []
            
            faiss.normalize_L2(query_np)
            
            search_k = min(top_k * 3, self.index.ntotal) if filters else top_k
            
            scores, indices = self.index.search(query_np, search_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                
                if score < min_score:
                    continue
                
                metadata = self.metadata_store.get(int(idx), {})
                
                if filters:
                    match = True
                    for key, value in filters.items():
                        if metadata.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                results.append({
                    "id": int(idx),
                    "score": float(score),
                    "metadata": metadata
                })
                
                if len(results) >= top_k:
                    break
            
            return results
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []
    
    async def batch_search(
        self,
        query_vectors: List[List[float]],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        results = []
        for query_vector in query_vectors:
            result = await self.search(query_vector, top_k, filters)
            results.append(result)
        return results
    
    async def get_by_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        if vector_id not in self.metadata_store:
            return None
        
        return {
            "id": vector_id,
            "metadata": self.metadata_store[vector_id]
        }
    
    async def get_by_ids(self, vector_ids: List[int]) -> List[Dict[str, Any]]:
        results = []
        for vid in vector_ids:
            result = await self.get_by_id(vid)
            if result:
                results.append(result)
        return results
    
    async def update_metadata(self, vector_id: int, metadata: Dict[str, Any]) -> bool:
        if vector_id not in self.metadata_store:
            return False
        
        self.metadata_store[vector_id].update(metadata)
        return True
    
    async def delete_by_id(self, vector_id: int) -> bool:
        if vector_id not in self.metadata_store:
            return False
        
        del self.metadata_store[vector_id]
        return True
    
    async def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        ids_to_delete = []
        
        for vid, metadata in self.metadata_store.items():
            match = True
            for key, value in filters.items():
                if metadata.get(key) != value:
                    match = False
                    break
            if match:
                ids_to_delete.append(vid)
        
        for vid in ids_to_delete:
            del self.metadata_store[vid]
        
        return len(ids_to_delete)
    
    async def clear_all(self) -> bool:
        if not FAISS_AVAILABLE:
            return False
        
        self.metadata_store = {}
        self.id_counter = 0
        self._init_index()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_vectors": self.index.ntotal if FAISS_AVAILABLE and self.index else 0,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "is_trained": self.index.is_trained if FAISS_AVAILABLE and self.index else False,
            "use_gpu": self.use_gpu,
            "db_path": self.db_path
        }
    
    async def rebuild_index(self) -> bool:
        if not FAISS_AVAILABLE:
            return False
        
        self._init_index()
        self.id_counter = 0
        return True


vector_db = None

def get_vector_db() -> VectorDB:
    global vector_db
    if vector_db is None:
        vector_db = VectorDB()
    return vector_db
