Title: 学习 chisel 系列 #1： Install Chisel
Date: 2020-05-10 14:56
Category: IC
Tags: chisel, sbt
Slug: learning_chisel_series_1_install
Author: Qian Gu
Series: Learning Chisel
Summary: 安装 chisel 环境
Status: draft

安装步骤可以看 chisel3 在 Github 主页上的 [安装 guide][chisel_install]，也可以看 sbt 
的 [安装 guide][sbt_install]。下面是我的安装记录，不过增加了国内如何修改 maven repo 的步
骤，因为 maven 官方服务器在国外，速度实在是太慢了，只有几 KB/s 的样子。

[chisel_install]: https://github.com/freechipsproject/chisel3/blob/master/SETUP.md
[sbt_install]:  https://www.scala-sbt.org/release/docs/Installing-sbt-on-Linux.html

## Install JDK 8

chisel 依赖于 JAVA 8，所以我们得安装对版本。具体的安装方式有很多，Ubuntu 下最简单的方式是
安装 openjdk8，

```
#!bash
sudo apt-get update
sudo apt-get install openjdk-8-jdk
```

安装完成后用 `java -version` 来确认版本。

## Install sbt

直接看 [sbt 官网下载页面][sbt_download] 即可，Ubuntu 使用下面的命令，

```
#!bash
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get install sbt
```

[sbt_download]: https://www.scala-sbt.org/download.html


安装之后就可以使用 `sbt --help` 来查看具体使用方法。

### Override sbt repo setting

因为 maven 官方服务器在国外，国内下载的速度非常非常慢。我一开始按照教程直接从国
外下载，尝试了十几次都上完全下不动，从网上搜索了一下，学习了 java 和 maven 的背
景知识，才知道原来要修改设置，使用国内的源速度会快很多。

网上的大部分资料都是 aliyun 的说明，所以我一开始按照 aliyun 的说明修改了设置，
但是发现也完全下载不动，怀疑是设置不对、我自己网络的问题，折腾了一上午也没有搞
定，一度怀疑人生。后来无意中发现了网易的源，尝试了一下竟然成功了。

从 sbt 的文档中可以知道要想对某个特定项目使用自定义的 rerp，步骤如下：

1. 设置 repo 的地址
2. 打开 override 的开关

第一步 repo 的设置格式如下，

在 `~/.sbt` 目录下面新建一个 `repositories` 的文件，在文件中添加下面的内容即可：

```
[repositories]
  local
  mirrors-163: https://mirrors.163.com/maven/repository/maven-public
  maven-central
```
sbt 运行时会按照 `local > my-maven-repo > my-ivy-repo` 的顺序挨个查找。

第二步在命令行中加上 `-Dsbt.override.build.repos=true -v` 选项。（其中 `-v` 是
为了显示更多信息，方便定位问题）。

### install chisel3

因为 chisel3 本质是 scala 的一种方言，虽然 scala 可以和 gcc 一样安装在整个系统范围内，但
是 scala 更推崇为每个 project 安装一个版本，所以还推出了 `sbt` 工具来管理。因为 chisel 
tutorial 已经建好了 project，我们直接使用即可。

首先下载 chisel tutorial，

```
#!bash
git clone https://github.com/ucb-bar/chisel-tutorial.git
```

然后 cd 到这个目录下，按照教程直接 `sbt run -Dsbt.override.build.repos=true -v`，我的
速度可以达到 200KB/s，可能是因为我网络的原因，经常下载到一半就会自动断掉，查看 log 是服务器
拒绝访问，我怀疑是服务器为了公平，防止个别人长时间占用大带宽所以会定时拒绝访问。解决方法也很
无脑，不断重复执行 `sbt run` 即可，大概重复十几次就能下载全所有的依赖包，最后提示
 hello world 编译成功：

> [info]   Compilation completed in 29.212s.
> [info] running hello.Hello 
> 
> [info] [0.003] Elaborating design...
> 
> [info] [11.039] Done elaborating.
> 
> Total FIRRTL Compile Time: 2369.9 ms
> 
> Total FIRRTL Compile Time: 11.2 ms
> 
> End of dependency graph
> 
> Circuit state created
> [info] [0.013] SEED 1589008225153
> test Hello Success: 1 tests passed in 6 cycles taking 0.207663 seconds
> [info] [0.101] RAN 1 CYCLES PASSED
> [success] Total time: 107 s (01:47), completed May 9, 2020 3:10:50 PM

## Install verilator & gtkwave (Optional)

前面的环境已经可以，已经可以将 chisel 转换成 verilog 代码，所以这两个工具不是必须的。如果想
对产生的 verilog 做进一步的仿真和 debug，则需要安装这两个工具，分别替代 `vcs` 和 `verdi`。

verilator 是一款开源免费的仿真器，可以给 verilog 生成 cycle 级别的 C++/SystemC 仿真模型
，是 vcs 的免费替代品。最省事的方式是用 `apt-get` 安装，也可以自己下载源码在本地编
译。

```
#!bash
sudo apt-get install verilator
```

gtkwave 顾名思义，是一款基于 gtk 界面的波形查看工具，是 verdi 的免费替代品，直接用 
`apt-get` 安装即可，

```
#!bash
sudo apt-get install gtkwave
```

至此，chisel 的环境就算全部 ok 了。

<br>

## Ref

[Installing sbt on Linux][sbt_install]

[sbt换源，解决速度慢的问题](https://segmentfault.com/a/1190000021817234)

[Override all resolvers for all builds](https://www.scala-sbt.org/1.x/docs/Library-Management.html#Override+all+resolvers+for+all+builds)
