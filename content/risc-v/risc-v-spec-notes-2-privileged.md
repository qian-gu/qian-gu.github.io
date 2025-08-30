Title: RISC-V Spec 阅读笔记 #2 —— Privileged ISA
Date: 2021-03-25 17:29
Category: RISC-V
Tags: RISC-V, Spec
Slug: risc-v-spec-notes-2-privileged
Author: Qian Gu
Series: RISC-V Notes
Summary: Volume II: Privileged ISA 读书笔记

[TOC]

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
|  2    |  10  | -Reserved-       |       |
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

RISC-V 中的 opcode `SYSTEM` 用来编码所有的特权指令，这些指令可以分为两类：

+ `zicsr` 子集中定义的 atomically read-modify-write CSR 的指令(即 CSR 指令)
+ 其他 privileged 指令

除了 Unprivileged ISA 中描述的 CSR 之外，implementation 还可以包含一些其他 CSR，这些 CSR 在某些特权级别下可以通过 `Zicsr` 中的指令进行访问。虽然 CSR 和特权指令都绑定了某个特权等级，但是也可以被更高等级访问。

### Address Mapping Conventions

CSR 的编址使用独立的 12bit 空间，所以理论上最多可以编码 4096 个 CSR。一般的惯例是，最高的 4bit 用来编码 CSR 的读写属性，

+ `csr[11:10]` 表示 CSR 的读写属性，00/01/10 = read/write，11=read-only
+ `csr[9:8]` 表示可以访问该 CSR 的最低特权等级，00 = User，01 = Supervisor，10 = Hypervisor，11 = Machine

!!! tip
    CSR 使用高位 bit 来表示访问的最低权限，这种方法可以简化硬件检错电路，提供更大的 CSR 地址空间。但是这种方法确实会约束 CSR 的地址映射。

出现下列情况，会抛出一个 illegal instruction exception：

+ 访问一个不存在的 CSR
+ 访问的特权等级不够高
+ 对一个 RO 类型的 CSR 进行写操作（一个 R/W 类型的 CSR 的某些字段可能是 RO 类型，对这些字段的写操作应该被忽略掉。）
+ M 模式下访问 debug CSR 地址段的 CSR

spec 还对 standard 和 custom CSR 地址做了区间划分，custom 区间作为保留地址段，在未来也不会被重定义。

M-mode 的 0x7A0~0x7BF 地址段留作 debug 用，其中 0x7A0~0x7AF 可以在 M-mode 下访问，剩余的 0x7B0~0x7BF 只能在 debug mode 下访问。如果在 M-mode 下访问后面这段地址，implementation 应该触发 illegal instruction exception。

!!! tip
    高效虚拟化要求在虚拟环境中尽可能多地以 native 方式执行指令，而特权访问则 trap 到 virtual machine monitor 中。有些 CSR 在低特权等级下为 RO 属性，但是在高特权等级下为 RW 属性，这种 CSR 会被 shadowed 到另外一个新的 CSR 地址。这样就可以在正常 tarp 非法访问的同时， 避免错误 trap 本来运行的低特权访问。目前 counter 类CSR 是唯一被 shadow 的 CSR。
    比如 hpmcounter3~hpmcounter31 的属性分别为 URO 和 MRW，且在 U-level 和 M-level 分别有映射地址。

### CSR Listing

所有的 CSR 可以分类两类：

+ user-level standard CSR：包括 timer、counter、FP CSR 和 N 子集添加的 CSR。
+ Privileged CSR：剩余的 CSR 都必须在某个更高的特权等级下才能访问。

需要注意的是：并不是所有的 implementation 都要实现所有的 CSR。

### Field Specifications

#### WPRI

Reserved Writes Preserve Values, Reads Ignore Values

某些 R/W field 留作未来使用。对于这些 field，软件应该忽略读到的值，向这个 CSR 的其他 field 写入值时，硬件应该保持 reserved field 的原值。为了前向兼容，未实现这些 reserved field 的 implementation 应该直接 tie0。

!!! tip
    为了简化软件模型，reserved field 在未来进行向后兼容的重新定义时，必须处理好使用一组非原子性 read/modify/write 指令序列来更新其他字段的场景。否则，原始的 CSR 定义必须声明该 field 只能原子性地更新，比如通过两条 set/clear 指令组成的序列。如果修改过程中的中间值不合法，则可能会有潜在的问题。

#### WLRL

Write/Read Only Legal Values

某些 R/W filed 只能配置一些 legal value，其他值作为保留不能使用。软件只能向这些 filed 写入 legal value，而且除非该 field 本身就存储着 legal value（比如上次写入/复位等），否则软件也读不到 legal value。

!!! tip
    implementation 只需要有足够的 bit 能表示所有的 legal value 即可，但是软件读取时必须返回完整的所有 bit。比如某个字段的 legal value 为 0~8，共需要 4-bit 表示，表示范围内的 9 ~ 15 为 illegal value。软件读取时，即使当前值为 7，只需要 3bit，硬件仍然要返回完整的 4bit。

当写入 illegal value 时，implementation 可以（但不是强制）触发一个 illegal instruction exception。当写入 illegal value 后，软件读取的值由硬件决定，可以是任意一个值，但是必须满足确定性原理。

**确定性原理：旧值和写入的新非法值确定，返回值也必须是确定性的。**

#### WARL

Write Any Values, Reads Legal Values

某些 R/W field 只支持一组 legal value，但是允许写入任何值。当写入 illegal value 后，软件读回的一定是 legal value。假设写该 field 没有其他副作用，则可以向其中逐个写入配置值后再重新读出，通过这种方法就能知道支持的 legal value 集合。

当写入 illegal value 时，implementation 不会触发 exception。写入 illegal value 后，软件会读到一个任意 legal value。同理，该 legal value 必须满足确定性原理。

### CSR Width Modulation

当 CSR 的位宽发生变化时（比如修改 MXLEN 或 UXLEN），CSR 的新位宽和 writable field 的值由以下算法决定：

1. previous-width CSR 的 value 被复制到一个相同位宽的临时寄存器中。
2. 对于 previous-width CSR 的 RO bit，临时寄存器的对应 bit 设置为 0。
3. 将临时寄存器的位宽修改为 new width。
    - 如果 new-width $W$ < previous-width，则只保留临时寄存器的低 W bit。
    - 如果 new-width $W$ > previous-width，则将临时寄存器 0 扩展到 W bit。
4. new-width CSR 的每个 writable field 等于临时寄存器的对应 bit 的 value。

修改 CSR 位宽不属于 read/write CSR，所以不会产生任何 side effect。

## Machine-Level ISA

TODO: here

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

一个完整系统中的地址空间包含了各种各样的 address region，有些是 memory，有些是 memory-mapped 的 CSR，还有些是空洞 hole；有些 memory region 不支持读/写/执行，有些不支持 subword/sublock 粒度的访问；有些不支持原子性操作；有些不支持 cache coherence 或拥有不同的 memory model。同理，memory mapped 的 CSR 在访问位宽、原子操作、read/write 访问是否有副作用等方面也各不相同。在 RISC-V 系统中，物理地址 region 的这些属性有一个专门的术语 `Physical Memory Attributes (PMAs)`。

**PMA 是硬件的固有属性，在系统运行时几乎不会变化。** 和 PMP 不同，PMA 不会随着运行程序的上下文发生变化。有些 memory region 的 PMA 属性在 chip design 时就已经确定了，比如片上 ROM。另外一些在 board design 时确定，比如片外总线上挂载的是什么芯片。片外总线上可以挂载一些支持冷/热拔插的设备。某些设备可以在运行时支持重配置 PMA 以支持不同的用途，比如一个片上 RAM 在某个应用在中被缓存到私有 cache 中，也可以在另外一个应用中被配置为共享的 uncacheable 空间。

大部分系统都要求硬件在一旦确定物理地址之后，在后续 pipeline stage 中做一些必要的 PMA 检查，因为有些特定操作并不是所有 region 都支持，或者有些操作需要获取 PMA 当前的配置值。虽然某些架构是在 virtual page 中声明 PMA，然后通过 TLB 来告诉 pipeline 这些信息，但是这个方法会将一些 platform 信息注入到 virtual layer，而且一旦某个 page table 中某个 memory region 没有被正确初始化，就会导致系统错误。另外，可用的 page size 对于设置 PMA 来说可能并不是最优选择，这会导致地址空间碎片以及浪费宝贵的 TLB entry。

RISC-V 则把 PMA 分离出来，并且用一个独立的硬件 PMA checker 进行检查：

+ 大部分情况下，每个 region 的 PMA 是在系统设计时就已经确定了的，所以可以直接在 PMA checker 中以硬连线的方式实现。
+ 对于 runtime 可配置的 PMA，则可以通过一些 memory mapped CSR 对每个 region 以合适的粒度进行配置（比如片上 SRAM 可以灵活地划分为 cacheable 和 uncacheable 区域）。

包括虚实地址转化引起的隐式访问在内，任何访问物理地址的行为都会触发 PMA 检查。为了帮助系统 debug，规范强烈建议：**尽可能精确地捕获导致 PMA 检查失败的物理地址访问。** 精确的 PMA 违例包括 instruction/load/store access-fault exception 以及虚拟内存的 page fault。实际中并不能一直捕获到精确异常，比如探测某些以访问失败作为发现机制的一部分的 legacy bus 时，从 slave device 返回的 error response 是非精确异常。

为了正确地访问设备或者是控制其他硬件单元（比如 DMA）去访问 memory，PMA 对软件来说必须是可读的。因为 PMA 和硬件平台的设计紧密相关，很多 PMA 来自平台规格，所以软件可以通过访问平台信息的方式来获取 PMA 信息。某些 device，特别是 legacy bus，不支持通过探索尝试的方式获取 PMA，如果对其发起一个不支持的访问，则会返回 error response 或 timeout。通常，平台相关的 machine code 会提取这些 PMA 信息并通过某种标准表示方式将其转发给上层特权等级更低的软件。 

对于 platform 支持的可配置 PMA，应该提供一个接口，通过该接口向运行在 machine mode 的 driver 发送配置请求，由 driver 进行正确的配置。比如，切换某些 memory region 的 cacheability 可能会涉及到一些 platform 相关的操作，比如只能在 machine mode 下进行的 cache flush。

常见的 PMA 大概包含下面几方面。

#### Main memory / IO / empty

对于一个 memory region 来说，最重要的属性就是它映射的是常规 main memory 还是 I/O 设备或空洞。main memory 拥有一些后文描述的属性，而 I/O 设备的属性会更广泛一些。非 main memory 的 memory，比如 device scratchpad RAM，被归类为 I/O 段。空地址段会被归类不支持任何访问的 I/O 空间。

#### Supported Access Type

描述 region 支持从 8bit Byte 到 long multi-word burst 之间的哪些访问位宽，以及每种访问位宽是否支持非对齐访问。

!!! tip
    虽然运行在 RISC-V hart 上的软件不能直接生成对 memory 的 burst 访问，但是软件可以对 DMA 进行编程来访问 I/O 设备，所以需要知道支持哪些位宽访问。

main memory 永远都支持所有 device 要求的所有 width 下的 read/write 操作，同时可以声明是否支持 instruction fetch。

!!! tip
    1. 某些平台可能会强制要求所有 main memory 都支持 instruction fetch，而某些平台可能会禁止在某些 main memory region 进行 instruction fetch。
    2. 在某些 case 中，processor/device 可能支持一些其他访问位宽，但是必须兼容 main memory 支持的访问类型。

I/O region 可以指定每种位宽支持的 R/W/X 组合。

对于基于 page 的 virtual memory，I/O 和 memory region 可以指定支持哪些 hardware page table read/write 组合。

!!! tip
    类 unix 系统通常要求所有 cacheable main memory 都支持 page table walk。

#### Atomicity

Atomicity PMA 描述 region 支持哪些原子指令，原子指令可以分为 LR/SC 和 AMO 两类。

!!! tip
    某些平台可能强制要求 cacheable main memory 必须支持系统中所有 processor 的所有原子指令。

##### AMO

AMO 的支持可以分为`AMONone`，`AMOSwap`，`AMOLogical`，`AMOArithmetic` 共 4 个等级，main memory 和 I/O 可能支持部分子集或完全不支持 AMO 操作。

!!! tip
    spec 推荐 I/O region 尽可能支持 AMOLogical。

##### Reservability PMA

对 LR/SC 访问的支持可以分为 `RsrvNone`，`RsrvNonEventual`，`RsrvEventual` 共 3 个等级。

!!! tip
    - spec 推荐 main memory region 尽可能支持 `RsrvEventual`。大部分 I/O region 不支持 LR/SC 访问，因为这些访问最方便建构在 cache-coherence 方案之上，但是有些可能支持 `RsrvEventual` 或 `RsrvNonEventual`。
    - 当 LR/SC 访问 `RsrvNonEventual` 的 memory region 时，当软件检测到无法访问时，软件应该提供备选的 fall-back 机制。

##### Alignment

支持 aligned LR/SC 和 aligned AMO 访问的 memory region 可能还支持 misaligned LR/SC 和 misaligned AMO 以某些位宽访问某些地址。如果 misaligned LR/SC 或 AMO 以某种位宽访问某个地址时触发了 address-misaligned exception，那么所有以该位宽访问该地址的 load，store，LR/SC 和 AMO 访问都应该触发 address-misaligned exception。

!!! tip
    A 子集不支持非对齐的 LR/SC 和 AMO 访问。非对齐 AMO 访问由 `Zam` 子集提供，非对齐的 LR/SC 访问目前还没有标准化，所以非对齐的 LR/SC 访问必须触发 exception。

    当非对齐的 AMO 触发 address-misaligned exception 时，强制要求非对齐的 load，store 也触发 address-misaligned exception，这样就可以模拟 M-mode trap handler 中的 misaligned AMO 访问。该 handler 使用 global mutex，在 critical section 模拟该访问，以这样的方式保证原子性。当非对齐 load/store 的 handler 使用同一个 mutex 时，以该位宽访问该地址的所有访问都是 mutually atomic。

对于某些非对齐访问，implementation 可以通过触发 access-fault exception 的方式表明不应该在 trap handler 中模拟该行为。当以某种位宽访问某个地址时，如果所有 misaligned AMO 和 LR/SC 都触发了 access-fault exception，那么以该位宽访问该地址的所有常规非对齐 load/store 则不要求原子性执行。

#### Memory Ording PMAs

为了实现 FENCE 指令和原子指令 order bit 提供的 order 功能，地址空间被分为 main memory 和 I/O 两类。

一个 hart 对 main memory region 的访问不仅能被其他 hart 观测到，也会被其他能对 main memory 发起访问的 device（比如 DMA）观测到。coherent main memory 的 memory model 要么是 RVWMO 要么是 RVTSO，incoherent main memory region 的 memory model 由 implementation 决定。

一个 hart 对 I/O region 的访问不仅能被其他 hart 和 bus master device 观测到，也会被目标 I/O slave
device 观测到。I/O region 的访问要么是 relax order 要么是 strong order：

- 以 relax order 访问 I/O region，其他 hart 和 master device 观测到的行为和以 RVWMO 访问 main memory region 类似。
- 以 strong order 访问 I/O region，其他 hart 和 master device 观测到的为 program order。

#### Coherenece and Cacheability

coherenece 是针对单个物理地址而言的属性，表示某个 agent 对该地址的 write 对系统中的其他 agent 都可见。注意，不要把 coherence 和 memory consistency model 混淆，内存一致性模型规定给定某个地址的历史读写信息后，读该地址的返回值应该是什么。RISC-V 中不鼓励使用 hardware incoherent region，因为它会导致软件复杂化，性能和功耗恶化。

一个地址段的 cacheability 属性不会改变软件对该地址段的 view，这些 view 不包括其他 PMA 中规定的属性（比如 main memory 和 I/O 空间的划分、访问顺序、支持的访问类型、支持的原子操作、coherence 等）。因此，cacheability 在指令集中被视为 M-mode 软件管理的 platform level setting。

当一个 platform 支持对某个 memory region 配置 cacheability 时，一个和 platform 相关的 M-mode routine 负责修改配置，并在必要时 flush cache。因此，只有在 cacheability 的变换的这段时间内系统为 incoherent，这种中间的变化状态不应该对 S/U mode 可见。

!!! tip
    指令集将 cache 分为了：
    
    - master private：每个 master 私有
    - master shared：位于 master 和 slave 之间，可能有多级
    - slave private：由 slave 私有，对 coherence 无影响

    对于不支持 cache 的 share memory region 来说，coherence 很直观，PMA 只需要表明该 region 不支持被 private 或 shared cache。

    对于 read-only 的 memory region 来说，coherence 也很直观，无需 coherence 机制就可以被多个 agent 安全地多次 cache。PMA 只需要表明该 region 只支持 read，不支持 write 即可。

    有些 read-write memory region 可能只支持一个 agent 访问，这种场景下无需 coherence 机制就可以被 master private cache。PMA 会表明该 region 可以被 cache，而且可以被 cache 在一个 shared cache 中，因为其他 agent 不会访问该 region。

    如果一个 agent 可以 cache 一个 read-write region，且该 region 也可以被其他 agent 访问（无论是否为 cache 或 no cache），都需要一套 cache-coherence 机制。如果没有 hardware cache coherence，则必须提供 software cohere scheme，但是通常软件实现都比较困难且存在严重的性能问题。hardware coherence scheme 通常需要更复杂的硬件，也会影响到性能，但是对软件是不可见的。

    对于每个支持 hardware coherence 的 region 来说，PMA 应该表明该 region 支持 coherence 且当系统中 coherence controller 有多个时，PMA 要指明该 region 使用哪个 controller。对于某些系统来说，controller 是下一级 cache，而该级 cache 的 coherence 又依赖于下下级 cache。

    platform 中的大部分 memory region 对软件来说都是 coherent 的，因为这些 region 的 PMA 属性都是固定的，要么 uncached，要么 read-only，要么 hardware cache-coherent，要么只能由一个 agent 访问。

如果 PMA 表明该 region 不支持 cache，则对该 memory region 的访问必须由 memory 自身来满足，不能依靠任何 cache。

#### Idempotency

幂等性 idempotency：执行多次和一次的效果一样。

- main memory region 是 idempotent。
- I/O region 的 read/write idempotent 是分开的：read 具有幂等性，而 write 不具有。

如果访问不具有幂等性，也就是说会产生潜在的副作用，那么必须避免 speculative 或 redundant 访问（因为他们都可能会导致多次访问）。

!!! tip
    虽然 hardware 会对 non-idempotent region 避免 speculative 或 redundant 访问，但是还是有必要确保软件或编译优化不会对 non-idempotent region 生成投机访问。

    non-idempotent region 可能不支持非对齐访问。非对齐访问应该触发 access-fault exception 而不是 address-misaligned exception，以此来表明软件不应该通过拆分成多次小颗粒的访问来模拟非对齐访问，因为这种行为会引起预期之外的副作用。

对于 non-idempotent region 来说，不允许 implementat 提前或投机地进行 implicit
read/write，除非是以下特例。

当进行非投机的 implicit read 时，允许 implementation 额外从包含本次 implicit read 地址的 NAPOT region 中读取任意长度的数据量。而且如果是 instruction fetcch，允许 implementat 额外从下一个 NAPOT region 中读取任意 byte 数据量。这些额外的读数据可以作为后续的提前或投机访问的结果。这些 NAPOT region 的大小由 implementation决定，但是必须不超过支持的最小 page size。

### PMP

为了安全运行以及故障隔离，需要限制 hart 上运行的软件可以访问的物理地址，这个需求可以通过一个可选的 `Physical Memory Protection (PMP)` 单元实现，它可以为每个 hart 提供每个 memory region 的访问属性控制寄存器。PMP 和 PMA 是并列关系，同步进行检查。

虽然 PMP 的访问粒度是和平台相关的，但是标准的 PMP 编码支持的最小 region 大小为 4 Byte。某些 region 的特权属性可以直接用 hardwire 实现，比如某些 region 只有 M-mode 下可访问。

!!! tip 
    不同平台对 PMP 的需求不同，有些平台还会额外提供其他的 PMP 指令来增强/代替本小节描述的方案。

当 core 运行在 S/U-mode 时，PMP checker 会检查所有的访问，包括：

- S/U-mode 下的取指
- `mstatus.MPRV = 0` 时 S/U-mode 下的数据访存
- `mstatus.MPRV = 1` 且 `mstatus.MPP` 包含 S/U 时任何 mode 下的数据访存
- S-mode 下的虚拟地址翻译时对 page table 的访问
- (可选地) M-mode 下且 locked region 的访问

事实上，PMP 设置 S/U-mode 下的访问权限（默认无权限），在 M-mode 默认有所有地址的权限。

违反 PMP 的访问会被 core 捕获，触发精确异常。

!!!note
    PMP 主要检查的是 S-mode 和 U-mode，因为用户程序运行在这两个级别中。而 M-mode 下 core 必须拥有全部的访问权限，所以 M-mode 不是 PMP 的主要应用场景。

#### PMP CSRs

spec 规定最多支持 16 个 PMP region，每个 region 由一个 8-bit 配置寄存器 `pmpxcfg` + 一个 MXLEN-bit 的地址寄存器 `pmpaddrx` 共同描述。所有 PMP CSR 均为 WARL，且只能在 M-mode 下访问。

##### pmpcfg

为了最小化上下文切换的代价，`pmpxcfg` 是按照小端模式密集存储在一起的。所以可以算出来

+ RV32 需要 4 个 CSR (`pmpcfg0` ~ `pmpcfg3`) 来存储 `pmp0cfg` ~ `pmp15cfg`
+ RV64 需要 2 个偶数下标 CSR `pmpcfg0`, `pmpcfg2` 来存储 `pmp0cfg` ~ `pmp15cfg`，奇数下标 `pmpcfg1`, `pmpcfg3` 是非法的

!!! tip
    RV64 不使用奇数下标 pmpcfg 的原因：减小支持多种 MXLEN 的代价。比如，无论是 RV32 还是 RV64，PMP entry 8~11 都在 pmpcfg2 中。

每个 8bit 的 `pmpxcfg` 规定了对应 region 的 L/A/X/W/R 五个属性：

- 当 W/R/X 被置 1 时，表示该 region 允许 write/read/instruction execution。当无权限时，触发对应的 store/load/instruction access fault。
- A 字段表示 `pmpaddrx` 的地址匹配模式，支持 OFF/TOR/NA4/NAPOT 共 4 种模式。
- L 字段表示该 region 被 lock，无法向 `pmpxcfg` 和 `pmpaddrx` 写入新值。

当 MXLEN 发生变化时，`pmpxcfg` 的值保留不变，但是出现在对应的 `pmpcfgy` 的对应 bit 中。比如当 MXLEN 从 64 变化到 32 时，`pmp4cfg` 从 `pmpcfg0[39:32]` 移动到 `pmpcfg1[7:0]`。

!!!note
    implementation 可以实现 `pmpxcfg` 寄存器，然后根据 MXLEN 用多个 `pmpxcfg` 组合得到 `pmpcfgy`。

##### pmpaddr

PMP 地址寄存器为 CSR `pmpaddr0` ~ `pmpaddr63`：

- RV32：每个 pmpaddr 保存 addr[33:2]，即 34bit 地址
- RV64：每个 pmpaddr 保存 addr[55:2]，即 56bit 地址

因为 PMP region 颗粒度可能大于 4 Byte，所以并不是 pmpaddr 的每个 bit 都会被实现，所以 pmpaddr 为 WARL。

!!! tip
    因为 Sv32 page-based 虚拟地址方案支持 34bit 地址空间，所以 RV32 PMP 要支持比 XLEN 更大的地址区间。同理，Sv39 和 Sv48 page-based 虚拟地址方案支持 56bit 地址空间，所以 RV64 PMP 需要覆盖相同地址范围。

虽然 PMP region 的最小粒度为 4 Byte，但是 platform 可以定义更粗的颗粒度。一般来说，PMP region 的颗粒度必须保持一致，为 $2^{G+2}$ Byte。

- 当 $G \geq 1$ 时，NA4 模式不可用
- 当 $G \geq 2$ 且 pmpcfg.A[1] = 1 时，为 NAPOT 模式，读出的 pmpaddr[G-2:0] 为全 1。
- 当 $G \geq 1$ 且 pmpcfg.A[1] = 0 时，为 OFF/TOR 模式，读出的 pmpaddr[G-1:0] 为全 0。pmpaddr[G-1:0] 并不会影响到 TOR 下的地址匹配逻辑。（从这条规则可以推理出下面软件检测 PMP region 粒度的方法）

!!!note
    - 颗粒度 != 容量，所有 region 的颗粒度必须相同，但是大小可以不同。
    - 最小颗粒度决定了 G，也决定了 pmpaddr[G-2:0] 的值，所以硬件可以 hardwire 实现，不需要使用寄存器。
    - 虽然修改 pmpxcfg.A 会影响到 pmpaddrx 的读出结果，但实际上并不会改变底层 pmpaddrx 存储的 bit。特别是，当 pmpxcfg.A 从 NAPOT 改到 TOR，又从 TOR 该回 NAPOT，pmpaddrx[G-1] 都会保持原值不变。
    - 从分类讨论描述可以推断出来，NAPOT 模式下 PMP region 地址和容量对齐；TOR 模式下地址和容量无对齐约束。比如最小粒度为 4KB，region size = 32 KB，则 NAPOT 模式下地址必须为 32 KB 的整数倍，如 32 KB，64 KB，96 KB 等；而 TOR 模式下地址只需要是 4KB 的整数倍即可，如 4KB，8KB，12KB 等。

软件可以通过以下方式得到 PMP region 的粒度：

1. 向 pmp0cfg 写入全 0，将地址匹配设置为 OFF
2. 向 pmpaddr0 写入全 1
3. 读回 pmpaddr0，如果 LSB 1 为 bit[G]，则粒度为 $2^{G+2}$ Byte

!!!note
    这个方法的原理：根据前面的规则，OFF 模式下读到的 pmpaddr[G-1:0] 为全 0，pmpaddr[MXLEN-1 : G] 为全 1。所以 LSB 1 的下标就是 G，从而可以根据公式算出粒度。

##### address matching

pmpxcfg.A 决定了如何翻译和使用 pmpaddrx 的值：

- NAPOT 模式利用 region 容量和起始地址对齐的约束，只靠 pmpadddr 一个寄存器就可以同时表示 region 容量和 region 起始地址。因为对于 2 的幂次对齐的地址，其实低位是冗余的，可以用这些低位来表示容量。
- TOR 模式下，第 i 个 entry 的地址区间为 [$pmpaddr_{i-1}$, $pmpaddr_i$)

##### locking

pmpxcfg.L = 1 表示该 entry 被 lock，当 pmpxcfg.L = 1 时，会忽略对 pmpxcfg 和 pmpaddrx 的写操作。如果 pmpxcfg.L = 1 且 pmpxcfg.A = TOR，则对 $pmpaddr_{x-1}$ 的写操作也会被忽略掉。

L 和 A 无关，即使 pmpxcfg.A = OFF，置位 L 也会 lock 该 entry。一旦 entry 被 lock，就只能通过复位来释放。

L 字段除了 lock 功能外，还会表示是否在 M-mode 下进行 R/W/X 权限检查：

- 当 L = 1，强制 M/S/U mode 都会检查权限
- 当 L = 0，不检查 M-mode 下访问的权限（所有访问都 success），只检查 S/U mode 下的 R/W/X 权限

##### priority and matching

地址匹配逻辑如下图所示：

::uml:: title="PMP 地址匹配逻辑"
start
:match PMP entry;
note right: lowest number entry matching any byte of an access
switch (match result)
  case (full match)
    if ((L == 0) & (prv == M)) then (yes)
      :success;
    else (no)
        :check R/W/X;
    endif
  case (partial match)
    :fail;
  case (no match)
    if (prv == M) then (yes)
      :success;
    else (no)
      :fail;
    endif
endswitch
stop
::end-uml::

failed 的访问会触发对应 exception。单条指令可能会拆分出多个非原子访问序列（比如非对齐访问，访问虚地址 etc），一旦序列中某个访问 failed，即使其他访问 success 且产生了副作用，仍然会触发 exception。

#### Paging

PMP 机制支持基于 page 技术的 Virtual-Memory 系统。当启用 page 时，访问虚拟地址的指令可能会产生多次物理地址访问，包括隐式的查询 page table，PMP 会检查所有的这些物理地址访问。隐式查询 page table 时为 S-mode。

spec 允许支持虚拟地址的 implementation 在实际物理地址访问前投机地进行地址翻译，而且允许把翻译结果缓存起来。从地址翻译到发起物理地址访问，PMP 检查可以发生在这段时间内的任何时候，所以当 PMP CSR 被修改后，M-mode 的软件必须把最新的配置同步到虚拟地址系统已经任何 PMP 翻译缓存中。具体方法：修改 PMP CSR 后使用 rs1 = x0 和 rs2 = x0 的 `SFENCE.VMA` 指令。

如果不支持虚拟系统，则不需要 `SFENCE.VMA` 指令。

## Supervisor-Level ISA

TODO
