Title: RISC-V Spec 阅读笔记 #1 —— Intro & Base ISA & Zicsr
Date: 2020-11-17 21:55
Category: RISC-V
Tags: RISC-V, Spec
Slug: risc_v_spec_notes_1
Author: Qian Gu
Series: RISC-V Notes
Summary: Volume I: Unprivileged ISA 读书笔记，Intro + Base + Zicsr
Status: draft

!!! note

    Spec 文档的版本号:20191213


## Introduction

整个 Spec 分为两部分：

+ Volume I: Unpriviledge ISA
+ Volume II: Priviledge ISA

### Hardware Platform Terminology

| 术语                 |      含义                   |
| ------------------- | --------------------------- |
|  hardware platform  | RISC-V core + non-RISC-V core + accelerator + memory + I/O + interconnect |
|  core               | 包含独立的 IFU 的模块 |
|  coprocessor        | 附着在 RISC-V core 上，主要由 RISC-V 控制，具有有限的自主控制权运行扩展指令 |
|  accelerator        | 不可编程的固定函数单元 / 针对特定功能的可以自动运行的 core |

### Software Execution Environment and Harts

`EEI (Execution Environment Interface)`：定义了程序的初始状态，Hart 的数量和类型，包括 hart 支持的特权模式、memory 的访问及特性、所有指令的行为、对中断和异常的处理。EEI 的典型例子有 Linux 的 `ABI (Application Binary Interface)` 和 RISC-V 的 `SBI (Supervisor Binary Interface)`。

EEI 的实现方式有多种：

+ Bare metal：hart 由硬件直接实现，可以访问所有的地址空间，硬件平台定义上电复位后的执行环境
+ 操作系统通过对处理器和 memory 的控制，提供不同层级的执行环境
+ 管理程序对 guest 访问提供不同层级的执行环境
+ 仿真器，比如 Spike、QEMU、rv8 等

`Hart`：硬件线程，自动取指和执行所涉及的硬件资源的统称。（有些处理器中包含多个硬件线程，每个线程有自己独立的 RF 等上下文资源，不同线程共享同一份运算资源）

### ISA Overview

RISCV ISA 由必选的 Base Integer ISA 和其他可选 ISA 组成。

必选的 base interger ISA 有 4 种形式，它们的区别在于 register 的位宽、register 的数量、寻址空间大小： 

| ISA | XLEN (register 位宽) | registe 数量 | 寻址空间范围 (Byte) |
| ---- | -------------- | ---------- | ----------------- |
| RV32I | 32 | 32 | $2^{32}$ |
| RV64I | 64 | 32 | $2^{64}$ |
| RV32E | 32 | 16 | $2^{32}$ |
| RV128I | 128 | 32 | $2^{128}$ |

!!! commentary

    4 个 base ISA 被当作完全不同的 ISA 来对待，所以有个常见问题：

    `Q：为什么不设计一个统一的 ISA，即让 RV32I 是 RV64I 的子集？之前的一些 ISA(SPARC, MIPS) 就采用了这样的设计规则，使得可以在 64bit 的硬件上运行 32bit 的程序。`

    A：ISA 分开设计的优点是可以独立优化，不需要支持其他 ISA 的操作，缺点是为了在一个 ISA 上仿真另外一个 ISA 会导致硬件复杂化。实际上寻址模式和捕获非法指令的不同往往意味着即使某两个 ISA 是子集关系仍然需要进行某种模式切换，RISC-V 的 base ISA 之间的相似性可以降低支持多版本的开销。虽然理论上可以把 32bit 的 lib 和 64bit 的代码链接在一起，但因为程序调用和系统调用方式的不同实际中并不可行。

    RISC-V 提供了一个 misa 寄存器来控制在同一份电路上仿真不同的 ISA，而且 SPARC 和 MIPS 也放弃了支持直接在 64bit 系统上运行 32bit 程序。

### Memory

`RVWMO(RISC-V Weak Memory Ordering)` 模型。

### Base ISA Encoding

所有 base ISA 都按照 16bit 对齐，即其指令长度都是 16bit 的倍数。

使用术语 `IALIGN` 表示指令对齐约束，IALIGN 的取值只能是 16 或 32：base ISA 的 IALIGN 是 32,C ISA 和其他扩展 ISA 可以是 16。

使用术语 `ILEN` 表示某个实现支持的最大指令长度，它永远是 `IALIGN` 的整数倍，

Memory 系统既可以是大端模式，也可以是小端模式，但是指令存储一定是以 16bit 为单位的数据包的小端模式。

### Exceptions, Traps, Interrupts

+ `Exception` 表示指令执行中处理器本身出现异常情况而停止执行当前程序
+ `Interrupt` 表示外部异步事件导致处理器停止执行当前程序，转而去完成其他事情，完成后再继续之前的程序
+ `trap` 表示由 exception 或 interrput 导致的控制权转移

4 种不同的 trap：

| | Contained | Requested | Invisible | Fatal |
| --- | ----- | ---------- | --------- | ----- |
| Execution terminates ? | N | N | N | Y |
| Software is oblivious? | N | N | Y | Y |
| Handled by environment? | N | Y | Y | Y |

## RV32I Base ISA

一共有 40 条指令，查询 reference card 即可。

!!! note

    一些资料中会描述说 I 指令集包含 47 条指令，这里有点歧义。准确的说，Spec 中 I 子集只包 40 条指令，通常所说的 47 条指令是把另外两个必要的子集也包含在内：

    + `Zifencei` 子集：包含 1 条指令 `FENCE.I`
    + `Zicsr` 子集：包含 6 条 csr 相关的指令

### Register

分为两类：

+ 通用寄存器：一共有 32 个，XLEN=32，x0 为常数 0，还有个特殊的 register 即 `pc`
+ `CSR` 寄存器：control and state register，内部寄存器，专有的 12bit 地址编码空间

I 子集只涉及通用寄存器，CSR 寄存器在后面的 `Zicsr` 部分介绍。

### Format

主要有 4 种格式：

+ `R` (Register)
+ `I` (Immediate) 
+ `S` (Store)
+ `U` (Upper)

指令长度都是 32bit，按照 4Byte 对齐存储。

RISC-V 把 rs1, rs2, rd 的在不同指令中的位置都固定成一样，这样可以简化硬件译码逻辑。除了 CSR 指令中的 5bit 立即数，其他指令中的立即数都是按照有符号的方式扩展，并且放在指令可用空间的最左边 bit 位置，以降低硬件复杂度。特别地，所有立即数的符号位都在指令的第 31bit，这样可以加速符号扩展电路。

!!! commentary

    译码模块中识别 register 的标识符的逻辑通常都是关键路径，所以我们在设计指令格式的时候，不管是什么格式类型的指令，都把标识符放在固定位置，付出的代价则是指令中的立即数会随着指令类型变化。

    实际上，大部分立即数的位宽要么很小，要么就要占满 XLEN bit，我们选择了一种非对称的方式切分立即数（用两条指令来搬运一个立即数：第一条指令搬运低 12bit，第二条指令搬运剩余的 20bit），这样做的好处是可以增加常规指令 opcode 的编码空间。

    立即数都是符号为扩展的，因为我们没有发现 MIPS 中按 0 扩展能带来什么好处，这样做同时也能最大限度地保持 ISA 的简洁。

因为立即数的原因，所以有了另外两个变种格式：

+ `B` (Branch) 和 `S` 的唯一区别是 B 中的 12bit 立即数以 2 的倍数的方式用来编码分支的 offset，而且这 12bit 是精心设计过的，并不是简单的移位
+ `J` (Jump) 和 `U` 的唯一区别是 U 和 J 需要 shift 的 bit 位数不一样，同理，立即数的位置是精心设计过的，并不是简单填充

!!! commentary

    立即数的符号位扩展是最终要的操作之一，RISC-V 把所有立即数的符号位都放在第 31bit，好处是让符号位扩展和译码并行。

    虽然有些复杂的实现会给 branch 和 jump 指令计算分配独有的加法器，所以并不会收益于不同指令中的立即数位置固定，但是我们想降低最简实现的硬件成本。通过变换立即数的 bit 位置，而不是使用动态的硬件 mux，指令信号的 fanout 和 mux 数量大概减少为原来的一半。立即数混乱的编码带来的开销可以忽略不计。

### Integer Computational Instructions

计算指令只有两类：

+ `I-type`：register 和 immediate 相计算
+ `R-type`：register 和 register 相计算

两类都会有 rd 寄存器来保存结果，而且都不会产生算术异常。

!!! commentary

    我们并没有设计特殊的指令集来检测 overflow，因为可以用 branch 指令很廉价的实现。

    + 无符号数加法的 overflow 检查只需要在 add 指令后面加一条 branch 指令即可：

            #!text
            add t0, t1, t2
            bltu t0, t1, overflw

    + 有符号数加法，如果已知一个操作数的符号（I 类型加法），那么只需要在 add 后面加一条  branch 指令即可：

            #!text
            addi t0, t1, +imm
            blt t0, t1, overflow

    + 对于一般的有符号数 R 类型的加法，需要 3 条指令来检测求和结果是否比任何一个加数都小（除非一个操作数是负数）

            #!text
            add t0, t1, t2
            slti t3, t2, 0
            slt t4, t0, t1
            bne t3, t4, overflow

注意：

+ `SLTIU` 指令需要先对立即数进行符号位扩展，然后再当成无符号数来比较
+ `NOP` 是伪指令，以 `ADDI x0, x0, 0` 的方式实现

!!! commentary

    `AUIPC` 指令支持以“双指令序列”的方式访问当前 PC 的任意 offset 位置，可以用来做控制流的转移或者是数据访问。

    + 控制流转移： JAL + AUIPC
    + 数据访问： LOAD/STORD + AUIPC

    虽然当前 PC 值可以通过把立即数设置为 0 来实现，也可以通过 `JAL +4` 的方式实现，但是后者的问题在于可能会导致流水线停顿或者是污染 BTB。

!!! commentary

    一般 NOP 指令都用来处理地址边界问题以使得指令对齐，或者为指令修改预留空间。虽然 NOP 的实现方式有很多种，我们只定义了一种作为示范，给微架构层面的优化留有空间，同时也可以使得汇编代码的可读性更好。NOP 指令也可以用 HINT 指令来实现。

    选用 ADDI 来实现 NOP 的原因是，这样占用的资源最少（除非是在 decode 阶段把它优化掉了），只需要读一个 register，而且在超标量处理器中加法器是最常见的操作，AGU 可以像计算地址一样直接执行这条指令，其他的 register-register 指令（比如 ADD 或 logical 指令、shift 指令）都需要额外的硬件才能完成。

### Control Transfer Instructions

控制流相关的指令一共有两类，而且都没有 delay slot（延迟槽）：

+ 无条件跳转 jump
+ 有条件分支 branch

因为 `JAL` 指令属于 J-type，所以它包含的立即数的 [20:1] bit，所以可以跳转的范围是 [-1MB, +1MB] 内。标准的软件调用惯例是用 x1 作为返回地址，x5 作为备选的链接地址。

!!! commentary

    无条件 jump 指令都是使用 PC 的相对地址，以支持和地址不相关的代码。JALR 和 LUI 组合在一起可以访问 32bit 地址空间中的任一位置，首先 LUI 把目标地址的高 20bit 搬运到寄存器中，然后 JALR 把低 12bit 加上去就可以算出完整的 32bit 目标地址。同理，AUIPC 和 JALR 也可以跳转到相对于 PC 的任意 32bit 地址。

    需要注意的是，JALR 并不会像 branch 指令一样，把立即数当成是 2 的倍数，这样做的好处是可以避免立即数格式太多的问题。

    JALR 执行的时候，会把计算结果的的最低位清零，这样做的好处是可以稍微简化硬件设计，同时还可以空余出 1bit 空间来存储更多信息。虽然这么做可能会对地址错误检查有轻微的负面作用，但是错误的指令地址可以很快通过异常的方式发现。

    当 rs1=x0 时，JALR 可以用来实现单指令子程序，在 [-2KB, 2KB] 范围内跳转，可以实现 runtime lib 的快速调用。

RAS 预测是高性能 IFU 中的常见功能，但是前提是要能准确区分出函数调用和返回，协议规定了 JAL 和 JALR 所使用的寄存器序号可以用来辅助 RAS 预测：

+ 如果 JAL 的 rd=x1 或者是 rd=x5，那么就是函数调用，RAS 要 push
+ 如果 JALR 和 RAS 的行为可以查表

通过协议规定，compiler 和 core 配合就可以最大化地提高 RAS 的预测准确度。


!!! commentary

    有些 ISA 使用了特别的 bit 位来标识辅助 RAS，我们使用隐式的方式（约定寄存器号）来减少编码空间的占用。

所有的 branch 指令都是 B-type，所以它包含的立即数的 [12:1] bit，所以可以跳转的范围是 [-4KB, 4KB] 内。

协议规定软件要假设硬件是 BTFN 算法的方式，依次进行优化，这样可以提高低端 CPU 的预测性能。不同于其他 ISA，RISC-V 规定无条件跳转必须使用 JAL，而不能用 branch（条件设置为 true）。jump 指令要比 branch 的跳转范围大，而且不会污染 branch 预测表。

!!! commentary

    条件 branch 指令被设计成包含两个 register 的算数比较的方式（同 PA_RISC、Xtensa、MIPS R6），没有使用下面的方式：

    + 使用条件码 condition code（x86、ARM、SPARC、PowerPC）
    + 只使用一个 register 和 0 做比较（Alpha，MIPS）
    + 只有相等比较使用两个寄存器（MIPS）

    这样设计的主要原因是把比较和分支合并在一起，更加适合流水线，不需要使用额外的 condition code，也不需要使用寄存器保存中间结果，可以减少代码体积，降低 IFU 的带宽。付出的硬件代价也很小近似可以忽略。另外融合的指令可以在流水线的上游更早地观测到，更早地预测。

### Load and Store Instructions

RISC-V 中，端序是 byte 地址不变的。

!!! commentary

    在一个端序是 byte 地址不变的系统中，有下列特性：如果某个 1 byte 的数据被 store 在某种端序的 memory 的某个地址中，那么从那个地址中 load 1 byte 数据返回的数据也是那个值。

    + 小端系统：一个多 byte 数据，最低位的 byte 数据被存储在 memory 的低位地址中，剩余数据的地址按照顺序递增，load 指令会把低位地址的数据搬运到 register 的低位 byte 位置中
    + 大端系统：一个多 byte 数据，最高位的 byte 数据被存储在 memory 的最低地中中，剩余数据的地址按照顺序递减，load 指令会把高位地址的数据搬运到 register 的低位 byte 位置中

如果 load/store 的地址不对齐，那么可以用硬件来处理，也可以用软件来处理异常。

### Memory Ordering Instructions

RISC-V 使用存储器松散一致性模型，所以需要 FENCE 指令。没有定义的字段是为了以后更细精度的扩展而设置的保留位。为了保持前向兼容，硬件应该忽略这些 bit 位，软件应该将这些 bit 位设置为全 0。

!!! commentary

    我们选择了一个松散一致性模型以便让一个简单的微架构也能获得高性能，也方便未来进行扩展。将 I/O 和 memory 操作分离开来的好处是可以避免不必要的串行化。一个简单的微架构可以忽略 FENCE 中的前序和后序字段，把所有的 FENCE 指令都当成最严格的 FENCE 指令来执行。

## RV32E

RV32E 是专门为嵌入式 Emmbedded 设计的 ISA，目前还是 draft 状态，它和 RV32I 的唯一区别就是把 register 的数量减少到了 16 个。

!!! commentary

    实际上一开始是拒绝专门设计一个新的子 ISA 的，但是后来考虑到 32bit MCU 的需求，最终定义了这个子集，将来可能还会有 RV64E。

    我们发现在 RV32I 的小核中，高 16 个 register 大概占了除 memory 之外总面积的四分之一，所以去掉这 16 个 register 可以节省大约 25% 的面积和功耗。

    这个改变也对软件的调用惯例和 ABI 提出了要求。

RV32E 的 ISA 和 RV32I 完全一样，但是因为 register 只有 16 个，所有指令中 index 的字段可以释放出几 bit，未来的标准指令扩展都不会用到这些字段，所以可以给自定义扩展指令来使用。

## RV64I

RV64I 是 RV32I 的扩展。

`XLEN` 变成了 64，即 register 的宽带是 64bit。

RV64I 的大部分指令的操作数位宽都是 XLEN bit，有一些附加的指令来操作 32bit 的数，这些指令都在 opcode 后面加了 `W` 后缀来区分。这些 `*W` 指令会忽略掉高 32bit 数据，产生的结果也只保留 32bit。即 [63: XLEN-1] bit 的数据是一样的，结果扩展到 64bit 后保存在 register 中。

## RV128I

目前还是 draft 状态，定义这个子 ISA 的目的就是为了支持更大的地址空间。

!!! commentary

    目前暂时还不是很清楚我们什么时候需要比 64bit 更大的地址空间，世界上 Top500 的超级计算机拥有超过 1PB 的 DRAM，这需要超过 50bit 的地址线。一些仓储级的计算机已经包含了更大的 DRAM，而且固态硬盘和 interconnect 技术的发展可以能会产生更大地址空间的需求。万亿级别的系统研究需要 100PB 的空间，大概占用 57 根地址线。根据历史增长速度看，大概在 2030 年前就有可能超过 64bit 的范围。

    历史证明，无论何时只要出现地址不够用的情况，architect 们就会重复以前的争论，使用各种技术来扩充寻址范围，但是最终，128bit 的寻址方案将作为最简单、最佳解决方案而被采用。

RV128I 在 RV64I 的基础上定义，就如同 RV64I 在 RV32I 上定义一样。

## Zicsr

RISC-V 专门定义了一组 (control and status register, CSR) 寄存器来记录配置和运行状态，这些寄存器是内部寄存器，使用专有的 12bit 地址编码空间。

!!! commentary

    CSR 主要是在 Priviledge 架构中使用，但是一些 Unpriviledge 架构中也会用到一些，比如计数器和计时器，浮点状态等。

    因为计数器和计时器等不再被认为是 base ISA 中的必要成分，所以访问这些资源的指令 CSR 指令就独立出来自成一章。

只要程序中有指令会修改或者是受 CSR 影响，那么就会发生影式或者是显式的 CSR 访问。比如说，在某些修改或受 CSR 影响的指令执行完之后，后续修改 CSR 或受 CSR 影响的指令之前，会产生 CSR 访问。在具体指令执行之前，会有一个 CSR 读指令先读取 CSR 的状态，在指令执行完之后，会有一个 CSR 写指令更新相关的 CSR。

!!! commentary

    CSR 空间的模型和第二卷中定义的 Memory-Ordering PMAs 章节中定义的 weakly ordered memory-mapped I/O region 类似。