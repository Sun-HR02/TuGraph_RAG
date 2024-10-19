# 用GraphInsight打造可视化分析TuGraph

## 简介

图的可视化是分析和理解图数据的一种重要手段。TuGraph 内置了TuGraph Browser，为大多数用户提供了一个简单易用的图可视化界面。由于 TuGraph Browser 不支持自定义界面，因此一些有自定义界面需求的用户只能选择自行搭建新的前端界面。11月22日，蚂蚁集团将开源 GraphInsight（下文简称GI），该工具解决了快速搭建自定义图分析界面的问题。

作为例子，我们使用 GI 搭建了 TuGraph Explorer，一个与 TuGraph Browser 不一样的可视化前端。 用户可以前往 GitHub 下载 TuGraph Explorer 的前端资产包，并将其与 TuGraph 连接进行图可视化展示，具体步骤参看说明文档。



GraphInsight 是基于 AntV 开源技术栈构建的一款图可视化分析应用研发工具。开发者可根据业务需求，在线进行产品模块的组合搭建，快速生成新的图分析应用。使用GI，用户可以：

-   快速验证想法，享受搭积木的乐趣
    
-   零代码上手开发，专注你所关心的
    
-   极速部署上线，一切只为开放而生
    

TuGraph 是蚂蚁集团开源的高效 HTAP 图数据库。**它提供了完备的图数据库基础功能和成熟的产品设计，拥有完整的事务支持和丰富的系统特性，单机可部署，使用成本低，支持TB级别的数据规模。**随着 TuGraph 的开源，图数据库领域将迎来一款性能卓越、功能完备、生态丰富的开源产品。开发者可以聚焦应用层，轻松打造属于自己的图应用，从而提升行业整体技术应用水平。

**TuGraph 致力于打造开放的图计算生态**。除了完全开放TuGraph的代码外，我们还积极与其他系统实现对接。目前，TuGraph 已经对接了开源监控系统 Grafana, Prometheus，以及 HDFS，HIVE，Kafka，MySQL 等数据源。近期，我们开源了 OGM（Object Graph Model），方便用户使用面向对象的编程模式来调用 TuGraph。GraphInsight 是 TuGraph 对接的首个第三方图可视化工具，它将大大扩展 TuGraph 的可定制能力。未来，我们将继续接入更多生态工具，推进图数据库的标准化。

## **TuGraph 可视化工具简介**

-   TuGraph Browser：是 TuGraph 自带的可视化开发工具，主要用于开发人员进行数据和模型的操作。以及对服务资源实时状态的监控。
    
-   TuGraph Explorer：是基于 GI 搭建的 TuGraph 可视化分析工具，主要用于数据分析师和解决方案架构师对数据之间潜在关系和价值的挖掘。
    
-   Graphinsight：是基于 AntV 开源图技术栈构建的一款产品，它既是一款图可视化分析应用研发的工具，也是图可视分析的工具。可以供前端开发工程师基于 GI 提供的 SDK 进行图可视化应用的二次开发。也可以供产品解决方案架构师通过可视化的方式搭建带有业务语义的图应用。
    
-   TuGraph App Store：是基于 TuGraph 搭建的图应用开放市场，以 TuGraph DB 作为底层引擎，用户可以使用 GI 或通过 TuGraph DB 提供的 API 自主研发图应用，也可以通过 TuGraph App Store 进行图应用的分享和交流。
    
