Title: Verilog 项目配置
Date: 2015-04-20
Category: IC
Tags: project setting
Slug: verilog-project-setting
Author: Qian Gu
Summary: 一份简单的 verilog 项目设置

*参考书和网上的资料，自己总结的一个简单的项目设置，虽然实验室的项目和公司比起来很不规范，都是学生自己做的玩具类型的项目，但是聊胜于无，给自己一个参考。*

## Directory
* * *
分类存放文件，项目的目录结构如下：

    project
     |--- src             // 设计代码
     |     |--- header    // header file
     |     |--- module1   // module1.v
     |     |--- module2   // module2.v
     |     |--- ...
     |--- sim             // 验证代码
     |     |--- module1   // tb-module1.v
     |     |--- module2   // tb-module2.v
     |     |--- ...
     |--- vrf             // 编译、运行脚本
     |--- doc             // 文档
           |--- html      // doxverilog 文档
           |--- ref       // 设计参考文档

<br>

## Document
* * *

1. 省略应用文档（Datasheet、SPEC）

    实验室的小项目，设计很简单，而且是自己用，就不需要应用文档了。

2. 设计文档 —— doxverilog 生成

    最重要的文档，可以使用 doxverilog 生成。但是貌似 doxverilog 对 verilog 的支持实际上并不是非常好。结果勉强可以接受。

    除了常规的信息注释外，在源文件的注释中主要包含以下内容：

    1. 模块需要的文件列表（子模块文件）

    2. 模块的功能描述

    3. 模块的端口描述（直接在 ASNI-C 风格的端口声明处注释）

    4. 模块的参数配置

    5. 注意事项（`//% @note`）

    6. 参考文档列表

<br>

## Ref

