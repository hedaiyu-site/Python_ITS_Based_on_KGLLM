import pytest
import asyncio
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.vector_db import VectorDB, get_vector_db


class TestVectorDB:
    """向量数据库测试类"""
    
    @pytest.fixture
    def vector_db(self):
        db = VectorDB(
            dimension=1536,
            index_type="flat",
            db_path="./test_vector_db"
        )
        yield db
    
    def test_init(self, vector_db):
        assert vector_db.dimension == 1536
        assert vector_db.index_type == "flat"
        assert vector_db.is_initialized == True
    
    @pytest.mark.asyncio
    async def test_insert_vectors(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(5)]
        metadata_list = [
            {"node_id": i, "name": f"test_node_{i}", "type": "test"}
            for i in range(5)
        ]
        
        result = await vector_db.insert_vectors(vectors, metadata_list)
        
        assert "error" not in result
        assert result["inserted_count"] == 5
        assert len(result["ids"]) == 5
    
    @pytest.mark.asyncio
    async def test_insert_empty_vectors(self, vector_db):
        result = await vector_db.insert_vectors([], [])
        
        assert result["inserted_count"] == 0
        assert result["ids"] == []
    
    @pytest.mark.asyncio
    async def test_insert_mismatched_vectors(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(3)]
        metadata_list = [{"id": i} for i in range(2)]
        
        result = await vector_db.insert_vectors(vectors, metadata_list)
        
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_search(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(5)]
        metadata_list = [
            {"node_id": i, "name": f"test_node_{i}", "type": "test"}
            for i in range(5)
        ]
        
        await vector_db.insert_vectors(vectors, metadata_list)
        
        query_vector = [0.1] * 1536
        results = await vector_db.search(query_vector, top_k=3)
        
        assert len(results) <= 3
        for result in results:
            assert "id" in result
            assert "score" in result
            assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(5)]
        metadata_list = [
            {"node_id": i, "name": f"test_node_{i}", "type": "test" if i < 3 else "other"}
            for i in range(5)
        ]
        
        await vector_db.insert_vectors(vectors, metadata_list)
        
        query_vector = [0.1] * 1536
        results = await vector_db.search(
            query_vector,
            top_k=10,
            filters={"type": "test"}
        )
        
        for result in results:
            assert result["metadata"]["type"] == "test"
    
    @pytest.mark.asyncio
    async def test_search_with_min_score(self, vector_db):
        vectors = [[float(i) / 100] * 1536 for i in range(5)]
        metadata_list = [
            {"node_id": i, "name": f"test_node_{i}"}
            for i in range(5)
        ]
        
        await vector_db.insert_vectors(vectors, metadata_list)
        
        query_vector = [0.05] * 1536
        results = await vector_db.search(
            query_vector,
            top_k=10,
            min_score=0.5
        )
        
        for result in results:
            assert result["score"] >= 0.5
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, vector_db):
        vectors = [[0.1] * 1536]
        metadata_list = [{"node_id": 1, "name": "test_node"}]
        
        result = await vector_db.insert_vectors(vectors, metadata_list)
        vector_id = result["ids"][0]
        
        retrieved = await vector_db.get_by_id(vector_id)
        
        assert retrieved is not None
        assert retrieved["id"] == vector_id
        assert retrieved["metadata"]["name"] == "test_node"
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, vector_db):
        result = await vector_db.get_by_id(99999)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_metadata(self, vector_db):
        vectors = [[0.1] * 1536]
        metadata_list = [{"node_id": 1, "name": "test_node"}]
        
        result = await vector_db.insert_vectors(vectors, metadata_list)
        vector_id = result["ids"][0]
        
        success = await vector_db.update_metadata(vector_id, {"name": "updated_node"})
        
        assert success == True
        
        retrieved = await vector_db.get_by_id(vector_id)
        assert retrieved["metadata"]["name"] == "updated_node"
    
    @pytest.mark.asyncio
    async def test_delete_by_id(self, vector_db):
        vectors = [[0.1] * 1536]
        metadata_list = [{"node_id": 1, "name": "test_node"}]
        
        result = await vector_db.insert_vectors(vectors, metadata_list)
        vector_id = result["ids"][0]
        
        success = await vector_db.delete_by_id(vector_id)
        
        assert success == True
        
        retrieved = await vector_db.get_by_id(vector_id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_delete_by_filter(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(5)]
        metadata_list = [
            {"node_id": i, "type": "test" if i < 3 else "other"}
            for i in range(5)
        ]
        
        await vector_db.insert_vectors(vectors, metadata_list)
        
        deleted_count = await vector_db.delete_by_filter({"type": "test"})
        
        assert deleted_count == 3
    
    @pytest.mark.asyncio
    async def test_clear_all(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(5)]
        metadata_list = [{"node_id": i} for i in range(5)]
        
        await vector_db.insert_vectors(vectors, metadata_list)
        
        success = await vector_db.clear_all()
        
        assert success == True
        
        stats = vector_db.get_stats()
        assert stats["total_vectors"] == 0
    
    def test_get_stats(self, vector_db):
        stats = vector_db.get_stats()
        
        assert "total_vectors" in stats
        assert "dimension" in stats
        assert "index_type" in stats
        assert stats["dimension"] == 1536
    
    @pytest.mark.asyncio
    async def test_save_and_load(self, vector_db):
        vectors = [[0.1] * 1536 for _ in range(3)]
        metadata_list = [
            {"node_id": i, "name": f"test_node_{i}"}
            for i in range(3)
        ]
        
        await vector_db.insert_vectors(vectors, metadata_list)
        
        success = vector_db.save_to_disk()
        assert success == True
        
        new_db = VectorDB(
            dimension=1536,
            index_type="flat",
            db_path="./test_vector_db"
        )
        
        stats = new_db.get_stats()
        assert stats["total_vectors"] >= 3


class TestVectorDBSingleton:
    """测试向量数据库单例"""
    
    def test_get_vector_db_singleton(self):
        db1 = get_vector_db()
        db2 = get_vector_db()
        
        assert db1 is db2


def cleanup_test_db():
    import shutil
    test_db_path = "./test_vector_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    cleanup_test_db()
