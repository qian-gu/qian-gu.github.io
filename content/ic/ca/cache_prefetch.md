
## Big Picture

Problem: `Memory Wall` 剪刀差

Solution: `Memory Hierarchy`

Cache works on locality

Cache Works depends on 2 premises:

- 固定的 cache size 能满足各种应用需求
- 固定的 allocate & replace 策略能满足各种场景

各种优化方法的一种：Prefetch

## What is Prefetch

预测请求，提前取回数据，隐藏访问时间。

## How to Prefetch

### Metric

`Q1：(accurate)如何预测 prefetch 地址？`

错误预测的 prefetch 的影响：

- pollution（有用的数据被 evict 出去）
- execussive traffic and contention

影响 accurate 的因素比较多，比如

- 数据的访问模式：连续遍历 or 跳跃不连续
- 分支跳转
- cache 的级数：L1 有完整信息供预测，lower 只能看到 higher miss 信息，且会受到 replace 的干扰

评价指标：

- `coverage`
- `accuracy`

$$coverage = \frac{miss\ eliminated\ by\ prefetch}{total\ miss \without \prefetch}$$

$$accuracy = \frac{miss\ eliminated\ by\ prefetch}{total\ prefetch\ request}$$

这两个指标是相互矛盾的，很难兼得。简单的 prefetcher 付出 accuracy 代价以换取 coverage，高级 prefetcher 可以同时获得很好的 accuracy 和 coverage。

`Q2：(timely)何时发出 prefetch 请求？`

太早或太晚都有问题：

- 太早发出会造成污染，而且可能在真正使用前又被 evict 出去
- 太晚发出实现不了隐藏 memory latency 的问题

`Q3：(replace)prefetch 回来的数据存储在何处？`

- binding prefetch：以前的传统做法是直接写入 rigister file，
- non-binding prefetch：现代 CPU 的做法是写入 cache memory 或者 buffer 中，多核系统中 prefetch 还会涉及到一致性协议：prefetch 的数据可能并不是最新的，所以需要硬件负责解决让 prefetch 拿到最新数据。


## Instruction Cache

### Next Line Prefetch

最简单的 prefetch，广泛流行于现代处理器中。每次 core 从 prefetcher 中取出一条 block 时，prefetcher 自动从下级中预取一条 block。

可以方便地扩展为预取 N 个 block 的方式。

### Fetch Directed Instruction Prefetch

branch 指令会影响 Next Line Prefetch 的效果，解决方法就是把 branch predictor 信息引入到 I$ 中，让 I$ 可以根据预测提前知道跳转地址，即 branch-predictor directed prefetcher。

FDIP(fetch directed instruction prefetching) 是 branch-predictor directed prefetcher 中的一种，通过 FTQ（fetch target queue）解耦 branch predictor 和 cache。

// TODO

## Data Cache


## Ref

-[ ] Lecture#28. A Primer on Hardware Prefetching. Babak Falsafi. 2014
