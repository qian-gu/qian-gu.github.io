Title: 时钟分频器
Date: 2014-10-13 22:26
Category: IC
Tags: clock design, clock dividers
Slug: clock-dividers
Author: Qian Gu
Summary: 总结常用的时钟分频方法

在 [时钟设计][clock design] 中提到过：

**Guideline：** 尽量避免使用分频时钟

如果要进行分频，可以使用 PLL/DLL 来实现，但是对于时钟要求不高的基本设计，通过语言进行时钟的分频相移仍然非常流行，首先这种方法可以节省芯片内部的锁相环资源，再者，消耗不多的逻辑单元就可以达到对时钟操作的目的。另一方面，通过语言设计进行时钟分频，可以看出设计者对设计语言的理解程度。

如果一定要使用分频时钟：

1. 对于资源比较丰富的 FPGA

    使用内部提供的 PLL/DLL，输出时钟信号可以配置成不同的频率（倍频/分频）和相位，这样的分频时钟是最稳定的。
    
2. 对于无法使用 PLL/DLL 的 FPGA

    对于这些情况，首先检查是否可以用 `CE` (clock enable) 来代替分频时钟，如果不行，则使用下面讨论的分频方法。

[clock design]: http://guqian110.github.io/pages/2014/09/12/the-clock-design-in-fpga-2-clock-design.html

## Counter

时钟分频一般都是通过计数器 counter 来实现的，计数器是分频的基础。

计数器可以分为很多种，[Counter on wiki][wiki]，这里不再跑题展开了，关于计数器的讨论见：[Counter in FPGAs][blog1]

[wiki]: http://en.wikipedia.org/wiki/Counter
[blog1]: http://guqian110.github.io/pages/2014/11/04/counter-design-summary.html

## Clock divider

### even clock divider

偶数分频是最简单的情况，使用计数器就可以完成。比如，产生一个分频系数为 N（偶数）的 50% 占空比的分频器一般有两种方法：

1. 计数器计数到 (N/2-1) 时，将输出翻转，同时将计数器复位到 0，重新开始计数

2. 计数器从 0 计数到 (N/2-1) 时，输出 1/0，从 N/2 计数到 (N-1) 时，输出 0/1

方案一只能实现固定的 50% 占空比，方案二则可以实现可以有限调整占空比。

### odd clock divider

如果对占空比没有要求，那么使用和偶数分频类似的方法，一个计数器就可以解决；如果要求占空比是 50%，则可以使用以下的方法：

[The Art of Hardware Architecture][art]:

> Conceptually, the easiest way to create an odd divider with a 50% duty cycle is to  generate two clocks at half the desired output frequency with a quadrature-phase relationship (constant 90° phase difference between the two clocks).
>
> The output frequency can then be generated by exclusive-ORing the two waveforms together.

**Steps**

1. 创建 ref-clk 上升沿触发的 0 ~ (N - 1) 的计数器 cnt（N 为奇数）

2. 使用两个 T flip-flop，分别产生各自的 enable

    + tff1-en: 当 cnt = 0 时，使能
    
    + tff2-en: 当 cnt = (N + 1) / 2 时，使能
    
3.  产生以下信号

    + div1：在 ref-clk *上升沿* 触发 tff1
    
    + div2：在 ref-clk *下降沿* 触发 tff2
    
4. 异或 div1 和 div2，得到输出 clk-out

在 [The Art][art] 中，举例介绍了 3 分频的情况：

Schematic:

![schematic](/images/clock-dividers/divide-3-sch.png)

Timing:

![timing](/images/clock-dividers/divide-3-timing.png)

[art]: http://www.amazon.com/The-Art-Hardware-Architecture-Techniques/dp/1461403960

### half integer clock divider

这种分频系数为 (N+1/2)，应该归类到小数分频中，但是因为它的小数部分是特殊的 1/2，所以可以在前面的讨论的基础上得到。

[The Art][art] 中分类讨论了半整数分频：

#### 50% Duty Cycle

以 1.5 分频为例，

Schematic:

![1.5 sch](/images/clock-dividers/divide-1-5-sch.png)

Timing:

![1.5 timing](/images/clock-dividers/divide-1-5-timing.png)

这种方法在仿真的时候是没有问题的，但是综合时可能会产生致命的问题：在切换时钟时，如果两路时钟信号的时延不相等，那么切换的时候就会产生毛刺。

(Xilinx 提供的原语 `BUFGMUX ` 有去除切换时钟时候的毛刺的功能，但是它只适用于全局时钟网络)

#### Non 50% Duty Cycle

如果占空比不是 50%，则可以通过以下的方法得到：

从

    N + 1/2 = (2N + 1) / 2

可知，N+1/2 分频也就是要求在 (2N+1) 个时钟周期内产生两个脉冲即可，这两个脉冲必须是等间隔分布的。

首先，可以采用长度为 (2N+1) 的移位寄存器，这些寄存器中只有一个是 1，其他都是 0，然后在时钟的驱动下循环移位，则就有了 (2N+1) 个时钟周期的计数。

其次，两个脉冲可以从这个移位寄存器中选取两个作为输出，但是不能简单地直接使用，因为无论怎样选择，这两个脉冲都不是等间隔分布的（一共 2N+1 个计数，抽取 2 个，剩余 2N-1 个计数，那么 2N-1 是个奇数，无法平分为两部分，所以不是等间隔的）。所以难点就在于如何得到两个等间隔的分布。The Art 的解决方法如下，以 4.5 分频为例：

Timing:

![4.5 timing](/images/clock-dividers/divide-4-5-timing.png)

从图中可以看到，当选择了两个连续的寄存器 (A, B)相或作为第一个脉冲输出之后，再选取相隔 N 的两个连续的寄存器 (C, D)，把它们移动半个时钟周期后，和原始的 D 相或，作为第二个脉冲输出，容易分析，它们是等间隔的。

### fraction divider

大概有两种方法吧：

1. 整数逼近法

2. 多次分频

**方法一：**

小数分频，最普通的方法是采用整数分频逼近法，比如 50 MHz 的时钟分频为 880 Hz，那么分频计数器:

    50000000/880 = 56818.18182
    
那么就用 56818 来近似，但是这种方法只有在分频系数很大时才比较好，分频系数越小，则误差越大。

**方法二：**

参考一篇博文：[verilog 实现小数分频（小数分频器）][blog2]

通过可变分频和多次平均的方法，然后通过控制单位时间内两种分频比出现的不同次数来获得所需要的小数分频值。

假设分频系数为 N+A/B，其中 N, A, B 都是整数，N 代表整数部分，A/B 表示小数部分。

由

    NB+A = N*(B-A) + (N+1)*A
    
可知，通过 (B-A) 次 N 分频 + A次 (N+1) 分频即可得到 N+A/B 分频。

到此还没有结束，还需要对这两种分频方式进行均匀的放置。可以借助一个计数器到达这个目的：每进行一次分频，计数值为10减去分频系数的小数部分，各次计数值累加。若累加结果小于10，则进行 N +1 分频，若大于或等于10，则进行 Ｎ 分频。

不同时钟分频组合时，“按照累积量和 10 比较” 原理： 当采用一种分频比，小数部分累积量大于 10，则表示小数部分累积达到了可以向整数部分进位的大小，这时候就应该插入另外一种分频比将小数部分积累的误差去掉，否则结果就不是均匀周期的时钟信号了。

举个例子：

比如 8.7 分频

    87 = 8*3 + 9*7
    
所以可以用 3 次 8 分频 + 7 次 9 分频得到 8.7 分频。因为 `10 -7 = 3`，前 3 次累积之和都小于 10，所以前 3 次进行 9 分频，第四次累积值为 12，去除进位后余 2，待下次继续累积，第四次结果 12 > 10，所以进行 8 分频。分频方案如下图所示：

![example](/images/clock-dividers/example.png)

[blog2]: http://blog.sina.com.cn/s/blog-6840802c0100izey.html

## Summary

本文总结了一些常用的时钟分频技术，虽然不推荐使用逻辑来对时钟信号进行分频，但是在一些要求比较的的情况下，使用逻辑分频不仅可以满足要求，还能降低资源消耗，不失为一种好方法。而且时钟分频也可以训练我们的设计能力。

## Reference

[The Art of Hardware Architecture][art]

[FPGA高手设计实战真经100则](http://www.amazon.cn/%E5%9B%BE%E4%B9%A6/dp/B00FW1RTZG)

[使用 VHDL 进行分频器设计](http://read.pudn.com/downloads126/sourcecode/embed/533229/VHDL%E5%88%86%E9%A2%91%E5%99%A8%E8%AE%BE%E8%AE%A1.pdf)

[verilog 实现小数分频（小数分频器）][blog2]

[任意分频的verilog语言实现](http://www.eetop.cn/blog/html/11/317611-13680.html)