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

### Controller

+ 阻塞式 Cache：基于 FSM 的控制器，必须要等到 Cache 处理完前一个请求后处理器才能继续执行
+ 非阻塞 Cache：性能更高

### Coherence

### RAID

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
    + 