Title: Patterson and Hennessy 学习笔记 #4 —— Chapter 4 The Processor
Date: 2020-12-20 22:28
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

## Introduction

第一章中提到，影响一个计算机性能的因素有 3 个：

+ 指令总数
+ 时钟周期
+ 每条指令的执行时钟数（CPI）

从第二章可知对于一个特定程序，由编译器和 ISA 共同决定了第一个因素：指令总数。而一个 processor 的实现决定了另外两个因素，所以这章介绍 RISC-V 处理器 `control path` 和 `data path` 的两种不同实现方案。

## A Simple Implementation Scheme

从 RISC-V ISA 中挑选出三种具有代表性的指令组成一个小子集，

+ 代表和 memory 交互的 `ld`, `st` 指令
+ 代表算术-逻辑运算的 `add`, `sub`, `and`, `or` 指令
+ 代表分支运算的 `beq` 指令

这个小子集非常具有代表性，其他指令的处理基本上都和这几个指令类似，搞懂了这几个指令的处理，其他指令的处理也就大同小异。以实现这个小子集为目标，处理器核设计的经典问题如下：

+ 取指：如何产生下一个 PC
+ 译码：如何产生内部控制信号
+ 读操作数：register file 的设计（包括端口数量、实现方式）
+ 执行：如何根据控制信号复用 ALU 等单元，完成算术运算、分支判断、访存地址计算 etc
+ 访存：如何访问 memory
+ 写回：未涉及

上面几个问题可以分成 `control path` 和 `data path` 两大类，各个击破。

![nopipe](/images/learning_patterson_and_hennessy_notes_4_chapter_4/nopipe.png)

这个实现方案中一条指令的所有处理都在一个 cycle 内完成，所有组合逻辑都在一起，显然这个方案的主频非常低。虽然 CPI 是 1, 但是时钟周期实在是太长了，所以性能非常差。历史上早期 CPU 的 ISA 非常简单，所以确实曾经用过这种实现方案，但是现在基本是不可接受的。

因为时钟周期要覆盖最恶劣的组合逻辑路径，所以即使我们尝试使用实现技巧优化大部分常见情况，单周期版本的实现方案的性能不会有任何提升，这和 **common case fast** 这一伟大思想相违背。

## An Overview of Pipeling

Pipeline 的基本概念，是在一个很长的组合逻辑路径中插入寄存器，切分成多个小段，这样时钟周期只需要 cover 住 latency 最长的小段即可，因此 Pipeline 可以提高时钟频率。需要注意的是插入寄存器后，处理单条指令的总时间（`latency`）实际上变长了，因为寄存器翻转也需要时间，但是由于指令可以重叠在一起并行处理，所以 Pipeline 提高系统的吞吐率（`throughput`），提高了整体性能（所有指令的总处理时间变小）。

假设整个组合逻辑被切分成 n 个 latency 相似的 stage，每个 stage 的 latency 为 T₀，则单周期方案需要的总时间为

$$T_{nopipe} = n * T_0$$

而 pipeline 方案，假设指令之间没有冒险，则所有之间直接可以完美重叠，则每条指令的执行时间为

$$T_{pipe} = T_0$$

显然在理想情况下，pipeline 版本的性能近似可以提高 n 倍，流水线切分地越细，每条指令的执行时间 T₀ 就越小，性能越高。一般低端 MCU 大概 2～3 个 stage，而高端 CPU 高达 10 个 stage。

性能提升 n 倍是非常理想的理论数据，实际上有很多因素导致最终效果稍差：

+ stage 并不是均匀切分
+ 指令之间有冒险，不能完美重叠
+ 流水线建立和撤销的开销

很容易就可以分析得出结论：当指令数量非常多时，近似可以忽略第三个因素。关于第二个因素 **冒险** 可以分为三类：

| 类型 | 含义 | 解决方法 |
| ----- | ---- | ----- |
| 结构冒险 `structural hazard` | 硬件 busy 无法计算下一条指令 | 硬件资源复制 |
| 数据冒险 `data hazard` | 数据依赖 RAW 等 | `forward` / `rename` |
| 控制冒险 `contrl hazard`/ 分支冒险 `branch hazard` | 取指不正确导致指令不能在预定时钟周期内执行 | `prediction`(`BTB`/`BTH`) / delay slot |

基本上每个 stage 都有对应的核心问题需要解决，各种各样的解决方案实现复杂度、消耗的资源和达到的性能都不相同，这些解决方案按照不同的方式组合在一起，就形成了高中低等不同系列的 CPU。关于每个 stage 的问题及解决方案可以扩展出很多内容，更详细的内容略。

!!! note
    除了存储系统外，pipeline 的有效运作是决定一个处理器 CPI 的最重要因素。不管实现方案是否简单、性能高低，结构冒险、数据冒险、控制冒险这三种冒险是 pipeline 中非常重要的问题。一般来说，

    + 结构冒险通常发生 FPU 中，因为它无法做到完全的 pipeline
    + 控制冒险通常发生在整数程序中，因为这些程序中 branch 出现概率很高
    + 数据冒险在整数、浮点中都会出现，一般浮点因为规则的存储和较低概率的条件分支所以更好处理一些，而整数更难处理一些

    有很多基于软硬件的技术通过调度来减少数据之间的依赖。

    Pipeline 是一个非常伟大的思想，基本上计算机体系结构的非常大一部分都是围绕着它做优化设计，虽然它可以提高性能，但是并不是没有代价，其中之一就是电路的复杂化，现代处理器多发射乱序执行的超标量处理器想想就非常复杂。

## A Pipelined Scheme

流水线可以按照很多方式划分，其中最典型的是 MIPS 的 **经典 5 级流水线**：

+ `IF`：取指
+ `ID`：译码
+ `EX`：执行
+ `MEM`：访存
+ `WR`：写回

整个 pipeline 里面，大部分数据流都是从左向右流动，只有两条是反向的，而这两条路径会引起两类冒险：

+ 第一条是 WR 阶段，执行执行结果写回到 regfile 中 ==> 数据冒险
+ 第二条是 IF 阶段，选择下一条 PC 的取值 ==> 控制冒险

![pipe](/images/learning_patterson_and_hennessy_notes_4_chapter_4/pipe.png)

## Exceptions

控制通路是处理器设计中最难的部分：正确控制和达到高频率都非常困难。控制必须处理的一个问题是 `exception` 和 `interrupt`，它们是除 branch 指令之外可以控制程序流的事件，主要用来处理 CPU 内部的 unexpected 事件，比如未定义的指令格式等。

许多架构中并不区分这两个概念，统称为 interrupt，比如 x86 。RISC-V 对这两种情况做了区分：

+ **exception**: 无论是内部还是外部原因，导致程序控制流发生变化的 unexpected change
+ **interrupt**：只用来描述外部因素导致控制流发生变化的情况

| 事件类型 | 由何处产生 | RISC-V 术语 |
| ------- | -------- | ---------- |
| 系统复位 | 外部 | Exception |
| I/O 设备请求 | 外部 | Interrupt |
| 用户程序唤醒操作系统 | 内部 | Exception |
| 使用未定义指令 | 内部 | Exception |
| 硬件故障 | 内外均可 | 两个术语均可 |

RISC-V 处理 Exception 时要做的事情就是：保存异常现场，然后把控制权交给操作系统，由操作系统完成合适的处理，比如执行某些提前定义好的处理、定制运行程序、上报 error 等，然后操作系统根据情况决定是否要中止程序还是继续运行。

操作系统要完成异常处理，必须要知道异常的原因和导致异常的指令，有两种方法传递这个信息：

+ 使用寄存器保存异常信息（`SPEC` / `SCAUSE`）
+ 使用向量中断 `vectored interrupts`

RISC-V 中没有使用向量中断，而是使用寄存器作为所有异常的单一入口，所以需要对寄存器内容做一些译码才能知道异常原因。对于 Exception 的处理和 branch 预测失败的处理非常相似，实际上硬件就是把 Exception 当成另外一种形式的 `control hazard` 来处理：

1. flush 流水线，然后从一个特定地址（中断处理程序）重新取指

    一般来说，要在 Ex 阶段就要把 Exception 指令 flush 掉，否则错误结果会写入到 dst 寄存器中，导致覆盖原来的有效值。很多时候，发生 Exception 的指令最终还是要正确执行完成的，所以最简单方法就是完成异常处理后重新取指、执行这条指令。

2. 保存 Exception 现场

    RISC-V 中定义了两个寄存器来保存异常现场：

    + supervisor exception program counter (`SPEC`) 保存异常指令的地址
    + supervisor exception cause register (`SCAUSE`) 有个特殊字段保存异常原因

Exception 处理中，要把 pipeline 中每一个 Exception 和相对应的指令对应起来是非常难的，所以有些设计者会在非关键情况下放松要求，这种叫做非精确中断/异常（`imprecise interrupt`/`imprecise exception`），也就是说引起异常的某一条指令，但是硬件记录的其实是另外一条指令，由操作系统去判断具体是哪一条引起的异常。与其相对的，严格要求的叫做精确中断/异常（`precise interrupt`/`precise exception`）。RISC-V 等一些处理器都支持精确异常，部分原因是非精确异常对操作系统来说很头疼，所以对于 pipeline 很深的设计一般要求要把发生异常时流水线上的所有指令都记录下来，这样做对硬件和软件来说都比较容易（另外一个原因是为了支持虚拟存储器）。

## Parallelism via Instructions

!!! tip
    这部分只是简述，《量化分析》中花费了一整个章节和附录，一共大概 200 多页来展开详细描述。

如前所述，pipeline 可以挖掘指令之间潜在的并行潜力，这种并行性叫做 Instructions Level Parallelism (`ILP`)。要想提高 ILP 一共有两种方法：

+ 增加 pipeline 的深度，让更多的指令可以重叠在一起

    stage 切分地越多，时钟频率也越高，理论性能提升上限就越高（前面分析的 n 倍），实际中有其他因素限制，并不是线性无线增长。

+ 多发射 `multiple issue`，复制内部的硬件资源，使得每个周期可以启动更多的指令

    多发射可以让 CPI 的值小于 1，比如一个 5 stage 的 3GHz 4-way 多发射处理器的峰值性能是 1.2 billion instruction/second，最小 CPI 是 0.25，每个 cycle 最多可以并行执行 20 条指令。现在高端处理器一般都是 3～6 发射，一些中端处理器的目标是 IPC = 2。实际上，指令并行多发射的前提条件非常多，比如指令之间有依赖。

实现多发射的方式可以大致分为两类：

| 类型 | 含义 |
| ----- | ---- |
| `static multiple issue` 静态多发射 | 编译器在编译时就已经做好了指令发射的判断 |
| `dynamic multiple issue` 动态多发射 | 硬件在执行时做发射的相关判断 |

无论是那种实现方式，都需要解决下面这两个问题：

1. 把指令打包到 `issue slot` 中

    即处理器如何判断在某个 cycle 下应该发射多少条、哪些指令？在静态发射处理器中大部分工作都由编译器负责处理，而在动态发射处理器中，虽然编译器也会做一部分优化工作，比如调整指令顺序，但是大部分工作都是主要由硬件负责完成。

2. 处理 `data hazard` 和 `control hazard`

    在静态处理器中由斌啊一起完成所有的数据冒险和控制冒险，而绝大多数动态发射处理器在运行时通过硬件技术消除冒险。

虽然分成了静态和动态两类，实际上这些方法之间都是相互借鉴的，没有任何一种方法是纯粹独立的。

### The Concept of Speculation

发掘 ILP 的一个重要方法是推测 Speculation，基于伟大思想之一的 **prediction**，speculation 是一种通过猜测指令运行结果，以使得依赖此指令的其他指令可以提前执行的方法。比如可以推测一个 branch 指令的结果，然后就可以提前执行 branch 之后的其他指令；另外一个例子是假设有 store 和 load 两条指令，推测它们指向不同地址，然后就可以把 load 放在 store 之前运行。

显然肯定会有推测出错的情况，所以任何推测机制都需要有某种方法可以检查推测结果是否正确，如果出错了要能回滚推测状态的指令结果。

推测可以由软件完成，也可以由硬件完成。这两种方法处理推测错误的方式也非常不同：

+ 软件方式：编译器一般会插入额外的检查推测正确性的指令，如果出错了会提供一个修复例程
+ 硬件方式：先把推测指令的结果 buffer 起来，等待解除了推测状态后写入到 register file/memory 中，如果推测错了则 flush 流水线，重新取正确的指令执行

如果处理得当，推测可以提高性能，反之会降低性能。下面详细展开静态/动态发射两种方案中的推测技术。

### Static Multiple Issue

所有的静态多发射处理器都会用到编译器来辅助完成指令打包和处理冒险这两个问题。某个时钟周期下同时发射的指令叫做 `issue packet`，可以把它们看成是一条更宽、同时操作多个操作数的“大指令”，这就是 Very Long Instruction Word （`VLIW`）。

大部分静态多发射处理器都依赖于编译器来完成一些冒险处理，但是实现方式千差万别：有些实现中编译器负责移除所有的冒险，比如调度指令顺序，插入 nop 指令等，因此硬件完全不需要任何冒险检测和 stall 控制逻辑；有些实现中编译器只保证 packet 内部无冒险，而 packet 之间的冒险需要硬件负责。

根据上面的讨论，假设我们有一个简单的静态双发射处理器：

+ 只允许 ALU/Branch 和 Load/Store 指令打包在一起（嵌入式处理器的常见设计）
+ 每个 cycle 发射的指令按照 64bit 对齐打包，且 ALU/Branch 在 LSB（通常为了简化译码逻辑，打包指令的格式有严格要求）
+ 如果不满足打包要求，则使用 Nop 凑数
+ 编译器负责 packet 内部无冒险，硬件负责处理 packet 之间的冒险

要实现这个规格，我们需要做下面一些改变：

+ 新增 packet 之间的冒险检测和 stall 控制逻辑
+ register file 新增读写端口
+ 额外的硬件资源执行指令

显然双发射最高可以将性能提高 2 倍，但是实际上因为各种开销和限制因素，很难达到理论效果，而且为了有效地挖掘多发射的潜在性能，对编译器和硬件调度技术要求很高。对于循环来说，有一种非常重要的优化技术就是 loop unrolling，即循环展开，通过循环展开把不同迭代次数的指令重叠在一起，从而挖掘出更高的 ILP。

书里面有个例子，对下面这段程序重排序，使得其在上述双发射处理器上的性能达到尽可能高。

```
#!text
Loop: ld   x31, 0(x20)      // x31=array element
      add  x31, x21         // add scalar in x21
      sd   x31, 0(x20)      // store result
      addi x20, x20, -8     // decrement pointer
      blt  x22, x20, Loop   // branch if x20 > x22
```

仔细分析代码，就可以知道前 3 条指令之间有依赖，最后两条指之间也有依赖，只有一对指令可以打包到一起，所以需要用 4 个 cycle 完成 5 条指令，IPC = 5/4 = 1.25，离理论最大值 2 差距很大。

重排序结果：

|      |   ALU/Branch instr  | Load/Store instr | clock Cycle |
| ---- | ------------------- | ---------------- | ----------- |
| Loop |                     |   ld x31, 0(x20) |       1     |
|      |  addi x20, x20, -8  |                  |       2     |
|      |  add x31, x31, x21  |                  |       3     |
|      |  blt x22, x20, Loop |   sd x31, 8(x20) |       4     |

按照 4 倍循环展开的结果：

|      |   ALU/Branch instr  | Load/Store instr | clock Cycle |
| ---- | ------------------- | ---------------- | ----------- |
| Loop |  addi x20, x20, -32 |   ld x28, 0(x20) |       1     |
|      |                     |   ld x29, 24(x20)|       2     |
|      |  add x28, x28, x21  |   ld x30, 16(x20)|       3     |
|      |  add x29, x29, x21  |   ld x31,  8(x20)|       4     |
|      |  add x30, x30, x21  |   sd x28, 32(x20)|       5     |
|      |  add x31, x31, x21  |   sd x29, 24(x20)|       6     |
|      |                     |   sd x30, 16(x20)|       7     |
|      |  blt x22, x20, Loop |   sd x31,  8(x20)|       8     |

经过循环展开后，8 个 cyle 可以完成 14 条指令，IPC = 14/8 = 1.75，如果迭代总次数为 4 次，则总时间由原来的 20 个 cycle 变为 8 个 cycle，而付出的代价就是需要使用额外的 4 个寄存器，同时代码体积也变为原来的 2 倍。

### Dynamic Multiple Issue

动态多发射处理器有个非常有名的外号——超标量处理器 `superscalar processor`，在最简单的超标量处理器中，指令是顺序发射的，由硬件决定当前时钟周期能否发射多少条并行指令。显然在这种超标量处理器上还是需要编译器配合优化才能达到最高的发射速率，得到最好的性能。

虽然同样都需要编译器调度，但是 superscalar 和 VLIW 在本质上是不同的：

+ superscalar 无论有无编译器调度，而且无论发射速率和流水线结构怎么变化，代码都可以正确执行
+ VLIW 必须要有编译器调度，而且在不同平台上运行时通常都要重新编译才能正确运行，即使有些处理器正确性可以保证，但是往往因为性能仍然需要重新编译

许多 superscalar 把动态发射算法扩展成一整套体系：`dynamic pipeline scheduling`，即动态调度算法。最经典的动态调度算法就是 Tomasolu 算法，涉及到的术语有 `reservation station`, `commit`, `reorder buffer`, `out-of-order execution`, `in-order commit` 等，这里不展开描述。

注意：目前所有动态调度算法都使用 in-order commit。

既然编译器也可以做调度，为什么 superscalar 还需要用动态调度算法呢？原因大概有 3 个：

+ 编译器无法预测所有的 stall，特别是 cache miss 等，动态调度可以让处理器隐藏某些 stall
+ 使用动态分支预测时，如果不搭配动态调度则 ILP 的性能提升非常有限
+ 静态调度无法适应硬件平台切换，必须重新编译，而动态调度不需要重新编译，对软件不可见，代码复用高

!!! note
    现代高性能处理器都可以在每个 cycle 发射多条指令，但是很不幸的是要维持高 issue rate 非常困难。比如，虽然现在处理器都可以达到 4～6 发射的并行读，但几乎没有什么应用可以保持在 2 以上的发射速率，主要原因有两个：

    + 主要性能瓶颈来自于无法避免的 data hazard，虽然基本无法优化真数据依赖 RAW，但是编译器和硬件通常连是否存在依赖都不确定，所以只能保守地认为存在依赖。一般来说，ILP 总是有优化空间的，但是因为太分散（可能存在于上千条指令之间），编译器和硬件往往力不从心。
    + memory hierarchy 的损失会导致 pipeline 无法保持满负荷运行，虽然有些 stall 可以掩盖起来，但是有限的 ILP 无法掩盖所有 stall。

### Energy Efficiency

动态调度算法和推测执行虽然可以挖掘 ILP，提高性能，但是代价之一就是更高的功耗。因为现在我们遇到了功耗墙的问题，所以目前的趋势是舍弃超长的 pipeline 和贪婪的推测算法，而是转向多核。

## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**谬论：pipeline 非常简单**

呵呵。

**谬论：pipeline 的概念和实现工艺无关**

显然，工艺的实现难度和代价会反过来影响设计的取舍。

**陷阱：没有考虑到 ISA 的设计会反过来影响到 pipeline 的设计**

很多复杂的 ISA 会导致实现的困难，这也是 RISC-V 的设计目标之一：用简单的 ISA 简化硬件设计，以达到更高的主频和性能。

## Summary

!!! important
    + pipeline 可以提高 throughput 但是不能减少 latency
    + pipeline 和 multiple issue 都可以提高 ILP
    + hazard 限制了可以达到的性能上限
    + static multiple issue 依赖编译器发现、解决 hazard
    + dynamic multiple issue 依赖硬件发现、解决 hazard
    + 基于软件/硬件实现的 scheduling 和 speculation 是降低 data hazard 负面效果的主要手段
    + 在功耗墙的背景下，现在的趋势是舍弃以前超深的流水线和复杂的推测算法，转向多核，在更粗粒度上寻求并行性