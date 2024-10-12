# 空间数据类型在图数据库中的应用案例

空间地理数据也是天然适合使用图数据库的一种场景，我们先来看看在图数据库中使用空间数据的几个经典场景:

## 场景案例一：判断某空间类型内的坐标

日常生活中我们通常需要在地图中查询距离自己一定距离内的景点/美食信息。对应的在图数据库中，即为判断哪些坐标在以某点为中心的圆形或矩形区域内，对应的Cypher查询语句如下:

```
# 判断在圆形区域内
WITH point({latitude: $latitude, longitude:$longitude}) AS radiusCenter
MATCH (p:Point)-[:HAS_GEOMETRY]-(poi:PointOfInterest)-[:HAS_TAGS]->(t:Tags)
    WHERE point.distance(p.location, radiusCenter) < $radius
RETURN p {
    latitude: p.location.latitude,
    longitude: p.location.longitude,
    name: poi.name,
    categories: labels(poi),
    tags: t{.*}                       
} AS point

# 判断在矩形区域内
MATCH (p:Point)-[:HAS_GEOMETRY]-(poi:PointOfInterest)-[:HAS_TAGS]->(t:Tags)
   WHERE point.withinBBox(
        p.location,
       point({longitude: $lowerLeftLon, latitude: $lowerLeftLat}),
       point({longitude: $upperRightLon, latitude: $upperRightLat})
   )
RETURN p {
  latitude: p.location.latitude,
  longitude: p.location.longitude,
  name: poi.name,
  categories: labels(poi),
  tags: t{.*}
} AS point



```

## 场景案例二：判断路径与某空间类型是否重合

移动物体的行动轨迹可以被抽象成一条线，这条轨迹往往伴随着时序信息。日常生活中，有时候我们想知道哪部分行动轨迹和给定区域有重合。对应在图数据库中，即判断一系列坐标中哪些坐标落在在空间类型内。对应的Cypher查询语句如下:

```
WITH point({latitude: $latitude, longitude: $longitude}) AS radiusCenter
MATCH (g: Geometry)
    WHERE any(
        p IN g.coordiates WHERE point.distance(p, radiusCenter) < $radius
    )
RETURN [n IN g.coordinates | [n.latitude, n.longitude]] AS route



```

# 空间数据类型在TuGraph-DB中的实现

## 需求分析

结合上述案例，我们可以分析总结出对空间数据类型的需求:

-   • 支持不同坐标系下（包括地球地理坐标系，平面几何坐标系等）不同空间数据类型（包括Point、LineString,、Polygon）的存储与创建
    
-   • 支持不同坐标系下的常见空间查询操作, 包括Distance、BoundingBox、Disjoint（判断两个数据是否相交）的查询等
    
-   • 支持空间数据索引（R-Tree）
    
-   • 支持常见空间数据格式的导入（ESRI Shapefile data / OpenStreetMap）
    
-   • 支持空间数据的可视化
    

## 空间数据类型的表示

空间数据类型可以用不同的坐标系来表示，EPSG<sup>[1]</sup>是一个标准化的地理空间参考系统标识符集合， 用于标识不同的地理空间参考系统，包括坐标系统、地理坐标系、投影坐标系等。通常使用EPSG编码表示数据的坐标系。行业内一般采用

-   • WGS84坐标系（没错，就是GPS系统的坐标系），标识符为EPSG 4326
    
-   • Cartesian（笛卡尔）坐标系（没错，就是你高中数学学的直角坐标系），标识符为EPSG 7203
    

WGS84是全球定位系统(GPS)的基础，允许全球的GPS接收器确定精确位置。几乎所有现代GPS设备都是基于WGS84坐标系来提供位置信息。在地图制作和GIS（地图制作和地理信息系统）领域，WGS84被广泛用于定义地球上的位置。这包括各种类型的地图创建、空间数据分析和管理等。

Cartesian（笛卡尔）坐标系，又称直角坐标系，是一种最基本、最广泛应用的坐标系统。它通过两条数轴定义一个平面，三条数轴定义一个空间，这些轴互相垂直，在数学、物理、工程、天文和许多其他领域中有着广泛的应用。

## 空间数据类型的实现

OGC(Open Geospatial Consortium) 定义了空间数据的标准表示格式，分别为EWKT(extended well known text)与EWKB(extended well known binary)格式，用于在不同系统和平台之间交换和存储空间数据，现已被广泛采用。

### EWKT

EWKT格式数据如下所示，先指定空间数据类型，再在括号内指定具体的坐标，一个坐标对表示一个点，每个坐标对之间用逗号隔开。其中，对于Polygon类型的数据，第一个坐标对需要与最后一个坐标对相同，形成闭合的面。

```
SRID=s;POINT (<x> <y>)
SRID=s;LINESTRING(<x1> <y1>, <x2> <y2>, …)
```

**注:** SRID默认为4326, 可以不指定

### EWKB

EWKB格式数据如下

-   • 第0-1位: 表示编码方式 00表示大端法，01表示小端法
    
-   • 第2 - 5位: 空间数据类型
    
-   • 0100: point
    
-   • 0200: linestring
    
-   • 0300: polygon
    
-   • 第6 - 9位: 数据维度
    
-   • 0020: 二维
    
-   • 0030: 三维
    
-   • 第10 - 17位: 坐标系的EPSG编码
    
-   • 第18 - n位: double类型的坐标对的16进制表示
    

**注:** 对于POINT类型，其EWKB格式为定长存储，固定长度为50，而对于其他类型，则为不定长。

### 实现思路

在TuGraph-DB的实现，基于boost geometry库的基础上进行封装，用EWKB格式存储数据，其中Point类型为定长存储50，其余皆为变长存储。我们支持了Point, Linestring与Polygon三种类型，同时支持了WGS84, CARTESIAN两种坐标系，数据类型与坐标系均可根据需要拓展。

## 在TuGraph-DB中使用空间数据类型

## 定义空间数据类型

TuGraph-DB当前已经支持Point、Linestring与Polygon三种类型

-   • Point：点，创建方式例如POINT(2.0, 2.0, 7203)
    
-   • Linestring：折线，创建方式例如LINESTRING(0 2,1 1,2 0)
    
-   • Polygon：多边形，创建方式例如POLYGON((0 0,0 7,4 2,2 0,0 0))
    

其中坐标点都是double型

## 相关函数介绍

创建空间数据相关函数，以Point为例：

| **函数名** | **描述** | **输入参数** | **返回值类型** |
| --- | --- | --- | --- |
| Point() | 根据坐标或EWKB创建Point | 坐标对(double, double) / EWKB format(string) | point |
| PointWKB() | 根据WKB与指定SRID创建Point | WKB format(string) , SRID(int) | point |
| PointWKT() | 根据WKT与指定SRID创建Point | WKT format(string) , SRID(int) | point |

查询用相关函数：

| **函数名** | **描述** | **输入参数** | **返回值类型** |
| --- | --- | --- | --- |
| Distance() | 计算两个空间数据间的距离 |   
 |   
 |
| 注：要求坐标系相同 | Spatial data1, Spatial data2 | double |   
 |
| Disjoint() | 判断两个空间数据是否相交 |   
 |   
 |
| 注：开发中 | Spatial data1, Spatial data2 | bool |   
 |
| WithinBBox() | 判断某个空间数据是否在给定的长方形区域内 |   
 |   
 |
| 注：开发中 | Spatial data, Point1 | bool |   
 |

使用实例如下：

```
# 创建包含空间数据类型的点模型
CALL db.createVertexLabel('food', 'id', 'id', int64, false, 'name', string, true,'pointTest',point,true) 

# 插入标记美食点的数据
CREATE (n:food {id:10001, name: 'aco Bell',pointTest:point(3.0,4.0,7203)}) RETURN n

# 创建具有折线属性的点模型
CALL db.createVertexLabel('lineTest', 'id', 'id', int64, false, 'name', string, true,'linestringTest',linestring,true)

# 插入具有折线属性的点数据
CREATE (n:lineTest {id:102, name: 'Tom',linestringTest:linestringwkt('LINESTRING(0 2,1 1,2 0)', 7203)}) RETURN n

# 创建具有多边型属性的点模型
CALL db.createVertexLabel('polygonTest', 'id', 'id', int64, false, 'name', string, true,'polygonTest',polygon,true)

# 插入具有多边型属性的点数据
CREATE (n:polygonTest {id:103, name: 'polygonTest',polygonTest:polygonwkt('POLYGON((0 0,0 7,4 2,2 0,0 0))', 7203)}) RETURN n



```
