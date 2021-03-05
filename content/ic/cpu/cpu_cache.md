Title: CPU 关键技术 —— Cache
Date: 2021-01-13 19:21
Category: IC
Tags: CPU, Cache
Slug: cpu_cache
Author: Qian Gu
Series: CPU 关键技术
Status: draft
Summary: 总结 Cache 细节

#### block size

较大的 block 的可以更好地利用空间局部性，所以可以降低 miss rate，但是当 block 和 cache 容量的比例大到一定程度时，因为 block 的数量变得很少，此时会有大量的冲突，数据在被再次访问前就已经被替换出去了，而且太大的 block 内部数据的空间局部性也会降低，所以导致 miss rate 反而上升。

随着 block 的增大，miss rate 的改善逐渐降低，但是在不改变 memory 系统的前提下，miss penalty 会随着 block 的增大而增大，所以当 miss penalty 超过了 miss rate 的收益，cache 的性能就会变低。

!!! tip
    较大 block 会导致较长的传输时间，虽然这部分时间很难优化，但是我们可以隐藏一些数据传输的时间，从而降低 miss penalty。实现这个效果的最简单的技术叫做 `early restart`：一旦接受到需要的 word 就立即就开始执行，而不是等到整个 block 都返回后才开始执行。许多处理器都在 I-cache 上使用这个技术，而且效果甚佳，这是因为大部分指令访问都具有连续性。这个技术对于 D-cache 来说效果就没那么好了，因为数据访问的预测性没那么好，在传输结束前请求另外一个 block 中 word 的概率很高，而此时前一次请求的数据传输还没有结束，所以仍然会导致处理器 stall。

    还有一种更加复杂的机制叫做 `requested word first` 或者是 `critical word first`，这种方案会重新组织 memory 的结构，使得被请求的 word 优先返回，然后按照顺序返回后续数据，最后反卷到 block 的开头部分。这种方法比 early restart 稍微ie快一点，但是会受到相同的限制。