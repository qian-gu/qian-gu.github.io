Title: Patterson and Hennessy 学习笔记 #3 —— Chapter 3 Arithmetic For Computers
Date: 2020-12-13 12:55
Category: IC
Tags: Patterson and Hennessy
Slug: learning-patterson-and-hennessy-notes-3-chapter-3
Author: Qian Gu
Series: Patterson & Hennessy Notes
Summary: Patterson and Hennessy 读书笔记，第三章

> Numerical precision is the very soul of science.
> 
>   -- Sir D'arcy Wentworth Thompson,On Grwth and Form, 1917

## Integer

### Addition & Subtraction

**处理 overflow**

因为寄存器位宽是有限的，所以会产生 overflow，一般计算机都提供了 overflow 检测。对于补码形式的 signed 类型数据检测方法很简单，根据操作数、结果的符号位以及操作类型分类讨论判断即可。而对于 unsigned 类型而言，一般这些数据都是用来计算内存地址，产生的 overflow 都被忽略了。编译器可以用 branch 指令来检测 unsigned 类型数据是否发生了 overflow：加法的结果是否比任何一个加数都小，或者减法的结果是否比任何一个减数都大。

检测出发生了 overflow 之后应该怎么办呢？C 和 Java 会忽略 integer 的 overflow，但是 Ada 和 Fortran 要求必须通知程序，所以程序猿或者是编程环境要决定发生 overflow 时该如何处理。

和 overflow 相对的有一种不常见的处理：饱和处理 saturation。这种操作一般都出现在多媒体的相关处理中，比如音量的最大限度等例子。

**实现方案**

加法器的设计是一个非常经典的 IC 话题，它的速度取决于进位链的速度，有很多技术会预测进位 bit，其最坏的结果就是进位时间是 log2(W) 的函数（其中 W 是加法器的位宽）。这些预测信号的逻辑门更少所以速度更快，付出的代价就是消耗了更多的硬件资源来预测进位信号的正确值，最流行的结构就是超前进位加法器 `CLA`(carry lookahead adder)。

### Multiplication

$1010 * 1011 = 0110\_1110$，动手算一下就知道将 1010 和 1011 解释成 10 进制数或者是 2 进制等式都是成立的，因为他们的原理都一样：移位相加。

**实现方案**

1. 最简单直接的思路：模仿人类手工计算过程，相与 -> 移位 -> 相加

	只有一个加法器和移位器，时分复用，具体模块框图见原文。

2. 更快速的实现方案：资源换速度，乘法器展开

	前面的方案只有一个硬件通过若干次重复计算后累加出结果，将这个过程展开（unroll）就可以得到一个更快的（latency 更小）方案：给乘数的每一 bit 都和被乘数相与，然后相邻 bit 的结果相加，显然宽度是 W 的乘法只需要 W 个加法器，latency 是 W 个加法器 latency 的总和。显然这个组合逻辑太大了时钟频率很可能上不去。继续优化的思路是：采用并行树的方式。latency 只有 $log2(W)$ 次加法，代价是消耗了更多的硬件资源。

3. ALU 中的方案：

	使用前面提到的超前进位加法器 `carry save adders` 来构造乘法器，速度更快而且可以做成 pipeline 形式，提高吞吐率。最常见的实现方法是 booth-wallace + CLA 实现。

**Signed 处理**

Q：如何处理 signed/unsigned？

A：最简单的方法，先将 signed 转化为 unsigned，符号位单独处理（这个规则也适用于 signed 数据的其他运算）

!!! tip
	乘法器的设计和优化也是 IC 设计中的一个经典话题，历经几十年的发展，从最原始的阵列乘法器发展到经典的 booth-wallace 乘法器，目前仍然有很多相关研究和论文，其中大部分都是基于 booth 乘法器的结构或追求性能、或追求面积、或追求功耗等。

### Division

比乘法的使用频率更底，也更诡异，可能会出现无效运算：除数为 0 的情况。

$$Dividend = Quotient * Divisor + Remainder$$

**实现方案**

1. 最简单直接的思路：与乘法器同理，模仿人类手工计算过程，移位 -> 相减

	具体模块框图见原文。

2. 快速的除法器：`RST division`

	无法直接像乘法那样展开成多个加法器来加速，因为除法必须先算出前一次迭代结果的符号位之后才能开始下一次的迭代。加速除法的思路：每次迭代产生商的若干 bit，而不仅仅是 1bit。RST division 技术就是每次迭代的时候，基于 dividend 和 remainder 的高位 bit 来预测 quotient 的若干 bit，如果预测错了后面的步骤需要纠正这个错误。目前一般是每次预测 quotient 的 4bit 结果，这个算法的准确度取决于查找表中的是否有合适的数据。

3. 更快的除法器：`non-restoring division`

	前面两种都是 restoring 除法，每次迭代相减的结果是负数，需要将 divisor 恢复回去。不恢复的数学原理是：

	$$(r+d)*2-d=r*2+d*2-d=r*2+d$$

4. 更更快的除法器：`non-performing division`

	如果移位相减的结果是负数，则不保存减法的结果，平均减少 1/3 的算术操作。

**Signed 处理**

Q：如何处理 signed/unsigned？

A：需要特别注意 signed 除法必须保证 $-(x \div y)=(-x)\div y$，也即**保证 dividend 和 remainder 的符号必须相同。**

!!! note
    RISC-V 除法指令会忽略 overflow，所以软件必须自己检测 quotient 是否发生了溢出；对于除 0 运算也是一样，软件必须自己检测。

## Float Point

+ 科学计数法：小数点左边只有 1 位整数的表示方法
+ `normalized number`：没有 leading 0s

对于二进制浮点数，标准格式是：

$$1.xyz\ast2^{abc}$$

因为 word 的位宽是固定的，所以浮点数必须在 fraction 和 exponent 之间做折中，也就是精度和范围之间的取舍，

+ 增加 fraction 的 bit 位数可以提高精度但是会减小表示的范围
+ 增加 exponent 的 bit 位数可以扩大表示范围，但是会降低表示精度

如 chapter 2 所述，**一个好的设计需要有合理的折中。**

float 数的表示方法实际上就是 sign-and-magnitude 方式，1bit 符号 + E bit 指数 + F bit 尾数，表示的数据大小为：

$$(-1)^S * F * 2^E$$

**处理 overflow**

float 同理也会有 overflow 和 underflow，

+ overflow：正的指数太大无法完整保存在 exponent 字段
+ underflow：负的指数太大无法完整保存在 exponent 字段

解决 overflow/underflow 的方法很简单粗暴，增加 bit 即可：即 double 数据类型。

如果发生了 overflow/underflow 应该怎么通知用户呢？一些计算机会发出 exception 或者是 interrupts，然后由异常/中断处理程序来完成后续工作。但是 RISC-V 不会发出 exception 和 interrupt，而是要求软件查询 `floating-point control and status register (fcsr)` 这个寄存器来判断是否发生了 overflow/underflow。

### IEEE 754 Floating Point Standard

1980 年之后的所有 PC 都遵守这个标准，754 对浮点数做了进一步的规定，对许多特殊数都有定义，比如正负无穷和 NaN 等，具体标准内容略。

### Arithmetic 

**加法**

和人类手工计算过程类似，

1. 首先对齐 exponent
2. 然后计算 fraction
3. 对结果进行 normalize
4. 对结果进行 round

**乘法**

1. 指数部分相加
2. 尾数部分相乘
3. normalize 乘积
4. round 乘积
5. 设置符号位

### Subword Parallelism

多媒体处理一般处理的数据要比 word 窄，而且这些数据的操作都是相同的，所以就出现了一种新技术：通过对进位链的分割，实现 word 内部的数据的并行计算，相比于收益来说这种分割的代价是非常小的。

这种在一个 word 内部进行并行操作的技术叫做 `subword parallelism`，有时候也分到更加宏观的类别 `data parallelism` 中，这种技术有时候也叫做 `vector` 或者是 `SIMD`。

!!! tip
    目前 RISC-V 的向量指令还处于 draft 阶段，但是向量指令是现在的发展趋势，在未来必不可少。

## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

计算的错误和谬论一般都是由“计算机的数据是有限位宽的，而自然数是无限的”这一矛盾产生。

**谬论：就像左移指令可以代替 2 的指数次的乘法，右移指令可以代替除数是 2 的指数的除法运算。**

对于 unsigned 类型来说的确如此，但是对于 signed 类型的数据则显然不对，负数右移后在高位补充符号位，最后会永远是 -1，不会变成 0。

**陷阱：结合律不适用于浮点运算**

对于 integer 的运算，即使会发生 overflow 结合律也是适用的。但是对于浮点数，结合律是不适用的，因为计算机内的浮点数是用有限的 bit 来近似真实的数字，无法保存 overflow 的数字。这里有意思的是，对于定点的整数而言即使发生了 overflow 结合律仍然是适用的，找个例子就可以验证下面的等式是成立的，

$$-128+127+3 = -128+(127+3) = -128+(-126)=2$$

原因也很简单：整数运算 overflow 只会影响高位 bit，低位 bit 是不受影响的。

**谬论：并行执行策略不仅适用于 integer 类型，也适用于 float 类型**

上一条已经证明了结合律不适用于 float 类型，所以并行执行策略不一定适合 float 类型。所以写并行代码并且使用了浮点数的时候，程序猿要自己判断结果是不是可靠的，处理这个问题的领域叫做数值分析，关于这个问题本身就可以写一本书了。这也是 `LAPACK` 和 `SCALAPAK` 这类数学库流行的原因，它们的顺序执行和并行执行都已经被验证过是有效的。

**谬论：只有理论数学家才关心 float 数的精度问题**

一个经典故事，Intel 的 Pentium 系列处理器就出现过相关问题，为此付出了 5 亿美元召回有 bug 的芯片。

## Summary

!!! important
	+ 基本算术单元是 ALU 的核心组件
	+ 加法器、乘法器、除法器、integer/float 的处理每个 topic 都是经典问题
	+ 不同定位的处理器的性能差别的一个重要因素就是 ALU 中这些组件的实现方式和性能不同，这是个折中取舍的问题
