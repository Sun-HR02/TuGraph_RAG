# TuGraph Analytic 图数据集成

## 图数据集成

小伙伴们想玩一玩图计算，数据的导入工作总是绕不开的一个环节。为了降低大家数据导入操作的成本，提升图计算的整体使用体验，TuGraph Analytics推出了“图数据集成”能力，帮助大家通过简单配置完成数据导入工作。

要实现图上的数据处理，可大致分为三个阶段：

1.  1. **数据准备**：准备图的点边的原始数据。如文件（CSV/JSON）、Hive表、Kafka消息队列等数据源。
    
2.  2. **数据导入**：将原始的表结构数据（结构化/半结构化）格式化成图结构写入图引擎。一般采用编写SQL或基于引擎API开发数据导入任务。
    
3.  3. **数据分析**：基于图引擎对已经导入的图格式数据分析处理。一般使用GQL、Gremlin、Cypher等图分析语言处理，复杂的图算法（图上的迭代、采用、推理等）可能需要用户自己开发UDF。（Java/Python）
    

因此，实现图上的数据分析的前置动作便是图数据导入，简称“构图”。这里我们使用“图数据集成”的说法，是沿用了传统数据仓库里“数据集成”的概念。

TuGraph Analytics可以通过编写SQL代码实现高效的数据导入到图的能力。但当数据源头和表字段过多时，编写出来的DSL代码往往非常冗长，而且用户手动编写的代码容易出现插入的字段映射错位、数量不匹配等问题。为此，TuGraph Analytics的Console平台为用户提供了到图的一键“数据集成”功能，允许用户可在界面中选择输入表和对应的目标点边，平台会自动化生成对应的DSL代码，实现图数据导入，避免了大量冗长的代码的编写和校对工作。

## 任务设计

类似传统数据库表的INSERT操作，图数据集成则是向图的点边表插入数据。图中的点边也是一种表结构，每个点边都有相应的属性（对应表结构中的字段），并可以与数据源的表字段一一映射。所以可以通过给定外部输入表和目标点边的映射关系来描述图数据集成任务。

图数据集成任务维护了用户填写的输入表到图的目标点边的映射关系。映射关系结构为StructMapping的数组，每个StructMapping包含了表名、图名、和对应的字段映射项列表。

```
@EqualsAndHashCode(of = {"tableName", "structName"})
public static class StructMapping {
    private String tableName;
    private String structName;
    private List<FieldMappingItem> fieldMappings = new ArrayList<>();
}

@EqualsAndHashCode(of = {"tableFieldName", "structFieldName"})
public static class FieldMappingItem {
    private String tableFieldName;
    private String structFieldName;
}
```

任务发布阶段，根据映射关系生成相应的构图dsl代码。代码生成主要使用Velocity模板引擎框架，其模板如下:

```
USE GRAPH ${graphName};

#foreach(${insert} in ${inserts})
insert into ${graphName}(
    #foreach(${strcut} in  ${insert.structs})
    ${strcut.structName}.${strcut.structFieldName},
    #end
    ${END_FLAG}
) select
    #foreach(${strcut} in ${insert.structs})
    ${strcut.tableFieldName},
    #end
    ${END_FLAG}
from ${insert.tableName};
    
#end
```

**映射关系需满足如下约束：**

1.  1\. 一个目标点或边的数据只能来自一个输入表，而一个输入表可以写入多个点边。
    
2.  2\. 输入表字段类型和目标点边字段类型需要相同。
    
3.  3\. 目标点边上的meta字段（点id，边srcId, 边targetId等）必须插入。
