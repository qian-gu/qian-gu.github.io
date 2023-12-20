Title: Patterson and Hennessy 学习笔记 #6 —— Chapter 6 Parallel processors from Client to Cloud
Date: 2021-03-13 16:17
Category: IC
Tags: Patterson and Hennessy
Slug: learning-patterson-and-hennessy-notes-6-chapter-6
Author: Qian Gu
Series: Patterson & Hennessy Notes
Summary: Patterson and Hennessy 读书笔记，第六章

> I swing big, with everything I've got. I hit big r I miss big. I like to live as big as I can.
> 
>   -- Bebe Ruth
> 
>   -American baseball player-

## Introduction

计算机设计者一直追寻的“黄金之城”：只需要将现有的多个小计算机简单地连接在一起来构成功能强大的计算机，这就是多处理器 `multiprocessor`。几个概念：

| 术语                                                    |   含义                                       |
| ------------------------------------------------------ | -------------------------------------------- |
| `multiprocessor`                                       | 至少包含 2 个 processor 的计算机系统             |
| `task-level parallelism` / `process-level parallelism` | 在多个 processor 上同时运行相互独立的程序         |
| `paralle processing program`                           | 在多个 processor 上运行的单个程序                |
| `cluster`                                              | 通过局域网连接的一组计算机形成的大型 multiprocessor |
| `multicore microprocessor`                             | 在单芯片上包含多个 core 的 microprocessor        |
| `SMP`(shared memory processor)                         | 共享同一物理地址空间的并行处理器                   |

如第一章所述，因为功耗墙的原因，现在的发展趋势是多核，而非提高主频或者是改进 CPI，这也意味着关心性能的程序员必须成为并行程序员，因为串行等于速度慢。所以业界现在面临的主要问题是：**设计出一套软硬件，使得程序员可以轻松地写出能随着并行度变化的高效运行的程序。**

实现这个目标的难点不在于硬件，而是基本上没有什么重要软件被重新编写，以便在 multiprocessor 上高效运行。事实上在 multiprocessor 上写程序很困难，而且难度会随着 core 数量增长。为什么并行程序更加难开发呢？原因有几点：

+ 写并行程序的前提一定是有收益（性能 or 能效 更高），否则还不如写顺序程序，因为顺序程序写起来更加简单
+ 单处理器技术（超标量、乱序执行 etc）可以在不改变程序的前提下充分利用 `ILP`(instruction-level parallelism)，获得高性能
+ 并行程序有额外开销（掉队、分割任务、负载均衡、同步和通信）
+ `Amdahl` 定律

Amdahl 定律：

$$T_{after} = \frac{T_{affected}}{Amout\ of\ improve} + T_{unaffected}$$

也可以改写成：

$$speed\_up = \frac{T_{before}}{(T_{before}-T_{affected})+\frac{T_{affected}}{n}}$$

$$speed\_up = \frac{1}{(1-Frac_{affected}) + \frac{Frac_{affected}}{n}}$$

从书里面的两个例子可以看到，有时候必须增加问题的规模才能保持高加速比，而且负载不均衡对加速效果影响很大。

1960 年代提出的一种基于指令流和数据流的数量进行分类的方法：

|                      | signle data              | multiple data                   |
| -------------------- | ------------------------ | ------------------------------- |
| signle instruction   | `SISD` (Intel Pentium 4) | `SIMD` (SSE instruction of x86) |
| multiple instruction | `MISD` (Nop)             | `MIMD` (Intel Core i7)          |

SIMD 有两种重要表现形式：

+ `MMX`
+ `vector`

vector 和 scalar 相比的好处有：

+ 一条 vector 顶很多条 scalar，所以指令 fetch 和 decode 的带宽大幅降低
+ 硬件不需要检查 vector 中 element 之间的数据相关性
+ 比 MIMD 编程简单
+ 两条 vector 指令之间只需要检查一次相关性（scalar需要对每个element都进行检查），功耗更低
+ vector 一次从 DDR 搬运一整块数据时开销只有一次，scalar 是多次
+ loop 引起的 contrl hazard 在 vector 不存在
+ 指令带宽更低、不需要 hazard 检查、DDR 带宽利用率高，所以 vector 的能效比更高

vector 和 MMX 的对比：

+ MMX 是 `LVS` (vector length specific)，vector 是 `VLA` (vector length agnostic)
+ MMX 的 load/store 必须地址连续，而 vector 支持 index/stride 模式

## Hardware Multithreading

相关的几个术语：

| 概念 | 含义 |
| --------------------------------- | --------------------------------------------------------------- |
| `hardware multithreading`         | 在一个 thread 发生 stall 时硬件可以切换到另外一个 thread               |
| `thread`                          | 包含了 PC + register file + stack，共享同一片虚拟地址空间，切换不涉及 OS |
| `process`                         | 包含了 1 个或多个 thread、虚拟地址空间、OS 状态，切换涉及到 OS            |
| `SMT` Simultaneous multithreading | 利用多发射、动态调度使用资源，从而降低 thread 切换成本的技术            |

MIMD 是通过 process 和 thread 使得多个 core 一直保持 busy，从而提高性能和利用率，而 `hardware multithreading` 则可以让多个 thread 共享单一 core 的功能单元 FU (functional unit)，从而提高硬件的利用率。举个例子：比如某个 thread 发生了 stall，如果没有硬件多线程，那么 FU 就会处于 IDLE 状态，利用率下降；而如果有硬件多线程，那么可以切换执行另外一个线程，让 FU 一直保持 busy 状态，利用率不会下降。

显然每个 thread 都有自己的状态（比如 register file 和 PC），所以硬件要复制这些状态才能支持 hardware multithread，而且硬件切换 thread 的速度必须很快才行，否则还没等切换好 stall 已经解决了，那么硬件多线程就毫无意义了。一般 thread 的切换基本可以做到实时（1-2 cycle），而 process 的切换则需要花费成百数千的 cycle。

硬件多线程可以分为两类：

| 类型 | 定义 | 切换时间 | 优点 | 缺点 |
| ---- | ---- | ------ | --- | ---- |
| `fine-grained multithreading` | 每条指令执行后都发生切换 ，一般用 RR 轮询 threads | 1 cycle | 可以隐藏各种长短 stall 导致的 throughput 损失 | 某个 thread 可能会被其他 thread 阻塞 |
| `coarse-grained multithreading` | 只有在重大事件（如 last-evel cache miss）发生后才发生切换 | 多个 cycle | 对切换速度要求低 | 无法隐藏（如 shorter stall 导致的） throughput 的损失 |

`SMT` 是另外一种多线程技术，可以利用多发射、动态调度等技术使用硬件资源，在 ILP 的基础上还充分利用了 TLP。SMT 的主要思想是：

**多发射处理器内通常有多个 FU 可以并行使用，所以配合寄存器重命名和动态调度策略，就可以不检查多个 thread 之间的相关性，直接发射多条指令，相关性的检查和维护留给动态调度机制来解决。**

如果 superscalar 不支持 hardware multithreading，那么会受限于有限的 ILP，发生 stall 时甚至会使整个 core 处于 IDLE 状态，最终导致利用率不高。

## Multicore and Other Shared Memory Multiprocessors

前面已经描述了并行编程的困难之处，所以有个自然的问题：计算机设计者可以在这个问题上做些什么？答案之一是：为所有处理器提供一个共享的单一物理地址空间，这样程序就不需要关心自己的数据在哪里，从而降低并行程序的编写难度。这种处理器就叫做 `SMP` (shared memory multiprocessor)。还有一种方案是每个 core 都有自己的地址空间，然后显式地共享数据（即 cluster）。

SMP 可以分成两类：

| 类型                             | 含义                                           |
| ------------------------------- | ---------------------------------------------- |
| `UMA` uniform memory access     | DDR 中每个 word 对任何一个 core 的 latency 是一样的 |
| `NUMA` nonuniform memory access | DDR 中某些 word 对某些 core 的访问速度要更快一些     |

因为多个 core 可能会同时操作共享数据，所以 core 之间一定要做同步机制，否则就可能发生错误，其中一种同步方式就是锁 `lock`，保证任何时候只有一个 core 操作数据，别的 core 必须等待直到锁被释放。RISC-V 中相应的是 A 子集中的相关指令。

!!! tip
    除了提供共享的单一物理地址空间之外，还有另外一种选择：物理地址空间是分散的，但是虚拟地址空间是统一的，由操作系统负责处理通信。这种方案已经被尝试过了，但是开销太大了。

## Introduction to GPU

略

## Cluster, Warehouse Scale Computer, and Other Message-Passing Multiprocessor

略

## Multiprocessor Benchmarks and Performance Models

### Benchmark

benchmark 不仅仅是一个单纯的指标，它关系到销售量、设计者的声誉，所以要保证无法通过小 trick 获得好的虚假结果，也要能实实在在地体现出真实应用场景中的性能。为了避免各种小 tricks，一个重要规则就是：不能修改 benchmark，代码和数据结构都是固定的，只有一个正确结果。违背了这个规则结果就是无效的。

几个常见的 benchmark：

+ `Linpack`
+ `SPECrate`
+ `SPLASH` / `SPLASH2`
+ `NAS`
+ `PARSEC`

随着技术的发展，以前的旧 benchmark 显得有些过时，不断有新的 benchmark 被提出来。

### Performance Models

和 benchmark 相关的另外一个话题就是性能模型，因为有各种新的体系结构不断被提出，所以如果有一个简单的模型可以比较不同体系结构的性能，将是非常有益的。这个模型不需要非常精确，只要能说明一些问题即可。

cache 中的 3C 模型就是一个很好的例子，它忽略了很多重要因素，比如 block 大小、block 放置策略、block 替换策略等等。而且它还有些含糊不清，比如 miss 的原因在不同的设计中是不一样的。即使如此，这个模型仍然流行了 25 年，原因就是它提供了一个深刻理解程序行为的途径，可以说明一些设计中的问题，帮助体系结构的设计者和程序员改进自己的设计。

而对于多核系统来说，我们也需要一个这样的模型。首先，我们可以将一个程序/系统分成两部分：计算 + 存储。

+ 计算：显然最高性能由总的计算资源决定，当资源利用率是 100% 时就达到了最高性能，不可能比这个值再高，这个值就是硬件系统的峰值性能
+ 存储：最常见的指标就是带宽

根据下面这个量纲公式，

$$\frac{Operation/Sec}{Operation/Byte} = Byte/Sec$$

可以知道，分母表述了一个算子自身的性质，算子对计算量和数据量需求的比例。这个指标叫做计算密度 `arithmetic intensity`。

将这几个概念组合在一起就得到了大名鼎鼎的 `Roofline Model`：

+ 横坐标是 算子的 arithmetic intensity，单位是 OPs/Byte
+ 纵坐标是可以 算子在该系统上可以获得的性能，单位是 GOPs/Sec
+ 屋顶是硬件系统的峰值性能
+ 屋檐是硬件系统的存储带宽性能
+ 任何一个算子肯定是落在 Roofline 的下面
+ 一旦硬件系统确定了，Roofline 就不会改变，变化只是算子可以获得的性能
+ 算子落在斜线屋檐下面，表示它是带宽受限
+ 算子落在屋顶下面，表示它是计算受限
+ 屋顶的“脊点”，是计算机系统的重要指标
    + 过于靠右，表示只有 intensity 很大的程序才能充分利用资源，达到最大性能
    + 过于靠左，表示几乎任何程序都可以达到最大性能

如果我们的程序的结果远远低于模型上界，即离 Roofline 很远，应该做哪些优化呢？

还是分类讨论，

+ 如果是计算受限
    + 平衡操作：避免因为其他因素成为瓶颈。比如算子中一般浮点运算和浮点加法、浮点乘法的数量一样多，如果浮点加法/乘法资源太少、或者加法/乘法指令太少，则会导致浮点性能达不到最高
    + 提高 ILP 且使用 SIMD：避免指令瓶颈导致硬件资源 IDLE
+ 如果是带宽受限
    + 软件预取：提前取数，减少 memory 等待时间
    + 内存关联：从不同 memory 分散取数会导致性能下降，分配数据时尽量让 thread 和 data 都分配到同一个 processor 上

## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**谬论：Amdahl 定律不适用于并行计算机**

在 weak scaling 问题上得出的错误结论，Amdahl 定律仍然适用于并行计算机。

**谬论：峰值性能可以代表实际性能**

首先单核系统就很难达到峰值性能，其次多核并行处理时 Amdahl 定律也告诉我们想获得完美的峰值性能几乎不可能。更实际的做法是用 Roofline 模型来分析系统实际可以达到的整体性能。

**陷阱：开发软件时不针对多核系统做优化**

软件针对硬件专门设计，充分利用硬件资源，才能达到最高性能

**陷阱：不用提升带宽就可以获得很高的 vector 性能**

从 Roofline 模型可以看到，带宽对系统的性能有很大的影响。

## Summary

!!! important
    + 单纯地把多个 processor 连接到一起并不能很轻易就获得高性能（并行软件很那写 + Amdahl 定律）
    + 计算机行业的未来已经绑定在并行化上了
    + SIMD 和 vector 比 MIMD 的能效高
    + 想要达到高性能，程序员必须将自己的串行程序并行化，或者直接重写全新的并行程序
