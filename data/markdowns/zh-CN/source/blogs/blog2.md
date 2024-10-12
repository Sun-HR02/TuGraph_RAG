# 图分析引擎技术解析

图分析引擎又称图计算框架，主要用来进行复杂图分析，是一种能够全量数据集运行快速循环迭代的技术，适用场景包括社区发现、基因序列预测、重要性排名等，典型算法有 PageRank、WCC、BFS、LPA、SSSP。

TuGraph 图数据管理平台社区版已于 2022 年 9 月在 Github 开源，本文将对 TuGraph 图分析引擎的技术进行剖析。

## 1 TuGraph 图分析引擎概览

TuGraph 的图分析引擎，面向的场景主要是全图/全量数据分析类的任务。借助 TuGraph 的 C++ 图分析引擎 API ，用户可以对不同数据来源的图数据快速导出一个待处理的复杂子图，然后在该子图上运行诸如 BFS、PageRank、LPA、WCC 等迭代式图算法，最后根据运行结果做出相应的对策。 在 TuGraph 中，导出和计算过程均可以通过在内存中并行处理的方式进行加速，从而达到近乎实时的处理分析，和传统方法相比，即避免了数据导出落盘的开销，又能使用紧凑的图数据结构获得计算的理想性能。

根据数据来源及实现不同，可分为 Procedure、Embed 和 Standalone 三种运行模式。其中 Procedure 模式和 Embed 模式的数据源是图存储中加载图数据，分别适用于 Client/Server 部署，以及服务端直接调用，后者多用于调试。

Standalone 模式的数据源是 TXT、二进制、ODPS 文件等外部数据源，能够独立于图数据存储直接运行分析算法。

TuGraph 图计算系统社区版内置 6 个基础算法，商业版内置了共 34 种算法。涵盖了图结构、社区发现、路径查询、重要性分析、模式挖掘和关联性分析的六大类常用方法，可以满足多种业务场景需要，因此用户几乎不需要自己实现具体的图计算过程。

<table><tbody><tr><td>算法类型</td><td>中文算法名</td><td>英文算法名</td><td>程序名</td></tr><tr><td rowspan="5">路径查询</td><td>广度优先搜索</td><td>Breadth-First Search</td><td>bfs</td></tr><tr><td>单源最短路径</td><td>Single-Source Shortest Path</td><td>sssp</td></tr><tr><td>全对最短路径</td><td>All-Pair Shortest Path</td><td>apsp</td></tr><tr><td>多源最短路径</td><td>Multiple-source Shortest Paths</td><td>mssp</td></tr><tr><td>两点间最短路径</td><td>Single-Pair Shortest Path</td><td>spsp</td></tr><tr><td rowspan="9">重要性分析</td><td>网页排序</td><td>Pagerank</td><td>pagerank</td></tr><tr><td>介数中心度</td><td>Betweenness Centrality</td><td>bc</td></tr><tr><td>置信度传播</td><td>Belief Propagation</td><td>bp</td></tr><tr><td>距离中心度</td><td>Closeness Centrality</td><td>clce</td></tr><tr><td>个性化网页排序</td><td>Personalized PageRank</td><td>ppr</td></tr><tr><td>带权重的网页排序</td><td>Weighted Pagerank Algorithm</td><td>wpagerank</td></tr><tr><td>信任指数排名</td><td>Trustrank</td><td>trustrank</td></tr><tr><td>sybil检测算法</td><td>Sybil Rank</td><td>sybilrank</td></tr><tr><td>超链接主题搜索</td><td>Hyperlink-Induced Topic Search</td><td>hits</td></tr><tr><td rowspan="4">关联性分析</td><td>平均集聚系数</td><td>Local Clustering Coefficient</td><td>lcc</td></tr><tr><td>共同邻居</td><td>Common Neighborhood</td><td>cn</td></tr><tr><td>度数关联度</td><td>Degree Correlation</td><td>dc</td></tr><tr><td>杰卡德系数</td><td>Jaccard Index</td><td>ji</td></tr><tr><td rowspan="5">图结构</td><td>直径估计</td><td>Dimension Estimation</td><td>de</td></tr><tr><td>K核算法</td><td>K-core</td><td>kcore</td></tr><tr><td>k阶团计数算法</td><td>Kcliques</td><td>kcliques</td></tr><tr><td>k阶桁架计数算法</td><td>Ktruss</td><td>ktruss</td></tr><tr><td>最大独立集算法</td><td>Maximal independent set</td><td>mis</td></tr><tr><td rowspan="8">社区发现</td><td>弱连通分量</td><td>Weakly Connected Components</td><td>wcc</td></tr><tr><td>标签传播</td><td>Label Propagation Algorithm</td><td>lpa</td></tr><tr><td>EgoNet算法</td><td>EgoNet</td><td>en</td></tr><tr><td>鲁汶社区发现</td><td>Louvain</td><td>louvain</td></tr><tr><td>强连通分量</td><td>Strongly Connected Components</td><td>scc</td></tr><tr><td>监听标签传播</td><td>Speaker-listener Label Propagation Algorithm</td><td>slpa</td></tr><tr><td>莱顿算法</td><td>Leiden</td><td>leiden</td></tr><tr><td>带权重的标签传播</td><td>Weighted Label Propagation Algorithm</td><td>wlpa</td></tr><tr><td rowspan="3">模式挖掘</td><td>三角计数</td><td>Triangle Counting</td><td>triangle</td></tr><tr><td>子图匹配算法</td><td>Subgraph Isomorphism</td><td>subgraph_isomorphism</td></tr><tr><td>模式匹配算法</td><td>Motif</td><td>motif</td></tr></tbody></table>



## 2 功能介绍

### 2.1 图分析框架 

图分析框架作为图分析引擎的“骨架”，可以联合多种模块有效的耦合协同工作。一般分为预处理、算法过程、结果分析三个阶段。

预处理部分用于读入数据及参数进行图构建及相关信息的存储统计，并整理出算法过程所需的参数及数据。

算法过程会根据得到的数据通过特定的算法进行逻辑计算，并得到结果数据。 结果分析部分根据得到的结果数据进行个性化处理（如取最值等），并将重要的信息写回和打印输出操作。

### 2.2 点边筛选器 

点边筛选器作用于图分析引擎中的 Procedure 和 Embed 模式。对于图存储数据源可根据用户需要和实际业务场景对图数据进行筛查，选择有效的点边进行图结构的构建。 2.3 一致性快照 TuGraph 中的 Procedure 和 Embed 模式能够提供数据“快照”，即建立一个对指定数据集的完全可用拷贝，该拷贝包括相应数据在某个时间点（拷贝开始的时间点）的镜像。由于 OLAP 的操作仅涉及读操作而不涉及写操作，OlapOnDB 会以一种更紧凑的方式对数据进行排布，在节省空间的同时，提高数据访问的局部性。 2.4 块状读写模块 块状读写模块作用于图分析引擎中的 Standalone 模式，用于对不同外部数据源的数据进行高效读入，同时也包含对内部算法处理后的图数据结果写回。 2.5 参数模块 参数模块作用于分析引擎中的 Standalone 模式，用于对图的一般信息（如数据来源，算法名称，数据输入、输出路径，顶点个数等）以及根据不同数据来源、不同算法所配置的不同信息参数进行接受和整理，传输给图算法及各个模块，同时将最终结果模块化展示。

## 4 小结

综上，图分析引擎可以高效、快速的处理多种来源的数据，其并行的图构建方式保证了内存占用小的特点。此外，图分析引擎也具有易于安装部署、灵活性高、耦合程度低、易于上手等对用户友好特性，可以帮助用户结合具体业务解决问题。
