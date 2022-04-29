Title: 乘法器小结
Date: 2022-03-26 11:24
Category: IC
Tags: multiplier, Baugh-Wooley, Booth-Wallace
Slug: multiplier_summary
Author: Qian Gu
Status: draft
Summary: 总结几种乘法器实现方式

## Array Multiplier

阵列乘法器原理非常简单，就和人类手算乘法的过程一样，把每个位置的乘积算出来，求和即可。如下图所示，

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0 -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b 
-----------------------------------------------------------------------
pp0                          p  p  p  p  p  p  p  p  p
pp1                    p  p  p  p  p  p  p  p  p
pp2              p  p  p  p  p  p  p  p  p
pp3        p  p  p  p  p  p  p  p  p
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

$$p_{ij}=b_{i}\cdot a_{j}$$

不同 pp 之间求和用 full adder 和 half adder 即可。这种乘法器实现消耗的资源非常多，且因为组合逻辑链路很长，所以时序也不好，实际中几乎不会真正使用到。

## Shift-Accumulate Mulitplier

《P&H》中的乘法器，速度慢但是消耗的资源少。主要原理就是每个 cycle 计算一个 pp 并将其累积到 psum，经过多个 cycle 逐渐累加得到最终结果。这种算法过程和除法过程类似，所以可以合并到一起，一个模块同时实现乘法和除法。

## Booth-Wallace Multiplier

Booth-Wallace 乘法器是目前应用最广泛的乘法器。

### Modified Booth Encode I

booth radix-4 算法的原理：假设两个有符号数 A 和 B 相乘，

$$B=-b_{n-1}2^{n-1}+\sum_{i=0}^{n-2}b_i2^i = \sum_{i=0}^{n/2-1}(-2b_{2i+1}+b_{2i}+b_{2i-1})2^{2i}$$

所以给 B 补上 $b_{-1}=0$ 后，按照每 3bit 一组的方式进行编码，得到下表：

| $b_{2i+1}$ | $b_{2i}$ | $b_{2i-1}$ | code | Operation | $Neg_i$ | $One_i$ | $Two_i$ | $p_{ij}$                |
| :--------: | :------: | :--------: | :--: | :-------: | :-----: | :-----: | :-----: | :---------------------: |
|    0       |    0     |    0       |  +0  |     +0    |    0    |    0    |    0    |    $0$                  |
|    0       |    0     |    1       |  +1  |     +A    |    0    |    1    |    0    |    $a_j$                |
|    0       |    1     |    0       |  +1  |     +A    |    0    |    1    |    0    |    $a_j$                |
|    0       |    1     |    1       |  +2  |     +2A   |    0    |    0    |    1    |    $a_{j-1}$            |
|    1       |    0     |    0       |  -2  |     -2A   |    1    |    0    |    1    |    $\overline{a_{j-1}}$ |
|    1       |    0     |    1       |  -1  |     -A    |    1    |    1    |    0    |    $\overline{a_j}$     |
|    1       |    1     |    0       |  -1  |     -A    |    1    |    1    |    0    |    $\overline{a_j}$     |
|    1       |    1     |    1       |  +0  |     +0    |    0    |    0    |    0    |    $0$                  |

先考虑最简单的情况：假设每个 pp 都是正数且 code 没有负数，那么就不需要在每个 pp 的高位补符号位 0，且计算每个 pp 时没有取反过程。计算过程如下图所示：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0 -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                          p  p  p  p  p  p  p  p  p
pp1                    p  p  p  p  p  p  p  p  p
pp2              p  p  p  p  p  p  p  p  p
pp3        p  p  p  p  p  p  p  p  p
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

说明：因为包含 x2 的操作，所以每个 partial product 的位宽为 N+1。

### Sign Extension

!!! note
    这部分主要参考了 [Appendix A. Sign Extension in Booth Multipliers][appendix]，仿照原文的无符号数乘法可以得到有符号数的 MBE 算法。

[appendix]:http://i.stanford.edu/pub/cstr/reports/csl/tr/94/617/CSL-TR-94-617.appendix.pdf

以 N = 8 bit 乘法为例。首先，假设每个 pp 都为负数且 code 为负数，

+ 因为 pp 为负数，所以每个 pp 高位扩展符号位 1
+ 因为 code 为负数，所以计算每个 pp 时，除了取反操作外，还需要给 pp 的 LSB 加 1

所以乘法过程如下所示：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0 -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0     1  1  1  1  1  1  1  p  p  p  p  p  p  p  p  p
pp1     1  1  1  1  1  p  p  p  p  p  p  p  p  p     1
pp2     1  1  1  p  p  p  p  p  p  p  p  p     1
pp3     1  p  p  p  p  p  p  p  p  p     1
pp4                                1
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

这些前缀会额外消耗资源和功耗，所以需要做一些处理将其尽量消除，具体过程如下。

首先，对上图的前缀 1 进行预求和，可以等效出下面的过程：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                    1  1  p  p  p  p  p  p  p  p  p
pp1              1  0  p  p  p  p  p  p  p  p  p     1
pp2        1  0  p  p  p  p  p  p  p  p  p     1
pp3     0  p  p  p  p  p  p  p  p  p     1
pp4                                1
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

当某个 pp 为正数时需要撤销前缀，假设 pp 的符号位为 s，

+ 当 s = 0 时，pp 为正数，给前缀的 LSB 加 1
+ 当 s = 1 时，pp 为负数，不需要额外处理

当 code 为正数时，需要撤销 LSB 的 1。这两种情况可以用下面的过程表示：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
                         ~s
pp0                    1  1  p  p  p  p  p  p  p  p  p
pp1              1 ~s  p  p  p  p  p  p  p  p  p     n
pp2        1 ~s  p  p  p  p  p  p  p  p  p     n
pp3    ~s  p  p  p  p  p  p  p  p  p     n
pp4                                n
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

其中

+ s 表示 pp 的符号
+ n 表示 code 的符号，当 code 为负数时 n = 1，否则 n = 0

这时，我们已经消除了大部分的前缀 1，但是引入了一个额外的 pp，即 pp0 上方的 ~s。根据真值表可将 s 合并到 pp0 中：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                ~s  s  s  p  p  p  p  p  p  p  p  p
pp1              1  s  p  p  p  p  p  p  p  p  p     n
pp2        1 ~s  p  p  p  p  p  p  p  p  p     n
pp3    ~s  p  p  p  p  p  p  p  p  p     n
pp4                                n
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

我们将 pp 的数量从 N/2+2 降低到了 N/2+1 个。仔细观察，上面这个图示中每个 pp 的第 9 bit 实际上就是 s，所以将其可以改写成：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                ~s  s  s  s  p  p  p  p  p  p  p  p
pp1              1  s  s  p  p  p  p  p  p  p  p     n
pp2        1 ~s  s  p  p  p  p  p  p  p  p     n
pp3    ~s  s  p  p  p  p  p  p  p  p     n
pp4                                n
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

对于 pp2 和 pp3 的 MSB 部分组成的小三角，根据真值表可以把 pp2 的前缀 1 合并到 pp 3 里面，同理 pp1 的可以前缀可以合并到 pp2 里面；合并后剩下的左上角的 4 个 s 也可以改写成下面的形式。

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                   ~s  s  s  p  p  p  p  p  p  p  p
pp1                 1 ~s  p  p  p  p  p  p  p  p     n
pp2           1 ~s  p  p  p  p  p  p  p  p     n
pp3     1 ~s  p  p  p  p  p  p  p  p     n
pp4                                n
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

可以列出真值表证明这个计算过程和上面是等价的，但是每个 pp 的长度都缩减了 1bit。

至此，我们就得到了 conventional Modified Booth Encoding(MBE I) 算法。

**encoder:**

$$neg_i=b_{2i+1}\cdot(\overline{b_{2i}}+\overline{b_{2i-1}})$$
$$one_i=b_{2i} \oplus b_{2i-1}$$
$$two_i=\overline{b_{2i+1}}\cdot b_{2i}\cdot b_{2i-1}+b_{2i+1}\cdot\overline{b_{2i}}\cdot\overline{b_{2i-1}}$$

**decoder:**

$$p_{ij}=one_i\cdot(neg_i\oplus a_j) + two_i\cdot(neg_i\oplus a_{j-1})=\overline{(\overline{one_i} + neg_i \odot a_j) \cdot (\overline{two_i} + neg_i \odot a_{j-1})}$$

**综合结果：**

TSMC 7nm + synopsys DC, 1GHz + 30% over constrain

| implementation | area (mm^2) |
| -------------- | ----------- |
| MBCODEC        |   11.9153   |
| Wallace-tree   |   13.0234   |
| CLA            |    7.8660   |
| Total          | **32.9962** |

后续的改进集中在以下几个方面：

+ 让 pp 更规则化，更规则的 pp 会让 area 更小，frequency 更高
    + 方法1：每个 n 和上方的 p 合并，产生更规则的 pp
    + 方法2：优化掉最后一个 pp，将 pp 的数量缩减到 N/2
+ 提高 pp 求和的速度，主要就是 wallace tree 和 CLA

### Modified Booth Encode II

参考文献：[High-speed Booth encoded parallel multiplier design][paper1]

[paper1]:https://ieeexplore.ieee.org/abstract/document/863039

MBE II 的优化方向是提出一种新的 encode 方案，使得 encoder 和 decoder 都得到简化，从而降低功耗，提高速度。

| $b_{2i+1}$ | $b_{2i}$ | $b_{2i-1}$ | code | Operation | $neg_i$ | $one_i$ | $two_i$ | $z_i$ | $p_{ij}$                |
| :--------: | :------: | :--------: | :--: | :-------: | :-----: | :-----: | :-----: | :---: | :---------------------: |
|    0       |    0     |    0       |  +0  |     +0    |    0    |    1    |    0    |  1    |    $0$                  |
|    0       |    0     |    1       |  +1  |     +A    |    0    |    0    |    1    |  1    |    $a_j$                |
|    0       |    1     |    0       |  +1  |     +A    |    0    |    0    |    1    |  0    |    $a_j$                |
|    0       |    1     |    1       |  +2  |     +2A   |    0    |    1    |    0    |  0    |    $a_{j-1}$            |
|    1       |    0     |    0       |  -2  |     -2A   |    1    |    1    |    0    |  0    |    $\overline{a_{j-1}}$ |
|    1       |    0     |    1       |  -1  |     -A    |    1    |    0    |    1    |  0    |    $\overline{a_j}$     |
|    1       |    1     |    0       |  -1  |     -A    |    1    |    0    |    1    |  1    |    $\overline{a_j}$     |
|    1       |    1     |    1       |  -0  |     -0    |    1    |    1    |    0    |  1    |    $0$                  |

同理，根据 truth table 可以推导出 encoder 和 decoder 的表达式：

**encoder:**

$$neg_i=b_{2i+1}$$
$$one_i=b_{2i} \odot b_{2i-1}$$
$$two_i=b_{2i+1}\oplus b_{2i}$$
$$z_i=b_{2i+1} \odot b_{2i}$$
$$neg\_fix_i=b_{2i+1} \cdot \overline{b_{2i} \cdot b_{2i-1}}$$

**decoder:**

$$p_{ij}=\overline{one_i} \cdot (neg_i\oplus a_j) + \overline{two_i + z_i} \cdot (neg_i\oplus a_{j-1})=\overline{(one_i + neg_i \odot a_{j}) \cdot (two_i + z_i + neg_i \odot a_{j-1})}$$

**综合结果：**

TSMC 7nm + synopsys DC, 1GHz + 30% over constrain

| implementation | area (mm^2) |
| -------------- | ----------- |
| MBCODEC        |   14.8154   |
| Wallace-tree   |   12.9276   |
| CLA            |    7.5650   |
| Total          | **35.3081** |

!!! warning

    从表达式就可以看出来，MBE II 的 encoder 要比 MBE I 的简单很多。需要注意的是：因为这种编码方案里面，neg/one/two 的值和其本身定义并不一致，所以需要额外的 z 来纠正。同理，pp 阵列示意图中的 n 必须使用修正过的 neg_fix。

    从实际综合结果来看，虽然 MBE II 的门数更少，但是面积要比 MBE I 的大一些，推测原因是 MBE II 用到了较多的 XOR，而 XOR 的面积是 AND 和 OR 的 1.5~3 倍之间，所以虽然门数减少了，但总面积反而增大了。

### Modified Booth Encode III

参考文献：[High-speed Booth encoded parallel multiplier design][paper1]

在 MBE I 的基础上继续优化，因为 $a_{-1}$ 和 $b_{-1}$ 是我们在低位补的 1'b0，这是预先确定的，所以可以直接列出 $pp_0$ 和 $neg_i$ 的 truth table，然后把每个 $pp_0$ 和 $neg_i$ 合并，得到求和结果 $t_{i0}$ 和进位 $c_i$。因为 $c_i$ 相比于 $neg_i$ 左移了 1bit，使得 pp 更规则，节省了相应的求和操作，所以可以减小一些面积。

$$t_{i0} = p_{i0} \oplus neg_i$$

$$c_{i} = p_{i0} \cdot neg_i$$

将其扩展到 MBE I 的 truth table 上，可以得到：

| $b_{2i+1}$ | $b_{2i}$ | $b_{2i-1}$ | code | Operation | $Neg_i$ | $One_i$ | $Two_i$ | $p_{ij}$                | $t_{i0}$ | $c_i$            |
| :--------: | :------: | :--------: | :--: | :-------: | :-----: | :-----: | :-----: | :---------------------: | :------: | :--------------: |
|    0       |    0     |    0       |  +0  |     +0    |    0    |    0    |    0    |    $0$                  |    0     |   0              |
|    0       |    0     |    1       |  +1  |     +A    |    0    |    1    |    0    |    $a_j$                |   $a_0$  |   0              |
|    0       |    1     |    0       |  +1  |     +A    |    0    |    1    |    0    |    $a_j$                |   $a_0$  |   0              |
|    0       |    1     |    1       |  +2  |     +2A   |    0    |    0    |    1    |    $a_{j-1}$            |     0    |   0              |
|    1       |    0     |    0       |  -2  |     -2A   |    1    |    0    |    1    |    $\overline{a_{j-1}}$ |     0    |   1              |
|    1       |    0     |    1       |  -1  |     -A    |    1    |    1    |    0    |    $\overline{a_j}$     |   $a_0$  | $\overline{a_0}$ |
|    1       |    1     |    0       |  -1  |     -A    |    1    |    1    |    0    |    $\overline{a_j}$     |   $a_0$  | $\overline{a_0}$ |
|    1       |    1     |    1       |  +0  |     +0    |    0    |    0    |    0    |    $0$                  |     0    |   0              |

可以推出 $t_{i0}$ 和 $c_i$ 的表达式：

$$t_{i0}=a_0\cdot(b_{2i-1} \oplus b_{2i})$$
$$c_i=b_{2i+1}\cdot(\overline{b_{2i}+b_{2i-1}}+\overline{a_0 + b_{2i}}+\overline{a_0 + b_{2i} \odot b_{2i-1}})$$

或者

$$c_i=neg_i \odot (\overline{a_0} + \overline{one_i})$$

!!! warning

    参考论文中的 $c_i$ 计算公式是错误的。

相应的 pp 阵列如下图所示：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                   ~s  s  s  p  p  p  p  p  p  p  t
pp1                 1 ~s  p  p  p  p  p  p  p  d  c
pp2           1 ~s  p  p  p  p  p  p  p  t  c
pp3     1 ~s  p  p  p  p  p  p  p  t  c
pp4                             c
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

**综合结果：**

TSMC 7nm + synopsys DC, 1GHz + 30% over constrain

| implementation | area (mm^2) |
| -------------- | ----------- |
| MBCODEC        |   10.5883   |
| Wallace-tree   |   11.1902   |
| CLA            |    6.8810   |
| Total          | **28.6596** |

从综合结果上可以看到这种方法相比于 MBE I 面积有了一定优化，但是因为没有消除掉最后一个 pp，所以面积还是较大。

### Modified Booth Encode IV

参考文献：[Modified Booth Multipliers With a Regular Partial Product Array][paper2]

[paper2]:https://ieeexplore.ieee.org/document/4912330

将最后一个 pp 优化掉后，wallace tree 就可以少一级，资源、面积和功耗都会相应有优化。具体做法也很简单，就是将上面阵列中的 $p_{i1}$ 和 $c_i$ 再做一次加法，得到 $t_{i1}$ 和进位 $d_i$，然后将 $d_i$ 和 $pp_0$ 的高位 $\overline{s_0}s_0s_0$ 合并出新的 $\alpha_2\alpha_1\alpha_0$。

由二进制加法的定义可以知道：

$$t_{i1} = p_{i1} \oplus c_i$$

$$d_{i} = p_{i1} \cdot c_i$$

将其扩展到 MBE III 的 truth table 上，就可以得到：

| $b_{2i+1}$ | $b_{2i}$ | $b_{2i-1}$ | code | Operation | $Neg_i$ | $One_i$ | $Two_i$ | $p_{ij}$                | $t_{i0}$ | $c_i$            | $t_{i1}$                             | $d_{i}$              |
| :--------: | :------: | :--------: | :--: | :-------: | :-----: | :-----: | :-----: | :---------------------: | :------: | :--------------: | :----------------------------------: | :------------------: |
|    0       |    0     |    0       |  +0  |     +0    |    0    |    0    |    0    |    $0$                  |    0     |   0              |    0                                 |    0                 |
|    0       |    0     |    1       |  +1  |     +A    |    0    |    1    |    0    |    $a_j$                |   $a_0$  |   0              |   $a_1$                              |    0                 |
|    0       |    1     |    0       |  +1  |     +A    |    0    |    1    |    0    |    $a_j$                |   $a_0$  |   0              |   $a_1$                              |    0                 |
|    0       |    1     |    1       |  +2  |     +2A   |    0    |    0    |    1    |    $a_{j-1}$            |     0    |   0              |   $a_0$                              |    0                 |
|    1       |    0     |    0       |  -2  |     -2A   |    1    |    0    |    1    |    $\overline{a_{j-1}}$ |     0    |   1              |   $a_0$                              | $\overline{a_0}$     |
|    1       |    0     |    1       |  -1  |     -A    |    1    |    1    |    0    |    $\overline{a_j}$     |   $a_0$  | $\overline{a_0}$ | $\overline{a_0}\oplus\overline{a_1}$ | $\overline{a_0+a_1}$ |
|    1       |    1     |    0       |  -1  |     -A    |    1    |    1    |    0    |    $\overline{a_j}$     |   $a_0$  | $\overline{a_0}$ | $\overline{a_0}\oplus\overline{a_1}$ | $\overline{a_0+a_1}$ |
|    1       |    1     |    1       |  +0  |     +0    |    0    |    0    |    0    |    $0$                  |     0    |   0              |    0                                 |    0                 |

根据 truth table，可以推出下面的表达式：

$$\epsilon=a_1\oplus (a_0\cdot b_{2i+1})$$
$$t_{i1}=neg_i\cdot\epsilon + two_i\cdot a_0$$
$$d_{i1}=neg_i\cdot\overline{a_0+a_1\cdot(b_{2i} \oplus b_{2i-1})}$$

或

$$d_{i1}=\overline{\overline{b_{2i+1}}+a_0}\cdot\overline{(b_{2i-1}+a_1)\cdot(b_{2i}+a_1)\cdot(b_{2i}+b_{2i-1})}$$

还可以列出 $\overline{s_0}s_0s_0$ 和 $d_i$ 的 truth table 如下，

| $\overline{s_0}$ | $s_0$ | $s_0$ | $d_i$ | $\alpha_2$ | $\alpha_1$ | $\alpha_0$ |
| :--------------: | :---: | :---: | :---: | :--------: | :--------: | :--------: |
|        1         |   0   |   0   |   0   |      1     |     0      |       0    |
|        1         |   0   |   0   |   1   |      1     |     0      |       1    |
|        0         |   1   |   1   |   0   |      0     |     1      |       1    |
|        0         |   1   |   1   |   1   |      1     |     0      |       0    |

根据 truth table，可以推出下面的表达式：

$$\alpha2=\overline{s_0\cdot \overline{d_i}}$$
$$\alpha1=s_0\cdot \overline{d_i}=\overline{\alpha2}$$
$$\alpha0=s_0\odot\overline{d_i}$$

!!! warning

    原文中 Table II 中关于 $t_{i1}$ 的值有笔误，但是表达式是正确的。

相应的 pp 阵列如下图所示：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                   ~a  a  a  p  p  p  p  p  p  p  t
pp1                 1 ~s  p  p  p  p  p  p  p  d  c
pp2           1 ~s  p  p  p  p  p  p  p  t  c
pp3     1 ~s  p  p  p  p  p  p  t  t  c
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

**综合结果：**

TSMC 7nm + synopsys DC, 1GHz + 30% over constrain

| implementation | area (mm^2) |
| -------------- | ----------- |
| MBCODEC        |  11.2723    |
| Wallace-tree   |   8.8920    |
| CLA            |   7.2504    |
| Total          | **27.4147** |

### Unsigned and Signed

如果要同时支持 unsigned 和 singed 乘法，有两种情况：

1. 只支持同类型相乘，即 singed x signed 或 unsigned x unsigned
2. 支持任意类型相乘

由[参考文献 1][appendix]可以知道，8bit unsigned 的 pp 阵列如下图所示：

```
#!text
bit    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0  -1

   A                            a  a  a  a  a  a  a  a
 x B                            b  b  b  b  b  b  b  b  0
-----------------------------------------------------------------------
pp0                ~n  n  n  p  p  p  p  p  p  p  p  p
pp1              1  n  p  p  p  p  p  p  p  p  p     n
pp2        1 ~n  p  p  p  p  p  p  p  p  p     n
pp3    ~n  p  p  p  p  p  p  p  p  p     n
pp4     p  p  p  p  p  p  p  p     n
-----------------------------------------------------------------------
   C    x  x  x  x  x  x  x  x  x  x  x  x  x  x  x  x
```

unsigned 和 signed 的主要区别是：

+ 每个 pp 的高位由 n 而不是 s 组成
+ unsigned 的每个 pp 位宽要多 1bit
+ unsigend 的 last pp 组成与 unsigned 不同

所以支持第一种情况很简单，只需要根据数据类型，条件生成 pp 即可，后级的 wallace-tree 和 cla 可以复用。

支持第二种情况时：

+ 对于被乘数，当其为 unsigned 时，需要在 MSB 扩展 1bit 的 0，转化为 signed 类型
+ 对于乘数，unsigned/signed 主要影响的是 last pp 的组装方式
    + 当其为 signed 类型时, last pp 只由 neg 和 padding 0 组成
    + 当其为 unsigned 类型时，last pp 由 neg 和额外产生的 pp 组成
    + 如果是基于 MBE_IV，那么 unsigned 类型需要重新计算出 4 个 $\alpha$ 值

根据 truth table，可以得到

$$s_i=(i==0)?\ p_{MSB} : neg_i$$
$$\alpha_0=d\oplus s_0$$
$$\alpha_1=\overline{n_0}\cdot s_0\cdot d + n_0\cdot(\overline{s_0}+s_0\oplus d)$$
$$\alpha_2=n_0\cdot\overline{s_0\cdot d}$$
$$\alpha_3=\overline{n_0}+n_0\cdot s_0\cdot d$$

### Wallace Tree

## Summary

Array multiplier 实现最简单，但是消耗的面积最大，频率也最低，所以现实中不会有人使用这种方式；Baugh-Wooley multiplier 实现简单，消耗的资源少，但是需要多个 cycle 才能完成一次计算，所以一般应用在对性能要求不高的低功耗场景中；Booth-Wallce multiplier 应用最广泛，目前绝大多数乘法器都是基于 MBE 设计的。

**Signed 实际综合结果：**

TSMC 7nm + synopsys DC, 1GHz + 30% over constrain

| implementation | DesignWare  | MBE_I area (mm^2) | MBE_II area (mm^2) | MBE_III area (mm^2) | MBE_IV area (mm^2) |
| -------------- | ----------- | ----------------- | ------------------ | ------------------- | ------------------ |
| MBCODEC        |    -        |     11.9153       |    14.8154         |     10.5883         |    11.2723         |
| Wallace-tree   |    -        |     13.0234       |    12.9276         |     18.1902         |     8.8920         |
| CLA            |    -        |      7.8660       |     7.5650         |      6.8810         |     7.2504         |
| Total          | **22.5310** |    **32.9962**    |   **35.3081**      |    **28.6596**      |   **27.4147**      |
| increase       |             |      46.4%        |     56.7%          |      27.2%          |     21.7%          |

最优化的版本还是比 DesignWare 差了 21.7%，可能的原因是 DesignWare 用了更先进的 wallace-tree，待深入研究。

**Unsigned 实际综合结果：**

TSMC 7nm + synopsys DC, 1GHz + 30% over constrain

| implementation | DesignWare  | MBE_I area (mm^2) | MBE_II area (mm^2) | MBE_III area (mm^2) | MBE_IV area (mm^2) |
| -------------- | ----------- | ----------------- | ------------------ | ------------------- | ------------------ |
| MBCODEC        |    -        |     14.4734       |    18.5638         |     13.5432         |    17.4830         |
| Wallace-tree   |    -        |     18.3722       |    18.7279         |     18.3175         |    22.1479         |
| CLA            |    -        |      7.4830       |     8.3448         |      7.1136         |     7.8250         |
| Total          | **26.7991** |    **40.3970**    |   **45.8006**      |    **39.1111**      |   **47.8937**      |
| increase       |             |      50.7%        |     70.9%          |      45.9%          |     78.7%          |


## Ref

[Appendix A. Sign Extension in Booth Multipliers][appendix]
[High-speed Booth encoded parallel multiplier design][paper1]
[Modified Booth Multipliers With a Regular Partial Product Array][paper2]
