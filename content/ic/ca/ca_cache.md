Title: Computer Architecture 笔记 —— Cache
Date: 2021-11-20 19:21
Category: IC
Tags: Computer Architecture, Cache
Slug: ca_cache
Author: Qian Gu
Series: Computer Architecture 笔记
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

!!! note

    冯诺依曼结构中有个永恒的主题：如何喂饱饥饿的 CPU，即如何提供稳定的指令流和数据流：

      + 指令流：分支预测
      + 数据流：cache

    经过多年发展，大概能达到半饱的程度：4 发射的结构，IPC = 2 就已经很不错了。

## 如何确定 Cache 规格？

cache 的规格可以总结为下面几个问题。

### 容量选择

`Q：Cache 的总容量应该设置为多少合适？`

A：没有标准答案，应该根据 `应用需求` 和 `微架构` 设计特点做出选择。

首先，cache 容量对 area 有最直接的影响，一般 cache 占用处理器 60% ~ 80% 的晶体管和 30% 以上的总面积，在某些处理器中甚至达到了 80% 的面积。所以确定 cache 容量时，首先要考虑的就是面积约束（即 area 和 money）。

其次，在满足面积约束的前提下，显然希望 cache 性能越高越好。根据 3C 模型，可以知道

+ 增加容量的优点：可以降低 capacity miss，从而降低整体的 miss rate
+ 增加容量的缺点：导致时序变差，导致 hit time 和 miss penality 变大

所以 cache 容量是一把双刃剑，并不是越大性能就越高。

目前的主流方案是多级 cache，不同级别的 cache 设计目标不同，所以容量规格也不同。因为其他级 cache 的出现，每一级 cache 的最佳规格、设计思路与单级 cache 方案完全不同：

+ L1 离 core 最近，其目标是跟上 core 的速度，所以会选择小容量、低相联度的结构，牺牲一些 hit rate，尽量减小 latency，换取高 throughput 和低 hit time。它的容量和 block size 相比于单级 cache 来说都要小很多，以减小 miss penality
+ L2 离 core 远一些，其目标则是低 miss rate，所以会选择大容量、高相联度的结构，牺牲一些频率、throughput 和 latency，换取更低的 miss rate。它的容量和 block size 都要比单级 cache 要大很多

### Block 大小选择

`Q：每个 block 的大小应该设置为多少？`

A：应该根据 `cache size` 做出选择。常见的组合：cache size = 4KB，block size = 32B; cache size > 64KB, block size = 64B。

较大的 block 可以更好地利用空间局部性，所以可以降低 miss rate，但是当 block 占 cache 容量的比例大到一定程度时，因为 block 的数量变得很少，此时会有大量的冲突，数据在被再次访问前就已经被替换出去了，而且太大的 block 内部数据的空间局部性也会降低，所以会导致 miss rate 反而上升。

随着 block 的增大，miss rate 的改善逐渐降低，但是在不改变 memory 系统的前提下，miss penalty 会随着 block 的增大而增大，所以当 miss penalty 超过了 miss rate 的收益，cache 的性能就会变低。

block 的大小还依赖于下一级存储器的 latency 和 throughput：

+ latency 和 throughput 越大，越应该使用大 block：因为每次 miss 可以取得更多的数据，但是 miss penality 增长很小（因为此时 miss penality 的主要成分是 latency，所以增大 block 额外传输数据的时间占比很小）
+ latency 和 throughput 越小，越应该使用小 block：因为这种情况下增大 block 并不会节省多少时间（比如小块的 penlaty*2 和一个两倍大小 block 的 penalty 相同，此时显然选小 block 更好，还能减小 conflict miss）

!!! tip
    较大 block 会导致较长的传输时间，虽然这部分时间很难优化，但是我们可以隐藏一些数据传输的时间，从而降低 miss penalty。实现这个效果的最简单的技术叫做 `early restart`：一旦接收到需要的 word 就立即就开始重启流水线，而不是等到整个 block 都返回后才重启。许多处理器都在 I-cache 上使用这个技术，效果甚佳，这是因为大部分指令访问都具有连续性。这个技术对于 D-cache 来说效果就没那么好了，因为数据访问的预测性没那么好，在传输结束前请求另外一个 block 中 word 的概率很高，而此时前一次请求的数据传输还没有结束，所以仍然会导致处理器 stall。

    还有一种更加复杂的机制叫做 `requested word first` 或者是 `critical word first`，这种方案会重新组织 memory 的结构，使得被请求的 word 优先返回，然后按照顺序返回后续数据，最后反卷到 block 的开头部分。这种方法比 early restart 稍微快一点，但是会受到相同的限制。

### 映射方式

`Q：应该如何组织 cache 的存储结构？`

A：根据 `cache size` 三选一，有个一般性的规律：

**2:1 cache rule of thumb**：容量为 N、直接映射的 miss rate = 容量为 N/2、相联度为 2-way 的 miss rate。

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

A： 实际需求和数据访问模式，还有其他约束条件共同决定

常见的组合方式：

|       | hit           |  miss              |
| ----- | ------------- | ------------------ |
| 方式一 | write back    | write allocate     |
| 方式二 | write through | write non-allocate |

hit 下两种不同处理方式的对比：

| 策略             | 优点                  | 缺点                  | 应用    |
| --------------- | --------------------- | -------------------- | ------ |
| `write through` | 硬件简单、flush 代价小   | 性能差                | L1     |
| `write back`    | hit 效率高、带宽利用率高  | 硬件复杂、flush 代价高  | L2 之后 |

下面分类讨论不同策略的含义和优缺点。

#### Write-Through(WT) + write allocate

**定义：** hit 时同时写入 cache memory 和 lower memory；miss 时 allocate，先读回后写入

**优点：** 兼顾了 fast retrieval 和 data lost risk，维护一致性简单

**缺点：** 只加速 read；write latency 差

**适用场景：** write once，retrieval frequently 的场景（偶尔个别 write latency 可忍受）

#### Write-Back(WB) + write allocate

**定义：** hit 时写入 cache memory，不写入 lower memory；miss 时 allocate，先读回后写入

**优点：** 同时加速 read/write；兼顾了 fast retrieval 和 write latency

**缺点：** 有 data lost risk，维护一致性困难

**适用场景：** read-write 混合场景

#### Write-Around(WA)

**定义：** write through + write non-allocate

**优点：** 避免 pollution（一次性数据不会 flood），无 data lost risk，维护一致性简单

**缺点：** 只加速 read；write latency 差

**适用场景：** 不频繁 retrieval write data；stream 应用

#### Write-Invalid(WI)

**定义：** 只写入 lower memory，write hit 时 invalid 命中行

**优点：** 确保 read 性能，无 data lost risk，维护一致性简单

**缺点：** 只加速 read；write latency 差

**适用场景：** read intensive 应用

#### Write-Only(WO)

**定义：** write 同 write back，read 不会存储到 cache memory

**优点：** 确保 write 性能

**缺点：** 只加速 write；有 data lost risk，维护一致性困难

**适用场景：** write intensive 应用

#### Pass-Through(PT)

**定义：** bypass 所有请求到 lower memory

**优点：** N/A

**缺点：** N/A

**适用场景：** debug

#### Summary

| policy   | speedup | retrieval | write latency  | consistency | data lost risk | speical          |
| -------- | ------- | --------- | -------------- | ----------- | -------------- | ---------------- |
| WT + WA  |   RO    |     +     |                |      +      |        +       |                  |
| WB + WA  |   RW    |     +     |         +      |             |                |  RW mix          |
| WA       |   RO    |     +(RO) |                |      +      |        +       |  Stream          |
| WI       |   RO    |     +(RO) |                |      +      |        +       |  Read intensive  |
| WO       |   WO    |     +(WO) |         +      |             |                |  Write intensive |
| PT       |         |           |                |             |                |  debug           |

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

### 实例：T-head C906

TODO

## Cache 的性能指标

`Q：如何评价一个 cache 的性能？`

### AMAT

Cache 最常用的性能指标是： `AMAT`(Average memory aceess time) ，显然 Cache 系统设计越合理，对 core 表现出来的性能越好，AMAT 就越小。根据定义可以知道 AMAT 的计算公式如下：

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

### 其他指标

AMAT 是 dcache 对外表现出来的综合性指标，如果想评估深入评估 dcache 微架构，那么应该用更多的细分指标来衡量。

最基本的指标是所有硬件都适用的 `throughput` 和 `latency`，描述 cache 响应命令的吞吐率和时延。

Cache 特有的最简单的指标是命中率 `hit ratio`，描述 cache 规格/微架构是否合理，合理的设计命中率都比较高，95% 以上。

另外如果想衡量 prefetch 的性能，主要有两个指标 `coverage` 和 `accuracy`，

$$coverage=\frac{miss\ eliminated\ by\ prefetch}{total\ miss\ without\ prefetch}$$

$$accuracy=\frac{miss\ eliminated\ by\ prefetch}{total\ prefetch}$$

coverage 描述了漏警性能，accuracy 描述了虚警性能，一般这两者很难兼得。同理，victim cache 也可以用类似的指标来衡量。

## Cache 的性能分析模型

**3C 模型**，也就是分析清楚 cache 的 miss 可以分为几类，每一类的产生原因是什么：

+ `compulsory miss`
+ `capacity miss`
+ `conflict miss`

一旦知道了 miss 产生的原因，也就可以针对性地采用各种方法来降低。虽然按照 3C 模型来分析时，优化某个因素的行为可能会导致另外一个因素的恶化，但是总体上它仍然是个很有用的工具，可以帮助我们在做设计时对 cache 性能进行建模（而且目前我们也没有更好的模型）。

!!! note

    当系统中有多个 cache 时，会额外再增加一个 C `coherency miss`，即为了保持一致性导致 cache 进行 flush，产生 miss。此时就是 4C 模型。

## Cache 性能优化方法

有了 cache 模型，就可以根据模型来优化性能，针对性能公式中的每个因子，优化思路可以分为下面几类：

| 优化思路            | 优化方法                                                          |
| ----------------- | ---------------------------------------------------------------- |
| 减小 hit time      | 小而简单的 L1 cache、路预测、Vitural Index/Physical Tag、serial 访问 |
| 减小 miss rate     | 增大容量、增大 block size、增加关联度、预取、软件优化                   |
| 减小 miss penalty  | victim cache、write buffer、多级 cache、关键字优先、写合并            |
| 提高 throughput    | pipeline、multibank(多端口)、非阻塞                                 |

!!! note

      miss penality 本质是就是一块数据的搬运耗时，可以借用“火车过山洞”模型：

      假设火车长度为 l，火车的时速为 v，火车头进入山洞的时刻为 t1，火车头出山洞的时间为 t2，火车尾出山洞的时刻为 t3，那么可以将火车过山洞的过程和数据搬运过程对应起来

      | 火车过山洞    | 搬运数据                                |
      | ----------- | -------------------------------------- |
      | t2-t1       | latency                                |
      | v           | throughput                             |
      | l           | data_amount                            |
      | t3-t2 = l/v | transfer_time = data_amount/throughput |

      火车过山洞的总时间 = t3 - t1 = (t3-t2) + (t2-t1)

      数据传输的总时间 = transfer_time + latency

      所以优化 miss penality 的方法主要就是下面这 3 种：

      + 减小 latency，这个取决于 hierarchy 中的下一级， cache 很难改变
      + 减小 data_amout，每次 miss 时少取一些数据
      + 增加 throughput，提高 cache 和 hierarchy 下一级之间的传输带宽

### Small and Simple L1 Cache

面临的问题：复杂 L1 的速度很难跟上 core 的时钟频率。

解决思路：思路1（减小 hit time），简化硬件设计、减小 size 和 associativity，从而减小 hit time。

付出的代价：miss rate 增加，需要下级 cache 作为补充。

### Way Prediction

面临的问题：对于并行访问 tag 和 data 的组相联 cache，必须经过下面 3 个步骤，

1. 读 tag memory
2. 比较 tag 内容
3. 根据读 tag 的结果选中 & 操作 data memory（mux + 写 data memory）

整个过程组合逻辑很长，hit time 较长，所以时钟频率无法做到很高。

解决思路：思路1（减小 hit time），采用 prediction bits，把组相联的 cache 当初直接相联来用，那么第二步的比较 tag 就只有 1 个 way 做比较，如果命中则相当于直接相联 cache 结构；否则在下个周期检查剩余 way 的 tag。因为这种方式第二步的组合逻辑变少，hit time 就变短了。

付出的代价：使得 pipeline 难以实现。

!!! note

      还有一种更进一步的做法叫做 `way selection`，即第一步也只读 1 个 way 的 tag，如果 miss 则需要重新读剩余 tag、作比较、操作 data memory。这种方法显然可以更省功耗，但是缺点就是一旦 miss，付出的代价很大，因为要完成重新执行一遍步骤123。

### Vitural Index/Physical Tag

面临的问题：全部使用虚拟地址时，必须经过一道查询 TLB 的过程，增加了整体的访问 latency。

解决思路：思路1（减小 hit time），采用 page offset 作为 cache tag，省去查询 TLB 的过程。

付出的代价：实现复杂度增加，功耗增加。

### Serial 访问

+ parrel：tag array 和 data array 并行访问，根据 tag array 的读结果产生 mux 信号，从 data array 的结果中选出目标 way
+ serial：先访问 tag array，根据结果产生 data array 的片选信号，直接读出目标 way

面临的问题：parrel 方式 critial path 较长，频率低

解决思路：思路1（减小 hit time），采用 serial 方式优化 critical path，同时因为省去了不必要的读 data array，所以功耗也更低。

### Cache Size

面临的问题：cache 容量不够，数据频繁被替换。

解决思路：思路2（降低 miss rate），降低 capacity miss

付出的代价：导致 hit time 变大，同时成本和功耗也会变高。

### Block Size

面临的问题：block 太小，对空间局部性的利用不充分。

解决思路：思路2（降低 miss rate），可以充分利用空间局部性，降低 compulsory miss。而且扩大 block size 会导致 tag 位宽变小，相应地可以减小一点功耗。

付出的代价：导致 miss penality 变大；而且过大的 blocksize 会适得其反。

### Set Associativity

面临的问题：关联度太小，一个 set 内频繁竞争。

解决思路：思路2（降低 miss rate），降低 conflict miss。

付出的代价：导致 hit time 变大，同时成本的功耗也会变高。

### Prefetch

面临的问题：如果每次发生 miss 时只取回当前 cache line，那么 cache 向 DDR 发送的 burst len 和 outstanding 都很小，效率很低。频繁发生 compulsory miss。

解决思路：思路2（降低 miss rate）。在取回当前 cache line 的同时以大 burst len 和 outstanding 高效地多取一些相邻数据，这样访问这些预取数据时就不会发生 miss。

+ 软件预取：有些 ISA 定义了预取指令，程序员可以通过软件进行预取
    + register prefetch：把数据预取到 register 中
    + cache prefetch：把数据预取到 cache 中
+ 硬件预取：cache 自主可以观测 unit-stride 和 stride 的规律，自动预取数据

| 方案                          | 含义                                                      |
| ---------------------------- | --------------------------------------------------------- |
| `OBL` (one block look-ahead) | 每次多预取一个 cache block                                  |
| `stream buffer`              | 多预取的数据存储在 stream buffer 中，miss 时再写入 cache line  |
| `SPT` (stride predict table) | 硬件检测 load 是否存在 stride 模式，取回数据直接写入 cache line |
| `stream cache`               | 结合 steam buffer 和 SPT，把预取回来的数据放在一个小 cache 中   |

预取数据不直接存到 cache 中的原因是避免“cache 污染”，但是 stream buffer 不灵活，所以改进方案是把预取数据放到一个 stream cache 中。

付出的代价：硬件复杂度增加，消耗更多资源。

!!! note

      prefetch 有效的前提是有剩余带宽未被利用。如果 prefetch 干扰了正常 miss 的读取，那么反而会降低性能。

### Software Optimize

纯软件，不需要改任何硬件。

同样也可以分为两类：改善 miss rate 或者是改善 miss penality。

+ loop interchange：交换嵌套 loop 的顺序
+ bloking：对数据分块处理

### Vicitm Cache

面临的问题：conflict miss 导致频繁的读写下一级 memory，导致整体性能降低。增加相联度代价太大，其他 set 没有这个需求。

解决思路：思路2（降低 miss rate），另外增加一个小容量（通常 4~16 个数据）、全相联的 cache，缓存被替换出来的数据。一般和 main cache 为 exclusive 关系。

和 Victim Cache 相对应的还有一种 Filter Cache，即在数据进入 main cache 前，先写入 Filter cache，等数据再次被使用时才写入 main cache，用来过滤偶然数据，提高整体利用率。

付出的代价：硬件复杂度增加。维护 victim cache 和 main cache 之间的一致性。

### Write Buffer(读优先)

面临的问题：如果发生 miss 时被替换的 block 为 dirty，则必须先将其写回下级 memory 后才能把目标 block 读进来，整个过程是串行的。当写下级的代价很高时，会导致 miss penality 很大。

解决思路：思路3（减小 miss penality），先将 dirty block 写入一本本地的 write buffer，为目标 block 尽早腾出空间。等下级 memory 空闲时，再将dirty block 写入其中。

+ 对于 write-back 的 cache，就是把 dirty cache line 整条都写入 write buffer
+ 对于 write-through 的 cahe，就是把 dirty data 写入 write buffer

L1 D-cache 通常采用 write-through 方案，配合 write buffer 提高性能。

付出的代价：硬件复杂度增加。cache 发生 miss 时首先要查询 write buffer（需要 CAM）

### Write Merging

面临的问题：如果 core 每次只写一个 word，那么普通 write buffer 的每个 entry 的大部分空间都会被浪费掉，write buffer 很容易达到 full。

解决思路：思路3（减小 miss penality），每次把数据写入 write buffer 时，检查是否可以合并到已有 entry 中。

付出的代价：硬件复杂度增加。

### Multiple Level

面临的问题：单级 cache 无法同时满足 fast hit 和 few miss 的需求。

解决思路：思路3（减小 miss penality），存储器层次结构 L1 + L2 + L3。一般 L1/L2 为每个 core 私有，L2/L3 共享。

+ L1： 小容量、低关联度、write-through
+ L2/L3: 大容量、高关联度、write-back

付出的代价：面积变大、解决一致性问题、硬件复杂度增加。

### Critical Word First

面临的问题：core 每次访问实际上只需要一个 word，但是 cache miss 时取要取回整个 block，耗时较长。

解决思路：思路3（减小 miss penality），采用“不耐心”的做法，优先向下级 memory 请求 miss 的 word，一旦读回来立即返回给 core。

付出的代价：硬件控制复杂化。

### Early Restart

面临的问题：同 Critical word first

解决思路：思路3（减小 miss penality），另外一种“不耐心”的做法，按照正常顺序请求数据，但是取回数据后立即把 word 发给 core。

付出的代价：硬件控制复杂化。

!!! note

      critical word first 和 early restart 只有在 block size 很大时收益才比较明显。

### Pipeline

面临的问题：读 D-cache 时 tag memory 和 data memory 可以并行同时读；但是对于写 D-cache，必须经过 way prediction 小节中提到的 3 个过程。整个过程串行操作时钟频率会很低，一般的做法是分为两个 cycle，第一拍读 tag 作比较，第二拍写 data memory。此时 throughput 为 0.5 instr/cycle。

解决思路：思路4（提高 throughput），将整个过程 pipeline 化，达到 1 instr/cycle 的 throughput。

付出的代价：硬件复杂度增加。后续指令要额外检查 pipeline 上的数据，增加 forward 通路。显然 pipeline 越深，mispredict 时 flush 的代价就越大，同时 load-to-use 的 latency 也越大。

!!! note

      pipeline 主要应用在 L1 上，因为它的访问带宽会限制 instruction throughput。目前大多数 core 的 L1 都采用 3~4 级 pipeline 的方式。

### Multibank

面临的问题：单 bank 的最高 throughput = 1 instr/cycle，无法满足超标量处理器的需求

解决思路：思路4（提高 throughput）。多 bank（多端口）有几种常见方案：

一般多端口的实现方案有以下几张：

| 实现方案                 | 含义                                             | 备注                  |
| ------------------------|------------------------------------------------ | ---------------------|
| `true multiple port`    | 真正的多端口，memory 有相应数量的读写端口             | 实现代价太大，不可接受   |
| `virtual multiple port` | memory 仍然是单端口，cache 频率是 core 的倍数        | 可扩展性差，现在不可接受 |
| `copy multiple port`    | memory 仍然是单端口，但是复制多份，保持 copy 之间的同步 | 浪费资源，同步控制复杂   |
| `multiple bank`         | memory 仍然是单端口，按照地址分 bank 交织             | 折中方案，普遍应用      |

分 bank 按照地址交织，也有一些缺点，比如要依靠编译器降低冲突概率；发生冲突时性能变差；内部 crossbar 对 PR 不友好，但是相比于其他几个方案，代价最小，应用最广泛。

付出的代价：增加硬件复杂度，消耗更多资源。

!!! note

      multibank 应用在 L1 时主要为了提供高 throughput，应用于 L2, L3 时更主要的目标是做功耗控制。

### Non-blocking

面临的问题：miss 会阻塞 core 的流水线，效率低。

解决思路：思路4（提高 throughput），cache 在处理当前 miss 的同时处理后续的请求。

付出的代价：增加硬件复杂度，消耗更多资源（MSHR）。

`in-cacche MSHR`：给 tag array 新增额外的 1bit transient 信号，如果某 entry 处于 transient mode，tag array 保存 base address，data array 保存所有的 MSHR 信息，具体形式既可以是 implicit 也可以是 explicit。

| MSHR 实现方式 | 优点                                 | 缺点                           |
| ------------ | ----------------------------------- | ------------------------------ |
| implicitly   | 消耗资源少（不需要记录 offset）         | 一个 word 只能 miss 一次、深度固定 |
| explicitly   | 同一个 word 可以 miss 多次、深度灵活可配 | 消耗资源多（需要额外记录offset）   |
| in-cache     | 不需要任何额外资源保存 MSHR             | 处理步骤增多，latency 变大        |

## 参考资料

Computer Organization and Design RISC-V Edition. David A. Patterson, John L. Hennessy

Computer Architecture: A Quantitative Approach. John L. Hennessy, David A. Patterson

Processor Microarchitecture: An Implementation Perspective. Antonio Gonzalez

《计算机体系结构》 胡伟武

《超标量处理器》 姚永斌
