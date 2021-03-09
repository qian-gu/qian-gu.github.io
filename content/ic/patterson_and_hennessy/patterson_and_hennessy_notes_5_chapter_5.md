Title: Patterson and Hennessy 学习笔记 #5 —— Chapter 5 Large and Fast:Exploiting Memory Hierarchy
Date: 2020-12-20 22:28
Category: IC
Tags: Patterson and Hennessy
Slug: learning_patterson_and_hennessy_notes_5_chapter_5
Author: Qian Gu
Series: Patterson & Hennessy Notes
Summary: Patterson and Hennessy 读书笔记，第五章
Status: draft

> Ideally one would desire an indefinitely large memory capacity such that any particular ... word would be immediately available. ... We are ... forced to recognize the possibility of constructing a hierarchy of memories, each of which has greater capacity than the preceding but which is less quickly accessible.
> 
>   -- A. W. Burks, H. H. Goldstine, and J. von Neumann
> 
>   _Preliminary Discussion of the Logical Design of an Electronic Computing Instrument_, 1946

## Introduction

如前所述，码农和硅农之间有一个矛盾：码农希望内存无限大的同时访问速度足够快，而硅农手上的存储器容量大的速度不够快、速度快的容量不够大。实际上程序访问数据并不是完全随机的，**局部性原理** 告诉我们，在任何时候程序大概率都是只访问地址空间中相对较小的一部分：

+ 时间局部性：如果某个数据被访问了，那么近期很可能会被再次访问
+ 空间局部性：如果某个数据被访问了，那么和它相邻的数据也很可能被访问

!!! tip
    程序的局部性源自于它的结构：大部分程序都包含循环，所以有很高的时间局部性；程序顺序存储，所以有很高的空间局部性，而且顺序访问数据（数组）时，数据也有很高的空间局部性。

所以解决前面矛盾的方式就是：利用局部性原理，构建存储器层级结构 `Memory Hierarchy`，用最低的成本向用户提供尽可能大的存储容量的同时，使得速度和最快的存储器相当。

Memory Hierarchy 的几个概念：

| 概念                   | 含义                                                            |
| ---------------------- | -------------------------------------------------------------- |
| 块 `block`/行 `line`   | 对于任一相邻的两层来说，高层和底层之间交换数据的最小单位                   |
| 命中 `hit`             | 处理器需要的数据存储在高层存储器中                                    |
| 缺失 `miss`            | 处理器需要的数据没有存储在高层存储器中                                 |
| 命中率 `hit rate`      | 在高层存储器中找到数据的访问比例，被当作 Memory Hierarchy 的性能指标     |
| 缺失率 `miss rate`     | 1 - `hit rate`                                                 |
| 命中时间 `hit time`     | 访问某层的时间，包含了判断 hit/miss 逻辑在内的的总时间开销              |
| 缺失惩罚 `miss penalty` | 从低层向高层搬运一个 block 的时间开销，包含了访问块、逐层传输、插入数据等   |

!!! tip
    Memory Hierarchy 对计算机的性能至关重要，硅农们为此设计了大量复杂精巧的设计，本章做了大量简化和抽象，只讨论最基本的知识。

    在大部分真实的计算机系统中，Memory Hierarchy 就是一个真实的层次结构，高低层之间是包含关系，这意味着一个数据除非出现在 i+1 层，否则它不可能出现在第 i 层。

## Memory Technologies

主要有 4 种：

|      种类      |   价格 |  速度 |     应用   |
| ------------- | ------| ----- | --------- |
| SRAM          | 最贵   |  最快 |  cache/TCM |
| DRAM          | 贵     |  快   | DDR       |
| Flash         | 便宜   |  慢   | 二级存储    |
| Magnetic disk | 最便宜  |  最慢 | 硬盘       |

## Caches

!!! tip
    Cache 大概是 prediction 思想最重要的例子。依赖于局部性原理，Cache 可以靠自身的一套机制在预测错误时取回正确数据，现代计算机中的 Cache 的命中率通常保持在 95% 以上。

Cache 的形式就是一张 table，大概可以分成 3 个字段：

+ valid 指示本 entry 是否有效
+ tag 指示本 entry 保存的是 DDR 的哪个地址的数
+ data 保存具体数据

使用地址索引 cache 时，地址会相应地被分成 3 部分：

+ offset：索引 block 内部的 byte
+ index：索引 block
+ tag：和 cache 中的 tag 做比较

!!! tip
    假设在 64bit 系统中有个直接映射的 cache，一共有 $2^n$ 个 block，每个 block 的大小为 $2^m$ 个 word，

    那么 offset 的位宽为 $m+2$ bit，index 的位宽为 $n$ bit，tag 的位宽为 $64-(m+2)-(n)$ bit，所以 cache 占用的总 bit 为，

    $2^n*(block\ size + tag\ size + valid\ size) = 2^n*(2^m*32 + (64-n-m-2) + 1)$

    但是一般说 cache 容量的时候都只指 data 部分的容量。所以 n = 10, m = 1 时，这个 cache 的容量是 4 KiB。

### Mapping

Cache 的组织方式可以分为 3 类：

|               类型              |          优点        |        缺点      |
| ------------------------------ | ------------------- | ---------------- |
| 直接相联 `directly associative` | 硬件简单              | 冲突概率高，利用率低 |
| 全相联 `fully associative`      | 冲突概率低、利用率高    | 硬件实现复杂        |
| 组相联 `set associative`        | 折中                 | 折中              |

直接相联和全相联可以看成是组相联的特例：

+ 直接相联 = 1-way 组相联
+ 全相联 = 只有 1 个 set 的组相联

!!! tip
    + 一般来说，在容量一定的前提下，混合 cache 的 miss rate 要比分离 cache 低一些。但是分离 cache 的带宽更高，这个优点的收益超过了 miss rate 的增加。
    + 多级 cache 的设计和最优化单级 cache 的设计理念是不一样的。和单级 cache 相比，多级 cache 中的第一级容量一般都更小，block 也更小，所以 miss penalty 也更小。而第二级一般比单级 cache 容量更大，因为第二级的访问时间的重要性没有那么高，容量更大的同时 block 也更大，为了降低 miss reate 一般第二级使用更高的相联度。

### Writing

如果是 hit 情况，可以有两种操作：

+ `write through`：把数据同时写入 cache 和 DDR
+ `write back`：只把数据写入 cache，替换时再把该 block 全部写入 DDR

write through 的优势：

+ 即使需要配合 write buffer，实现依然要比 write back 简单
+ 处理 miss 比较简单，因为不需要把 block 写入低层系统

write through 的缺点：

性能很差。假设一个系统中有 10% 的 store 指令，直接写入 DDR 需要花费 100 个 cycle，而没有 cache miss 时的 CPI 为 1,那么整个系统的 CPI 为 $1 + 100 * 10\% = 11$，性能大概降低了 10 倍。

write back 的优点：

+ 速度快，可以以 cache 的速度接收单个 word
+ 同一个 word 的多次操作可以合并成一次低层操作
+ 一整块写回低层时，可以充分利用高带宽传输

如果是 miss 情况，也可以有两种操作：

+ `write non-allocate`：直接把 block 写入 DDR
+ `write allocate`：把该 block 从 DDR 中读到 cache 中，分配空间保存，然后再替换成新数据

产生 write non-allocate 的主要原因是有些程序会写整个 block，比如操作系统可能会把 memory 中的某一个 page 全部填 0。在这种情况下，取回数据就没有必要了。

一般 write through 和 write non-allocate 搭配，write back 和 write allocate 搭配。如果 write back 中某个被修改过的 block 发生了 miss，那么就必须先把该 block 写回到 DDR 然后再把新数据写入该 block。简单地直接用新数据覆盖该 block 会丢失之前的修改数据，因为这些数据没有在低层中进行备份。所以要完成这个过程要么花费两个 cycle（第一个 cycle 检查是否 hit，第二个周期执行写操作），要么使用 write buffer（只花费一个 cycle，先把修改的数据写入 DDR，在下一个周期把新数据从 buffer 写入 cache）。

### Replace

常见的替换策略有 3 种：

+ 随机替换
+ `FIFO`
+ `LRU` (least recently used)

一般来说，在相联度不低（2-way 或 4-way）的时候 LRU 的实现代价非常高，因为要追踪记录使用信息的代价很高。即使是 4-way 也是用近似的方法来实现：4-way 分成两组，先用 1bit 记录那一组是 LRU，再在组内使用 1bit 记录哪个 block 是 LRU。


### Measuring Cache Performance

CPU time 可以分成两部分：CPU 的执行时间 + 由于 memory 系统导致的 stall 时间。一般来说，cache hit 的开销时间算在执行时间内，所以有下面的公式：

$CPU\ time = (CPU\ execution\ clock\ cycles + Memory\ stall\ clock\ cycles) * Clock\ cycle\ time$

我们假设 Memory stall 的时间开销主要来自于 cache miss，并且使用简化的 memory 模型。实际处理器中，读写产生的 stall 非常复杂，精确的性能预测通常需要对处理器和存储系统进行非常详细的仿真。所以我们可以定义下面的公式：

$Memory\ stall\ clock\ cycles = (Read\ stall\ cycles + Write\ stall\ cycles)$

其中读的 cycle 数可以用每个程序中读指令的数量、读操作的 miss penalty、读 miss rate 三个因素来定义：

$Read\ stall\ cycles = \frac{Reads}{Program} * Read\ miss\ rate * Read\ miss\ penalty$

写的情况要复杂一些，对于 write through 的 cache 而言，分为两部分：

$Write\ stall\ cycles = (\frac{Writes}{Program} * Write\ miss\ rate * Write\ miss\ penalty) + Write\ buffer\ stall$

因为 write buffer 不仅和写指令的频率有关，还和写操作的执行时机有关，不能用简单公式来计算。幸运的是，如果系统设置合理，wirte buffer 的阻塞时间可以变得很小，近似忽略。如果系统设计不合理，则设计人员应该用更深的 write buffer 或者是使用 write back 机制。

在大部分 write through 方案中，读写的 penalty 是一样的（都是从 DDR 中读回数据），假设 write buffer 部分可以忽略不计，则上面的公式可以简化为：

$Memory\ stall\ clock\ cycles = \frac{Memory\ access}{Program} * Miss\ rate * Miss\ penalty$

或者是：

$Memory\ stall\ clock\ cycles = \frac{Instrcutions}{Program} * \frac{Misses}{Instrcution} * Miss\ penalty$

有时候设计人员还会用另外一种方式来评估 cache 的设计：`AMAT`(Average memory aceess time)

$AMAT = Time\ for\ a\ hit + Miss\ rate * Miss\ penalty$

### The Three Cs

所有的 miss 可以被分为 3 类（`3C` 模型）：

|                     类型                           |                 含义                   |
| ------------------------------------------------- | ------------------------------------- |
| `Compulsory Miss` 强制失效 / `Cold Miss` 冷启动失效  | 对 Cache 中没有出现的数据第一次访问引起的失效 |
| `Capacity Miss` 容量失效                           | 因为容量有限，block 被替换后再次访问导致的失效 |
| `Conflict Miss` 冲突失效 / `Collision Miss` 碰撞失效 | 多个 block 竞争同一个 set 时导致的冲突      |

这几种失效相互之间是关联的，改变设计中的某一方面会直接影响到其中某几种失效。

|      设计修改    | 对 miss rate 的影响 |           可能对性能产生的负面影响                    |
| --------------- | -----------------| ------------------------------------------------- |
| block size ↑    | capacity miss ↓  | access latency ↑                                  |
| associativity ↑ | conflict miss ↓  | access latency ↑                                  |
| cache size ↑    | miss rate ↓      | miss penalty ↑, miss rate ↑ when very large block |

### Controller

+ 阻塞式 Cache：基于 FSM 的控制器，必须要等到 Cache 处理完前一个请求后处理器才能继续执行
+ 非阻塞 Cache：性能更高

### Coherence

+ `coherence`：定义了 read 操作返回什么数据
+ `consistency`：定义了 write 值什么时候才能被 read 操作返回

**问题产生的原因：**

共享数据在多个 cache 都有备份，多个备份之间会出现一致性问题。

**解决方法：**

多核系统一般通过一种硬件协议来维护 cache 之间的一致性，这个协议叫做 `cache coherence protocals` Cache 一致性协议。显然问题由共享数据引起，所以一致性协议的关键就在于追踪所有共享 block 的状态。

最流行的一致性协议叫做 `snooping` 窥探协议：每个 cache 不仅从 memory 中复制了 block 数据，同时还复制了 block 的状态，按照分布式的方式管理这些状态。每个 cache 都可以通过广播媒介（总线/网络）访问，而且每个 cache 控制器都会监听媒介，判断自己是否包含了当前总线上访问的数据。snooping 的实现比较简单，但是它的可扩展性比较低（因为不同所有 core 之间都要交互，复杂度和通信量成指数增长）。

有种保证一致性的方法：确保每个 core 在写数据时是互斥访问，因为这种协议在写一个数据时会设置其他 cache 中的备份无效，所以叫做 `write invalidate protocal`。

!!! tip
    一般来说 cache 之间是以 block 为单位进行数据交换和更新，所以 block 大小对一致性的影响很大，增加 block 会导致 cache 之间的带宽需求上升。

    较大的 block 还会导致 `false sharing` 的问题：2 个不相关的数据落到了同一个 block 中时，尽管两个 core 访问的是不同的数据，但是还是会发生数据交换。所以程序员和编译器要谨慎放置数据以避免发生假共享。

如果一个存储系统满足了下面 3 个条件，就可以认为该存储系统是一致的：

1. 处理器 P 对位置 X 的 write 后面紧跟着 P 对 X 的 read 操作，并且 write 和 read 之间没有其他处理器对 X 进行操作，那么 read 返回的一定是 write 的值
2. 在其他处理器对 X 完成 write 之后，P 对 X 进行 read 操作，这两个操作之间要有足够的时间间隔，并且没有其他处理器对 X 进行写操作，这是 P 的 read 返回的一定是 write 的数据
3. 对同一个地址的操作是串行执行的，即任何两个处理器对同一个地址的操作在所有处理器看来都是相同的顺序

!!! tip
    虽然上面的 3 个条件可以保证一致性，但是一个写数据什么时候对其他 core 可见也是一个重要问题。假设 core1 刚写了一个数据，core2 马上读相同地址，那么 core2 就不一定能读回最新值，因为可能写数据都还没离开 core1。这个写数据什么时候被其他 core 可以看到的问题叫做 `memory consistency model` 内存一致性模型。

    我们做了两个假设：1. 一个 write 操作只有等所有 core 都可以看到写效果才能算是完成；2. 处理器不能修改访问 memory 的顺序。这两个限制可以允许 core 对 read 操作进行重拍序，但是强制要求 write 操作必须是程序顺序。

!!! tip
    因为系统的 input 可能会绕过 cache 直接改变 memory 的内容；output 可能也会用到 write-back cache 中的最新数据，所以单核系统中，就像多核之间的 cache 一样，I/O 和 cache 之间也有一致性问题。虽然这两种一致性问题的原因很相似，但是它们的特点不一样，所以解决方法也不一样。具体来说，I/O 包含多个数据备份的情况很少出现，而且要尽可能地避免这种情况；而多核系统中不同 cache 备份同一个数据则很常见。

!!! tip
    除了 snooping 这种分布式的监听协议外，基于目录的 cache 一致性协议（`directory-based cache coherence protocal`）将物理存储器的共享块的状态集中存储在一个地点，叫做目录。虽然基于目录的协议要比监听方式的实现代价要高一些，但是这种方法可以减少 cache 之间的通信，所以可以扩展更多的处理器。

## Dependable Memory Hierarchy

如果 memory hierarchy 只是单纯的追求速度，无法保证可靠性，那么它将毫无吸引力。如第一章介绍，dependability 的重要方法就是冗余。所以我们首先讨论如何定义和测量可靠性，然后再看看如何通过冗余设计出可靠的存储器。

### Defining Failure

|                概念                 |                       含义                                 |
| ---------------------------------- | --------------------------------------------------------- |
| service accomplishment             | 交付的服务与预期相符                                          |
| service interruption               | 交付服务与预期不符                                             |
| failure                            | 从 accomplishment 到 interruption 的跳变                     |
| restoration                        | 从 interruption 到 accomplishment 的跳变                     |
| reliability                        | 持续提供 accomplishment 能力的度量，从开始到 failure 的时间间隔    |
| `MTTF`, mean time to failure       | reliability 的度量方法                                        |
| `AFR`, annual failure rate         | 给定 MTTF 时，设备在一年中出现 fail 的比例                        |
| `MTTR`, mean time to repair        | service interruption 的度量                                  |
| `MTBF`, mean time between failures | = MTTF + MTTR                                               |
| availability                       | 连续两次 interruption 之间 accomplishment 能力的度量，计算公式如下 |

$Availability = \frac{MTTF}{MTTF + MTTR}$

我们希望系统有很高的可用性 availability，一种简单表示方法是“可用性 9 的数量”，类似于黄金纯度一样，9 的数量越多表示可用性越好。增加 MTTF 或者是减少 MTTR 都可以提高可用性。

为了提高 MTTF，可以提高元件的质量或者是设计一个不受元件故障的系统。因为元件故障不一定和导致系统 failure，所以专门定义一个词 fault 来表示元件的故障。有 3 种方法提高 MTTF：

+ `fault avoidance`：合理构建系统避免发生 fault
+ `fault tolerance`：采用冗余措施，发生 fault 时系统仍然正常工作
+ `fault forecasting`：预测故障，在发生之前替换失效元件

为了减小 MTTR，可以采用检测、诊断、修复工具来处理 failure。

### Hamming SEC/DED

Richard Hamming 因为发明这个编码于 1968 年获得图灵奖。如果一种编码可以检测出是否发生 1 bit 错误，我们将其称为 1 bit 错误检测编码 error detection code。

Hamming 编码采用“奇偶校验”码来检测是否发生错误：统计码字中 1 的数量，然后根据统计结果设置校验位（奇数为 1, 偶数为 0）。所以 N+1 的总 bit 中 1 的个数永远是偶数个，如果从 memory 中读出的数据包含奇数个 1,那么就说明发生了错误。

显然，这个方案只能检测到奇数个错误的情况，而且同时发生 3 个错误的概率非常小，所以一般用来检查 1 bit 错误。

Hamming 为了实现纠正错误的目的，设计一种将数据映射到距离为 3 的码字的方式，为了表达敬意，我们称为 Hamming Error Correction Code, `ECC`。因为这种编码可以纠正 1bit 错误，检测 2bit 的错误，所以叫做 Single Error Correcting/Double Error Detecting (SEC/DED)，它广泛地应用于服务器的内存中。一般 8 byte 的数据正好需要 1byte 的额外开销，所以许多双列直插式存储模块 DIMM 的宽度是 72 bit。

!!! tip
    一般 SEC/DED 一般在存储器中属于典型情况，而在网络传输中，发生突然错误情况比较典型，这个时候采用的是循环冗余校验 Cyclic Redundancy Check, `CRC`。

## Virtual Memory

DDR 也可以充当 disk 的 “cache”，这种技术叫做虚拟存储器 `virtual memory`，就像 cache 一样，局部性原理也适用于 VM。两者的概念相同，但是因为历史原因，术语并不一样：

+ block <--> page
+ miss <--> page fault

因为每个程序都有自己的地址空间，所以 VM 要实现从程序地址空间到物理地址之间的转换，这个转换操作加强了一个程序的地址空间和其他 VM 之间的保护。

基于 page 的管理方式，`virtual address` 被分成了 `virtual page number` 和 `page offset` 两部分，其中 virtual page number 被转换成 `physical page number`，而 page offset 则保持不变，这个过程就是一次地址转换。virutal page 数量比 physical page 数量多得多是描述一个无限容量的虚拟存储器假象的基础。

page fault 的代价非常高，每次都要花费几百万个 cycle 才能完成处理（DDR 的速度大概是 disk 的 100,000 倍）。所以 VM 系统的很多设计决策都受 page fault 的影响：

+ page 必须要足够大，以缓解很长的访问时间。典型 page 的大小为 4～16 KB
+ 采用全相联的结构来降低 page fault
+ 通过软件处理，软件相比于 disk 的开销非常小，而且可以采用聪明的替换算法，至少能稍微降低一点 miss rate，算法的开销就值了
+ 不可能使用 write through，只能用 write-back





## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**陷阱：写代码或通过 compiler 生成代码时忽略 memory 系统的行为**

另外一个描述是：在写代码时，程序员可以忽略存储器存储结构。显然，这个结论是错误的。

**陷阱：模拟一个 cache 时，忘记说明 byte 地址和 block 大小**

要区分清楚 byte 地址、block 地址，word 地址。举例说明，假设有个容量为 36 Byte 的 cache，block 大小为 4 Byte，那么内存地址 36 的 block 地址是 9，所以映射到 block1 中（$9\ modulo\ 8 = 1$）；如果 36 是 word 地址，那么它会映射到 block4 中（$36\ modulo\ 8 = 4$）。

**陷阱：对于共享 cache，组相联度 < 核的数量/共享该 cache 的线程数**

如果 way 数比 core/线程数量少时，可能会有严重的性能缺陷。比如，32 个 core 竞争同一个 set 内的 16 个 way，性能很差。

**陷阱：用平均的 memory 访问时间来评估 out-of-order 处理器的存储器层次**

如果发生 miss 时处理器阻塞，那么就可以用平均时间来评估；如果是乱序执行的处理器，可能在 miss 时会继续执行其他指令，此时要准确评估存储器层次的唯一办法就是模拟乱序执行处理器和存储器层次。

**谬误：disk 实际的故障率和规格书中的一致**

实际评估的结果表明并不相同。

**谬误：操作系统是调度 disk 访问的最佳地方**

磁盘自己知道逻辑地址和映射的物理地址，所以磁盘比操作系统好。

**陷阱：为一个不支持虚拟化的 ISA 实现虚拟机监视器**

某些 ISA 要支持 VMM 必须新增一些其他指令。

## Summary

!!! important
    + 局部性原理让我们可以在保持 memory 低成本的同时获取高性能
    + cache 的基本设计包含了组织方式、更新算法、写回策略等
    + 3C 模型可以用来对 cache 性能的建模
    + 
    + 多级 cache 的优化更加方便，优化方式也更多
    + 借助软件，重新组织代码也可以提高局部性
    + 硬件预取也可以提高性能