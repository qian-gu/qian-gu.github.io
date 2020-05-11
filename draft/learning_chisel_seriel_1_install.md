Title: 学习 chisel 系列之 1： install
Date: 2020-05-10 14:56
Category: IC
Tags: chisel, sbt
Slug: learning_chisel_series_1_install
Author: Qian Gu
Summary: 安装 chisel 环境。

## install JDK 8

## install sbt

安装之后就可以使用 `sbt --help` 来查看具体使用方法了。

## override sbt repo

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

```
[repositories]
local
my-maven-repo: https://example.org/repo
my-ivy-repo: https://example.org/ivy-repo/, [organization]/[module]/[revision]/[type]s/[artifact](-[classifier]).[ext]
```

sbt 运行时会按照 `local > my-maven-repo > my-ivy-repo` 的顺序挨个查找。

第二步在命令行中加上 `-Dsbt.override.build.repos=true -v` 选项。（其中 `-v` 是
为了显示更多信息，方便定位问题）

所以我们只需要在 
`~/.sbt` 目录下面新建一个 `repositories` 的文件，在文件中添加下面的内容即可：

```
[repositories]
  local
  mirrors-163: https://mirrors.163.com/maven/repository/maven-public
  maven-central
```

然后就可以按照教程直接 `sbt run -Dsbt.override.build.repos=true -v`，我的速度可
以达到 200KB/s，可能是因为我网络的原因，经常下载到一半就会自动断掉，查看 log 是
服务器拒绝访问，我怀疑是服务器为了公平，防止个别人长时间占用大带宽所以会定时拒
绝访问。解决方法也很无脑，不断重复执行 `sbt run` 即可，大概重复十几次就能下载全
所有的依赖包，最后提示 hello world 编译成功：

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

<br>

## Ref

[sbt换源，解决速度慢的问题](https://segmentfault.com/a/1190000021817234)
[Override all resolvers for all builds](https://www.scala-sbt.org/1.x/docs/Library-Management.html#Override+all+resolvers+for+all+builds)
