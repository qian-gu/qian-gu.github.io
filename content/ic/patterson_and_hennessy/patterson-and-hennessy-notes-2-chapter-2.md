Title: Patterson and Hennessy 学习笔记 #2 —— Chapter 2 Instructions: Language of the Computer 
Date: 2020-11-29 21:49
Category: IC
Tags: Patterson and Hennessy
Slug: learning-patterson-and-hennessy-notes-2-chapter-2
Author: Qian Gu
Series: Patterson & Hennessy Notes
Summary: Patterson and Hennessy 读书笔记，第二章

> I speak Spanish to God, Italian to women, French to men, and German to my horse.
> 
>   -- Charles V, Holy Roman Emperor

## Introduction

计算机和人很像，要让它服从指挥，就必须使用它的“语言”。计算机语言中基本的单词是指令 `instructions`，整个词汇表叫做指令集（合）`instruction set`。使用不同指令集的计算机就像是不同地方的人，而且指令集之间的区别像是同一种语言的不同“方言”，所以掌握了一个指令集，其他的就很容易掌握了。不同指令集之所以能做到相似，并不是一件偶然事件，而是有其背后的道理：

1. 所有的计算机用到的硬件技术有着相似的底层原则
2. 所有的计算机都必须提供一组最基本的操作
3. 计算机设计者有着共同的目标：找到一种语言（ISA），在最大化性能、最小化成本和能耗的前提下，可以轻松地构建硬件和编译器

> It is easy to see by formal-logical methods that there exist certain [instruction
sets] that are in abstract adequate to control and cause the execution of any
sequence of operations.... The really decisive considerations from the present
point of view, in selecting an [instruction set], are more of a practical nature:
simplicity of the equipment demanded by the [instruction set], and the clarity of
its application to the actually important problems together with the speed of its
handling of those problems.
> 
>  -- Burks, Goldstine, and von Neumann, 1947

**Simplicity of the equipment** 这个设计哲学不仅适用于 1950 年代也适用于现代计算机。本章的内容就是学习一种遵循这个哲学的 ISA —— `RISC-V`，主要内容如下，

+ 硬件中如何体现这一哲学
+ 高层编程语言和底层原语之间如何映射

!!! info
    如原文所说，每个小节围绕一个指令子集，讲清楚设计原理和高层编程语言的关系，这种 top-down, step-by-step 的方式可以做到真正的深入浅出，让你不仅知其然，还知其所以然，所谓圣经不是浪得虚名。很多资料（特别是国内的教科书）不注重知识背后的原理和方法，采用灌输式的方法，很容易打击学习者的兴趣。

## Three Principles of Hardware Design

1. **Simplicity favors regularity. 简单源于规整**

    RISC-V 中的很有算术指令都和加法类似，很自然地有 3 个操作数：两个源操作数，一个目的操作数。显然操作数数量固定要比动态变化更简单，“让所有的指令都包含相同数量的操作数”体现了 **keep the hardware simple** 这一设计哲学。

2. **Smaller is faster. 越小越快**

    和高层编程语言不同的是，算术指令的操作数必须来自有限个寄存器 `register`。寄存器是硬件的基本元素，而且对程序员是可见的，所以可以把它看作是构造计算机这个“建筑”的“砖块”。RV64 中的寄存器宽度为 64bit，因为 64bit 非常频繁地出现，所以 RV 架构给它起了一个特别的名字：`doubleword`，对应地给 32bit 起名叫 `word`。

    高层编程语言中的变量和硬件中的寄存器的一个主要区别就是：寄存器数量是有限的，一般为 32 个。把寄存器限制在 32 个原因就是本条设计原则：越小越快。道理很显然，寄存器越多，mux 就越复杂时钟频率也就越低。

    这个原则并不是绝对的，31 个寄存器也不见得就比 32 个寄存器更快（不要钻牛角尖抬杠），但是这个原则依然非常重要。计算机设计者必须平衡好一组矛盾：程序希望寄存器越多越好，而硬件希望寄存器少一些以提高时钟频率。RISC-V 使用 32 个而不是 31 个寄存器的另一个原因是指令格式中的 bit 数（rs 和 rd 使用 5bit编码）正好可以寻址 32 个寄存器。

    !!! note
        因为寄存器的数量远小于程序中的变量数，所以编译器会将常用的变量放在寄存器中，不常用的变量放在 memory 中，有需要时再从 memory 中读到寄存器中使用。把不常用的变量存回到 memory 的过程叫做寄存器溢出 `spilling`。

        显然，register 和 memory 相比，访问时间短、吞吐率高、功耗小，所以为了获得更高的性能，节约功耗，ISA 中必须有足够的 register，而且编译器也必须高效使用它们。

    显然，寄存器是硬件的核心元素，有效使用寄存器是提高程序性能的关键。RISC-V 的命名惯例：每个寄存器以 `x` 开头，后面加上序号，所以寄存器的名字为 `x0`, `x1`, ... `x31`。

3. **Good design demands good compromises. 优秀的设计需要合适的折中**

    由前面的设计规则可知，我们既想让所有的指令长度都相等，又想让它们的格式都保持一致，这样硬件实现起来最简单。但是实际上只定义一种指令格式是无法满足需求的，这里产生了矛盾。RISC-V 采用了折中方案：

    保持所有指令长度相同，但是为不同类型的指令设计了不同的指令格式。

    RISC-V 一共定义了 4 种类型的指令：`R`, `I`, `S`, `U`，其中 `S` 类型有一个变种类型 `SB` 类型，`U` 类型有个变种 `UJ` 类型，详细的指令格式参考 RISC-V 的 spec 即可。

## Endian

一般 memory 都使用的是 byte 地址，当有个数据长度超过一个 byte 时，就会遇到大小端问题：应该以哪个 byte 地址作为这个数据的地址呢？
    
+ 使用数据最左边的 bit 的地址（即 big end 的 byte）作为数据的寻址地址
+ 使用数据最右边的 bit 的地址（即 little end 的 byte）作为数据的寻址地址

RISC 采用的是 little-endian 类型。

!!! warning
    很多体系结构中，要求 word 的地址必须是 4Byte 对齐，doubleword 的地址必须是 8Byte 对齐。RISC-V 和 x86 没有对齐约束，但是 MIPS 有约束。

许多程序中都会用到常数，比如地址自增 1 来自动指向数组中的下一个元素。如果每次都从 memory 中用 load 指令来搬运这个常数则显得很低效，解决方法就是把常数放在指令中。常数作为操作数是非常常见的，实际上，`addi` 是 RISC-V 中最常见的指令。而常数 0 更加重要，它可以提供各种用法来简化指令集。比如，想得到一个数的相反数，则用 0 减去它即可。所以 RISC-V 用专用的寄存器 `x0` 来存储常数 0。（**common case fast** 哲学的体现）

## Signed and Unsigned Numbers

参考以前的一篇总结：[原码、反码、补码](https://qian-gu.github.io/posts/cs/signed-number-representations.html)

## Addressing Modes

RISC-V 一共有 4 种寻址模式：

| 寻址类型 | 含义 |
| ------ | ---- |
| **Immediate addressing 立即数寻址** | 操作数是常数，保存在指令当中 |
| **Register addressing 寄存器寻址** | 操作数保存在寄存器中 |
| **Base/displacement addressing 基址寻址** | 操作数保存在 memory 中，其地址为寄存器和指令中常数相加的结果 |
| **PC-relative addressing PC 相对寻址** | 分支指令中，跳转地址为 PC 和指令中的常数相加的结果 |

## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**谬论：更强大的指令意味着更高的性能**

RISC 和 CISC 之争，现在的趋势是大部分都转向 RISC，连 x86 指令也通过内部的微码化来模拟 RISC。

**谬论：使用汇编语言编程来获取最高性能**

在很久以前，编译器性能还不够好时，汇编程序员是占优势的。但是通过不断的改进，现在编译器产生的代码与手工编写的汇编代码在性能上的差距在快速缩小。一个汇编程序员想要和编译器竞争，必须对计算机体系结构中的流水线和存储器层次有非常深刻的理解才行。

即使手工编写的代码速度更快，但是还是不应该选择这种方法，原因如下，

1. 花费更多的 coding 时间
2. 可移植性差
3. 难以维护

**陷阱：商用计算机二进制向后兼容的重要性意味着成功的指令集不需要改变**

x86 指令的演变用事实说明，在保持向后兼容神圣不可侵犯的同时，也要不断地添加新指令。

**陷阱：忘记 byte 寻址的机器中连续的 word/doubleword 地址相差不是 1**

汇编代码容易出错的例子：必须程序员自己清楚地计算地址，而用高级语言则不需要考虑这些因素。

**陷阱：在 automatic 类型变量的定义域外面使用指针指向该变量**

无论是汇编还是高级语言，都要注意这一点，常见的新手易犯的编程错误。

## Summary

> Less is more.
> 
>   -- Robert Browning, Andrea del Sarto, 1855

stored-program 计算机的两大准则：

1. 指令和数据都是数字
2. 使用可以修改的存储器

基于这两个概念，一台计算机上就可以运行不同的程序，应用在各个领域。

为机器选择指令集需要在指令数量、单条指令的运行 cycle 数、时钟频率等因素之间做精妙的平衡。本章提供了 3 条准则来指导指令集的设计者如何做一些 tricky 的折中：

1. Simplicity favors regularity.
2. Smaller is faster.
3. Good design demands good compromises.

指令集的设计中也应用到了计算机体系结构领域中的 common cast fast 原则，比如 RISC-V 中对于条件分支指令使用 PC 相对寻址，对于大位宽的常数操作数使用立即数寻址。

RISC-V 中每个类型的指令都有对应的编程语言中的元素，

| RISC-V 指令类型 | 编程元素 |
| ------- | ------- |
| 算术指令 | 赋值语句 |
| 传输指令 | 处理数组/结构体之类的数据结构的语句 |
| 条件分支指令 | if/for 等语句 |
| 无条件分支指令 | 函数调用/返回，case/switch 语句 |

这些指令并不是平等的，有一小部分指令出现的频率非常高。指令出现概率的不同在 datapath，control，pipeline 中扮演着非常重要的角色。
