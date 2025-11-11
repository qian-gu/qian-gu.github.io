Title: ViT 笔记
Date: 2025-11-06 23:41
Category: Algorithm
Tags: Transformer, ViT
Slug: vit-note
Author: Qian Gu
Summary: ViT 论文笔记。

[TOC]

## Introduction

![vit-arch](/images/vit-note/vit-arch.png)

1. 2022 年 CV 影响力最大的工作。
2. 挑战了 2012 年 AlexNet 以来 CNN 在 CV 中的绝对统治地位。
3. 结论：在足够多的数据上训练，可以不需要 CNN，直接使用标准 transformer 就能解决好视觉问题。
4. 打破了 CV 和 NLP 的壁垒，开启了 CV 新时代。

!!!note
    transformer 在 NLP 很成功，CV 也在尝试引入 transformer。在 CV 领域，self-attention 要么和 CNN 一起使用，要么替换一部分 conv 层，但是整体上还是保持整体结构不变。ViT 的贡献是证明了这种对于 CNN 的依赖是完全不必要的，纯 transformer 也可以表现得很好。特别是在大规模数据集上预训练后迁移到中小数据集（ImageNet、CIFAR-100、VATB）上，能获得和 SOTA CNN 相当的效果。

!!!note
    从模型上来说，ViT 最大的创新是 tokenization，其他部分保持 transformer block 不变。

## Backgroud

将 Transformer 引入 CV 面临的问题：

- 与文本不同，图像包含更多的信息，并且以像素的像是呈现；
- 如果按照每个像素 1 个 token 的方式处理，计算量爆炸，当前硬件很难支持；
- Transformer 缺少 CNN 的归纳偏差（先验信息，提前做好的假设），比如平移不变形和局部感受野，所以 transformer 需要更大数据集；
    - 平移不变性 translation equivariance：先平移还是先 conv，结果不变，因为无论物理平移到哪里，只要是相同的输入搭配相同的 kernel，输出结果就相同。
    - 局部性 locality：图片相邻区域有相邻的特征，所以用 kernel 在图片上滑动。
- CNN 通过逐层叠加扩大感受野，Transformer 的感受野是全图，但计算量比 CNN 更大；

!!!note
    因为 self-attention 的算法复杂度为 $O(n^2)$，所以在 NLP 中 sequence length 不会太长，一般几百到上千，如 256，512。但是引入到 CV 领域，pixel 数量远超过这个量级，会引起计算量爆炸的问题。这也是为什么 CNN 一直占主导地位的原因。

业界一些方法如下：

- local MSA：只在 1 个邻域内做 attention
- sparse transformer：scalable approximation to global self-attention
- 动态 size 中应用 attention

这些方法虽然效果不错，但是用到了特殊 attention pattern ，硬件上很难高效支持。

## Model Architecture

**主要思想：尽量不修改 transformer block，保持通用性，以利用现成的高效实现的代码。在 embedding 阶段压缩计算量。**

$Z_0 = [X_{class};, X_p^1E; X_p^2E; \dots; X_p^NE] + E_{pos}, \qquad E \in \mathbb{R}^{(N+1) \times D}$

$Z_l^{\prime} = MSA(LN(Z_{l-1})) + Z_{l-1}, \qquad \qquad \qquad \qquad l = 1 \dots L$

$Z_l = MLP(LN(Z_l^{\prime})) + Z_l^{\prime}, \qquad \qquad \qquad \qquad \qquad l = 1 \dots L$

$y = LN(Z_L^0)$

| 符号 | 含义                            |
| ---- | ------------------------------- |
| C    | channel                         |
| H    | height                          |
| W    | width                           |
| P    | patch size                      |
| N    | $N = HW / P^2$，sequence length |
| D    | hidden dimension                |
| L    | transformer block length        |

论文给出的集中模型参数配置：

| model     | L    | Hidden size D | MLP size | Heads | Params |
| --------- | ---- | ------------- | -------- | ----- | ------ |
| ViT-Base  | 12   |  768          | 3072     | 12    |  86M   |
| ViT-Large | 24   | 1024          | 4096     | 16    | 307M   |
| ViT-Huge  | 32   | 1280          | 5120     | 16    | 632M   |

- 模型参数可以搭配不同的 patch size，如 16x16 或 32x32；（论文题目就是 1 个 word = 1 个 16x16 patch）
- MLP size 表示 encoder 中 MLP block 第一个 linear 的输出维数，论文设置固定的 4 倍的 D；

流程：

1. 将图片转为 patches 序列
2. 将 patches project 成 embedding
3. 添加 position embedding
4. 添加 class token
5. 把 sequence 送入 transformer encoder 处理
6. 用 MLP head 分类

![vit-aiminate](/images/vit-note/vit.gif)

### patch embedding

降维方法：切分 patch。每个 patch 内的所有 pixel 维度转换后当作 1 个 token，token 数量可以降低 P^2 倍。

目标：将 (C, H, W) 的图像转化为 1 个维度为 (N, D) 的 token 序列。

实现方法：

1. 将图像分为 (P, P) 大小的、没有 overlap 的 N 个 patch；
2. 每个 patch 展平后经过 linear projection（FC 层，公式 1 中的 $E$）转化为 1 个 token；

patch embedding 的作用就是把 CV 问题转化为 NLP 问题，模型后续部分就和 CV 没什么关系了。

### position embedding

图像和文本类似，也有先后顺序，不能随意打乱。所以也要给每个 token 添加位置信息。ViT 用的是 1D learnable 1D position embedding，因为消融实验表明 2D 效果相比于 1D 没有明显提升。

!!!note
    position embedding 是加上去的，而不是 concat，所以不影响维度。

position embedding 的作用就是添加位置信息。

### class token

参考 BERT 的 [class] token，ViT 也给 sequence 添加了 1 个 learnable token，这个 token 经过 encoder 处理后为 $Z_L^0$，然后通过 MLP head 得到 $y$（公式4），表示图像类别。

可以看出来 class token 也有 position embedding，而且永远都是 0。

所以 encoder 的输入、输出维度均为 (N+1, D)。

### transformer encoder

- encoder 由 $L$ 个 transformer block 组成；
- 每个 transformer block 和标准 block 结构完全一样；
- 每个 transformer block = MSA block + MLP block，每个 block 输入前添加 LN，输出添加 residual connection；
- MLP block = Linear + GELU + Linear；

encoder 输出为公式 3。

!!!note
    - ViT 中使用的 transformer block 是 encoder 中的结构，没有用 decoder 中的 block 结构。

### MLP head

transformer encoder 输入输出维度不变，都是 (N+1, D)。对于分类任务来说只需要 [class]token 的结果，所以从 (N+1, D) 中挑出 (1, D) 送入 MLP head 即可。

MLP head 只包含 1 个 Linear。

MLP head 的作用就是做最终的分类。

## Hybrid Architecture

encoder 的 input sequence 可以是 CNN 提取出来的特征，即公式 1 的输入 X 不再是原始图像，而是 fature map。

一种特殊情况下 feature map 的 patch 为 1x1，即 CNN 将 spatial dimension 转换到了 OFM 维度，此时 $E$ 可以被省略。

## Ref

[AN IMAGE IS WORTH 16X16 WORDS: TRANSFORMERS FOR IMAGE RECOGNITION AT SCALE](https://arxiv.org/pdf/2010.11929)
