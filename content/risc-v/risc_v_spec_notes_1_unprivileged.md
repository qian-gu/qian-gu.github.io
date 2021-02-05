Title: RISC-V Spec 阅读笔记 #1 —— Unprivileged ISA
Date: 2020-11-17 21:55
Category: RISC-V
Tags: RISC-V, Spec
Slug: risc_v_spec_notes_1_unprivileged
Author: Qian Gu
Series: RISC-V Notes
Summary: Volume I: Unprivileged ISA 读书笔记
Status: draft

!!! note

    Unprivileged ISA 文档的版本号:20191213

## Introduction

RISC-V 的目标可以说非常宏大、也非常务实，可以用这几个关键词来概括：完全 open、可实现、通用、模块化、可扩展。RISC-V 在定义时尽可能地规避了具体的实现细节（虽然 ISA 中有些设计是出于实现考虑的），所以这个 ISA 应该当成各种不同实现方案的统一软件可见接口，而非某种特定微架构实现的专属。整个手册分为两部分：

+ Volume I: Unpriviledge ISA
+ Volume II: Priviledge ISA

在设计这些 ISA 时都遵循了尽量移除对特定微架构的依赖，这样在简化 ISA 同时也保证了实现时最大程度的灵活性。

!!! tip
    ISA 作为软件和硬件之间的接口，其地位非常重要。曾经有很多各种各样的 ISA，其中大部分都随着历史消亡了，只剩下个别占领了市场主流，并不断演进。但是目前大部分 ISA 被商业产权保护，普通人无法使用，而且因为要向后兼容而有历史包袱，在这样的背景下，RISC-V 最早起源于 UC Berkeley 的教学需求，逐渐发展壮大，如今在业界如火如荼。

    定义一个新的 ISA 并不是简单定义指令集就足够的，还需要大量的投入，比如文档、编译器工具链、测试套件、教学材料等等，即使这些都全做出来了别人也不一定会用，做出来简单，要想推动整个生态是件非常难的事情。看看 RISC-V 基金的董事会和赞助商，就会发现全是著名科技公司和大佬，也只有他们才能集整个产业届的力量推动新的 ISA 发展。

### Hardware Platform Terminology

| 术语                 |      含义                   |
| ------------------- | --------------------------- |
|  hardware platform  | RISC-V core + non-RISC-V core + accelerator + memory + I/O + interconnect |
|  core               | 包含独立的 IFU 的模块 |
|  coprocessor        | 附着在 RISC-V core 上，由 RISC-V 指令流控制，具有有限的自主控制权运行自己的扩展指令 |
|  accelerator        | 不可编程的固定函数单元 / 针对特定功能的可以自动运行的 core |

### Software Execution Environment and Harts

RISC-V 程序的行为依赖于它的执行环境，`EEI (Execution Environment Interface)` 定义了下面这些内容：

+ 程序的初始状态
+ Hart 的数量和类型
+ hart 支持的特权模式
+ memory/IO 的访问及特性
+ 所有合法指令的行为
+ 中断和异常的处理

EEI 的典型例子有 Linux 的 `ABI (Application Binary Interface)` 和 RISC-V 的 `SBI (Supervisor Binary Interface)`。

EEI 的实现方式有多种：

| 实现方式 | 含义 |
| ------- | ----- |
| Bare metal | hart 由硬件直接实现，指令可以访问所有的物理地址空间，硬件平台定义上电复位后的执行环境 |
| 操作系统     | 通过对处理器和 memory 的控制，不同用户级的 hart 复用有限的物理处理器线程 |
| 管理程序     | 对 guest 访问提供不同层级的执行环境 |
| 仿真器      | 在另一个硬件平台（如 x86）上模拟 RISC-V 的 hart，比如 Spike、QEMU、rv8 等 |

`Hart`：硬件线程，自动取指和执行所涉及的硬件资源的统称。（有些处理器中包含多个硬件线程，每个线程有自己独立的 RF 等上下文资源，不同线程共享同一份运算资源）

### ISA Overview

RISCV ISA 由必选的 Base Integer ISA 和其他可选 ISA 组成，完整的子集列表直接看 spec 即可。其中必选的 base interger ISA 和以前的 RISC 处理器的 ISA 非常相似，只是去掉了分支延迟槽和可选的变长编码，一共有 4 种形式，它们的区别在于 register 的位宽、register 的数量、寻址空间大小： 

| ISA | XLEN (register 位宽) | registe 数量 | 寻址空间范围 (Byte) |
| ---- | -------------- | ---------- | ----------------- |
| RV32I | 32 | 32 | $2^{32}$ |
| RV64I | 64 | 32 | $2^{64}$ |
| RV32E | 32 | 16 | $2^{32}$ |
| RV128I | 128 | 32 | $2^{128}$ |

!!! tip

    4 个 base ISA 被当作完全不同的 ISA 来对待，所以有个常见问题：

    Q：为什么不设计一个统一的 ISA，即让 RV32I 是 RV64I 的子集？一些早期 ISA(SPARC, MIPS) 就采用了这样的设计规则，使得可以在 64bit 的硬件上运行 32bit 的程序。

    A：ISA 分开设计的优点是可以针对某个子集独立优化，不需要为支持其他子集而消耗资源，缺点则是在一个 ISA 上仿真另外一个 ISA 会硬件会更复杂。实际上寻址模式和捕获非法指令的不同往往意味着即使某两个 ISA 是子集关系仍然需要两套电路以及某种模式切换，而且 RISC-V 的 base ISA 之间的相似性可以降低多版本的开销。虽然理论上可以把 32bit 的 lib 和 64bit 的代码链接在一起，但因为程序调用和系统调用接口的不同实际中并不可行。

    RISC-V 的特权架构中 misa 寄存器有个字段专门用来控制在同一份电路上如何模拟不同的 base ISA，而且可以看到 SPARC 和 MIPS 也放弃了对在 64bit 系统上直接运行 32bit 程序的支持。

### Memory

+ memory 地址是循环的，最大的地址溢出后自动回到 0 地址，硬件计算地址时会自动忽略溢出
+ 一般地址空间被分成了不同段，访问不允许的地址应该报 exception
+ RISC-V 默认使用 `RVWMO(RISC-V Weak Memory Ordering)` 作为内存一致性模型

### Base ISA Encoding

RISC-V 指令可以是变长的，但是所有 base ISA 都按照 16bit 对齐，即其指令长度都是 16bit 的倍数。

使用术语 `IALIGN` 表示指令对齐约束，IALIGN 的取值只能是 16 或 32：base ISA 的 IALIGN 是 32，C 子集和其他扩展 ISA 可以是 16。使用术语 `ILEN` 表示某个实现支持的最大指令长度，它永远是 `IALIGN` 的整数倍，具体的指令编码格式略。

Memory 系统既可以是大端模式，也可以是小端模式，但是指令存储一定是以 16bit 为单位的数据包的小端模式。

### Exceptions, Traps, Interrupts

+ `Exception` 表示指令执行中处理器本身出现异常情况而停止执行当前程序
+ `Interrupt` 表示外部异步事件导致处理器停止执行当前程序，转而去完成其他事情，完成后再继续之前的程序
+ `trap` 表示由 exception 或 interrput 导致的控制权转移到 trap handler

4 种不同的 trap：

|     | Contained | Requested | Invisible | Fatal |
| --- | --------- | --------- | --------- | ----- |
| Execution terminates ? | N | N | N | Y |
| Software is oblivious? | N | N | Y | Y |
| Handled by environment? | N | Y | Y | Y |

## RV32I Base ISA

一共有 40 条指令，查询 reference card 即可。

!!! tip

    一些资料中会描述说 I 指令集包含 47 条指令，这里有点歧义。以前的版本中 I 确实有 47 条指令，但是在最新的版本中，I 子集只包 40 条指令，通常所说的 47 条指令是把另外两个必要的子集也包含在内：

    + `Zifencei` 子集：包含 1 条指令 `FENCE.I`
    + `Zicsr` 子集：包含 6 条 csr 相关的指令

    在一些实现中，可能会把 ECALL/EBREAK 当成一条永远 trap 的硬件指令来处理，且把 FENCE 指令当成 NOP 来处理，这时 I 子集的指令条数就缩水到了 38 条。

    除了 A 子集需要特殊的硬件来支持原子性操作之外，RV32I 基本上可以模拟任何其他子集。

### Programmers' Model

程序员可见的寄存器分为两类：

+ 通用寄存器：一共有 32 个，XLEN=32，其中 x0 为常数 0，还有个特殊的 register 即 `pc`
+ `CSR` 寄存器：control and state register，内部寄存器，专有的 12bit 地址编码空间

I 子集只涉及通用寄存器，CSR 寄存器在后面的 `Zicsr` 部分介绍。

!!! tip
    在一个 ISA 中寄存器的个数对代码体积、性能、功耗有巨大的影响。到底应该设计多少个 register 也是有讲究的，有种意见是对于 I 子集只用 16bit 的指令编码 16 个 register 就已经足够了，但是如果指令中包含 3 个寄存器地址，则光地址就需要 12bit，只剩了 4bit 来编码 opcode，这基本上是不可能的。而如果指令只包含 2 个地址，那么实现相同功能就需要更多的指令，降低效率。为了简化硬件设计也应该避免 24bit 这种中间长度的指令格式，所以最终选择了 32bit 的指令来编码 32 个寄存器。寄存器数量多一些对性能提升也有帮助，比如 loop unrolling, software pipelining, cache tiling。

### Format

主要有 4 种格式：

+ `R` (Register)
+ `I` (Immediate) 
+ `S` (Store)
+ `U` (Upper)

指令长度都是 32bit，按照 4Byte 对齐存储。RISC-V 的指令格式也是精心设计过的，目的就是为了简化硬件的译码电路：

+ 不同指令中的 rs1, rs2, rd 都在固定位置
+ 所有指令中的立即数都是按照有符号的方式扩展（除了 CSR 指令中的 5bit 立即数）
+ 所有立即数都放在指令可用空间的最左边 bit 位置
+ 所有立即数的符号位都在指令的固定位置，第 31bit

!!! tip

    译码模块中识别 register 的标识符的逻辑通常都是关键路径，所以 RISC-V 在设计指令格式的时候，不管是什么格式类型的指令，都把标识符放在固定位置，付出的代价则是指令中立即数的位置会随着指令类型变化。

    实际上，大部分立即数的位宽要么很小，要么就要占满 XLEN bit，RISC-V 选择了一种非对称的方式切分立即数（用两条指令来搬运一个立即数：第一条指令搬运低 12bit，第二条指令搬运剩余的 20bit），这样做的好处是可以增加常规指令 opcode 的编码空间。

    所有立即数都是符号为扩展的，因为我们没有发现 MIPS 中按 0 扩展能带来什么好处，这样做同时也能最大限度地保持 ISA 的简洁。

因为立即数的原因，所以有了另外两个变种格式：

+ `B` (Branch) 类型：它和 `S` 一样都用 12bit 来编码立即数，唯一区别是 B 中的立即数是 S 中立即数的 2 倍，也就是说 S 中的 12bit 表示 imm[11:0]，而 B 中的 12bit 表示 imm[12:1]，而且这 12bit 在指令中的位置是精心设计过的，并不是简单移位
+ `J` (Jump) 类型：它和 `U` 的关系也是类似的，唯一区别是 U 和 J 需要 shift 的 bit 位数不一样，同理，立即数的位置是精心设计过的，并不是简单填充

!!! tip

    立即数的符号位扩展是其关键路径之一，RISC-V 把所有立即数的符号位都放在第 31bit，好处是让符号位扩展和译码并行。

    虽然有些复杂的实现会给 branch 和 jump 指令计算分配专有加法器，所以并不会收益于不同指令中的立即数位置固定的设计，但是我们想降低最简实现的硬件成本。通过变换立即数的 bit 位置，而不是使用动态的硬件 mux，指令信号的 fanout 和 mux 数量大概减少为原来的一半。而这种混乱的立即数编码带来的开销可以忽略不计。

I 子集一共有 40 条指令，大概可以分成 4 类：

|   类型   |  数量  |
| ------- | ----- |
| 计算指令 | 21 |
| 控制转移指令 | 8 |
| Load/Store 指令 | 8 |
| Memory 顺序指令 | 1 |
| 系统调用和断点 | 2 |

### Integer Computational Instructions

计算指令只有两类：

+ `I-type`：register 和 immediate 相计算
+ `R-type`：register 和 register 相计算

两类都会有 rd 寄存器来保存结果，而且都不会产生算术异常。

!!! tip

    我们并没有设计特殊的指令集来检测 overflow，因为可以用 branch 指令很廉价的实现这个功能。

    + 无符号数加法的 overflow 检查只需要在 add 指令后面加一条 branch 指令即可：

            #!text
            add t0, t1, t2
            bltu t0, t1, overflw

    + 有符号数加法，如果已知一个操作数的符号（I 类型加法），那么只需要在 add 后面加一条 branch 指令即可：

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

!!! tip

    `AUIPC` 指令支持以“双指令序列”的方式访问当前 PC 的任意 offset 位置，可以用来做控制流的转移或者是数据访问，可以访问想对于当前 PC 值的任意 32-bit 地址。

    + 控制流转移： JAL + AUIPC
    + 数据访问： LOAD/STORD + AUIPC

    虽然当前 PC 值可以通过把立即数设置为 0 来实现，也可以通过 `JAL +4` 的方式实现，但是后者的问题在于可能会导致流水线停顿或者是污染 BTB。

!!! tip

    一般 NOP 指令都用来处理地址边界问题以使得指令对齐，或者为指令修改预留空间。虽然 NOP 的实现方式有很多种，我们只定义了一种作为示范，给微架构层面的优化留有空间，同时也可以使得汇编代码的可读性更好。NOP 指令也可以用 HINT 指令来实现。

    选用 ADDI 来实现 NOP 的原因是，这样占用的资源最少（除非是在 decode 阶段把它优化掉了），只需要读一个 register，而且在超标量处理器中加法器是最常见的操作，AGU 可以像计算地址一样直接执行这条指令，其他的 register-register 指令（比如 ADD 或 logical 指令、shift 指令）都需要额外的硬件才能完成。

### Control Transfer Instructions

控制流相关的指令一共有两类，而且都没有 delay slot（延迟槽），如果跳转地址没有对齐，则会产生一个不对齐异常。

+ 无条件跳转 jump
+ 有条件分支 branch

因为 `JAL` 指令属于 J-type，所以它包含的立即数的 [20:1] bit，所以可以跳转的范围是 [-1MB, +1MB] 内。JAL 会把 (pc+4) 这值存到 rd 中，一般标准的软件调用惯例是 rd = x1 作为返回地址，x5 作为 alternate link register。

!!! tip
    这个 alternate link register 可以在保留常规的返回地址寄存器 rd 的同时，可以支持调用一些代码量非常小的例程，之所以选择 x5 是因为在标准调用中它是一个临时寄存器，而且和 x1 的编码只有 1bit 不同。

!!! tip
    无条件 jump 指令都是使用 PC 的相对地址，以支持和地址不相关的代码。JALR 和 LUI 组合在一起可以访问 32bit 地址空间中的任一位置，首先 LUI 把目标地址的高 20bit 搬运到寄存器中，然后 JALR 把低 12bit 加上去就可以算出完整的 32bit 目标地址。同理，AUIPC 和 JALR 也可以跳转到相对于 PC 的任意 32bit 地址。

    需要注意的是，JALR 不会像 branch 指令一样，从 imm[1] 开始编码（2 的倍数），这样做的好处是可以避免硬件中立即数格式太多的问题。

    JALR 执行的时候，会把计算结果的的最低位清零，这样做的好处是可以稍微简化硬件设计，同时还可以空余出 1bit 空间来存储更多信息。虽然这么做就需要对地址进行错误检查，所以有些轻微的性能损失，但是错误的指令地址可以很快触发异常。

    当 rs1=x0 时，JALR 可以用来实现单指令子程序，在 [-2KB, 2KB] 范围内跳转，可以实现 runtime lib 的快速调用。

RAS 预测是高性能 IFU 中的常见功能，但是前提是要能准确区分出函数调用和返回，协议规定了 JAL 和 JALR 所使用的寄存器序号可以用来辅助 RAS 预测：

+ 如果 JAL 的 rd=x1 或者是 rd=x5，那么就是函数调用，要把 rd 寄存器的值 push 进 RAS
+ JALR 和 RAS 的行为可以查表

遵守协议的规定，compiler 和 core 配合就可以最大化地提高 RAS 的预测准确度。

!!! tip

    有些 ISA 使用了特别的 bit 位来标识辅助 RAS，我们使用隐式的方式（约定寄存器号）来减少对编码空间的占用。

所有的 branch 指令都是 B-type，所以它编码了立即数的 [12:1] bit，所以可以跳转的范围是 [-4KB, 4KB] 之间。

协议规定软件要假设硬件是 BTFN 算法的方式，依次进行优化，这样可以提高低端 CPU 的预测性能。不同于其他 ISA，RISC-V 规定无条件跳转必须使用 JAL(rd=x0)，而不能用 branch（条件设置为 true）。因为 jump 指令要比 branch 的跳转范围大，而且不会污染条件 branch 的预测表。

!!! tip

    条件 branch 指令被设计成包含两个 register 的算数比较的方式（同 PA_RISC、Xtensa、MIPS R6），没有使用下面的方式：

    + 使用条件码 condition code（x86、ARM、SPARC、PowerPC）
    + 只使用一个 register 和 0 做比较（Alpha，MIPS）
    + 只有相等比较使用两个寄存器（MIPS）

    这样设计的主要原因是把比较和分支合并在一起，更加适合常规流水线，不需要使用额外的 condition code，也不需要使用寄存器保存中间结果，可以减少代码体积，降低 IFU 的带宽，还可以在 IF 阶段就被提前检测到，即使是和 0 比较这种设计，也会引入不可忽略的 latency。这样设计付出的硬件代价也很小近似可以忽略。另外融合的指令可以在流水线的上游更早地观测到，更早地预测。

    曾经考虑过在指令中加入静态分支提示，但最终并没有加，虽然静态分支提示可以缓解动态预测器的压力，但是需要占用更多的编码空间，还需要软件做 profiling 才能获得最好的结果，而一旦 profiling 和实际不一致，性能就很差。

    没有包含类似 ARM 条件码的原因是：条件码需要占用指令的额外 bit，需要额外的指令来设置/清除，增加了硬件复杂度，而和它一起配合使用的静态预测的效果可能并不好。

### Load and Store Instructions

RISC-V 是一个 load-store 体系结构，即只有 load/store 才可以访问 memory，计算指令只能和寄存器打交道，而且 RISC-V 的端序是 byte 地址不变的。

!!! warning
    + 如果 load 指令的 rd 是 x0，即使读回来的数据被丢弃了，也必须报一个任意类型的 exception

在一个端序是 byte 地址不变的系统中，有下列特性：如果某个 1 byte 的数据被 store 在某种端序的 memory 的某个地址中，那么从那个地址中 load 1 byte 数据返回的数据也是那个值。

+ 小端系统：一个多 byte 数据，LSB 被存储在 memory 的低位地址，剩余数据的地址按照顺序递增，load 指令会把低位地址的数据搬运到 register 的 LSB 中
+ 大端系统：一个多 byte 数据，MSB 被存储在 memory 的低位地中，剩余数据的地址按照顺序递减，load 指令会把高位地址的数据搬运到 register 的 LSB 中

RV32I 的地址空间是 32bit，按照 byte 地址访问，由 EEI 规定合法的地址段。无论端序如何，如果访问地址是天然对齐的，那么就不会产生任何异常，如果访问地址不是天然对齐的，那么具体行为取决于 EEI。EEI 可以允许非对齐访问，由硬件或者软件处理，也可以不允许非对齐访问，直接抛出异常。

!!! tip
    非对齐访问对于移植旧代码、使用 packed-SIMD 扩展的应用程序、处理外部打包的数据结构时很有用。之所以通过 load/store 来允许 EEI 自主选择非对其访问的处理方式，原因就是想简化硬件设计。

    有一种备选方案：在 base ISA 中不允许非对齐访问，额外再设计一个 ISA 来支持非对齐访问，比如某些特殊指令或者是硬件特殊的寻址模式。这个方案的问题在于：

    + 特殊指令使用难度大，导致 ISA 复杂化
    + 要么处理器添加了额外状态（CSR），要么导致现有 CSR 的访问复杂化
    + 基于 for 循环的 packd-SIMD 程序可能要根据数据对齐模式修改多个版本的代码，使得代码生成复杂化，产生额外开销
    + 新的硬件寻址模式必然要消耗大量的指令编码空间，而且也要消耗一下硬件资源来实现

即使实现了非对齐访问，在某些实现中可能性能很差；而且硬件处理非对齐访问时可能会将其拆分成多个子指令来处理，此时需要额外的同步机制来保证访问的原子性。

!!! tip
    标准中非对齐访问的原子性不是必须的，这样 EEI 就可以自由选择是用不可见的 machine trap 还是软件 handler 来处理非对齐访问。如果硬件支持非对齐访问，那么软件只需要直接用简单的 load/store 即可，发生非对齐访问时，硬件会自动优化。

### Memory Ordering Instructions

RISC-V 支持在一个单一的用户地址空间内运行多个 hart，每个 hart 都有自己的 pc 和 register，执行自己的指令流。而由 EEI 来完成 hart 的创建和管理。不同 hart 之间可以通过共享存储器来实现通信和同步，又因为 RISC-V 使用存储器松散一致性模型 `RVWMO`，所以需要 FENCE 指令来定义不同 hart 之间的指令执行顺序。从原则上讲，FENCI 之后的指令观测不到 FENCE 之前的指令行为，即 FENCI 像一道屏障一样，隔断了前后的指令流。

RISC-V 把数据存储器访问分为了 4 类：

+ I：设备读 device-input
+ O：设备写 device-output
+ R：存储器读 device-read
+ W：存储器写 device-write

配合前后的概念，所以可以实现很多中组合，达到非常精细的控制。FENCI 中没有定义的字段是为了以后更细精度的扩展而设置的保留位。为了保持前向兼容，硬件应该忽略这些 bit 位，同时软件应该将这些 bit 位设置为全 0。

!!! tip

    我们选择松散一致性模型的目的是让一个简单的微架构能获得高性能的同时也方便未来进行扩展。将 I/O 和 memory 操作分离开来的好处是可以避免不必要的串行化。一个简单的微架构可以忽略 FENCE 中的前序和后序字段，保守地把所有的 FENCE 指令都当成最严格的 FENCE 指令来执行即可。

### Environment Call and Breakpoints

系统指令一般是在特权模式使用，全部是 I 类型的指令。大概可以分为两类：

+ 自动 read-modify-write CSR 的指令
+ 其他特权指令

这里只描述非特权指令，只有两条且都向 EEI 会出发一条精确的服务请求。

+ `ECALL` 用来向 EEI 发送服务请求，请求的参数则一般放在寄存器文件中
+ `EBREAK` 用来把控制权转移给 debugger

!!! tip
    系统指令经过精心设计，可以在简单实现中用软件 trap 实现，而一些高端实现可能直接用硬件实现该指令。

### HINT Instructions

HINT 指令一般用来给微架构传达性能提示。RV32I 给 HINT 预留了大量的编码空间，且全部用 rd = x0 的计算指令来表示。所以 HINT 和 NOP 类似，只会导致 pc 向前移动以及改变性能计数器，除此之外不会改变硬件架构中任何可见的状态。实现中直接把 HINT 忽略都是符合标准的。

!!! tip
    HINT 这所以设计成这样，是方便硬件实现。简单实现中既可以把 HINT 当成一条恰好并不会产生任何影响的指令来走完所有 pipeline stage，也可以直接把它丢弃。

    虽然 HINT 编码空间很大，而且划分了 standard 空间和 custom 空间，但是目前还没有定义好 standard HINT。

## Zifencei

这个子集只包含一条指令 `FENCE.I`，它可以实现对同一个 hart 的 instruction memory 的写指令和取指之间的显式的同步控制，目前这是唯一一个保证 hart 的 store 和 fetch 之间可见性的标准机制。

这条指令是用来同步一个 hart 的 data 和 instruction 之间的关系，如果没有这条指令，RISC-V 就无法保证后续的取值操作能观测到前序的 store 结果。因为 FENCE.I 只用来处理单个 hart 内部的关系，所以如果有多个 hart，为了保证某个 hart 的 store 结果可以被其他 hart 观测到，应该在 FENCE.I 之前先调用一条 FENCE 指令。

!!! tip
    为了支持各种不同的实现，FENCE.I 指令做过精心的设计。简单实现可以直接 flush 流水线，清空 I-cache 即可。复杂一些的实现可能会有更高级的操作。

    FENCI.I 之前是 I 子集的一部分，但是因为下面两个原因，从 I 子集中挪了出来，不再是必须实现的指令了。

    + 在某些系统中，实现 FENCE.I 的代价很大。比如有些设计中 I-cache 和 D-cache 都是 incoherent 形式时，一旦遇到 FENCE.I 指令，就必须清空两个 cache。如果在共享 cache / memory 之前有多级独立的 I/D cache，这个问题会更加严重。
    + 在类 Unix 系统中，这条指令并没有强大到足以在 user level 使用。因为 FENCE.I 只能处理 hart 内部的同步，但是 OS 可能会在遇到 FENCE.I 时重新调度 user hart，所以现在 Linux ABI 都是要求产生一个系统调用来保证取指的 coherent。

## RV32E

TODO

RV32E 是专门为嵌入式 Emmbedded 设计的 ISA，目前还是 draft 状态，它和 RV32I 的唯一区别就是把 register 的数量减少到了 16 个。

!!! tip

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

!!! tip

    目前暂时还不是很清楚我们什么时候需要比 64bit 更大的地址空间，世界上 Top500 的超级计算机拥有超过 1PB 的 DRAM，这需要超过 50bit 的地址线。一些仓储级的计算机已经包含了更大的 DRAM，而且固态硬盘和 interconnect 技术的发展可以能会产生更大地址空间的需求。万亿级别的系统研究需要 100PB 的空间，大概占用 57 根地址线。根据历史增长速度看，大概在 2030 年前就有可能超过 64bit 的范围。

    历史证明，无论何时只要出现地址不够用的情况，architect 们就会重复以前的争论，使用各种技术来扩充寻址范围，但是最终，128bit 的寻址方案将作为最简单、最佳解决方案而被采用。

RV128I 在 RV64I 的基础上定义，就如同 RV64I 在 RV32I 上定义一样。

## Zicsr

RISC-V 专门定义了一组 (control and status register, CSR) 寄存器来记录配置和运行状态，这些寄存器是内部寄存器，使用专有的 12bit 地址编码空间。

!!! tip

    CSR 主要是在 Priviledge 架构中使用，但是一些 Unpriviledge 架构中也会用到一些，比如计数器和计时器，浮点状态等。

    因为计数器和计时器等不再被认为是 base ISA 中的必要成分，所以访问这些资源的指令 CSR 指令就独立出来自成一章。

只要程序中有指令会修改或者是受 CSR 影响，那么就会发生影式或者是显式的 CSR 访问。比如说，在某些修改或受 CSR 影响的指令执行完之后，后续修改 CSR 或受 CSR 影响的指令之前，会产生 CSR 访问。在具体指令执行之前，会有一个 CSR 读指令先读取 CSR 的状态，在指令执行完之后，会有一个 CSR 写指令更新相关的 CSR。

!!! tip

    CSR 空间的模型和第二卷中定义的 Memory-Ordering PMAs 章节中定义的 weakly ordered memory-mapped I/O region 类似。