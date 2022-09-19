Title: AXI4 协议小结
Date: 2022-09-10 10:53
Category: IC
Tags: AXI4
Slug: axi4_summary
Author: Qian Gu
Summary: AXI4 协议阅读 & 实践笔记

## 参考资源

网上有很多关于 axi 协议的文章，但是大多含糊不清，且混杂作者的个人错误理解，所以应该参考 arm 官方第一手资料。

+ [Learn the architecture - An introduction to AMBA AXI][learn-the-architecture]
+ [AMBA AXI and ACE Protocol Specification Version H.c][ihi0022]

[learn-the-architecture]: https://developer.arm.com/documentation/102202/0300/AXI-protocol-overview
[ihi0022]: https://developer.arm.com/documentation/ihi0022/latest

## AMBA 简介

AMBA（Advanced Microcontroller Bus Architecture）是 arm 制定的片上互联标准协议。AMBA 广泛应用在 SoC 中，好处在于：

+ 有效的 IP 复用：通过标准接口实现 IP 复用
+ 灵活性：提供一系列协议支持不同的应用场景和需求
+ 兼容性：不同 vendor 提供的 IP 通过标准接口实现互联
+ 广泛性：业界广泛应用

AMBA 协议从时间维度看，从 AMBA 1 到 AMBA 5 目前发展到了第 5 代；从协议维度看，从低速到高速包含 APB、AHB、AXI、ACE、CHI 多种协议：

+ APB：低速系统外设
+ AHB：高速总线
+ AXI：系统高性能总线
+ ACE：在 AXI 的基础上扩展支持 cache coherence
+ CHI：分层协议，支持系统级的 coherent

### AXI4 总结

#### 特点

+ 适用于 high-bandwidth, low-latency 设计
+ 支持 high-frequency，不需要复杂的 bridge
+ 满足多种模块的接口需求
+ 适用于有高 initial access latency 的 memory controller
+ 支持灵活的 interconnect 架构设计
+ 向下兼容 AHB 和 APB

关键特性：

+ data 和 address/control 通道分离
+ 通过 strob 信号支持 unaligned transfer
+ 只需要提供初始地址支持 burst transaction
+ read/write 通道分离，以支持低成本的 DMA
+ 支持发射多个 outstanding 地址
+ 支持 transaction 乱序完成
+ 支持插入寄存器达到时序收敛

#### AXI 架构

一共 5 个 channel，其中 AR 和 R 用于读，AW，W 和 B 用于写。因为采用 data 和 address/control 分离的架构，所以 AXI 协议：

+ 允许地址提前于数据发出
+ 支持多个 outstanding transaction
+ 支持乱序完成

每个 channel 都用 valid-ready 握手机制来确保数据成功传输：source 用 valid 标识通道上的 address，data 以及其他控制信号都有效，destination 用 ready 标识自己可以接收信息。R 和 W 通道各自带有一个 last 信号标识每个 transaction 的最后一个 transfer。

#### 术语

+ `master` = `manager`，发起 transaction 的 component
+ `slave` = `subordinate`，接收并相应 request 的 agent
+ `transaction`：master 和 slave 之间完成一次信息交互所包含的全部操作
+ `burst`：一次 transaction 中 payload 放在一个 burst 中完成传输
+ `transfer` = beat，一个 burst 包含多个 transfer/beat

#### 接口约束

+ 所有 channel 共用一个时钟，所有输出信号只能在时钟上升沿只有变化
+ master 和 slave interface 之间不能有其他组合逻辑
+ 共用一个异步置位，同步撤销的 active-low 复位信号
+ 复位期间 arvaid，awvalid，wvalid，rvalid 和 bvalid 必须为 0，其他信号可以是任意值
+ 复位撤销后的下一个时钟上升沿之后，master 才能拉高 arvalid，awvalid 或 wvalid
+ 


1.  **Design for Moore's Law**

    摩尔定律：电路的集成度每 18 ~ 24 个月翻一倍。

    Intel 的创始人之一 Gordon Moore 在 1965 年作出的预测。因为计算机的设计周期长达数年时间，很有可能项目结束时候的工艺和项目开始时相差非常大，所以设计者要预测未来技术的发展，不能对标当下的技术水平，防止做出来的时候 spec 已经落后了。

    从目前的趋势来看，由于物理技术的限制摩尔定律很有可能失效，Intel 也被大家戏称为牙膏厂。为了继续获得性能的提升，大家纷纷转向 ASIC 芯片，比如目前如火如荼的 AI 硬加速芯片。

2.  **Use Abstraction to Simplify Desing**

    不管是硅农还是码农都要发明一些技术来提高自己的效率，否则由于摩尔定义，资源动不动翻倍会导致设计时间变得非常长。其中一个非常重要的技术就是在不同层次进行抽象，把底层的实现细节通过抽象隐藏起来，只提供一个高层的简单接口。

    通过抽象，顶层可以不关心底层的实现细节，只专注于自己的功能，抽象带来的“模块化设计”可以大幅提高效率。

    这个思想应用非常广泛，典型代表是 OSI 的参考模型。

3.  **Make the Common Case Fast**

    不同领域的共同规律：common case 比 corner case 更重要，而且 common case 也比 corner case 更加容易提升性能。加速 common case 的前提是要知道什么是 common case，而这一点很多时候只有通过仔细的实验和分析才能确定。

    俗话常说“抓住主要矛盾”，“好钢用在刀刃上”，这个思想就是要求我们能分清问题的主次，把大部分的精力投入到主要问题上，获得更高的全局收益。

4.  **Performance via Parallelism**

    显而易见，并行的性能更高。十个人搬转的速度当然比一个人更快。

5.  **Performance via Pipelining**

    流水线实际上是并行的一种，但是因为它实在是太重要，太基础了，在计算机系统中应用太广泛了，所以单独列出来。

    经典故事“汽车装配流水线”。

6.  **Performance via Prediction**

    有时候，不一定非要等到完全确定之后再开始做一件事情，提前预测开始做往往获得的性能更高，前提是从错误中恢复的代价不高。

    典型代表：CPU 中的预测技术。

7.  **Hierarchy of Memories**

    码农一般都想要让 memory 尽可能的速度快、容量大、价格便宜，而这是矛盾的，硅农的解决方法是用 memories hierarchy 兼顾各个指标： 

    `L1 cache >> L2 cache >> L3 cache >> DDR >> Disk`

8.  **Dependability via Redundancy**

    计算机不光要速度快，还要可靠。任何硬件都有可能出错，解决方法就是冗余。

    某些对可靠性要求非常高的应用系统都是通过冗余备份来提高可靠性，比如航天，大型服务器。
    
## Performance

### Defining Performance

套用知乎名言：“先问是不是，再问为什么”（狗头保命）。性能是一个很宽泛的问题，在仔细展开讨论之前必须先定义清楚一个问题：

Q：计算机的性能是什么？

因为计算机自身的类型多种多样（PC，server，embedded），它们使用了各种各样的技术来提升硬件性能；再加上软件的大小和复杂度也有区别，所以要确定计算机的性能是一个复杂的问题。书里面举例了一个“如何比较飞机性能”的问题，实际上下面三个问题是很类似的。

1. 确定/比较 计算机的性能
2. 确定/比较 飞机的性能
3. 确定/比较 汽车的性能（更接地气）

他们的共性就是评价标准是多维的，飞机/汽车有最大巡航里程、最快巡航速度、最大载客量等指标，计算机也有执行时间、典型功耗、体积（芯片的 PPA）等指标。下面我们做第一条约束，

**我们定义计算机的性能是一个时间的函数，也就是说我们并不关心其他因素（比如价格、体积等）。**

+ `response time` = `execution time`：计算机完成一个任务的总时间，包括硬盘访问、内存访问、I/O 操作、操作系统开销、CPU 执行时间等等，一般 PC 和移动设备最关心这个指标

+ `throughput` = `bandwidth`：单位时间内完成的任务量。一般 servers 更关心这个指标

所以很多时候我们要根据类型来区分不同的计算机，对每个类型采用不同的 {performance matrics, applications} 的组合作为 benchmark。

在接下来的前几章中我们主要关心的是 response time，对于这个指标，性能最大意味着 response time 最小，所以可以这么定义计算机的性能：

$$Performance_X = \frac{1}{Execution\ time_X}$$

在比较两个不同的计算机时，“X 比 Y 快 n 倍” = “X 的速度是 Y 的 n 倍” 指的是同一个意思，即

$$\frac{Performance_X}{Performance_Y} = n$$

为了简单起见，统一使用“X 的速度是 Y 的 n 倍”（`as fast as`）这种方式。因为 performance 和 execution time 是倒数关系，为了避免歧义，约定下面的描述

+ improve performance = increase performance
+ improve execution time = decrease execution time

### Measuring Performance

根据前面的讨论，我们把 time 作为 performance 的度量标准：完成等量的任务，花费时间最短的计算机的性能最高。但是即使把性能约束在时间这个维度上，依然不够明确，因为“时间”也有很多种。

+ `wall clock time` = `response time` = `elapsed time`，表示完成任务的总时间，包含了所有因素
+ `CPU execution time` = `CPU time` = `user CPU time` + `system CPU time`，表示 CPU 在特定任务上花费的计算时间

    + `user CPU time`，表示 CPU 在这个程序本身上花费的时间
    + `system CPU time`，表示 CPU 在这个程序相关的操作系统上花费的时间
    + 要区分这两个时间实际上是很困难的，因为很难明确定义操作系统的哪些活动是对应哪个特定程序的，而且不同的操作系统的功能也不相同

为了保持一致，使用下面的术语，

+ `system performance` 指的是一个空载系统上的 `elapsed time`
+ `CPU performance` 指的是 `user time`

### The Classic CPU Performance Equation

一个程序的执行时间 = 这个程序包含的 cycle 数 × 每个 cycle 的时长，所以有下面的公式，

$$CPU\ execution\ time = CPU\ clock\ cycles * clock\ cycle\ time\tag{1}$$

其中一个程序包含的 cycle 数 = 包含的所有指令数 × 平均每条指令的 cycle 数，即

$$CPU\ clock\ cycles = Instructions * Average\ clock\ cycles\ per\ Instr\tag{2}$$

这里涉及到一个非常重要的概念 `clock cycles per instruction`，也简称为 **`CPI`**，表示执行一条指令花费的 cycle 数。因为不同的指令完成的任务不同，花费的时间也不同，所以 CPI 指的是所有指令的平均 cycle 数。有了 CPI， 两个使用相同 ISA 的不同计算机之间的比较就很容易了，因为它们的指令条数肯定是一样多的。

!!! note
    CPI 不仅和具体的硬件实现有关，而且和程序也有关系，不同的程序用到的指令类型和数量必然是不相等的，算出来的平均数也不相等。

    CPI 实际上是有可能小于 1 的，所以有些人用 CPI 的倒数作为另外一个指标，`instructions per clock cycle`，简称 `IPC`。

把公式 2 带入到公式 1 之中，就可以得到经典的 CPU 性能公式：

$$CPU\ time = Instruction\ count * CPI * Clock\ cycle\ time\tag{3}$$

也可以写成，

$$CPU\ time = \frac{Instruction\ count * CPI}{Clock\ rate}\tag{4}$$

这个公式其实就是下面公式，只不过给了每个元素一个新的定义，

$$Time = \frac{Seconds}{Program} = \frac{Instructions}{Program} * \frac{Clock\ cycles}{Instruction} * \frac{Seconds}{Clock\ cycle}\tag{5}$$

永远都要记住：**只有 time 是最可靠的指标，其他子指标比如指令条数、CPI 等都不可靠。**

下表列出了影响一个程序的 performance 的因素，以及具体的影响方式，

| 硬件/软件 | 影响到了什么 | 如何影响的 |
| -------- | ----------- | -------- |
| 算法 | Instrcution count, CPI | 算法决定了一共有多少条指令和指令类型 |
| 编程语言 | Instrcution count, CPI | 不同的编程语言翻译出的指令数量和类型也不相同 |
| 编译器 | Instrcution count, CPI | 编译器是算法和底层指令之间的桥梁，必然会影响到具体的指令翻译 |
| ISA | Instrcution count, CPI, clock rate | ISA 对 3 个因素都有影响 |

## The Power Wall

功耗分为两部分：动态功耗、静态功耗。

动态功耗可以通过公式算出来，

$$Power \propto \frac{1}{2} * Capacitive\ load * Voltage^2 * Frequency\ switched\tag{6}$$

其中 `Frequency switched` 是时钟频率的函数，`Capacitive load` 是晶体管的 fanout 和工艺的函数。

从 Intel X86 架构芯片 30 年间 8 代 CPU 的时钟频率和 power 关系图中可以看到，随着时间发展，时钟频率提高了近 1000 倍，但是 power 只提高了大概 30 倍，原因就在于电压的不断降低。

从前面 performance 的讨论可以知道，我们不能采用降低时钟频率的方式来降功耗，因为这会伤害到性能。那么我们可以无限降低电压吗？答案是不行，现在业界遇到的问题就是电压不能再低了，否则晶体管就像水龙头一样，无法完全关闭。虽然动态功耗是 CMOS 功耗中的大头，但是静态功耗也逐渐占据主角，在服务器中静态功耗能达到 40%，所以人们发明了各种技术来降低静态功耗，但是电压很难再进一步降低了。

虽然有各种各样的昂贵技术来冷却芯片，但是继续提高功耗对于 PC（甚至是 servers）来说代价太高了，对移动设备就更不用说了，这就是所谓的功耗墙。

## The Switch from Uniprocessors to Multiprocessors

遇到了功耗墙怎么办？只能舍弃这 30 年来的老路线（提频），选择另外一条路线：多核。

在过去，码农不需要改任何一行代码，就可以每 18 个月让自己的程序性能翻倍（摩尔定律），但是现在由于摩尔定律的失效，码农必须重新写他们的程序，以充分利用多个核。

!!! note
     强制要求码农转换到显式的并行编程是一件高风险的事情（Intel 的安腾系列处理器）。但是，随着多核概念的普及，整个 IT 界已经接受了并行编程，码农们最终会转向显式的并行编程。

为什么并行编程这么难推广呢？

+ 编程困难，人的大脑更适合线性思维，很难处理并行的事情，编程也是同理
+ 调度困难，必须要减少核之间的通信和同步开销，防止这些额外的开销抵消并行带来的性能提升

## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**陷阱：期望局部的性能提升和整体性能成比例**

`common case fast` 思想对整体性能的提升效果取决于 common case 到底有多 common，典型例子就是 [Amdahl's Law][amdahl]。

假设一个程序运行时间是 100s，其中 80s 是乘法运算，那么应该把乘法运算的性能提高到原来的多少倍才能使总计算时间减小到 20s 呢？

根据 Amdahl 定律，

$$T^* = \frac{T_{improved}}{Amout\ of\ improve} + T_{unaffected}\tag{7}$$

在这个例子里，有

$$20 = \frac{80}{n} + 20$$

可以知道实际上不可能达到 20s 的。

!!! note
    CPU 性能计算公式和 Amdahl 定律是设计系统时候的常用工具。

[amdahl]: https://en.wikipedia.org/wiki/Amdahl%27s_law

**谬论：利用率低的计算机功耗也低**

实际上 Google 的服务器上 10% 的负载消耗了 33% 的功耗。

**谬论：性能设计和能效设计是不相关的事情**

能量是功耗在时间上的积分，所以如果通过软硬件优化减少了程序的计算时间，就能同时降低功耗。

**陷阱：把性能公式中的子集作为评价性能的标准**

前面已经描述过，只有把 3 个因素都考虑进去，得到的性能结果才是可靠的，取其中任何一个、两个子指标都会导致不可靠的结果。比如，常用的 `MIPS(million instructions per second)` 指标，

$$MIPS = \frac{Instrcution\ count}{Execution\ time * 10^6}\tag{8}$$

MIPS 描述的是指令执行速度，计算机越快相应的 MIPS 指标就越高。MIPS 指标非常容易理解，但是把它作为性能指标是有问题的，

1. 只考虑了指令执行速度，但是没考虑指令的数量，对于不同 ISA 的计算机，不能直接比较它们的 MIPS
2. 即使是同一台计算机，MIPS 值也会随着程序的不同而变化，没有固定值

    实际上，把公式 3 和公式 8 可以得到下面的公式，

    $$MIPS = \frac{clock\ rate}{CPI * 10^6}$$

    因为 CPI 是个变化值，所以 MIPS 也是个变化值。

3. 如果一个程序的指令数量变多，但是同时每条指令的执行速度变快，那么 MIPS 的值就完全不能反映出实际的真实性能

    比如下面这个例子，

    | 测量方式 | 计算机 A | 计算机 B |
    | ------- | ------- | ------- |
    | 指令数 | 10 billion | 8 billion |
    | 时钟频率 | 4 GHz | 4 GHz |
    | CPI | 1.0 | 1.1 |

    可以算出来 A 比 B 的 MIPS 指标高，但实际上 A 的性能比 B 差，MIPS 指标和真实情况背道而驰。

## Summary

!!! important
    + 8 个伟大思想是计算机体系结构的基本，应用非常广泛
    + 计算机程序的性能是多个影响因素的共同作用结果
    + 性能的定义：`response time` 和 `throughput`
    + 经典性能公式
    + 目前的问题：功耗墙
    + 功耗墙的解决方法：多核 + 并行

----------

## Road Map for This Book

计算机可以划分为经典的 5 部分：`datapath`, `control`, `memroy`, `input`, `output`，分别在后续几章介绍：

+ `datapath`：Chapter 3, Chapter 4, Chapter 6, Appendix B
+ `Control`：Chapter 4, Chapter 6, Appendix B
+ `Memory`：Chapter 5
+ `Input`：Chapter 5, Chapter 6
+ `Ouptut`：Chapter 5, Chapter 6