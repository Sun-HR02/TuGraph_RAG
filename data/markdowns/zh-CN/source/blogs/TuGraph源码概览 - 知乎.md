# TuGraph源码概览

## 整体介绍

### 玩转服务

```text
## 方案1: docker启动
docker pull tugraph/tugraph-db-centos7
docker run -d -p 7070:7070 -p 9090:9090 --name tugraph_demo tugraph/tugraph-db-centos7 lgraph_server
web界面： http://$ip:7070/

## 方案2： 本地启动
修改配置文件：/usr/local/etc/lgraph.json
启动：cd build/output && ./lgraph_server
web界面：http://127.0.0.1:7070/
默认用户名：admin, 默认密码：73@TuGraph

## 多图目录结构
ls  /var/lib/lgraph/movie_db
38427636E3E5188C22A4BE6131981117  A0099623759818E9D75952405C121117  _audit_log_ log .meta
.meta也是独立的图，存储了多图的meta信息

## 每个图都有独立的插件和数据文件；图内部多组LMDB应该只是逻辑上的区分；
ls -a /var/lib/lgraph/movie_db/A0099623759818E9D75952405C121117
.  ..  _cpp_plugin_  _python_plugin_  data.mdb  dbi.log  lock.mdb  wal.log.2

## 启动graph-explore：[如何在本地启动 TuGraph Explore · Yuque](https://www.yuque.com/antv/gi/gfm9ba)
 体验地址：http://localhost:7001/tugraph/explore.html
```

### Cypher兼容

-   基于开源[openCypher github]
-   强schema
-   仅仅支持单label，匹配node时必须指定label
-   路径匹配时没有边去重
-   返回对象时，只返回vid
-   流程：[Cypher.g4] -> 用[antlr4]编译 -> CypherBaseVisitor解析 -> 执行算子树 -> 优化 -> 执行 -> 结果

### 数据模型

[Schema定义]

-   \[数据类型\]: BOOL，INT8，INT16，INT32，INT64，DATE，DATETIME，FLOAT，DOUBLE，STRING，BLOB
-   \[更省空间\] 点必须指定唯一主键::，但是属性column支持optional，边必须指定两个点的label.
-   \[更省索引空间\] 用户必须主动指定索引，减少不必要的主键开销
-   \[neo4j兼容\] 导入文件支持csv和json两种格式

### 数据导入

-   \[导入\]： 包含配置文件 和 数据文件：

-   配置文件: 为json格式, 又包含schema和files两个part，这样将所有的点、边导入文件可以写在一个schema里，减少导入操作
-   数据文件: 里面又有header schema部分

-   支持全量离线导入，性能快
-   支持增量在线导入，数据按160M为原子单位，可以从特定偏移重试导入
-   支持[dataX导入](https://github.com/TuGraph-db/tugraph-db/blob/master/doc-zh/2.operating/6.tools/3.tugraph-datax.md)  
    

### 存储过程

[支持python以及c++版本存储过程]，TuGraph支持：

-   编写、编译存储过程：需要lgraph的header和so库依赖；
-   加载存储过程；
-   使用存储过程；
-   列出存储过程；
-   更新存储过程；
-   删除存储过程

### OLAP

-   包含基础的olap算法包
-   提供OLAP基础分析接口和结构(FrontierTraversal、PathTraversal)，通过和存储过程融合，用户可以实现自定义分析任务

## 代码导读

### Txn & Graph：

基于k-v实现，乐观事务线程批量提交，基于lmdb和wal日志

-   db、transaction依赖于\[lmdb开源库\]([https://github.com/LMDB/lmdb/tree/mdb.master/libraries/liblmdb](https://github.com/LMDB/lmdb/tree/mdb.master/libraries/liblmdb))，基于memory mmap实现，锁机制基于POSIX locks实现
-   事务分为乐观事务和悲观事务
-   支持wal持久化，单机版本没有binlog
- \[持久化\]Graph -> K-V映射规则(graph\_data\_pack.h)

    -   Node按照存储规模分为四类：
        -   \[PACKED\_DATA\] 打包存储：VertexId ->(outEdgeOff|inEdgeOff|Property|OutEdge|InEdge
            -   其中Edge格式为按照<label\_id, tid, vid2, eid>排序

        -   \[VERTEX\_ONLY\] VertexId -> Property
        -   \[OUT\_EDGE\] Vid\_LabId\_Ts\_DstId\_EdgeId -> EdgeValue
        -   \[IN\_EDGE\] Vid\_LabId\_Ts\_SrcId\_EdgeId -> EdgeValue  

- Edge没有单独存储，而是和Node信息混存一起

    -   EdgeProperty和Node的出边信息混存在一起
    -   这种连续存储法，在每次更新第i个边的属性时候，需要把整个EdgeValue批量进行data copy，代价有点高（所以限制了每个edge property）的大小

    -   为防止写入放大太高，限制了每个EdgeValue大小不超过NODE\_SPLIT\_THRESHOLD = 1000， 从N用1Byte也可以看出来。


-   大小约束
    -   edge property < 32KB
    -   vertex property 大小没有限制

-   write\_set\_:
    -   key: string,TuGraph限制其最大511B\[MDB\_MAXKEYSIZE\]
    -   value: version|op\_type|data
        -   version: 每次事务批量提交时的txn\_id，支持底层cas更新
        -   op\_type: 1: Put; 0: getForUpdate; -1: Delete
        -   可以根据version来判断版本新|旧


### 调度执行

-   包含36个算子、3类Func，详细请参考类图（清晰图参考附件）:  
    

-   接口丰富，包括：
    -   schema管理
    -   索引操作：创建、查询、修改、删除、重建
    -   账户管理、权限管理：创建、查询、修改、删除
    -   多图管理：创建、查询、修改、删除
    -   快照、备份、导入、导出
    -   异步任务管理
    -   Plugin自定义存储过程管理
    -   AP算法：最短路径、全图最短路径、pagerank

-   TuGraph源于openCypher，算子明显借鉴了neo4j的开源算子体系，不过也有不少特定优化点，比如ImmeidateArgument、InQueryCall
-   在Func上：TuGraph分为Filter类、Arithmetic、Agg三类，和neo4j比较类似
-   算子执行层面，TuGraph是volcano拉模型，每次从child中获取一条结果
-   执行计划优化上，TuGraph支持：EdgeFilter下推，TopSort合并，NodeFilter下推，NodeVid下推，求边数使用RelationshipCount算子优化，repeatWithLimit优化。
-   TuGraph采用的是类似GremlinTraversalStrategy的优化方式，也就是每个Strategy对Plan进行Apply，有效率低、相互依赖、优化冲突、丢失等等问题

```text
explicit PassManager(ExecutionPlan *plan) : plan_(plan) {
    all_passes_.emplace_back(new PassReduceCount());
    all_passes_.emplace_back(new EdgeFilterPushdownExpand());
    all_passes_.emplace_back(new LazyProjectTopN());
    all_passes_.emplace_back(new PassVarLenExpandWithLimit());
    all_passes_.emplace_back(new LocateNodeByVid());
    all_passes_.emplace_back(new LocateNodeByIndexedProp());
}
void ExecutePasses() {
    for (auto p : all_passes_) {
        if (p->Gate()) p->Execute(plan_);
    }
}
```

### AP分析部分

-   基于BSP算法
-   支持bfs、lcc(Local Correlation Coefficient)、lpa、pagerank、sssp、wcc六种算法, 应该是和[ldbc analyic](https://graphalytics.org/)相对应
-   基于子图进行AP算法执行，提供丰富的AP基础运算封装
    -   快照类 Snapshot<E>
    -   顶点数组 ParallelVector<T>
    -   顶点集合 ParallelBitset
    -   边数据结构 AdjUnit/AdjUnit<Empty>
    -   边集合数据结构 AdjList<E>

-   特征：
    -   \[存、算效率高\]使用bit来存储node
    -   \[计算性能\] 使用[OpenMP](https://www.openmp.org/resources/)，[教学视频](https://www.youtube.com/watch?v=nE-xN4Bf8XI&list=PLLX-Q6B8xqZ8n8bwjGdzBJ25X2utwnoEG)实现并行编程


-   使用流程：参考Plugin使用流程

### Plugin

-   支持python和cpp库
-   执行流程
    -   用户[编写plugin文件](https://github.com/TuGraph-db/tugraph-db/blob/master/doc-zh/3.developer-document/4.procedure.md)，编译，上传(查看，删除)
    -   服务端本身有6个AP算法(用户自定义存储过程)编译为so（Plugin本身支持源码编译、so加载、zip包加载）
    -   服务端按照<procedure\_name, dynamc\_lib>进行存储，有KvTable和本地Path路径的持久化
    -   用户通过cypher语法或者http协议根据plugin名称动态调用Process函数
    -   结果集写入到response中


### 导入导出

-   \[在线导入\]import\_online
    -   导入点、边文件：
        -   通过db.importor.dataImportor主动上传|主备之间同步，将data通过post请求进行传输
        -   在线校验并进行持久化

    -   导入schema文件
        -   db.importor.schemaImportor
        -   在线校验并持久化  

-   \[离线导入\]import\_v3;
    -   文件导入计划生成
        -   根据node文件列表和edge文件列表计算依赖关系：比如：person->person, person-create->movie; person-like->move
        -   根据schema中每个文件大小对齐排序，找到到最大的顶点文件，并加入deque中作为第一个待导入的node文件加入plan中
        -   从deque去pop出该node，并计算出和其有edge关联的其他node文件按照大小排序后一次插入deque；
        -   从dequeu中pop出第一个node文件，并继续3步骤

    -   导入过程
        -   选择当前待导入最大的node文件
        -   导入和node有关联的node2
        -   导入之间的edge
        -   pop 最大的node点，继续1步骤，导入尚未导入的最大node文件

-   优势：
    -   相比先导入点在导入边，这种是导点导边混合导入的模式优先将复杂的点和关联关系导入，此时数据量较少，而边又是重操作，性能要高不少
    -   可以更快的发现点、边不完整的异常
    -   导入直接通过pipeline方式写入文件，文件名为：${name}\_next\_vid


### 全文检索部分

-   基于lucuene jar包实现，支持vertex和edge的query模糊匹配
-   支持查询类型为property\_key:property\_value\_\*

### 可视化部分

-   包括[Web Browser]和[TuGraph Explore]两类
    -   WebBrowser侧重于日常的操作、管理、监控
    -   Explore基于[GraphInsight]构建，提供完整的图探索分析能力

        -   下面只介绍WebBrowser实现机制  

-   调用链路：  
    采用vue框架\[cypher.vue -> cypher-result-graph.vue\] -> typescript脚本 -> http -> \[后端\]cpprest:
-   前端目录：deps/tugraph-web目录
    -   调用路径\[change-pwd\]：views|components -> store -> service
    -   \[结果展示\]：图 cypher-result-graph.vue、表cypher-result-table.vue、json：cypher-result-code.vue
    -   \[图布局\] cypher.vue 中有力导，网络，树形等布局选项
    -   \[可视化\] 使用的[cytoscapec]插件


-   Graph指标监控系统
    -   lgraph\_monitort通过db.monitor.serverInfo()、CALL db.monitor.tuGraphInfo()上报到prometheus中
    -   基于prometheus进行汇聚
    -   抓取：tugraph-web/src/service/db-info/db-info.ts， http接口从后端取
    -   绘图：views/control-board/db-status/db-status.vue
    -   绘图原理：基于grafana模板 TuGraph-grafana-template.json


### RPC接口

-   语言语言：java、cpp、python、restful - 交互协议：cpp/java实现brpc、http
-   cpp 编解码：brpc交互基于protobuf，设计有json和binary两种交互协议，不过client端写死为json交互格式
-   瘦客户端：client端只提供交互，不提供高可用，线程池等等 - server端：
-   根据lgraph.json配置图系统
-   根据brpc初始化service服务，挂在到lserver和resetful server后端
-   由HandleRequest进行请求处理, 目前支持10类请求

```text
*kGraphApiRequest*= 11,
*kCypherRequest*= 12,
*kPluginRequest*= 13,
*kHaRequest*= 14,
*kImportRequest*= 15,
*kGraphRequest*= 17,
*kAclRequest*= 18,
*kConfigRequest*= 19,
*kRestoreRequest*= 20,
*kSchemaRequest*= 21,
```