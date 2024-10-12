## TuGraph开源JAVA客户端工具TuGraph-OGM，无缝对接JAVA开发生态

## 简介

TuGraph 图数据库提供了 JAVA、C++、Python 等多种语言的 SDK 支持，方便客户在各种场景下使用。用户使用 SDK 向TuGraph服务器发送Cypher请求，服务器则以 JSON形式返回数据。近日，TuGraph 推出了一款面向 JAVA 客户端用户的开发工具 TuGraph-OGM (Object Graph Mapping)，为用户提供了对象操作接口，相较 Cypher/JSON 接口应用起来更加便捷。

OGM 类似于关系数据库中的 ORM（Object Relational Model），可以将数据库返回的数据自动映射成 JAVA 中的对象，方便用户读取，而用户对这些对象的更新操作也可以被自动翻译成 Cypher 语句发送给服务器。这样即便是完全不懂 Cypher 的用户，也可以通过操作对象与数据库进行交互，大大降低了图数据库的使用门槛。

TuGraph-OGM 同时也兼容其他开源产品 OGM 工具如 Neo4j-OGM，方便用户将工程在不同数据库与 TuGraph数据库间无缝迁移。本文将对 TuGraph-OGM 进行全面的介绍。

## 0 映射原理

TuGraph-OGM 将 JAVA 对象映射为图的对象，类映射为点，类的属性映射为图中的属性，类中的方法映射为操作 TuGraph 的查询语句。



以电影场景为例，对演员、电影、导演之间的关系进行数据化，就形成了非常典型的图数据。举一个简单的示例，演员Alice在1990年和2019年分别出演了两部电影《Jokes》和《Speed》，其中《Jokes》的导演是Frank Darabont。

以图的思维来看，演员、导演、电影可以被映射为三种不同的节点，而出演、执导可以被映射为两种边，映射结果如上图所示，将数据存入图数据库后，相关的开发人员就可以使用各类图查询语言对数据进行查询。

但对非图数据库相关的开发人员来说，这个例子中的演员、导演、电影作为实体，同样可以映射为类中的对象，而与实体相关联的对象可以通过集合存储，这是大多数开发人员熟悉的领域。



## 1 TuGraph-OGM架构

TuGraph-OGM可被看做一个"翻译器"，主要功能是将开发人员对JAVA对象的一些操作翻译为TuGraph可理解的图查询语言Cypher请求，并将该操作返回的结果，再次翻译为JAVA对象。



## 2 使用示例

详细示例请参考tugraph-ogm-integration-tests 在`pom.xml`中引入依赖

```xml
<dependency>

<groupId>org.ne04j</groupId>

<artifactId>ne04j-ogm-api</artifactId> «version>0.1.0-SNAPSHOT</version> </ dependency>

‹dependency>

<groupId>org.ne04j</groupId>

‹artifactId>ne04j-ogm-core</artifactId> «version>0.1.0-SNAPSHOT</version> </ dependency>

‹dependency>

<groupId>org.ne04j</groupId>

‹artifactId>tugraph-rpc-driver</artifactId> «version>0.1.0-SNAPSHOT</version> </ dependency>
```



### **2.1 构建图对象**

首先需要通过注解标明图中的实体。

@NodeEntity：该注解标明的类为节点类。

@Relationship：用于标明边，同时@Relationship中可指定label与边的指向。

@Id：用于标明identity，是OGM中数据的唯一标识。



### **2.2 与TuGraph建立连接**

当前TuGraph-OGM提供了RPC driver用于连接TuGraph，具体配置如下所示：

```java
// 配置

String databaseUri = "list://ip:port";

String username = "username";

String password = "password";

//启动driver

Driver driver = new RpcDriver();

Configuration.Builder baseConfigurationBuilder = new Configuration.Builder()

•uri(databaseUri)

• verifyConnection (true)

•credentials (username, password);

driver.configure(baseConfigurationBuilder.build());

// 开启session

SessionFactory sessionFactory = new SessionFactory(driver, "entity_path");

Session session = sessionFactory.openSession();
```



### **2.3 通过OGM进行增操作**

OGM支持对TuGraph的实体执行CRUD 操作，同时支持发送任意TuGraph支持的Cypher语句，包括通过CALL调用存储过程。

**CREATE**

在完成图对象的构建后，即可通过类的实例化创建节点，当两个节点互相存储在对方的集合（该集合在构建时被标注为边）中，就形成了一条边，最后使用session.save方法将数据存入数据库。

注意：TuGraph数据库为强schema类型数据库，在创建实体前需要该数据的label已经存在，且新建过程中需要提供唯一的主键。

```
Movie jokes = new Movie（"Jokes"，1990）； // 新建Movie节点jokes session.save(jokes); // 将jokes存储在TuGraph中

Movie speed = new Movie("Speed", 2019);

Actor alice = new Actor("Alice Neeves");

alice.actsIn(speed);

session.save(speed);

/1 将speed节点与alice节点通过ACTS_IN进行连接 11 存储speed节点以及speed关联的边和alice节点
```

### **2.4 通过OGM进行删操作**

**DELETE**

使用session.delete方法删除节点，同时会删除与节点相关联的所有边。

```java
session.delete(alice); // 删除alice节点以及相连的边

Movie m = session. load(Movie.class, jokes.getId); // EjokesTaMidsiXjokes# 点

session.delete(m);

// 清空数据库

session.deleteAll(Movie.class);

session.purgeDatabase ();

1/ 删除所有Movie节点

// 删除全部数据
```



### **2.5 通过OGM进行改操作**

**UPDATE**

修改已创建的节点的属性，再次调用session.save方法会对节点进行更新。

```java
speed.setReleased (2018);

session.save(speed);
```



### **2.6 通过OGM进行查操作**

**MATCH**

session.load方法用于根据节点id查找节点。 session.loadALL方法用于批量查找节点，支持通过多个节点id查找节点、查找某一类型的所有节点、带有filter的查询。 filter查询需要新建Filter，传入参数ComparisonOperatorx0;可选为：EQUALSx0;、GREATER\_THANx0;、LESS\_THAN

![](https://mdn.alipayobjects.com/huamei_qcdryc/afts/img/A*J3Z1TrA0BncAAAAAAAAAAAAADgOBAQ/original)

**QUERY WITH CYPHER**

OGM支持通过queryForObject、query方法向TuGraph发送Cypher查询，由于Cypher查询的灵活性，需要用户自行指定返回结果格式。

session.queryForObject方法：需要在方法第一个参数处指定返回类型，可设定为某一实体类或数字类型。

session.query方法：Cypher查询的返回结果被存储为Result类型，其内部数据需要用户自行解析，以下方代码为例，传入数据库的Cypher为CREATE查询，返回结果createResult可被解析为QueryStatistics，可获取到此次查询被创建的节点与边的数目。

![](https://mdn.alipayobjects.com/huamei_qcdryc/afts/img/A*lkxXS660eEgAAAAAAAAAAAAADgOBAQ/original)

## 关于TuGraph

高性能图数据库 TuGraph（https://github.com/TuGraph-family/tugraph-db） 由蚂蚁集团和清华大学共同研发，经国际图数据库基准性能权威测试，是 LDBC-SNB 世界纪录保持者，在功能完整性、吞吐率、响应时间等技术指标均达到全球领先水平，为用户管理和分析复杂关联数据提供了高效易用可靠的平台。

历经蚂蚁万亿级业务的实际场景锤炼，TuGraph 已应用于蚂蚁内部150多个场景，助力支付宝2021年资产损失率小于亿分之0.98。关联数据爆炸性增长对图计算高效处理提出迫切需求，TuGraph 已被成熟应用于金融风控、设备管理等内外部应用，适用于金融、工业、互联网、社交、电信、政务等领域的关系数据管理和分析挖掘。

2022年9月，TuGraph 单机版开源，提供了完备的图数据库基础功能和成熟的产品设计，拥有完整的事务支持和丰富的系统特性，单机可部署，使用成本低，支持TB级别的数据规模。