Title: FPGA 数字处理基础 (1)
Date: 2014-05-14 23:25
Category: IC
Tags: digital processing
Slug: fpga-digital-processing-basic-1
Author: Qian Gu
Summary: 总结 FPGA 处理数字信号的基础知识 (1)

## 数字处理基础

**数字处理基础**主要包括两个方面：

+ 数的表示
+ 常用算术运算的实现

下面分别讨论。

## 数的表示

这部分讨论对于计算机(PC)、数字信号处理器件(DSP)、数字芯片(包括 FPGA) 都是成立的。

### 人类如何计数

最早我们的祖先采用的是结绳计数，经过几千年的发展，现在我们使用的 10 进制位置计数法 。那么我们为什么偏偏选择 10 这个数字呢？

大名鼎鼎的 [Charles Petzold][CP] 在他的著作 [code][code] 中分析了我们的计数进制现象 。原因其实很简单，10 这个数字对于我们如此特别只是因为我们有 10 个手指(脚趾)，于是我们采用了 10 进制，并且逐渐习惯了它 。他在书中模拟了一下进制系统的演化过程，让我们逐渐从人类的 10 进制思维逐渐转化到计算机的 2 进制系统中：

假设我们是卡通动画中的人物，比如米老鼠 Mickey，仔细观察它就会发现，他的每个手只有 4 个手指，理所当然，他采用 8 进制来计数。如果更进一步，假设我们是龙虾，那么我们的每一只钳子上有两个 “手指”，一共有 4 个手指，所以，我们会采取 4 进制计数系统。最后，假设我们是海豚，那么我们只有两个鳍来计数了，这时候的计数系统就是 2 进制数字系统了。

**r 进制 to 10 进制**

只需要按权值展开就可以了，比如： 

2 进制数 `110101` 对应的 10 进制数为 `32 + 16 + 4 + 1 = 53` 

8 进制数 `B65F` 对应的 10 进制数为 `11 × 16^3 + 6 × 16^2 + 5 × 16 + 15 × 1 = 46687`

**10 进制 to r 进制**

整数部分：基数连除，逆序取余

小数部分：基数连乘，顺序取余

[CP]:http://en.wikipedia.org/wiki/Charles-Petzold
[code]:http://book.douban.com/subject/4822685/

### 计算机如何计数

#### 正数 & 负数

人类和计算机的计数原理是完全不同的，所以采用的方法也是完全不同的。对于人来说，区分正负数只需要在数字绝对值前添加一个符号 `+` 或者 `-` 即可，但是计算机只有 `0` 和 `1` 这两个符号可以使用；对于人来说，减法借位很容易，但是对于计算机硬件电路来说这是一件很麻烦的事。

常用的表示方法有 3 种：**原码**、**反码**、**补码** 。对于计算机而言，硬件上最容易实现的是补码，这也是大多数计算机采用补码系统的原因 。

以前总结过一篇博客，[原码、反码、补码][blog1]。

#### 整数 & 小数

1. 整数

    对于整数而言，不存在小数点的问题，所以自然地将我们人类所熟悉的 10 进制数转化为计算机熟悉的 2 进制数，分配足够的空间存储起来就 ok 。

2. 小数

    在计算机中，整数和小数之间并不是很容易转换，而且小数的存储和处理要比整数复杂。对于小数可以有两种方法来表示：**定点数** & **浮点数**

    定点数的意思是小数点在数中的位置是固定不变的。整数可以看作是一种特殊的定点数，小数点在数的末尾。值得注意的是小数点的位置信息并没有和数字存储在一起，所以，使用定点数的程序必须知道小数点的位置。
    
    浮点数的意思是小数点在数中的位置是变化的。当代大部分计算机处理浮点数的标准是 IEEE 在 1985 年制定的 ANSI/IEEE Std 754-1985 。

    在计算机出现不久的年代，计算机处理浮点数是一件很重要但也让人头疼的事。最早，还没有专门处理浮点数的硬件，所以程序猿必须编写软件来完成浮点数的计算。浮点数在科学运算和工程类程序中极为重要，因此常常被赋予很高的优先级，在计算机发展的早期，为新制造的计算机做的第一项工作就是为其编写浮点数运算程序。

    如果可以直接利用计算机机器码指令来实现浮点数的计算，类似于 16 位处理器上进行乘法和除法运输，那么这台机器上所有的浮点数运算都会变得更快。IBM 公司在 1954 年发布了 IBM 704，它是第一台将浮点数运算硬件作为可选配件的商用计算机。该机器的浮点运算硬件可以直接进行加法、减法、乘法和除法，其他的浮点运算必须通过软件来实现。

    从 1980 年开始，浮点运算硬件开始应用于桌面计算机，这起始于 Intel 当年发布的 8087 数字协同处理(Numberic Data Coprocessor)芯片，当时这种集成电路被称为 **数学协同处理器(math coprocessor)** 或者 **浮点运算单元(floating-point,FPU)**。8087 不能独立工作，必须和 8086 或者 8088 一起工作，所以被称为 “**协处理器**”。

    在最初版本的 IBM PC 主板上，位于 8080 芯片的右边有一个 40 个管脚的插槽供 8087 芯片接入，但是，这个插槽是空的，如果用户需要浮点运算则必须单独购买一块 8087 芯片。数字协处理器并不能加速所有的程序的运行速度，比如文字处理程序几乎用不到浮点运算，而电子表格处理程序对浮点数运算依赖程度很高。

    安装了数学协处理器，程序员必须使用协处理器的机器码指令来编写特定的程序，因为数学协处理器不是标准硬件。最后就出现了这样的局面：如果机器上安装了数学协处理器，程序员就要学会编写相应的应用程序以支持它的运行；如果没有安装，程序员必须通过编程来模拟它进行浮点数的运算。

    在 1989 年发布的 486DX 芯片中，FPU 已经内建在 CPU 的结构里，但是在 1991 年发布的 486SX 中，又没有内建 FPU，到了 1993 年发布的奔腾芯片中，CPU 内置 FPU 再次成为标准，并且是永远的标准。在 1990 年发布的 68040 芯片中，摩托罗拉首次将 FPU 集成到 CPU 中，在此之前是使用 68881 和 68882 数学协处理器来支持 68000 家族的微处理器。PowerPC 芯片同样使用了内置 FPU 的技术。

    FPGA 不同于微处理器，它内部没有内置 FPU(不包括硬核)，对于FPGA，浮点数可以克服定点数动态范围小的缺点，但是在运算时，实现浮点数的硬件实时成本高，处理速度慢，所以在非实时运算中有广泛的应用。对于通信系统中的信号，一般都是实时处理的，所以在 FPGA 开发中，一般只使用定点数 。

[blog1]: http://guqian110.github.io/posts/cs/signed-number-representations.html

## 常用算术运算的 FPGA 实现

### 加法

在 Verilog HDL 中，直接使用运算符 `+`，其本质上是一种并行加法器，应该保证两边的数位宽是一致的。举个栗子

    #!verilog
    module add_4 (x, y, C);
    
        input   [3:0]   x;
        input   [3:0]   y;
        output  [3:0]   sum;
        output          C;
        
        assign {C, sum} = x + y;
        
    endmodule

### 乘法

第一种方法，最简单，直接使用运算符 `*`，如下所示 。但是这种方法写出来的代码效率很低，甚至有时候是不可综合的，实际应用中基本不会采用这种方法。

    #!verilog
    assign p = x * y;

第二种方法是自己写代码实现乘法运算，或者是使用 IP COre。一般 FPGA 中都集成了硬核的乘法器，所以可以有两种方案来实现乘法器，DSP48 硬核 或者是 Slice 搭建 。

### 除法

除法是四则基本运算中最复杂的，也是最难实现的。除法可以看作是乘法的逆运算，但除法要复杂的多，最大的区别是乘法中的一些操作可以并行支持，通过流水线提高计算速度，但是除法必须顺序执行，运算最耗时间。

Verilog 提供了除法运算符 `/`，如下所示。但是只有在除数为 2 或者 2 的整幂次时才是可综合的，其余情况都不可综合 。

    #!verilog
    q <= a/b;

常用的方法是采用 IP Core，可以完成定点数和浮点数两类算法。

### Cordic 算法

[Cordic 算法][cordic] 算法即坐标旋转数字计算方法，是J.D.Volder1于1959年首次提出，主要用于三角函数、双曲线、指数、对数的计算。该算法通过基本的加和移位运算代替乘法运算，使得矢量的旋转和定向的计算不再需要三角函数、乘法、开方、反三角、指数等函数。

它通常应用在没有硬件乘法器的应用中，比如微控制器、FPGA 中，cordic 进行的所有操作只有加法、移位和查表 。

Coridc 算法可以自己编写代码实现，也可以使用 IP Core 。

!!!note
    事实上，所有的 IP 软核理论上都可以自己写，因为这些软核实际上就是别人写好的代码和文档，类似于C语言中的库函数。

[cordic]: http://en.wikipedia.org/wiki/CORDIC

## 参考

[《无线通信的 Matlab 和 FPGA 实现》](http://book.douban.com/subject/3795386/)

[code](http://book.douban.com/subject/4822685/)
