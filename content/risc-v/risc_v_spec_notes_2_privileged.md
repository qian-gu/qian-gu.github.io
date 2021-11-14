Title: RISC-V Spec 阅读笔记 #2 —— Privileged ISA
Date: 2021-03-25 17:29
Category: RISC-V
Tags: RISC-V, Spec
Slug: risc_v_spec_notes_2_privileged
Author: Qian Gu
Series: RISC-V Notes
Summary: Volume II: Privileged ISA 读书笔记
Status: draft

!!! note

    Privileged ISA 文档的版本号:20190608-Priv-MSU-Ratified

## Introduction

Unprivileged 的补集，包含了运行操作系统和支持外设所需要的特权指令、额外功能。

### Software Stack Terminology

| 术语     |      含义                                                                                |
| --------| -----------------------------------------------------------------------------------------|
|  `ABI`  | Application Binary Interface, ABI = user-level ISA + ABI calls to AEE                    |
|  `SBI`  | Supervisor Binary Interface, SBI = user-level + supervisor-level ISA + SBI calls to SEE  |
|  `HBI`  | Hypervisor Binary Interface, HBI = user-level ISA + HBI calls to HEE                     |
|  `AEE`  | Application Execution Environment                                                        |
|  `HEE`  | Hypervisor Execution Environment                                                         |

观察 spec 中的示意图，可以发现整个 stack 的结构本质上就是不断套娃的过程：

+ 最简单是“裸机系统”

    ABI 作为中间抽象借口，隐藏了底层 AEE 的实现细节，对上面的 Application 提供了一个标准抽象借口，这样上层的 Application 就不需要再关心底层实现，这样 AEE 的实现可以更灵活，可以直接用 RISC-V 硬件实现，也可以是一个运行在其他架构机器上的模拟器。

+ 套第一层娃，支持单操作系统

    在 ABI 和 AEE 之间插入一层 OS，Application 和 OS 之间通过 ABI 交互，OS 和 SEE 之间通过 SBI 交互。同理，SEE 的实现也可以是真实的硬件，也可以是 hypervisor 提供的虚拟机。

+ 套第二层娃，虚拟机支持多操作系统

    在 OS 和 SEE 之间再插入新的一层 hypervisor，每个 OS 通过 SBI 和 hypervisor 交互，hypervisor 通过 HBI 和底层的 HEE 交互。

整个 stack 的核心思想可以总结为：**通过抽象的 Interface 对上层提供统一标准借口，隔离底层细节。**

RISC-V 的硬件不仅要实现 Privileged ISA，还要包含一些其他功能才能完整支持各种执行环境（AEE、SEE、HEE）。

!!! tip
    大部分的 supervisor-level ISA 在定义的时候，都没有把 SBI 从 execution environment 或者是硬件平台中分离出来，这样会导致虚拟化和开发新硬件平台时变得更复杂。

    目前 RISC-V 的 ABI、SBI、HBI 都还在定义中。

### Privilege Levels

| 级别   | 编码  |  名字            |  缩写  |
| ------|------|----------------- | ------|
|  0    |  00  | User/Application |  `U`  |
|  1    |  01  | Supervisor       |  `S`  |
|  2    |  10  | _Reserved_       |       |
|  3    |  11  | Machine          |  `M`  |

一共定义了 3 个特权层次，其中 M 是强制要求所有实现都必须支持的，M 的层次最高，它可以不受限制地访问底层的完整硬件资源，一般最简实现只支持 M 即可。U 模式是为了支持传统的 Application，S 模式则是为了支持 OS。

每个 level 都会有一组核心 Privileged ISA，再附加一些可选的扩展指令和变种指令。任何一个实现可以根据资源和目标折中选择支持 3 种 level 的组合。这些 level 是通过 CSR 来定义的，任何一个 hart 任何时候必然处于 3 种 level 中的某一种。

允许的组合：

| 级别数量 | 支持的模式 | 用途                    |
| ------- | -------- | ----------------------- |
| 1       | M        | 简单嵌入式系统            |
| 2       | M, U     | 带安全功能的嵌入式系统     |
| 3       | M, S, U  | 运行 Unix-like 的操作系统 |

### Debug Mode

Debug 可以看做是一个比 M 模式级别更高的特权模式，可能会有一些专用的 CSR 和地址空间。RISC-V 的 debug 模式定义在另外一个标准文档中。

## Control and Status Registers (CSRs)

RISC-V 中的 opcode = `SYSTEM` 的字段用来编码特权指令，这些指令可以分为两类：

+ `zicsr` 子集中定义的 atomically read-modify-write CSR 的指令
+ privileged 中定义的其他指令

除了 Unprivileged ISA 中描述的 CSR 之外，一个实现还可以包含一些其他 CSR，这些 CSR 在某些特权级别下可以通过 Zicsr 中的指令进行访问。因为特权分了等级，而 CSR 一般和特权等级是一一对应的，所以 CSR 也可以划分等级，可以被同级或更高级别的特权指令访问。

### Address Mapping Conventions

CSR 的编址使用独立的 12bit 空间，所以理论上最多可以编码 4096 个 CSR。一般的惯例是，最高的 4bit 用来编码 CSR 的读写属性，

+ `csr[11:10]` 表示 CSR 的读写属性
+ `csr[9:8]` 表示可以访问该 CSR 的最低特权等级

完整的地址映射区间查 spec 即可。

!!! warning
    出现下列情况，都会抛出一个非法指令的异常：

    + 访问一个不存在的 CSR
    + 访问的特权等级不够高
    + 对一个 RO 类型的 CSR 进行写操作
    + M 模式下访问 debug CSR 地址段的 CSR

    一个 R/W 类型的 CSR 的某些字段可能是 RO 类型，对这些字段的写操作应该被忽略掉。

所有的 CSR 可以分类两类：

+ user-level CSR：包括 timer、counter、FP CSR 和 N 子集添加的 CSR
+ Privileged CSR：剩余的 CSR

### Field Specifications

| 类型     |      含义    |
| --------| ------------ |
| `WPRI` Reserved Write Preserve, Read Ignore | 某些保留的 RW 字段，写入其他字段时保留本字段的原值，读出时软件应该忽略返回值 |
| `WLRL` Write/Read only Legal | 某些 RW 字段只有部分取值合法，软件不能写非法值，只有写入合法值后才能假设读回值合法 |
| `WARL` Write Any, Read Legel | 某些 RW 字段只有部分取值合法，但是允许写入任何值，读出时返回合法值     |

+ 为了保持前向兼容，不提供 WPRI 字段的实现时应该把这些字段 tie 0
+ 给 WLRL 字段写入非法值，实现可以自行决定是否抛出非法指令异常，当写入非法值后，读出值可以是任意值，但是必须保持确定性
+ 给 WARL 字段写入非法值，实现不应该抛出异常，但是写入非法值后，必须保持读出值的确定性

## Machine-Level ISA

M-mode 的特权等级最高，而且是唯一强制要求实现模式，它用于访问底层硬件，是上电复位后进入的第一个模式。M-mode 包含一个可扩展的核心 ISA，具体实现可以根据支持的特权等级和自身的硬件特性来扩展它。

### Machine-Level CSRs

略。

### Machine-Mode Privileged Instructions

一共 6 条，可以分成 3 类：

| 类型      | 指令                    |
| --------- | ---------------------- |
| 系统调用   | `ECALL`, `EBREAK`      |
| Trap 返回  | `MRET`, `SRET`, `URET` |
| WFI       | `WFI`                  |

### Reset

一旦复位，要满足下面要求，除此之外的状态不做要求。

+ hart 必须处于 M-mode，
+ `mstatus` 的 `MIE` 和 `MPRV` 字段要复位成 0
+ `misa` 字段要复位到支持的最大子集和最宽的 `MXLEN`
+ `pc` 要复位到实现预先定义好的 reset vector
+ `mcause` 要保存导致复位的原因
+ PMP 的 `A` 和 `L` 字段设置为 0

### NMI

Non-Maskable Interrupts 的作用是发生硬件错误时，不管中断使能是否打开，直接跳转到预先定义好的 NMI vector，在 M-mode 下运行。`mepc` 保存发生 NMI 的下一条指令；`mcause` 保存导致 NMI 的原因，具体值由实现自定义，但是 0 表示 unknown，所以如果实现不关心 NMI 的原因，那么直接保存 0 即可。

### PMA

一个完整系统中的地址空间包含了各种各样的地址段，有些是真实的 memory 域，有些是 memory-mapped 的 control register，还有些是空洞段。有些 memory 域不支持读/写/执行，有些不支持 subword/sublock 的访问，有些不支持原子性操作，有些不支持 cache 一致性协议或是 memory 模型不一样。RISC-V 系统中，对这些属性有一个专门的术语 `Physical Memory Attributes (PMAs)`。

PMA 是硬件的固有属性，所以在系统运行时很少变化。大部分系统都要求硬件动态地检查一些 PMA，某些架构是通过 TLB 来通知 pipeline 这些 PMA 信息，但是这个方法有很多缺点。RISC-V 则把 PMA 的标准独立出来，并且用一个独立的硬件 PMA checker 来检查 PMA：

+ 大部分情况下，一些属性是在芯片设计时就已经固定了的，所以可以直接在 checker 中以硬连线的方式实现
+ 另外 runtime 时可配置的属性，则可以通过一些和平台相关的、memory 映射的 control register 来实现（比如片上 SRAM 可以动态地划分为 cacheable/uncacheable 区域）

为了帮助 debubg，协议强烈建议，只要有可能，就应该精确地捕获导致 PMA 检查失败的物理地址访问。为了正确地访问设备或者是控制其他硬件单元（比如 DMA）去访问 memory，PMA 对软件来说必须是可读的。

+ 对于一个地址段来说，最重要的属性就是它映射的是 main memory，还是 I/O 设备，还是空地址段。
+ 另外一个属性是访问类型：访问的位宽以及每种位宽下是否支持非对齐访问
+ 还需要描述该地址段是否支持原子指令，main memory 必须支持所有的原子指令，I/O 域可能只这次部分原子操作
+ main memory 只能是 RVWMO 或者是 RVTSO 模型中的一种；I/O 域则可以定义多个 channel 来实现多种访问顺序
+ 地址段的 cacheability 属性对软件是不可见的，一些平台支持可配置的 cacheability
+ main memory 是 idempotency（执行多次和一次效果一样）；I/O 域的 read 是 idempotent 的，而 write 不是

### PMP

`Physical Memory Protection (PMP)` 可以保证一个 hart 对某个地址段访问的安全性，PMP 配置值的检查过程是在 PMA checker 中进行的。虽然 PMP 的访问粒度是和平台相关的，而且平台中不同地址段的粒度也会变化，但是标准的 PMP 编码支持的最小段大小为 4 Byte。

!!! tip
    不同平台对 PMP 的需求是不同的，有些平台还会提供其他的 PMP 指令来增强/代替标准中描述的方案。

RISC-V 最多支持 16 个 PMP entries，每个 entry 由一个 8bit 的配置寄存器和一个 MXLEN 的地址寄存器定义。只要实现了任何一个 PMP entry，那么就要实现所有的 PMP CSRs，这些 CSR 的属性是 WARL，所以可以在硬件上直接 tie-0，而且只能在 M-mode 层级访问。

为了最小化上下文切换的代价，PMP 的配置寄存器是按照小端模式密集存储在一起的。

PMP 机制主要是为了实现基于 page 技术的 Virtual-Memory 系统。

## Supervisor-Level ISA

TODO