Title: 学习 chisel 系列之 2： Chisel Tutorial
Date: 2020-05-10 14:56
Category: RISC-V
Tags: chisel
Slug: learning_chisel_series_2_chisel_tutorial
Author: Qian Gu
Summary: 学习 Chisel 官方教程。
Status: draft

[chisel 环境安装][install_chisel]成功之后，就可以正式开始 chisel 的学习之旅了。

[install_chisel]: https://qiangu.cool/riscv/learning_chisel_series_1_install.html

## Chisel Tutorial

[Chisel Tutorial][tutorial] 是官方提供的教程，阅读 wiki，走完整个流程，就能掌握
chisel 的基本语法了。

[tutorial]: https://github.com/ucb-bar/chisel-tutorial

## Doc generattion

Tutorial 下面的 `doc` 目录里面包含了一篇 chisel 入门论文，只要按照 Makefile 中的提示
把所有的依赖包都安装好，就可以生成最终的 pdf 论文了。

<br>

## Wiki

### wire

只要用 `val` 声明一个变量，只要这个变量不是用 `Reg` 类型来赋值，那么它就会被解释成一个 
verilog 中的 `wire`，因此这个变量也可以随意赋值给其他变量，就像 verilog 中的 `wire` 的行
为一样。

### reg

verilog 中声明一个 `reg`，实际最终综合出来的可能是一条线 `wire`，也有可能是一个真正的寄存
器 `register`，这是 verilog 语法的历史问题导致的。即使是很多老手，也经常声明错。

chisel 和 verilog 的不同之处在于，如果一个 `Reg` 变量，那么它一定会综合出一个寄存器。

### bit  with inference

chisel 可以根据信号的连接，自动分析信号的位宽，所以我们可以省掉 verilog 中繁琐的位宽声明。


## Ref
