Title: Mamba 笔记
Date: 2025-10-22 23:11
Category: Algorithm
Tags: Mamba, S6
Slug: mamba-note
Author: Qian Gu
Summary: Mamba 论文笔记。

[TOC]

Transformer 自从提出来就统治了 LLM 领域，现在几乎所有模型都是基于 Transformer 的。为了进一步提高 LLM，业界还在不断推出有望超过 Transformer 的新架构，Mamba 就是其中之一。

Mamba 的本质是一种 SSM (State Space Model)，所以按照 SSM -> S4 -> S6(Mamba v1) -> Mamba v2 的顺序记录。

## Transformer 的问题

- Transformer 把输入看作是一个 token sequence。
- 当输入一个新的 token 时，Transformer 可以计算之前已经输入的任意一个 token 和当前输入之间的 attention。
- self-attention 是 Transformer 效果之所以那么好的原因，它使得 model 可以以无损的方式看到所有历史输入 token，而且训练速度还很快。

    - 如何记住所有历史：attention 矩阵记录了任意两个 token 之间的相关性；
    - 如何加速训练：训练时可以看到所有输入 token，attention 矩阵是一次性建立好的，而且 attention 不存在顺序计算的依赖关系，所以任意两个 token 之间的 attention 都可以并行 (parallelization) 计算。

- Transformer 的问题存在于 inference 计算量大，速度慢。

    - 因为 Transformer 的 decoder 存在自回归性，所有历史输出都要当成输入重新送入 model。
    - 比如推理第 $i$ 个 output token 时，要重新计算第 0 到 $i-1$ 个 token 之间的 attention，其实在输出第 $i-1$ 个 token 时，已经计算过第 0 到第 $i-2$ 之间的 attention 了。
    - **所以算法复杂度随着序列长度平方性地增长：生成长度为 $L$ 的 sequence，大约需要 $L^2$ 次计算，当 $L$ 增大时，代价就很大了。这是 Transformer 架构的一个主要瓶颈。**

## RNN

- RNN 是一个 sequence-based Network，每个 time step 用两个输入：当前的 time step $t$ 和前一个 time step 的 hidden state $h_{t-1}$，来预测当前的输出。
- 在计算当前 output 时，RNN 只需要看前一步的 hidden state 和当前输入即可，不需要像 Transformer 一样每次都重新计算所有 token 间的 attention。
- $h_t = tanh(Wh_{t-1} + Ux_t)$

![rnn](/images/mamba-note/rnn.png)

- 也就是说，RNN 的算法复杂度随着序列长度线性增长。
- 理论上 RNN 有着无限长的 context length，每个 hidden state 都是所有历史 hidden state 聚合产生，而且通常都是 compressed view。
- RNN 的问题：

    - 第一个问题：如下面的例子所示，随着新的 input token，RNN 会逐渐忘掉历史输入，所以**算法效果不如 Transformer。**
    - ![rnn expample](/images/mamba-note/rnn-example.png)
    - 第二个问题：RNN 递归的本质导致无法展开并行计算，因为存在一个 tanh，所以也没办法像 SSM 展开成 convolution 的形式来加速。

## SSM

### State Space

- State Space 包含了描述系统所需要的最小变量，它通过描述系统所有可能的 state 来将问题转化为数学表示。
- 通常，state space model 就是用来描述系统的当前状态，可能的下一状态，以及如何达到下一状态。
- state 可能需要多个变量才能表示，这些变量组合在一起形成的向量称为 `state vector`。
- state vector 和 LLM 中的 `embedding` 很像，在 LLM 中 embedding 用来描述 input sequence 的 state。
- 对于 NN 来说，系统的 state 就是 Network 的 hidden state。

### State Space Model

- SSM 是描述系统的当前 state 并根据当前 input 预测下一个 state 的模型。
- SSM 包含两个方程，通过求解这两个方程，就能揭示系统统计意义上的规律，并依此对系统 state 进行预测。

    - 状态方程：$h(t) = Ah(t) + Bx(t)$，
    - 输出方程：$y(t) = Ch(t) + Dx(t)$

![ssm continuous](/images/mamba-note/ssm-continuous.png)

- 状态方程：描述了系统 state 的变化，包含两部分因素：

    - A 矩阵描述了 $h(t)$ 如何随着时间变化；
    - B 矩阵描述了当前输入 $x(t)$ 如何影响 state 的变化；

![state equation](/images/mamba-note/state-equation.png)

- 输出方程：描述了系统 state 如何影响输出，包含两部分因素：

    - C 矩阵描述了当前 state 如何影响 output；
    - D 矩阵描述了当前 input 如何直接影响 output；

![output equation](/images/mamba-note/output-equation.png)

- 将这两个方程组合在一起，图形化表示如下。其中 D 矩阵的作用相当于 1 个 skip connection，所以一般 SSM 会忽略这个连接。

![ssm illustrated](/images/mamba-note/ssm-illustrated.png)

!!!note
    注意：矩阵 A，B，C，D 都是学习到的参数。

### Discrete SSM

- SSM 的目标就是求解方程，得到状态表示 $h(t)$，这样我们就能把 input sequence 转化为 output sequence。
- 从前面的公式能看出来，SSM 的输入是连续信号 $x(t)$，输出是连续信号 $y(t)$。
- 基于连续信号求解 $h(t)$ 比较难，而且我们的 input sequence 实际上也是离散的，所以需要找到一种方法把模型离散化。
- 模型离散化的方法叫做 0 阶保持 ZOHT(Zero Orde Holding Technique)。
- ZOHT 保持多久是一个可以学习到的参数，叫做 step size $\Delta$，表示 input 的分辨率。
- SSM 离散化方法如下：

    - 首先，通过 ZOHT 将输入的离散 token 转化为一个 SSM 可以处理的 continuous input；
    - ![ZOHT](/images/mamba-note/zoht.gif)
    - 其次，SSM 根据输入的连续信号预测出 continuous ouptut；
    - 最后，根据 ZOHT 的步长对 continuous output 采样，就能得到 discreted output；
    - ![sample](/images/mamba-note/sample.gif)

- 数学上，ZOHT 可以用如下的公式表示： 

![zoht-equation](/images/mamba-note/zoht-equation.png)

- 将 $\bar A$ 和 $\bar B$ 代入方程，就能得到 discrete SSM，它的输入是离散序列 $x_k$，输出是离散序列 $y_k$。

![discrete-ssm](/images/mamba-note/discrete-ssm.png)

!!!note
    存储时仍然是连续形式的矩阵 A，只是在过程中将其离散化。如同 S6 中用 $\Delta$ 给 A 扩维一样。

- SSM 的维度分析。TODO

### The Recurrent and Convolution Representation

- 从离散 SSM 的公式可以看出来，SSM 是一个循环递归的过程，所以可以转化成 RNN 表示方式。

![recurrent](/images/mamba-note/recurrent.png)

- 如果将 SSM 的输出公式逐个展开，则输出公式可以改写成下面的 convolution 表示方式。

![convolution](/images/mamba-note/convolution.png)

!!!note
    - 训练时一次性可以看到所有 input，而且 $K$ 则可以并行提前算好，所以 convolution 表示直接用 input 并行计算 output，跳过了 $h_k$ 的计算和迭代，因此可以加速训练过程。
    - 每个 $y_k$ 用到的 $K$ 和 $x$ 向量长度都不相等，如何转成 Convolution 表示？可能的做法：$x$ 序列加前缀 padding 对齐到最大长度即可。

- RNN 表示采用递归的方式，计算量小，产生 output 的方式和 decoder 自回归天然匹配，所以很适合 inference。
- CNN 表示跳过了 $h$ 的迭代，而且支持并行计算，所以很适合 training。

| Representation | 优点         | 缺点                | 适用场景  |
| -------------- | ------------ | ------------------- | --------- |
| Recurrent      | 计算量小     | output 之间无法并行 | inference |
| Convolution    | 可以并行计算 | 有限的 context      | training  |

### SSM Architecture

像 convolution 组成 CNN 一样，SSM 可以组成 SSMNN，比较出名的 SSM architecture 有：

- Linear Attention
- H3
- RetNet
- RWKV

## S4 and S4D

- 可以说 SSM 中最重要的就是矩阵 A，它捕获前一状态 $h_{t-1}$ 并生成当前状态 $h(t)$。
- **如何创建 A 就决定了模型是只记住 a few previous tokens 还是 every tokens so far。**
- 那么如何创建一个 A 来压缩很长的 context 呢？答案是高阶多项式投影算子 `HiPPO` （High-order Polynomial Projection Operators）。

![hippo](/images/mamba-note/hippo.png)

- Hippo 试图将迄今为止看到的所有 input 压缩成一个 coefficient vector，它用矩阵 A 构建了一个 state representation，该表示可以很好地捕获最近的 token 而衰减较旧的 token。

![hippo-matrix](/images/mamba-note/hippo-matrix.png)

- 用 Hippo 构建的 A 要比随机初始化的 A 效果要好得多。
- Hippo 背后的思想是它产生了一个可以记住历史的 hidden state，在数学上，它是通过记录 Legender 多项式的系数来实现这个效果的。
- 应用 Hippo 的 SSM 称为 Structured State Space for Sequence Model (S4)，S4 主要包含 3 部分：

![s4](/images/mamba-note/s4.png)

- 之所以叫 Structured，是因为矩阵 A 有特定格式，如 S4 用的对角线矩阵。
- 在实践中，为了提高可行性，S4D 的 A 为对角线矩阵，它继承了 S4 的优点，但同时更简单。

![s4d](/images/mamba-note/s4d.png)

!!!note
    **SSM 和 RNN 解决无限长 context 的区别**

    如果用有限长的 hidden state 去表征无限长的 context 信息，必然会有装不下的问题。面对这个矛盾，RNN 和 SSM 有不同的解决方法：

    - RNN 采用的是溢出和遗忘的方式，也就是随着新 input 会忘掉旧 input，所以算法效果不好。
    - SSM 采用 HiPPO 把无限长的 context 压缩到有限长的 hidden state 中，虽然对较旧 token 重建比较差，但是总好过直接忘掉。

- S4 算法和维度说明
    
    - $A \in \mathbb{R}^{N \times N}$，但是因为 A 是对角矩阵，所以只需要 N 个数据就能表示；
    - $B \in \mathbb{R}^{N \times D}$，每个 embedding 维度的 SSM 相互独立，而每个 SSM 的 B 维度本身为 $B \in \mathbb{R}^{N \times 1}$；
    - $C \in \mathbb{R}^{N \times D}$ 同理。

![s4-algo](/images/mamba-note/s4-algo.png)

## S6 (Mamba v1)

![mamba v1](/images/mamba-note/mamba-v1.gif)

!!!Important
    S4 最大的问题在于无论输入什么序列，每个 timestep 的 token 使用相同的 A，B，C，即不是 context-aware，所以在某些任务（如需要对 token 区别对待）上算法效果很差。

- S6 主要有以下两点改进：

    - Selective Scan Algorithm：可以过滤（不）相关信息
    - Hardware-aware Algorithm：通过 parallel scan，kernel fusion 和 recomputation 实现高效存储（中间）结果

- **S6 = s4 + Selective Scan Algorithm**

![s6](/images/mamba-note/s6.png)

- 虽然 s6 解决了选择性问题，但是代价是无法利用 convolution 表示并行计算来加速训练了。

    - s4 能用 Convolution 表示的原因是 A，B，C 都是静态的，$K$ 可以提前算好存起来；
    - s6 中 A，B，C 是动态的，所以无法提前把 $K$ 提前算好，也就无法用 convolution 表示来加速训练（因为 convolution 的定义就是用一个固定 Kernel 在 input 上滑动，即要求 Kernel 固定）；

### Selective Scan Algorithm

- **Selective Scan Algorithm = dynamic B/C + parallel scan**
- 从模型压缩的角度而言，RNN 和 Transformer 位于两个极端，要么压缩所有 history 要么完全不压缩，S6 尝试集两者所长：state 和 RNN 一样比较小，同时还拥有和 Transformer 类似的算法效果。 
- 实现这个目标的方法就是：有选择性地将 input 压缩到 state 中。
- 为了实现选择性，必须让参数依赖 input。
- 参数依赖 input 意味着不同 input 有不同的参数，即参数的维度会膨胀。
- 下面分析维度变化：

    - input $x_k$ 的维度为 (B, L, D)；
    - output $y_k$ 的维度为 (B, L, D)；
    - ![x y dimension](/images/mamba-note/xy-dimension.png)
    - 在 S4 中 A，B，C 是静态的，所有 token 共享，所以他们的维度都是 (D, N)；
    - ![s4-abc-dimension](/images/mamba-note/s4-abc-dimension.png)
    - 在 S6 中 B，C 是动态的，每个 token 都有自己的参数版本，所以他们的维度扩展了 L 和 B 两个维度；
    - ![s6-abc-dimension](/images/mamba-note/s6-abc-dimension.png)

![s6-algo](/images/mamba-note/s6-algo.png)

| 符号 | 含义                                      |
| ---- | ----------------------------------------- |
| B    | Batch size                                |
| L    | Sequence Length                           |
| D    | size of input vector, embedding dimension |
| N    | hidden state size，$N \ll L$              |

!!!note
    S4 和 S6 的矩阵 A 维度相同，这是因为我们希望 state 本身保持静态，由 B 和 C 引入动态性。

!!!note
    运算时 A，B，C 的维度都必须是 (B, L, D, N)，但是实际上存储时它们都不包含 D 维度，在离散化过程中通过和 $\Delta$ 做运算扩展维度实现。

!!!note
    总结论文中的公式，步骤，分析维度变化。

#### Parallel Scan

- 因为 s6 中参数依赖于 input，所以不能再用 convolution 形式来加速训练了，因为 convolution kernel 在 sequence 上滑动时必须保持固定不变。
- 所以必须重新找一种方法实现并行化，粗看 SSM 方程为迭代方式，每一步都依赖于前一步的迭代结果，但是实际上仍然有并行化的机会：这种方法就是 `Belloc Scan`。
- 因为 SSM 方程可以改写成 scan 的形式，所以可以用这种加速方法：

    - 定义一个新算子 $ (A_t, B_tx_t) \oplus (A_{t+1}, B_{t+1}x_{t+1}) = (A_tA_{t+1}, A_{t+1}B_tx_t + B_{t+1}x_{t+1})$。
    - 上面的公式可以简化为 $(a, b) \oplus (c, d) = (ac, cb+d)$，只需要保留第二项结果，即 $(a, b) \oplus (c, d) = (cb+d)$。

![parallel scan](/images/mamba-note/parallel-scan.png)

!!!note
    **Scan**

    scan 操作的定义：

!!!note
    **Belloc Scan** 是一种 Scan 并行加速算法。

### Hardware-aware Algorithm

- **Hardware-aware Algorithm =  kernel fusion + recompute**
- GPU 的 IO 瓶颈：SRAM 带宽大但是容量小，所有中间结果必须写回 DRAM，但是 DRAM 带宽有限，限制了整体性能。
- S6 和 self-attention 类似，尝试通过限制 DRAM 和 SRAM 之间的读写次数来规避 GPU IO 瓶颈。

#### kernel fusion

即只有最终结果写回 DRAM，中间结果只写入 SRAM。kernel fusion 包含：

- continuous A，B，C 存储在 DRAM，读入到 SRAM 后，用 $\Delta$ 离散化，进行维度扩展；
- Selective Scan Algorithm, state $h$ 保存在 SRAM 中；
- 用 C 乘以 h 也发生在 SRAM 中；

![kernel fusion](/images/mamba-note/kernel-fusion.gif)

### Calculation and Memory Size

TODO：总结论文中的分析

#### recomputation

- 在 forward pass 中计算出的 immediate state 在 backward pass 中也会用到，但是作者并没有把它们存在 DRAM 中，而是在 backward pass 中重新计算了一遍。 
- 乍看这样做的效率很低，但是重复计算的代价相比于从 DRAM 读回数据要小得多。

### Mamba Block

- 和 attention block 类似，Mamba block 也能组成 Mamba 网络。
- Mamba block 的组成：

    - 首先，和 Transformer 类似，projection 到更高的维度，做 embedding；
    - 其次，用 Convolution + SiLU 提取 feature，避免 token 独立计算；
    - 然后，用核心模块 SSM 处理；
    - 然后，残差连接；
    - 最后，用 projection 降维；

![mamba block](/images/mamba-note/mamba-v1-block.png)

## Mamba v2

虽然 S4 开发了 parallel scan 和 kernel fusion 等方法，但是因为它无法在 tensor core 上跑，不能利用大量的计算资源，所以作者后续又提出了 mamba v2 来改进这一点。

## Ref

[Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/pdf/2312.00752)

[A Visual Guide to Mamba and State Space Models](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mamba-and-state)

