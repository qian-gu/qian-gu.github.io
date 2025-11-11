Title: Swin Transformer 笔记
Date: 2025-11-08 00:26
Category: Algorithm
Tags: Transformer, Swin
Slug: swin-transformer-note
Author: Qian Gu
Summary: Swin Transformer 论文笔记。

[TOC]

## swin 架构特点

swin 是 ICCV 21 最佳论文，可以理解为多尺度的 ViT。

swin = **s**hift **win**dow

- 采用 Unet 结构，随着层数增加，分辨率递减，C 维度递增；而 ViT 分辨率保持不变；
- attention 局限在 window 内，计算复杂度线性增长；而ViT 二次方增长；

![swin-arch](/images/swin-transformer-note/swin-arch.png)

## swin 的好处

- attention 只局限在 non-overlapping local window 中
- 也支持 cross-window connection
- 可以对各种 scale 建模
- 计算量和 image size 成线性比例

## ViT 的问题

- low resolution 训练的 model 不适合作为 dense vision task 或 high resolution task 的 backbone
- 计算复杂度随着 resolution 二次方增长

!!!note
    - dense：每个 pixel 都需要进行预测 or 分类：常见任务有 语义分割、实例分割、全景分割、深度估计、光流估计
    - sparse：只需要关注图像中的特定点 or 区域，常见任务有：图像分类、目标检测、关键点检测（人脸检测的边框，关键点检测标出关节点的坐标）

## Patch Partition

- path size = 4x4
- 每个 patch 展平后的数据量为 $4*4*3 = 48$ 
- input (H, W, 3) -> (H/4, W/4, 48)

## Linear embedding

(H/4, W/4, 48) -> (H/4, W/4, C)，将 48 映射到 C dimension，完成 embedding 功能。

代码实现时可以用 1 个 conv2d 实现 patch partition + linear embedding：

```python
nn.Conv2d(in_chans=3, out_channels=embed_dim, kernel_size = patch_size, stride=patch_size)
```

## Patch Merging

完成降采样功能

- unshuffle 后宽高分辨率都减半， C 维度会变为 4C
- 用 linear projection 把 4C 重新映射（每个 stage 不同，stage2 映射为 2C，stage3 映射为 4C，stage4 映射为 8C）

## Swin Transformer Block

!!!note
    Q：为什么 swin 可以压低算力？

    A：

    - ViT 的 patch size 为固定值，所以 patch number（即 token 数量）和分辨率 $hw$ 为二次方关系
    - swin 的 window size 为固定值，窗内计算复杂度和窗口大小为二次方关系，但是因为窗口大小固定，所以计算复杂度为常数，而窗口数量和窗口大小成正比，所以整体计算复杂度为线性关系。

**STB = shift-window + MSA**

忽略 scale，sotfmax 计算，只考虑大头的 linear 和 QKV 矩阵乘

- 输入 token X 的维度为 (n, $d_{model}$)
- $W^Q$ 的维度为 ($d_{model}$, $d_{model}$)，$Q$ 的计算量为 $n*d_{model}^2$
- $W^K$ 的维度为 ($d_{model}$, $d_{model}$)，$K$ 的计算量为 $n*d_{model}^2$
- $W^V$ 的维度为 ($d_{model}$, $d_{model}$)，$V$ 的计算量为 $n*d_{model}^2$
- $QK^T$ 的维度为 ($n$, $n$)，计算量为 $n^2*d_{model}$
- $QK^TV$ 的维度为 ($n$, $d_{model}$)，计算量为 $n^2*d_{model}^2$
- $W^O$ 的维度为 ($d_{model}$, $d_{model}$)，计算量为 $n*d_{model}^2$

所以普通 MSA 的计算量为 $4*n*d_{model}^2 + 2*n^2*d_{model}$

论文中 $n = h*w$，$d_{model} = C$，所以总计算量为

$4*hw*C^2 + 2*(hw)^2*C$

计算复杂度和 hw 成平方关系 -> 不适合 large $hw$ 的情况。

### W-MSA

- 将 $h*w$ 个 patch 切分为 $\frac{h}{M} * \frac{w}{M}$ 个 window
- 每个 window 的分辨率为 M*M
- 在每个 window 内使用 MSA，则每个 window 内的计算量为 $4*M^2*C^2 + 2*M^4*C$

总计算量为

$\frac{h}{M}*\frac{w}{M}(4*M^2*C^2 + 2*M^4*C) = 4*hw*C^2 + 2*M^2*hwC$

计算复杂度和 hw 成线性关系 -> 适合 large $hw$ 的情况。

$\hat z^l = W-MSA(LN(z^{l-1})) + z^{l-1}$

$z^l = MLP(LN(\hat z^l)) + \hat z^l$

### SW-MSA

$\hat z^{l+1} = SW-MSA(LN(z^l)) + z^l$

$z^{l+1} = MLP(LN(\hat z^{l+1})) + \hat z^{l+1}$

## shift window

- 提供 cross-window connection
- window 内的所有 query 共享 key（之前的 slide window 不同的 query 有自己的 key）-> memory 友好

shift-window 之后会引入两个问题：

- window 数量变多
- window 分辨率不再固定

naive 的解法是将 shift 后的 window 分辨率 pad 到标准大小后计算，论文提到一种更聪明的方法：

- 先把原图 roll（h 和 w 方向都循环移动），形成 4 个区域
- 每个区域为 1 个独立窗口，需要 mask 掉其他区域后进行 attention 计算
- 计算完后再 unroll 回去

![shit-window](/images/swin-transformer-note/shift-window.png)

## Reference

[Swin Transformer: Hierarchical Vision Transformer using Shifted Windows](https://arxiv.org/pdf/2103.14030)
