Title: RISC-V Book 阅读笔记
Date: 2024-04-13 14:26
Category: RISC-V
Tags: RISC-V, Spec
Slug: riscv-book-note
Author: Qian Gu
Series: RISC-V Notes
Summary: The RISC-V Reader: An Open Architecture Atlas 读书笔记

[TOC]

## 为什么要有 RISC-V？

> 大道至简。
>
> ——列奥纳多·达·芬奇（Leonardo da Vinci）

年轻、开放、模块化。

### ISA 设计导论

计算机架构师在设计 ISA 时需要遵守的基本原则和做出权衡，评价一个 ISA 的 7 个指标：

+  **成本** 

    ISA 越简单，area 越小，成本越低。

+  **简洁** 

    简洁不光可以节省制造成本，还能节省设计和验证时间，降低文档开销，使得用户更加容易了解和使用。高端 implement 可以通过组合简单指令来提升性能，但是如果直接在 ISA 中添加更大、更复杂的指令会给低端 implement 带来负担。

+  **性能** 

     完成相同的任务，RISC 比 CISC 需要的指令更多，但是 RISC 因为其 ISA 的简洁性，可以通过更高的时钟频率和更小的 CPI 来弥补。

+  **架构和实现分离** 

    延迟分支槽：MIPS-32 ISA 在 architecture 层面解决某一时期某个 implement 的问题，导致其他和后续的 implement 为了保持向后兼容不得不做一些无用的工作。

    架构师除了不应该加入那些仅有助于一个 implement 的功能，也不应该加入阻碍某些实现的功能。比如 ARM-32 提供的 load multiple 指令，这个指令可以提升单发射 pipeline 的性能，但是会对多发射 pipeline 带来负面影响。因为简单的多发射实现无法支持 load multiple 指令和其他指令的并行调度，所以要么实现更复杂的多发射机制，要么降低这种情况下的指令吞吐。

+  **提升空间** 

    随着摩尔定律的终结，大幅提高性价比的唯一途径是 DSA（为特定领域添加自定义指令，如 DL、AR 等），所以 ISA 必须预留操作码空间。

+  **代码大小** 

    让代码变短是 ISA 架构师的目标，因为可以降低所需存储器的面积（嵌入式的一项巨大成本），降低 I$ 的 miss ratio，从而降低功耗（访问片外 DRAM代价远高于片上 SRAM）并提升性能。

+  **易于编程/编译/链接** 

    GPR 数量越多，编译器和汇编程序员的工作越轻松。ARM-32 有 16 个寄存器，X86-32 只有 8 个，现代 ISA 都有相对较多的 32 个。

    位置无关代码（Position Independent Code, PIC）有助于支持动态链接，因为共享库的代码可以放在不同地址。PC 相对分支和数据寻址是 PIC 的福音，RISC-V 支持 PC 相对寻址，但是 x86-32 和 MIPS-32 不支持。

!!!note
    ISA 就好比俄罗斯方块中的方块形状集合，集合要设计的够用且不冗余。

### 结语

> 用形式逻辑方法容易看出，存在某种抽象的 [指令集]，足以控制和执行任意操作序列……现在看来，选择一款 [指令集] 的真正决定性因素更多是实用性：[指令集] 所需装置的简洁性，应用于实际重要问题的清晰度，以及处理这些问题的速度。
> ——[Burks et al. 1946]

RISC-V 是一款最新的、清晰的、简约的、开放的 ISA，它以过去 ISA 所犯错误为鉴。RISC-V 架构师的目标是让它能用于从最小到最快的所有计算设备。遵循冯·诺依曼在 1940 年代的建议，RISC-V 强调简洁性以保持低成本，同时拥有大量寄存器和直观的指令执行速度，从而帮助编译器和汇编语言程序员将实际的重要问题转换为适当的高效代码。

## RV32I：RISC-V 基础整数指令集

> ……提升计算性能并让用户切实享受到性能提升的唯一方法是同时设计编译器和计算机。这样软件用不到的特性将不会在硬件上实现……
>
> ——法兰·艾伦（Frances Elizabeth “Fran” Allen），1981

### RV32I 指令格式

简洁的指令格式：

+ 简洁：四种基础格式 R(egister) + I(mmediate) + S(tore) + U(pper) + 两种扩展格式 B(ranch) + J(ump)
+ 性能：支持 3 个操作数
+ 性能：rs1，rs2，rd 位置固定，在 dec 前访问 GPR
+ 性能：imm 的符号位永远在 inst[31]，符号位扩展可在 dec 前进行
+ 易于编程：全 0 和全 1 为非法指令
+ 成本：精心挑选 op_code，使得 datapath 相同的指令共享 op_code，从而简化控制逻辑
+ 提升空间：RV32I 占用 32bit 指令编码空间不到 1/8，预留指令编码空间

### RV32I 寄存器

+ 易于编程：RISC-V = 32 个 GPR + 1 PC；ARM-32 = 16 个 GPR（包含 PC）
+ 简洁：实现相同功能，设置 x0 为常 0 可以简化操作，额外设置 PC 可以简化分支预测复杂度，且少占用一个 GPR

### RV32I 整数计算

+ 简洁：imm 总是符号位扩展，所以无需 imm 版本的 sub 指令
+ 简洁：虽然 branch 支持 2 个 GPR 之间的所有运算关系，还是提供 slt 方便处理更复杂的条件表达式
+ 易于编程：lui 搭配后续一条指令，可以构造出 32bit 的 imm；auipc 搭配 jal/jalr 可以实现相对于 PC 的任意偏移跳转和数据访问

### RV32I 取数和存数

+ 简洁：RV32I 只支持一种标准寻址模式： **偏移寻址** ，即跳转地址 = 寄存器 + imm[11:0]
+ 简洁：没有栈指令，ABI 中指定 x2 为 sp 就能使得标准寻址模式具有 push/pop 的优点，无需增加 ISA 复杂度
+ 易于编程：ARM-32 和 MIPS-32 要求数据按其长度对齐，RISC-V 无此要求

!!!note
    因为一条 32bit 指令无法容纳 32bit 地址，所以 linker 通常要把每个符号调整成 2 条 RV32I 指令。

    + 对于数据地址，需要调整为 lui 和 addi
    + 对于代码地址，需要调整为 auipc 和 jalr

    很多时候跳转距离没那么大，此时并不需要两条，linker 会多趟扫描代码，尽可能优化成一条 jal 指令（包含 imm[19:0]，可以寻址前后 1MB），这个过程叫做 linker relaxation。

### RV32I 条件分支

+ 简洁：RISC-V 没有 MIPS-32 的延迟分支，也没有 ARM-32 和 x86-32 的条件码
+ 简洁：auipc 的 imm 为 0 就可以得到当前 PC，x86-32 需要先调用函数把 PC push，然后读出 PC，最后再 pop
+ 简洁：大部分程序都忽略整数的算术溢出，所以 RISC-V 让软件检测溢出

### RV32I 无条件跳转

+ 简洁：RV32I 不支持复杂的过程调用指令，如 x86-32 的 enter/leave，Tensilica 的 register windows

!!!info
    register windows：通过远多于 32 个 GPR 来加速函数调用。在函数调用时，为其分配新的一组 32 个寄存器（也称为窗口），为了支持传参，两个函数的窗口会重叠，即有些寄存器同时属于两个相邻的窗口。

### 其他 RV32I 指令

+ 简洁：RISC-V 通过 memory-map IO 来访问设备，没有 x86-32 的专用 I/O 指令

### 结语

> 那些遗忘过去的人注定要重蹈覆辙。
>
> ——乔治·桑塔亚那（George Santayana），1905

得益于起步时间比过去的 ISA 晚 20∼30 年，RISC-V 架构师可以实践 Santayana 的建议，借鉴包括 RISC-I 在内不同 ISA 的设计，取其精华，去其糟粕。此外，RISC-V 国际基金会将以可选扩展的方式缓慢地演进指令集，以规避给过去的成功 ISA 造成麻烦的野蛮生长现象。

!!!important
    图 2.7 按照 7 个评价指标汇总了 ARM-32、MIPS-32、x86-32 和 RV32I 的对比

## RISC-V 汇编语言

> 给看似困难的问题找到简单的解法往往令人满足，而最好的解法通常是简单的。
>
> ——伊凡·苏泽兰（Ivan Sutherland）

### 函数调用过程

通常分为 6 个阶段：

1. caller 将参数放到 callee 可访问的位置
2. 调换到 callee 的入口（使用 jal）
3. 获取函数所需的局部存储资源，按需保存 GPR
4. 执行函数功能
5. 将返回值放到 caller 可访问的位置，恢复 GPR，释放局部存储资源
6. 将控制权返回给 caller（使用 ret）

!!!note
    保存寄存器由 callee 负责维护，重新解释上述过程如下：

    在 caller 中执行 call 指令跳转进入 callee 后，callee 首先做两件事：

    1. 分配 stack frame，为保存现场准备资源
    2. 将 callee 需要维护的保存寄存器存储到 stack 中

    当 callee 完成功能后，执行 ret 指令前做两件事情：

    1. 从 stack 向保存寄存器恢复现场
    2. 恢复保存寄存器 `sp` == 释放 stack frame（局部资源）

为了提升性能，应尽量把变量放在 GPR 中而不是内存中，同时要避免因为保存和恢复 GPR 而频繁访问内存。RISC-V 有足够的寄存器兼顾两者：既能把操作数放在 GPR，又能减少保存和恢复它们的次数。关键在于，一些寄存器不保证其值在函数调用前后保持一致，称为临时寄存器；另一些能保证，称为保存寄存器。不再调用其他函数的函数称为叶子函数。当一个叶子函数只有少量参数和局部变量时，可将其分配到寄存器，无需分配到内存。大部分函数调用均如此，此时程序无需将寄存器保存到内存。

典型例子 main 函数调用 prinf：

    #!sh
    # 编译，将 c 代码转化为 asm 代码，结果如图 3.6
    gcc -o hello.s -S hello.c
    # 编译，将 asm 代码转化为 .o 文件，.o 文件无法直接查看，需要先 dump，结果如图 3.7
    # 其中一些指令的地址字段是 0，需要 linker 填充
    gcc -o hello.o -c hello.s
    objdump -D hello.o >> hello.o.dump
    # 链接，将 .o 文件转化为 elf 文件，elf 文件无法直接查看，需要先 dump，结果如图 3.8
    # 地址字段已替换
    gcc -o hello hello.c
    objdump -D hello >> hello.dump

### 结语

> 保持简洁，直接。
> 
> —— 凯利·约翰逊（Kelly Johnson），提出“KISS原则”的航空工程师，1960

汇编器向简洁的 RISC-V ISA 增加了 60 条伪指令，在不增加硬件开销的同时令 RISC-V 代码更易于读写。RISC-V 提供一系列简单有效的机制，可降低成本、提高性能、易于编程。

## RV32M：乘法和除法指令

> 若无必要，勿增实体。
> 
> ——奥卡姆的威廉（William of Occam），约 1320

+ 在几乎任何处理器上，执行速度：移位 > 乘法 >> 除法。
+ 除以常数，可以转化成乘以一个近似的倒数，再校正积的高位部分
+ ARM-32 在 2005 之后才添加了除法指令；MISP-32 使用特殊的寄存器作为乘除法的 rd，所以需要额外的传送指令，会降低性能，增加体系结构的状态，降低切换任务的速度
+ mulh 和 mulhu 可以检查乘法溢出
+ 除数为 0 不会产生 trap，所以可以只在需要时通过 beqz 检查除数是否为 0
+ mulhsu 对 multi-word singed 乘法很有用

### 结语

> 最便宜、最快且最可靠的组件是那些不存在的组件。
> 
> ——切斯特·戈登·贝尔（C. Gordon Bell），著名小型计算机架构师

## RV32F 和 RV32D：单精度和双精度浮点数

> 达成完美之时并非无所可增，而是无所可减。
> 
> ——安托万·德·圣埃克絮佩里（Antoine de Saint-Exupéry），《人的大地》，1939

### 浮点寄存器

+ 性能：4 种指令格式中 rs 和 rd 只有 5bit 刚好表达 32 个 x 寄存器，为了保持指令格式不变，为浮点另外设置一组（32个）f 寄存器
+ 如果只支持 RV32F 则 FLEN=32，如果支持 RV32D 则 FLEN=64
+ fcsr 用于存放 round mode 和精确异常 flag
+ ARM-32 和 MIPS-32 有 32 个 float 寄存器，但是只有 16 个 double 寄存器（把两个 float 拼接成一个 double 使用）
+ x86-32 浮点运算早期使用 stack 而不是寄存器，后续版本增加了 8 个 64bit 浮点寄存器
+ ARM-32 和 x86-32 不支持 x 和 f 寄存器之间直接传送数据的指令，要实现该功能，必须先写内存，再读内存

### 浮点取数、存数和算术运算

+ 性能：许多浮点运算（矩阵乘法）在乘法后立即执行一次加法/减法，所以 RISC-V 提供了 fmadd、fmsub、fnmadd、fnmsub 指令

### 结语

> 少即是多。
> 
> ——罗伯特·勃朗宁（Robert Browning），1855。

## RV32A：原子指令

> 一切事物都应该尽量简单，但不能过分简单。
> 
> ——阿尔伯特·爱因斯坦（Albert Einstein），1933

RV32A 用于同步的原子操作有两种：

+ 原子内存操作（atomic memory operation，AMO）
+ 预订取数/条件存数（load reserved / store conditional）

为何 RV32A 要提供两种原子操作？答案是对应两种区别很大的使用场景。

场景一：编程语言开发者假定顶层的 ISA 提供原子的 compare-and-swap 操作：比较某寄存器和另一寄存器寻址的内存值，若相等，则将第 3 个寄存器的值与内存值交换。这是一种通用的同步原语，基于它可以实现其他任意 word 同步操作。

    #!text
    # 用 lr/sc 对内存 M[a0] 进行 compare-and-swap
    # 期望的旧值在 a1 中；期望的新值在 a2 中
    0: lr.w a3, (a0)  # 取出旧值
    4: bne a3, a1, 80  # 旧值是否等于 a1？
    8: sc.w a3, a2, (a0)  # 如果相等，则换入新值
    c: bnez a3, 0  # 如果失败，重试
    ... compare-and-swap 成功后的代码...
    ...
    80:  # compare-and-swap 失败
    ```

场景二：

    #!text
    # 用 AMO 实现 test-and-set 自旋锁，用于保护临界区
    0: li t0, 1 # 初始化锁值
    4: amoswap.w.aq t1, t0, (a0) # 尝试获取锁
    8: bnez t1, 4 # 若失败则重试
    ...临界区代码..
    20: amoswap.w.rl x0, x0, (a) # 释放锁
    ```

### 结语

RV32A 是可选的，一个不支持它的 RISC-V 处理器会更简单。然而，正如爱因 斯坦所言，一切事物都应该尽量简单，但不能过分简单。RV32A 正是如此，许多场景 都离不开它。

## RV32C：压缩指令

> 小即是美。
> 
> ——恩斯特·弗里德里希·舒马赫（E. F. Schumacher），1973

+ 代码大小：以前的 ISA 为缩减代码大小而添加很多指令和指令格式，ARM 和 MIPS 分别对 ISA 重新设计了两遍：ARM 设计了 ARM Thumb 和 Thumb2，MIPS 则设计了 MIPS16 和 microMIPS。这些新 ISA 给处理器和编译器带来额外的设计开销，同时还增加汇编语言程序员的认知负担。
+ 简洁：RV32C 采用一种新方法：每条短指令都必须对应一条标准的 32 位 RISC-V 指 令。此外，16 位指令仅对汇编器和链接器可见，并由它们决定是否将标准指令替换为相应的短指令。编译器开发者和汇编语言程序员无需关心 RV32C 指令及其格式，他 们只需知道最终得到的程序比大部分情况下更小。
+ 成本：尽管处理器设计者不能忽略 RV32C 指令，但能通过以下技巧降低实现开销：在执 行指令前通过一个译码器将所有 16 位指令翻译成相应的 32 位指令。

为什么有些架构师会跳过 RV32C：16bit 的 RV32C 和 32bit 的 RV32I 混合在一起会恶化 decoder 的时序，而在高性能处理器中，dec 本身就是时序瓶颈，所以很难处理这种情况。典型例子：

+ superscalar 一个 cycle 内 decode 多条指令
+ 宏融合 macrofusion：decoder 把多条指令组合成更复杂的指令来执行

### 结语

> 我本能写出更短的信，但我没有时间。
> 
> ——布莱兹·帕斯卡（Blaise Pascal），1656。

RV32C 让 RISC-V 编译出当今几乎最短的代码。您几乎能将其视为硬件辅助的伪指令。但这里汇编器将其隐藏起来，汇编语言程序员和编译器开发者无需感知。

## RV32V：向量

> 我追求简洁，无法理解复杂的事物。
> 
> ——西摩·克雷（Seymour Cray）

+ 性能：注数据级并行，该技术用于可在大量数据上并发计算的目标应用程序。最著名的数据级并行架构是 SIMD（Single Instruction Multiple Data，单指令多数据）。
+ 架构和实现分离：将向量长度和每个时钟周期的最大操作次数与指令编码分离，是向量架构的关键。向量微架构师可灵活设计数据并行硬件单元，不会影响程序员，而程序员无需重写代码即可享受更长向量的好处。
+ 易于编程/编译/链接：向量架构的指令数量比 SIMD 架构少得多。而且，与 SIMD 不同，向量架构的编译技术十分完善。

### 向量计算指令

+ RV32IMAFD 每一条整数和浮点计算指令基本都有对应的向量版本
+ 每条向量指令根据操作数的类型，有多个版本

### 向量寄存器和动态类型

+ 32 个名称以 v 开头的向量寄存器，但每个向量寄存器的元素数量并不固定，取决于操作的位宽和向量寄存器堆大小，后者由处理器设计者决定。

| 术语   | 含义                                 |
| ------ | ------------------------------------ |
| `VLEN` | 每个 VRF 的位宽，单位为 bit          |
| `mvl`  | 单条指令能正确运行的最大向量元素个数 |
| `vl`   | 待处理的向量元素个数                 |

+ 易于编程/编译/链接：RV32V 采取将数据类型和位宽与向量寄存器关联的新方法，而不是与指令操作码关联。程序在执行向量计算指令前，先在向量寄存器中设置数据类型和位宽。使用动态寄存器类型可大幅减少向量指令数量。动态类型向量架构能降低汇编语言程序员的认知负担和编译器中代码生成器的复杂度。
+ 
向量架构不如 SIMD 架构流行的一个原因是，大家担心添加很大的向量寄存器会增加中断时保存和恢复程序（上下文切换）的开销。动态寄存器类型有助于改善此情况。根据 RV32V 约定，软件在不使用向量指令时需要禁用所有向量寄存器，这意味着处理器既具备向量寄存器的性能优势，又仅在向量指令执行过程中发生中断时才引入额外的上下文切换开销。

### 向量取数和存数

+ 易于编程/编译/链接：虽然可以设置 stride = 1 使得 stride 兼容 unistride，但是提供 unistride 指令可以缩小代码体积和指令数。（vlds/vsts 需要 2 个 rs，而 vld/vst 只需要 1 个）
+ 易于编程/编译/链接：为了支持稀疏数组，提供 index 指令

### 向量操作的并行度

+ 性能：向量元素之间独立，硬件可以并行计算，每个 cycle 计算的元素数量由 VLEN 和 EEW 决定
+ 易于编程/编译/链接：在 SIMD 架构中，由 ISA 架构师决定每个 cycle 并行操作的最大数量和每个寄存器的元素数量，如果寄存器位宽翻倍，则指令数也翻倍，还需要同步修改编译器。RV32V 则由 implementation 决定，无需修改 ISA 和编译器，同一份 RV32V 程序，无需修改（修改代码和重新编译）就可以同时在最简单或最激进的向量处理器上运行。

### 向量操作的条件执行

一些向量计算包含 if 语句。向量架构不依赖于条件分支，而是用掩码禁止部分元素的向量操作。

### 结语

> 若代码可向量化，最好的架构就是向量架构。
> 
> ——吉姆·史密斯（Jim Smith）于 1994 年在国际计算机体系结构研讨会（ISCA）上的主题演讲

## RV64：64 位地址指令

> 在计算机设计中只有一种错误难以恢复——用于存储器寻址和存储管理的地址位 不足。
> 
> ——切斯特·戈登·贝尔，1976

+ 代码大小：RV64 基本上是 RV32 的超集，唯一例外是压缩指令。
+ 与 RISC-V 不同，ARM 决定采用最大主义方法来设计 ISA。
+ 成本：程序大小的差异显著，让 RV64 要么能通过较低的指令缓存缺失率提升性能，要么在缺失率尚可接受的前提下，采用更小的指令缓存来降低成本。

### 结语

> 成为先驱的一个问题是你总会犯错误，而我永远不想成为先驱。在看到先驱所犯错误后，第二个做这件事才是最好的。
> 
> ——西摩·克雷（Seymour Cray），第一台超级计算机的架构师，1976 年

64 位架构更能体现 RISC-V 设计的合理性，这对 20 年后才开始设计的我们是更容易实现的，因为我们能借鉴先驱经验，取其精华，去其糟粕。

## RV32/64 特权架构

> 简洁是可靠性的前提。
> 
> ——艾兹赫尔·韦伯·戴克斯特拉（Edsger W. Dijkstra）

高特权模式通常能访问低特权模式的所有功能，同时还具备若干低特权模式下不可用的额外功能，如中断处理和 I/O 操作。处理器通常在最低特权模式下运行，当发生中断和异常时，则将控制权转移到更高特权的模式。

RV 的 3 种模式：

+ machine mode
+ supervisor mode
+ user mode

特权架构指令很少，但是增加了若干 csr 来实现其新增功能。

+ 简洁：RV32 和 RV64 特权架构，两者的差异仅体现在整数寄存器的位宽。

### 机器模式

机器模式最重要的特性是拦截和处理异常 exception（不寻常的 runtime event）。RISC-V 将 exception 分为两类：

+ 同步异常 synchronous exception：指令执行的结果，比如访问非法地址，指令 opcode 无效
+ 中断 interrupt：和指令流异步的外部事件，比如鼠标点击。标准中断源有 3 个
	+ 软件 software：通过写入一个内存映射寄存器触发，通常用于一个 hart 通知另一个 hart，此机制在其他架构中称为处理器间中断 interprocessor interrupt
	+ 时钟 timer：mtime >= mtimecmp（内存映射寄存器）时触发
	+ 外部来源 external：由 PLIC（大部分外设都挂载在它上面）产生，PLIC 因平台而异

RISC-V 允许不对齐访存，但是仍包含访存地址不对齐异常。原因是考虑到不对齐访存的硬件实现较复杂，且出现频率很低，因此一些硬件实现方案选择不支持不对齐的普通访存操作。这类处理器需要陷入异常处理程序，然后通过一系列较小的对齐访存操作，来在软件中模拟不对齐访存。应用程序代码对此一无所知：不对齐访存操作仍然正确执行，虽然执行得慢，但硬件实现却很简单。此外，高性能处理器亦可在硬件中实现不对齐访存。

### 机器模式的异常处理

异常处理必须的 8 个 csr：

| 名称       | 全拼                      | 含义 |
| ---------- | ------------------------- | -------------------------------------------------------------------------------------------- |
| `mstatus`  | Machine Status            | 维护各种状态，如全局中断使能                                                                 |
| `mip`      | Machine Interrupt Pending | 记录当前的中断请求                                                                           |
| `mie`      | Machine Interrupt Enable  | 维护处理器的中断使能状态                                                                     |
| `mcause`   | Machine Exception Cause   | 指示发生了何种异常                                                                           |
| `mtvec`    | Machine Trap Vector       | 存放发生异常时处理器跳转的地址                                                               |
| `mtval`    | Machine Trap Value        | 存放当前自陷相关的额外信息，如地址异常的故障地址、非法指令异常的指令，发生其他异常时其值为 0 |
| `mepc`     | Machine Exception PC      | 指向发生异常的指令                                                                           |
| `mscratch` | Machine Scratch           | 向异常处理程序提供一个字的临时存储                                                           |

M-mode 响应 exception 的例子：

1. 首先检查条件 mstatus.MIE = 1，mie 和 mip 的 bit 位，满足条件后原子性地完成以下步骤
2. 将 exception 指令的 PC 保存到 mepc，然后把 PC 设置为 mtvec
	+ 对于 synchronous exception：mepc 指向触发 exception 的指令
	+ 对于 interrupt：mepc 指向 ISR 后恢复执行的指令
3. 把 exception 原因写入 mcause，并把故障地址或其他相关信息写入 mtval
4. 把 MIE 的旧值保存到 MPIE，把 mstatus.MIE 清零以屏蔽 interrupt
5. 把 exception 发生前的模式保存到 mstatus.MPP，然后把模式更改为 M

!!!note
    CSR 中没有记录当前的 privilege 等级，只有 MPP、SPP、UPP，所以软件无法查询得知当前处于哪个模式，原因是 ISA 认为软件开发人员应该准确地知道每段代码所处的特权等级，无需查询。
    从硬件设计的角度，内部需要有一个寄存器来记录当前状态，否则无法判断当前等级是否有权限执行某些指令。该内部寄存器未开放给软件，所以在 ISA CSR 中也不可见。

mscratch 的作用：提供一种快速的保存-恢复机制，可以直接把某个 XRF 写入到 mscratch，而不是 stack 中。如果需要保存更多的寄存器，一般 mscratch 指向一片空闲的内存，ISR 可以根据需求把想要的任意个寄存器内容写入到该空间：

1. 首先用 csrrw 指令交换 mscratch 和 a0 的内容（mscratch 是 csr，普通指令无法直接使用，必须先交换到 XRF 中。因为 ISR 没有参数，所以 a0 是空闲 XRF，可以用来和 mscratch 交换）
2. 将任意个 XRF 保存到内存中
3. 中断处理
4. 处理完后再从内存中恢复数据到 XRF
5. 用 csrrw 交换 mscratch 和 a0，恢复内容
6. 用 mret 返回

示例代码：

    #!asm
    # example：timer 中断的 ISR。
    # 假设
    # 1. mstatus.MIE=1 已打开全局中断使能
    # 2. timer 中断使能 mie[7]=1 已打开
    # 3. mtvec 设置为本处理程序的地址
    # 4. mscratch 指向一段 16Byte 的临时缓冲区
    
    # step1. 交换 mscratch 和 a0。a0 保持空闲内存供后续普通指令使用，mscratch 保存 a0 旧值，用于后续恢复
    csrrw a0, mscratch, a0
    
    # step2. 保存 XRF 到空闲内存。因为后续要使用到 a1, a2, a3, a4 这几个 XRF，所以先保存旧值
    sw a1,  0(a0)
    sw a2,  4(a0)
    sw a3,  8(a0)
    sw a4, 12(a0)
    
    # step3. 中断处理
    # 解析中断原因
    csrr a1, mcause        # 读出异常原因
    bgez a1, exception     # 若非中断则跳转，bgez 的 rs 是 signed 类型，中断对应的 MSB = 1 为负数
    andi a1, a1, 0x3f      # 单独取出中断原因
    li   a2, 7             # a2 = 时钟中断号
    bne  a1, a2, otherInt  # 若非 timer 中断则跳转
    # 处理 timer 中断，递增 mtimecmp
    la   a1, mtimecmp      # mtimecmp 是 memory map csr，读出该地址的到 a1
    lw   a2, 0(a1)         # 读出 mtimecmp 的低 32bit 到 a2
    lw   a3, 4(a1)         # 读出 mtimecmp 的高 32bit 到 a3
    addi a4, a2, 1000      # 给 mtimecmp 的低 32bit 加上 1000，求和结果保存到 a4
    sltu a2, a4, a2        # 计算进位，如果和 a4 比加数 a2 小，说明有进位，进位保存在 a2 中
    add  a3, a3, a2        # 把进位加到 mtimecmp 的高位 a3 上
    sw   a3, 4(a1)         # 保存递增后的 mtimecmp 高位
    sw   a4, 0(a1)         # 保存递增后的 mtimecmp 低位
    
    # step4. 恢复 XRF, a1, a2, a3, a4
    lw a4, 12(a0)
    lw a3,  8(a0)
    lw a2,  4(a0)
    lw a1,  0(a0)
    
    # step5. 恢复 a0 和 mscratch 旧值
    csrrw a0, mscratch, a0
    
    # step6. 从 ISR 返回
    mret

### 嵌入式系统中的用户模式和进程隔离

并非所有代码都是可信任的：底层 OS 代码可行度较高，可以访问所有硬件资源；应用程序代码可行度较低，需要进行限制：

+ 限制 U 模式代码可执行的指令（M 模式指令）和访问的资源（M 模式 CSR）
+ 限制 U 模式代码只能访问各自的内存，即 PMP（指定哪些内存可以让 U 模式访问）

### 现代操作系统的监管模式

TODO

### 页式虚拟内存

TODO

### 结语

> 一项又一项的研究表明，最优秀的设计师能更轻松地设计出更快、更小、更简洁、更明了的结构。伟大和平凡之间相差近一个数量级。
> 
> ——弗雷德·布鲁克斯（Fred Brooks, Jr.）, 1986.> 一款指令集的 7 个评价标准：
>
> + 成本
> + 简洁
> + 性能
> + 架构和实现分离
> + 提升空间
> + 代码大小
> + 易于编程/编译/链接

围绕这 7 个评价指标从全系统角度向读者介绍 RISC-V 的精巧设计和众多的取舍考量。
