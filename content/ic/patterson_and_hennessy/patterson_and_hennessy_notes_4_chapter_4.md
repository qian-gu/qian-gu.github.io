Title: Patterson and Hennessy 学习笔记 #4 —— Chapter 4 The Processor
Date: 2020-12-08 22:28
Category: IC
Tags: Patterson and Hennessy
Slug: learning_patterson_and_hennessy_notes_4_chapter_4
Author: Qian Gu
Series: Patterson & Hennessy Notes
Summary: Patterson and Hennessy 读书笔记，第四章
Status: draft

> In a major matter, no details are small.
> 
>   -- French Proverb

## Intro

第一章中提到，影响一个计算机性能的因素有 3 个：

+ 指令总数
+ 时钟周期
+ 每条指令的执行时钟数（CPI）

从第二章可知对于一个特定程序，由编译器和 ISA 共同决定了第一个因素：指令总数。而一个 processor 的实现决定了另外两个因素，所以这章介绍 RISC-V 处理器两种不同实现的 `control path` 和 `data path`。


## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**谬论：就像左移指令可以代替 2 的指数次的乘法，右移指令可以代替除数是 2 的指数的除法运算。**

对于 unsigned 类型来说的确如此，但是对于 signed 类型的数据则显然不对，负数右移后在高位补充符号位，最后会永远是 -1，不会变成 0。

**陷阱：结合律不适用于浮点运算**

对于 integer 的运算，即使会发生 overflow 结合律也是适用的。但是对于浮点数，结合律是不适用的，因为计算机内的浮点数是用有限的 bit 来近似真实的数字，无法保存 overflow 的数字。这里有意思的是，对于定点的整数而言即使发生了 overflow 结合律仍然是适用的，找个例子就可以验证下面的等式是成立的，

$$-128+127+3 = -128+(127+3) = -128+(-126)=2$$

原因也很简单：整数运算 overflow 只会影响高位 bit，低位 bit 是不受影响的。