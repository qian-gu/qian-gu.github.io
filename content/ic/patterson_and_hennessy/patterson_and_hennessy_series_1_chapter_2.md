Title: Patterson and Hennessy 学习系列 #1 —— Chapter 2
Date: 2020-06-13 12:55
Category: IC
Tags: Patterson and Hennessy
Slug: learning_patterson_and_hennessy_series_1_chapter_2
Author: Qian Gu
Series: Learning Patterson & Hennessy
Summary: Patterson and Hennessy 读书笔记，第二章
Status: draft

## Chapter 2 Instructions: Language of the Computer

> I speak Spanish to God, Italian to women, French to men, and German to my horse.
> 
>   -- Charles V, Holy Roman Emperor

### Introduction

ISA 和人类语言不同，掌握了一个 ISA，其他的就很容易掌握了。不同的 ISA 之所以能做到相似，并不是一件偶然事件，而是有背景的：

1. 所有的计算机用到的硬件技术有着相似的底层原则
2. 所有的计算机都必须提供一组最基本的操作
3. 计算机设计者有着共同的目标：找到一种语言（ISA），在最大化性能、最小化成本和能耗的前提下，可以轻松地构建硬件和编译器

    quote

`Simplicity of the equipment` 这个设计哲学是永恒的，1950 年代如此，现在设计计算机的时候依然如此。本章的内容就是学习一种遵循这个哲学的 ISA —— `RISC-V`，主要内容如下，

+ 硬件中如何体现这一哲学
+ 高层的编程语言和底层的原语是如何映射的

!!! note
    如原文所说，每个小节围绕一个指令子集，讲清楚设计原理和高层编程语言的关系，这种 top-down, step-by-step 的方式可以做到真正的深入浅出，让你不仅知其然，还知其所以然。很多资料（特别是国内的教科书）不注重知识背后的原理和方法，采用灌输式的方法，很容易打击学习者的兴趣。

### Operations of Computer Hardware

quote

加法之类的 RISC-V 指令的操作数很自然的都是 3 个：两个源操作数，一个目的操作数，“让所有的指令都包含相同数量的操作数”体现了 **保持硬件设计的简单性** 这一设计哲学。这个例子的背后隐藏着第一条设计原则：

> **Desing Principle 1: Simplicity favors regularity.**

### Operands of the Computer Hardware

前面已经约束了 RISC-V 运算指令必须有 3 个操作数，在此基础上进一步约束，这 3 个操作数必须来自于 32 个 64bit 的寄存器之中。这个约束的背后隐藏着第二条设计原则：

> **Design Principle 2: Smaller is faster.**

这个原则并不是绝对的，31 个寄存器并不是一定就比 32 个寄存器更快，但是这个原则依然非常重要。计算机设计者必须平衡好一组矛盾，程序希望寄存器越多越好，硬件希望寄存器少一些以提高时钟频率。RISC-V 使用 32 个而不是 31 个寄存器的另一个原因是指令格式中的 bit 数正好可以寻址 32 个寄存器。

RISC-V 的命名惯例：每个寄存器以 `x` 开头，后面加上序号，所以寄存器的名字为 `x0`, `x1`, ... `x31`。

大小端：
1. 使用地址最左边的 bit（即 big end 的 byte）作为地址
2. 使用地址最右边的 bit（即 little end 的 byte）作为寻址地址

!!! note
    地址对齐：很多体系结构中，要求 word 的地址必须是 4Byte 对齐，doubleword 的地址必须是 8Byte 对齐。
    RISC-V 和 x86 没有对齐约束，但是 MIPS 有约束。

许多程序中都会用到常数，比如地址自增 1 来自动指向数组中的下一个元素。如果每次都从 memory 中用 load 指令来搬运这个常数则显得很低效。解决方法就是把常数放在指令中。常数作为操作数是非常常见的，实际上，`addi` 是 RISC-V 中最常见的指令。而常数 0 更加重要，它可以提供各种用法来简化指令集。比如，想得到一个数的相反数，则用 0 减去它即可。所以 RISC-V 用专用的寄存器 `x0` 来存储常数 0。（**common case fast** 哲学的体现）

### Signed and Unsigned Numbers

参考以前的一篇总结：[原码、反码、补码](https://qiangu.cool/posts/cs/signed_number_representations.html)

todo： 补充补码求值公式/overflow的检测规则

补码名字的来源：

$$x + (-x) = 2^n$$
$$-x = 2^n - x$$

## Representing Instrcutions in the Computer


## Ref




