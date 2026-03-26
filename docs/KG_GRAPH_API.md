# 知识图谱可视化接口文档

## 接口概述

| 属性 | 值 |
|------|-----|
| **接口名称** | 获取知识图谱可视化数据 |
| **接口路径** | `GET /api/kg/graph` |
| **接口版本** | v1.0.0 |
| **认证要求** | 无需认证 |
| **响应格式** | JSON |

---

## 功能说明

该接口用于获取知识图谱的结构化数据，供前端可视化库（如 D3.js、ECharts、vis.js、AntV G6 等）渲染知识图谱。

### 核心特性

- 支持按课程类型筛选（基础/高级/全部）
- 支持层级深度控制（1-4级）
- 返回标准化的节点和边数据
- 节点包含父子关系，便于构建树形结构

---

## 请求参数

### Query Parameters

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `course_type` | string | 否 | null | 课程类型筛选 |
| `depth` | integer | 否 | 4 | 层级深度控制 |

### course_type 参数值

| 值 | 说明 |
|----|------|
| `basic` | 仅获取Python基础编程教程数据 |
| `advanced` | 仅获取Python高级教程数据 |
| 不传值 | 获取全部课程数据 |

### depth 参数值

| 值 | 返回层级 | 节点类型 | 适用场景 |
|----|----------|----------|----------|
| `1` | 仅课程 | Course | 课程概览视图 |
| `2` | 课程 + 章节 | Course, Chapter | 章节导航视图 |
| `3` | 课程 + 章节 + 小节 | Course, Chapter, Section | 小节目录视图 |
| `4` | 全部层级 | Course, Chapter, Section, KnowledgePoint, SubPoint | 完整知识图谱 |

---

## 请求示例

### JavaScript (Fetch API)

```javascript
// 获取全部课程，完整深度
fetch('http://localhost:8000/api/kg/graph')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取基础课程，完整深度
fetch('http://localhost:8000/api/kg/graph?course_type=basic')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取全部课程，仅到章节级别
fetch('http://localhost:8000/api/kg/graph?depth=2')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取基础课程，到小节级别
fetch('http://localhost:8000/api/kg/graph?course_type=basic&depth=3')
  .then(response => response.json())
  .then(data => console.log(data));
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

const getGraphData = async (courseType = null, depth = 4) => {
  const params = { depth };
  if (courseType) {
    params.course_type = courseType;
  }
  
  const response = await axios.get('http://localhost:8000/api/kg/graph', { params });
  return response.data;
};

// 使用示例
const graphData = await getGraphData('basic', 3);
```

### TypeScript

```typescript
interface GraphNode {
  id: string;
  name: string;
  type: 'Course' | 'Chapter' | 'Section' | 'KnowledgePoint' | 'SubPoint';
  parentId: string | null;
}

interface GraphEdge {
  source: string;
  target: string;
  type: 'HAS_CHAPTER' | 'HAS_SECTION' | 'HAS_KNOWLEDGE_POINT' | 'HAS_SUB_POINT';
}

interface GraphDataResponse {
  success: boolean;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

async function fetchGraphData(
  courseType?: 'basic' | 'advanced',
  depth: number = 4
): Promise<GraphDataResponse> {
  const params = new URLSearchParams();
  params.append('depth', depth.toString());
  if (courseType) {
    params.append('course_type', courseType);
  }
  
  const response = await fetch(`http://localhost:8000/api/kg/graph?${params}`);
  return response.json();
}
```

### Python (requests)

```python
import requests

def get_graph_data(course_type=None, depth=4):
    params = {'depth': depth}
    if course_type:
        params['course_type'] = course_type
    
    response = requests.get('http://localhost:8000/api/kg/graph', params=params)
    return response.json()

# 使用示例
data = get_graph_data(course_type='basic', depth=3)
print(data)
```

---

## 响应格式

### 响应结构

```json
{
  "success": true,
  "nodes": [...],
  "edges": [...]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `nodes` | array | 节点数组 |
| `edges` | array | 边（关系）数组 |

---

## 节点数据结构 (Node)

### 节点字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 节点唯一标识符 |
| `name` | string | 节点名称（显示文本） |
| `type` | string | 节点类型 |
| `parentId` | string \| null | 父节点ID，根节点为null |

### 节点类型说明

| type 值 | 中文名称 | 层级 | 示例 |
|---------|----------|------|------|
| `Course` | 课程 | 1 | Python基础编程教程 |
| `Chapter` | 章节 | 2 | 一、Python入门与环境 |
| `Section` | 小节 | 3 | Python语言概述 |
| `KnowledgePoint` | 知识点 | 4 | Python3简介 |
| `SubPoint` | 子知识点 | 5 | Python3解释器 |

### 节点示例

```json
{
  "id": "course_basic",
  "name": "Python基础编程教程",
  "type": "Course",
  "parentId": null
}
```

```json
{
  "id": "course_basic_ch_0",
  "name": "一、Python入门与环境",
  "type": "Chapter",
  "parentId": "course_basic"
}
```

```json
{
  "id": "course_basic_ch_0_sec_0",
  "name": "Python语言概述",
  "type": "Section",
  "parentId": "course_basic_ch_0"
}
```

```json
{
  "id": "course_basic_ch_0_sec_0_kp_0",
  "name": "Python3简介",
  "type": "KnowledgePoint",
  "parentId": "course_basic_ch_0_sec_0"
}
```

---

## 边数据结构 (Edge)

### 边字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | string | 源节点ID（父节点） |
| `target` | string | 目标节点ID（子节点） |
| `type` | string | 关系类型 |

### 关系类型说明

| type 值 | 中文含义 | 源节点类型 | 目标节点类型 |
|---------|----------|------------|--------------|
| `HAS_CHAPTER` | 包含章节 | Course | Chapter |
| `HAS_SECTION` | 包含小节 | Chapter | Section |
| `HAS_KNOWLEDGE_POINT` | 包含知识点 | Section | KnowledgePoint |
| `HAS_SUB_POINT` | 包含子知识点 | KnowledgePoint | SubPoint |

### 边示例

```json
{
  "source": "course_basic",
  "target": "course_basic_ch_0",
  "type": "HAS_CHAPTER"
}
```

```json
{
  "source": "course_basic_ch_0",
  "target": "course_basic_ch_0_sec_0",
  "type": "HAS_SECTION"
}
```

---

## 完整响应示例

### 示例1：获取基础课程，深度为2（课程+章节）

**请求：**
```
GET /api/kg/graph?course_type=basic&depth=2
```

**响应：**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "course_basic",
      "name": "Python基础编程教程",
      "type": "Course",
      "parentId": null
    },
    {
      "id": "course_basic_ch_0",
      "name": "一、Python入门与环境",
      "type": "Chapter",
      "parentId": "course_basic"
    },
    {
      "id": "course_basic_ch_1",
      "name": "二、基础语法与结构",
      "type": "Chapter",
      "parentId": "course_basic"
    },
    {
      "id": "course_basic_ch_2",
      "name": "三、数据类型",
      "type": "Chapter",
      "parentId": "course_basic"
    }
  ],
  "edges": [
    {
      "source": "course_basic",
      "target": "course_basic_ch_0",
      "type": "HAS_CHAPTER"
    },
    {
      "source": "course_basic",
      "target": "course_basic_ch_1",
      "type": "HAS_CHAPTER"
    },
    {
      "source": "course_basic",
      "target": "course_basic_ch_2",
      "type": "HAS_CHAPTER"
    }
  ]
}
```

### 示例2：获取全部课程，深度为1（仅课程）

**请求：**
```
GET /api/kg/graph?depth=1
```

**响应：**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "course_basic",
      "name": "Python基础编程教程",
      "type": "Course",
      "parentId": null
    },
    {
      "id": "course_advanced",
      "name": "Python高级教程",
      "type": "Course",
      "parentId": null
    }
  ],
  "edges": []
}
```

### 示例3：获取基础课程，深度为4（完整数据）

**请求：**
```
GET /api/kg/graph?course_type=basic&depth=4
```

**响应：**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "course_basic",
      "name": "Python基础编程教程",
      "type": "Course",
      "parentId": null
    },
    {
      "id": "course_basic_ch_0",
      "name": "一、Python入门与环境",
      "type": "Chapter",
      "parentId": "course_basic"
    },
    {
      "id": "course_basic_ch_0_sec_0",
      "name": "Python语言概述",
      "type": "Section",
      "parentId": "course_basic_ch_0"
    },
    {
      "id": "course_basic_ch_0_sec_0_kp_0",
      "name": "Python3简介",
      "type": "KnowledgePoint",
      "parentId": "course_basic_ch_0_sec_0"
    },
    {
      "id": "course_basic_ch_0_sec_0_kp_1",
      "name": "Python3解释器",
      "type": "KnowledgePoint",
      "parentId": "course_basic_ch_0_sec_0"
    }
  ],
  "edges": [
    {
      "source": "course_basic",
      "target": "course_basic_ch_0",
      "type": "HAS_CHAPTER"
    },
    {
      "source": "course_basic_ch_0",
      "target": "course_basic_ch_0_sec_0",
      "type": "HAS_SECTION"
    },
    {
      "source": "course_basic_ch_0_sec_0",
      "target": "course_basic_ch_0_sec_0_kp_0",
      "type": "HAS_KNOWLEDGE_POINT"
    },
    {
      "source": "course_basic_ch_0_sec_0",
      "target": "course_basic_ch_0_sec_0_kp_1",
      "type": "HAS_KNOWLEDGE_POINT"
    }
  ]
}
```

---

## 错误响应

### 参数验证错误

**请求：**
```
GET /api/kg/graph?course_type=invalid
```

**响应：** (HTTP 422)
```json
{
  "success": false,
  "message": "course_type必须为'basic'或'advanced'",
  "details": {
    "course_type": "invalid"
  }
}
```

### 服务不可用

**响应：** (HTTP 503)
```json
{
  "success": false,
  "message": "知识图谱服务不可用",
  "details": {}
}
```

---

## 前端可视化示例

### 1. 使用 ECharts 树形图

```javascript
async function renderTreeChart() {
  const response = await fetch('http://localhost:8000/api/kg/graph?course_type=basic&depth=3');
  const { nodes, edges } = await response.json();
  
  // 构建树形结构
  function buildTree(nodes, parentId = null) {
    return nodes
      .filter(node => node.parentId === parentId)
      .map(node => ({
        name: node.name,
        children: buildTree(nodes, node.id),
        itemStyle: {
          color: getNodeColor(node.type)
        }
      }));
  }
  
  const treeData = buildTree(nodes);
  
  const chart = echarts.init(document.getElementById('chart'));
  chart.setOption({
    series: [{
      type: 'tree',
      data: treeData,
      top: '10%',
      left: '15%',
      bottom: '10%',
      right: '20%',
      symbolSize: 12,
      orient: 'LR',
      label: {
        position: 'right',
        verticalAlign: 'middle'
      },
      leaves: {
        label: {
          position: 'right'
        }
      },
      expandAndCollapse: true,
      animationDuration: 550
    }]
  });
}

function getNodeColor(type) {
  const colors = {
    'Course': '#5470c6',
    'Chapter': '#91cc75',
    'Section': '#fac858',
    'KnowledgePoint': '#ee6666',
    'SubPoint': '#73c0de'
  };
  return colors[type] || '#999';
}
```

### 2. 使用 AntV G6 关系图

```javascript
import G6 from '@antv/g6';

async function renderGraph() {
  const response = await fetch('http://localhost:8000/api/kg/graph?depth=3');
  const { nodes, edges } = await response.json();
  
  // 转换为G6数据格式
  const data = {
    nodes: nodes.map(node => ({
      id: node.id,
      label: node.name,
      type: 'circle',
      style: {
        fill: getNodeColor(node.type)
      }
    })),
    edges: edges.map(edge => ({
      source: edge.source,
      target: edge.target
    }))
  };
  
  const graph = new G6.Graph({
    container: 'container',
    width: 800,
    height: 600,
    modes: {
      default: ['drag-canvas', 'zoom-canvas', 'drag-node']
    },
    layout: {
      type: 'compactBox',
      direction: 'LR',
      getId: d => d.id
    }
  });
  
  graph.data(data);
  graph.render();
}
```

### 3. 使用 D3.js 力导向图

```javascript
async function renderForceGraph() {
  const response = await fetch('http://localhost:8000/api/kg/graph?depth=4');
  const { nodes, edges } = await response.json();
  
  const width = 800;
  const height = 600;
  
  const svg = d3.select('#chart')
    .append('svg')
    .attr('width', width)
    .attr('height', height);
  
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-100))
    .force('center', d3.forceCenter(width / 2, height / 2));
  
  const link = svg.append('g')
    .selectAll('line')
    .data(edges)
    .enter().append('line')
    .attr('stroke', '#999');
  
  const node = svg.append('g')
    .selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('r', 8)
    .attr('fill', d => getNodeColor(d.type))
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));
  
  node.append('title').text(d => d.name);
  
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    
    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);
  });
}
```

### 4. 使用 vis.js 网络图

```javascript
async function renderVisNetwork() {
  const response = await fetch('http://localhost:8000/api/kg/graph?course_type=basic');
  const { nodes, edges } = await response.json();
  
  // 转换为vis.js数据格式
  const visNodes = new vis.DataSet(
    nodes.map(node => ({
      id: node.id,
      label: node.name,
      color: getNodeColor(node.type),
      font: { size: 14 }
    }))
  );
  
  const visEdges = new vis.DataSet(
    edges.map((edge, index) => ({
      id: index,
      from: edge.source,
      to: edge.target,
      arrows: 'to'
    }))
  );
  
  const container = document.getElementById('network');
  const data = { nodes: visNodes, edges: visEdges };
  
  const options = {
    layout: {
      hierarchical: {
        direction: 'LR',
        sortMethod: 'directed'
      }
    },
    interaction: {
      navigationButtons: true,
      zoomView: true
    }
  };
  
  new vis.Network(container, data, options);
}
```

---

## 数据转换工具函数

### 构建树形结构

```typescript
interface TreeNode {
  id: string;
  name: string;
  type: string;
  children: TreeNode[];
}

function buildTree(nodes: GraphNode[], parentId: string | null = null): TreeNode[] {
  return nodes
    .filter(node => node.parentId === parentId)
    .map(node => ({
      id: node.id,
      name: node.name,
      type: node.type,
      children: buildTree(nodes, node.id)
    }));
}

// 使用示例
const { nodes } = await fetchGraphData();
const tree = buildTree(nodes);
```

### 构建邻接表

```typescript
function buildAdjacencyList(edges: GraphEdge[]): Map<string, string[]> {
  const adjList = new Map<string, string[]>();
  
  edges.forEach(edge => {
    if (!adjList.has(edge.source)) {
      adjList.set(edge.source, []);
    }
    adjList.get(edge.source)!.push(edge.target);
  });
  
  return adjList;
}
```

### 查找节点路径

```typescript
function findPath(
  nodes: GraphNode[],
  edges: GraphEdge[],
  targetId: string
): GraphNode[] {
  const nodeMap = new Map(nodes.map(n => [n.id, n]));
  const path: GraphNode[] = [];
  
  let current = nodeMap.get(targetId);
  while (current) {
    path.unshift(current);
    current = current.parentId ? nodeMap.get(current.parentId) : null;
  }
  
  return path;
}

// 使用示例：查找"Python3简介"的学习路径
const path = findPath(nodes, edges, 'course_basic_ch_0_sec_0_kp_0');
// 返回: [Course节点, Chapter节点, Section节点, KnowledgePoint节点]
```

### 按类型筛选节点

```typescript
function filterNodesByType(nodes: GraphNode[], types: string[]): GraphNode[] {
  return nodes.filter(node => types.includes(node.type));
}

// 使用示例：只获取知识点
const knowledgePoints = filterNodesByType(nodes, ['KnowledgePoint', 'SubPoint']);
```

---

## 性能建议

### 数据量预估

| depth | 预估节点数 | 预估边数 | 建议场景 |
|-------|-----------|----------|----------|
| 1 | 2 | 0 | 课程选择 |
| 2 | ~20 | ~18 | 章节导航 |
| 3 | ~80 | ~78 | 小节浏览 |
| 4 | ~300+ | ~300+ | 完整图谱 |

### 优化建议

1. **按需加载**：根据用户交互动态调整 `depth` 参数
2. **课程筛选**：使用 `course_type` 参数减少数据量
3. **前端缓存**：缓存已获取的数据，避免重复请求
4. **虚拟滚动**：对于大量节点，使用虚拟滚动技术
5. **懒加载**：先加载浅层级，用户展开时再加载深层级

```javascript
// 懒加载示例
class KnowledgeGraphLoader {
  constructor() {
    this.cache = new Map();
  }
  
  async loadNode(nodeId, depth = 1) {
    const cacheKey = `${nodeId}-${depth}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }
    
    const data = await fetchGraphData(null, depth);
    this.cache.set(cacheKey, data);
    return data;
  }
}
```

---

## 常见问题 (FAQ)

### Q1: 如何判断节点是否有子节点？

**A:** 可以通过 `edges` 数组判断，或者检查是否有其他节点的 `parentId` 等于该节点ID：

```javascript
function hasChildren(nodeId, edges) {
  return edges.some(edge => edge.source === nodeId);
}

// 或者
function hasChildren(nodeId, nodes) {
  return nodes.some(node => node.parentId === nodeId);
}
```

### Q2: 如何获取某个节点的所有子孙节点？

**A:** 递归遍历：

```javascript
function getDescendants(nodes, edges, nodeId) {
  const children = edges
    .filter(e => e.source === nodeId)
    .map(e => e.target);
  
  const descendants = [...children];
  children.forEach(childId => {
    descendants.push(...getDescendants(nodes, edges, childId));
  });
  
  return descendants;
}
```

### Q3: 如何实现搜索高亮？

**A:** 前端过滤节点名称：

```javascript
function searchNodes(nodes, keyword) {
  const lowerKeyword = keyword.toLowerCase();
  return nodes.filter(node => 
    node.name.toLowerCase().includes(lowerKeyword)
  );
}
```

### Q4: 节点ID的命名规则是什么？

**A:** 节点ID采用层级命名格式：

```
course_{type}                           // 课程
course_{type}_ch_{chapterIndex}         // 章节
course_{type}_ch_{chapterIndex}_sec_{sectionIndex}  // 小节
course_{type}_ch_{chapterIndex}_sec_{sectionIndex}_kp_{kpIndex}  // 知识点
```

示例：
- `course_basic` - 基础课程
- `course_basic_ch_0` - 基础课程第1章
- `course_basic_ch_0_sec_0` - 基础课程第1章第1小节
- `course_basic_ch_0_sec_0_kp_0` - 基础课程第1章第1小节第1个知识点

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2024-03-25 | 初始版本，支持课程筛选和层级深度控制 |

---

## 联系方式

如有问题，请联系后端开发团队或查看主API文档：`http://localhost:8000/docs`
