Title: CPU 笔记 —— Cache
Date: 2021-01-13 19:21
Category: IC
Tags: CPU, Cache
Slug: cpu_cache
Author: Qian Gu
Series: CPU 笔记
Status: draft
Summary: 总结 Cache 的设计细节

!!! note
    Cache 是一个非常广泛、有深度的话题，无数的大牛在此道沉浸数十载，创造出了各种各样的优化技巧和实现技术，一篇短短的博文显然无法做到面面俱到，作为学习笔记，只争取说明白最基础的 Cache 知识。

## 为什么需要 Cache？

### 面临的问题

众所周知，处理器的集成度一直在按照摩尔定律逐渐提高，在 20 世纪的后 20 年内，core 的时钟频率也基本按照每 18 个月翻一番的速度增长，但是 DRAM 的时钟频率增长速度却每年只有 7%，所以两者的速度之间就形成了一个 `剪刀差`：随着时间的推移，这个差距会越来越大。即使在现在这个多核时代，core 的频率不再怎么提升了，这个差距仍然在扩大，因为核数量增加对内存的带宽需求也会相应增加。

这个问题是码农和硅农之间的矛盾：码农希望存储器的容量尽可能大的同时速度足够快，而实际上硅农受限于半导体技术，速度快的 SRAM 容量无法做得很大，成本太高；而容量大的 DRAM 速度无法做得很快。举个例子，假设一个 core 的频率为 2 GHz 的 4-way 超标量处理器，它直接访问 latency = 100ns 的 DRAM，那么访问一次 DRAM 的时间内处理器可以执行多少条指令呢？

$$4*100*10^{-9}*2*10^9 = 800$$

这显然是不可接受的。

### 解决方案

按照传统的冯·诺依曼结构，指令和数据都在内存中，CPU 只负责处理，内存和 CPU 关系就像是仓库和工厂，工厂加工的原料和生产出来的产品都要放在仓库中。但是摩尔定律和“剪刀差”导致工厂和仓库之间的运输能力成为整个系统的瓶颈，最简单直观的解决办法就是在工厂里面做一个小仓库，对应在处理器中就是存储器层次 `Memory Hierarchy`。

| 存储层次       | 大小      | 访问 latency   | 数据调度 | 调度单位 | 实现技术      |
| ------------- | -------- | ------------- | ------- | ------ | ------------ |
| register file | < 1 KB   | 0.25 ~ 0.5 ns | 编译器   | Word   | CMOS 寄存器堆  |
| cache         | < 16 MB  | 0.5 ~ 25 ns   | 硬件     | block  | CMOS SRAM    |
| memory        | < 16 GB  | 80 ~ 250 ns   | 操作系统  | page   | CMOS DRAM    |
| I/O device    | > 100 GB | 5ms           | 人工     | file   | disk         |

cache 能缓解问题的原因在于程序具有**局部性原理**：

+ `时间局部性`：一个数据被访问之后，短期内很大概率会被再次访问
+ `空间局部性`：一个数据被访问之后，短期内很大概率会访问相邻数据

Cache 的出现可以说是一种无奈的妥协。如果 DRAM 的速度足够快，或者 SRAM 的容量可以做到足够大，我们的烦恼不复存在了，cache 也没有存在的必要了。但是在未来一段时间内，当今硅工艺不发生革命性变化的前提下，这是很难实现的一件事情，所以 cache 是有必要的。

## 如何确定 Cache 规格？

cache 的规格可以总结为下面几个问题。

### 容量选择

`Q：Cache 的总容量应该设置为多少合适？`

A：没有标准答案，应该根据 `应用需求` 和 `微架构` 设计特点做出选择。

一般 cache 占用处理器 60% ~ 80% 的晶体管和 30% 以上的总面积，在某些处理器中甚至达到了 80% 的面积。显然增加容量可以降低 miss rate，但是增加容量是一把双刃剑，它会导致时序变差，增加 latency。目前的主流方案是多级 cache，不同级别的 cache 设计目标不同，所以容量规格也不同。

L1 离 core 最近，其目标是跟上 core 的速度，所以会选择小容量、低相联度牺牲一些 hit rate，尽量减小 latency，提高 throughput。除了性能考虑，另外一个原因是 L1 的成本最高，所以容量也无法做得很大。

L2 离 core 远一些，其目标则是低 miss rate，所以会选择大容量、高相联度，付出的代价则是频率、throughput 和 latency 稍微差一些。

### Block 大小选择

`Q：每个 block 的大小应该设置为多少？`

A：应该根据 `cache size` 做出选择。

较大的 block 的可以更好地利用空间局部性，所以可以降低 miss rate，但是当 block 占 cache 容量的比例大到一定程度时，因为 block 的数量变得很少，此时会有大量的冲突，数据在被再次访问前就已经被替换出去了，而且太大的 block 内部数据的空间局部性也会降低，所以会导致 miss rate 反而上升。

随着 block 的增大，miss rate 的改善逐渐降低，但是在不改变 memory 系统的前提下，miss penalty 会随着 block 的增大而增大，所以当 miss penalty 超过了 miss rate 的收益，cache 的性能就会变低。

!!! tip
    较大 block 会导致较长的传输时间，虽然这部分时间很难优化，但是我们可以隐藏一些数据传输的时间，从而降低 miss penalty。实现这个效果的最简单的技术叫做 `early restart`：一旦接收到需要的 word 就立即就开始重启流水线，而不是等到整个 block 都返回后才重启。许多处理器都在 I-cache 上使用这个技术，效果甚佳，这是因为大部分指令访问都具有连续性。这个技术对于 D-cache 来说效果就没那么好了，因为数据访问的预测性没那么好，在传输结束前请求另外一个 block 中 word 的概率很高，而此时前一次请求的数据传输还没有结束，所以仍然会导致处理器 stall。

    还有一种更加复杂的机制叫做 `requested word first` 或者是 `critical word first`，这种方案会重新组织 memory 的结构，使得被请求的 word 优先返回，然后按照顺序返回后续数据，最后反卷到 block 的开头部分。这种方法比 early restart 稍微快一点，但是会受到相同的限制。

### 映射方式

`Q：应该如何组织 cache 的存储结构？`

A：根据 `cache size` 三选一

cache 的工作方式和停车场非常类似，如果停车场（cache）中有可用的空车位（cache line），那么汽车（data）就可以停在该车位中；如果停车场已经没有空车位，那么就要先把某个车开出来（数据替换出去），然后才能把新来的车停进去。而在停车场找车时，如果停车场很大，而且所有的车都随机停，那么找车（查找数据）的速度就会很慢。

| 类型     | 类比         | 优点                    | 缺点                 |
| ------- | ----------- | ----------------------- | ------------------- |
| 直接映射 | 固定车位      | 硬件简单、成本低，查找速度快 | 不灵活、易冲突、利用率低 |
| 全相联   | 随机车位      | 冲突小、利用率高          | 硬件复杂，查找速度慢    |
| 组相联   | 区域内随机车位 | 折中                    | 折中                 |

组相联是另外两种方式的折中：组之间是直接映射、组内是全相联。直接映射可以看作是组数 set = full 的特例，全相联可以看作是 set = 1 的特例。

### 替换策略

`Q：如果一个 set 中没有可用的 way 时，应该把哪个 way 替换出去？`

A：根据 `associative` 和实现复杂度三选一

+ `LRU` (Least Recently Used)
+ `random`
+ `FIFO`

根据理论分析，应该把最不活跃的数据替换出去，因为它再次被用的概率最小，即 LRU 策略。但是 LRU 的实现代价比较高，一般超过 8 way 就不可接受了，所以常用方法是 pseudo-LRU，用较小的代价实现近似 LRU 的效果。另外两种则很直观。根据《量化分析》的统计结果，在小容量时 LRU 的效果最好，当容量变大后，LRU 和 random 的效果差不多，FIFO 的效果则取决于具体程序。

### 写回策略

`Q：cache 应该如何处理写回数据？`

A： 根据写回代价二选一

|       | hit           |  miss              |
| ----- | ------------- | ------------------ |
| 方式一 | write back    | write allocate     |
| 方式二 | write through | write non-allocate |

hit 下两种不同处理方式的对比：

| 策略             | 优点                  | 缺点                    | 应用    |
| --------------- | --------------------- | ---------------------- | ------ |
| `write through` | flush 时直接丢弃，代价小 | 硬件复杂、性能不高        | L1     |
| `write back`    | 写 cache 省事          | flush 时写回 DDR，代价高 | L2 之后 |

### 实例：Arm M 系列 cache 规格

[ARM M 系列配置](https://en.wikipedia.org/wiki/ARM_Cortex-M)

总结可以得到下面规律：

+ Cortex-M 系列定位为 MCU，主要应用于嵌入式领域
+ 中低端 core 内部没有集成任何类型的 cache（M0, M0+, M3, M4）
  + 在系统层次，可以为 core 配置系统级别的 cache/TCM
+ 高端 core 内部可能同时集成了 cache 和 TCM（M7）
  + STM32F7 中集成的 M7 是一款双发射、6-stage 的超标量嵌入式处理器，core 内部同时配置了 cache 和 TCM
  + I-cache 容量为 0~64KB，cache block 大小为 32B，2-way
  + D-cache 容量为 0~64KB，cache block 大小为 32B，4-way
  
### 实例：Arm A 系列 cache 规格

[ARM A 系列配置](https://en.wikipedia.org/wiki/List_of_ARM_microarchitectures#Designed_by_ARM)

总结可以得到下面规律：

+ Cortex-A 系列定位移动端和用户级应用
+ A 系列要支持 OS，所以全系配置了不同大小的 cache，舍弃了 TCM
+ 低性能 core 只集成了 L1 cache，高性能 core 还集成了 L2 cache，甚至是 L3

## Cache 的性能模型

性能用 `AMAT`(Average memory aceess time) 指标来分析（具体分析过程略），显然 Cache 系统设计越合理，对 core 表现出来的性能越好，AMAT 就越小。根据定义可以知道 AMAT 的计算公式如下：

$AMAT = Time\ for\ a\ hit + Miss\ rate * Miss\ penalty$

对于多级 Cache 系统，AMAT 公式如下（以两级 Cache 为例）：

$T_{avg}=H_1*C_1 + (1-H_1)*(H_2*(C_1 + C_2) + (1-H_2)*(C_1 + C_2 + M)$

每个符号的含义：

+ $H_1$ 表示 L1 cache 的命中率
+ $H_2$ 表示 L2 cache 的命中率
+ $C_1$ 表示 L1 cache 命中访问时间
+ $C_2$ 表示 L2 cache 命中访问时间（即 L1 miss 但是 L2 hit 的 penalty）
+ $M$ 表示 DDR 的访问时间（即 L2 miss 的 penalty）

也可以换一种算法：

$T_{avg}= C_1 + (1-H_1)*C_2 + (1-H_1)*(1-H_2)*M$

可以证明两种方式是等价的。

## Cache 性能优化

有了 cache 模型，就可以根据模型来优化性能，由性能模型可以看到，优化思路主要有两条路：

+ 降低 miss rate，减少 miss 出现的概率
+ 如果 miss 无法避免，减小 miss 时的 penalty

《量化分析》中总结了 10 种优化方法，简单记录一下具体优化方法。

### Prefetch

如果每次发生 miss 时只取回当前 cache line，那么 cache 向 DDR 发送的 burst len 和 outstanding 都很小，效率很低。所以预取的思路是：在取回当前 cache line 的同时以大 burst len 和 outstanding 高效地多取一些相邻数据，这样访问这些预取数据时就不会发生 miss。

预取可以通过软件也可以通过硬件实现，有些 ISA 定义了预取指令，程序员可以通过软件进行预取。硬件预取则是 cache 自主检测和预取。常见的硬件预取方式一共有 4 种：

| 方案                          | 含义                                                      |
| ---------------------------- | --------------------------------------------------------- |
| `OBL` (one block look-ahead) | 每次多预取一个 cache block                                  |
| `stream buffer`              | 多预取的数据存储在 stream buffer 中，miss 时再写入 cache line  |
| `SPT` (stride predict table) | 硬件检测 load 是否存在 stride 模式，取回数据直接写入 cache line |
| `stream cache`               | 结合 steam buffer 和 SPT，把预取回来的数据放在一个小 cache 中   |

预取数据不直接存到 cache 中的原因是避免“cache 污染”，但是 stream buffer 不灵活，所以改进方案是把预取数据放到一个 stream cache 中。

### Multiport

如果不是出于性能需求，一种低成本方法是多个访问端口先进行仲裁，然后再顺序访问 cache，这种多端口实际上是“虚假的多端口”。另外一种情况则是超标量或者是多核系统可能会有多个 load/store 指令同时执行，所以对 cache 的接口带宽提出了需求：高性能的场景要能支持同时读写多个数据。

一般多端口的实现方案有以下几张：

| 实现方案                 | 含义                                             | 备注                  |
| ------------------------|------------------------------------------------ | ---------------------|
| `true multiple port`    | 真正的多端口，memory 有相应数量的读写端口             | 实现代价太大，不可接受   |
| `virtual multiple port` | memory 仍然是单端口，cache 频率是 core 的倍数        | 可扩展性差，现在不可接受 |
| `copy multiple port`    | memory 仍然是单端口，但是复制多份，保持 copy 之间的同步 | 浪费资源，同步控制复杂   |
| `multiple bank`         | memory 仍然是单端口，按照地址分 bank 交织             | 折中方案，普遍应用      |

分 bank 按照地址交织，也有一些缺点，比如要依靠编译器降低冲突概率；发生冲突时性能变差；内部 crossbar 对 PR 不友好，但是相比于其他几个方案，是代价自小的，也是应用最广泛的。

### Non-blocking

### Way-predict

### Write Buffer

## 参考资料

Computer Organization and Design RISC-V Edition. David A. Patterson, John L. Hennessy

Computer Architecture: A Quantitative Approach. John L. Hennessy, David A. Patterson

Processor Microarchitecture: An Implementation Perspective. Antonio Gonzalez

《计算机体系结构》 胡伟武

《超标量处理器》 姚永斌
