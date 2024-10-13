# TuGraph-db

## 1. 简介
TuGraph 是支持大数据容量、低延迟查找和快速图分析功能的高效图数据库。
TuGraph的支持邮箱：tugraph@service.alipay.com

主要功能：

- 标签属性图模型
- 完善的 ACID 事务处理
- 内置 34 图分析算法
- 支持全文/主键/二级索引
- OpenCypher 图查询语言
- 基于 C++/Python 的存储过程

性能和可扩展性：

- LDBC SNB世界记录保持者 (2022/9/1)
- 支持存储多达数十TB的数据
- 每秒访问数百万个顶点
- 快速批量导入

## 2. 快速上手

一个简单的方法是使用docker进行设置，可以在DockerHub)中找到, 名称为`tugraph/tugraph-runtime-[os]:[tugraph version]`,
例如， `tugraph/tugraph-runtime-centos7:3.3.0`。

更多详情请参考 [快速上手文档](和 [业务开发指南]

## 3. 从源代码编译

建议在Linux系统中构建TuGraph，Docker环境是个不错的选择。如果您想设置一个新的环境，请参考[Dockerfile]

以下是编译TuGraph的步骤：

1. 如果需要web接口运行`deps/build_deps.sh`，不需要web接口则跳过此步骤
2. 根据容器系统信息执行`cmake .. -DOURSYSTEM=centos`或者`cmake .. -DOURSYSTEM=ubuntu`
3. `make`
4. `make package` 或者 `cpack --config CPackConfig.cmake`

示例：`tugraph/tugraph-compile-centos7`Docker环境

```bash
$ git clone --recursive https://github.com/TuGraph-family/tugraph-db.git
$ cd tugraph-db
$ deps/build_deps.sh
$ mkdir build && cd build
$ cmake .. -DOURSYSTEM=centos7
$ make
$ make package
```

## 4. 开发

我们已为在DockerHub中编译准备了环境docker镜像，可以帮助开发人员轻松入门，名称为 `tugraph/tugraph-compile-[os]:[compile version]`, 例如， `tugraph/tugraph-compile-centos7:1.1.0`。
