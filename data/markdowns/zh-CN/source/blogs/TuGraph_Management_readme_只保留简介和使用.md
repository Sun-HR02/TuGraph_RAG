# TuGraph Management

该仓库是TuGraph的任务管理工具

## 简介

TuGraph Management 是一款为TuGraph开发的算法任务管理工具。采用了sofastack与brpc作为通信框架，并使用sqlite进行持久化存储。

主要功能：

- 算法任务状态持久化存储

- 算法任务结果持久化存储

- 延时触发与定时触发算法任务支持

## 前提条件

- Java 8

- TuGraph Server 部署

## 使用

TuGraph Management使用Maven进行管理，请运行如下命令启动TuGraph Management

`mvn spring-boot:run`

TuGraph Management 使用了sofastack框架，并使用brpc与TuGraph进行通信，sofastack默认端口为`6071`，brpc默认端口为`6091`，如需修改服务端口，请修改`./src/main/resources/application.properties`文件中的对应配置项。

