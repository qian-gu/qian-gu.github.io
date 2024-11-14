Title: RISC-V Spec 阅读笔记 #2 —— Privileged ISA
Date: 2021-03-25 17:29
Category: RISC-V
Tags: RISC-V, Spec
Slug: risc-v-spec-notes-2-privileged
Author: Qian Gu
Series: RISC-V Notes
Summary: Volume II: Privileged ISA 读书笔记

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

RISC-V 中的 opcode = `SYSTEM` 的字段用来编码特权指令，这些指令可以分为两类：

+ `zicsr` 子集中定义的 atomically read-modify-write CSR 的指令(即 CSR 指令)
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

#### WPRI

Reserved Writes Preserve Values, Reads Ignore Values

某些 R/W field 留作未来使用。对于这些 field，软件应该忽略读到的值，向这个 CSR 的其他 field 写入值时，硬件应该保持 reserved field 的原值。为了前向兼容，未实现这些 reserved field 的 implementation 应该直接 tie0。

!!!note
    为了简化软件模型，reserved field 在未来进行向后兼容的重新定义时，必须处理好使用一组非原子性 read/modify/write 指令序列来更新其他字段的场景。否则，原始的 CSR 定义必须声明该 field 只能原子性地更新，比如通过两条 set/clear 指令组成的序列。如果修改过程中的中间值不合法，则可能会有潜在的问题。

#### WLRL

Write/Read Only Legal Values

某些 R/W filed 只能配置一些 legal value，其他值作为保留不能使用。软件只能向这些 filed 写入 legal value，而且除非该 field 本身就存储着 legal value（比如上次写入/复位等），否则软件也读不到 legal value。

!!!note
    implementation 只需要有足够的 bit 能表示所有的 legal value 即可，但是软件读取时必须返回完整的所有 bit。比如某个字段的 legal value 为 0~8，共需要 4-bit 表示，表示范围内的 9 ~ 15 为 illegal value。软件读取时，即使当前值为 7，只需要 3bit，硬件仍然要返回完整的 4bit。

当写入 illegal value 时，implementation 可以（但不是强制）触发一个 illegal instruction exception。当写入 illegal value 后，软件读取的值由硬件决定，可以是任意一个值，但是必须满足确定性原理。

**确定性原理：旧值和写入的新非法值确定，返回值也必须是确定性的。**

#### WARL

Write Any Values, Reads Legal Values

某些 R/W field 只支持一组 legal value，但是允许写入任何值。当写入 illegal value 后，软件读回的一定是 legal value。假设写该 field 没有其他副作用，则可以向其中逐个写入配置值后再重新读出，通过这种方法就能知道支持的 legal value 集合。

当写入 illegal value 时，implementation 不会触发 exception。写入 illegal value 后，软件会读到一个任意 legal value。同理，该 legal value 必须满足确定性原理。

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

一个完整系统中的地址空间包含了各种各样的地址段，有些是真实的 memory 域，有些是 memory-mapped 的 control register，还有些是空洞段。有些 memory 域不支持读/写/执行，有些不支持 subword/sublock 的访问，有些不支持原子性操作，有些不支持 cache 一致性协议或是 memory 模型不一样。同理，memory map 的控制寄存器在访问位宽、是否支持原子操作、以及 read/write 访问是否有副作用等方面也各不相同。在 RISC-V 系统中，这些属性有一个专门的术语 `Physical Memory Attributes (PMAs)`。

**PMA 是硬件的固有属性，所以在系统运行时很少变化。**和 PMP 不同，PMA 很少会随着运行程序的上下文来改变状态。有些 memory region 的 PMA 属性在 chip design 时就已经确定了，比如片上 ROM。另外一些在 board design 时确定，比如片外总线上挂载的是什么芯片。片外总线上可以挂载一些支持冷/热拔插的设备。某些设备可以在运行时支持重配置，以支持不同用户设置不同的 PMA 属性，比如，一个片上 RAM 可以在一个应用中被配置为私有空间，也可以在另外一个应用中被配置为共享空间。

大部分系统都要求硬件在知道物理地址之后做一些必要的 PMA 检查，比如有些物理地址不支持某些特定操作，而有些操作需要提前知道 PMA 当前的配置值。虽然某些架构是在 virtual page 中声明 PMA，然后通过 TLB 来通知 pipeline 这些信息，但是这个方法会将一些底层的平台些信息注入到上层的 virtual layer，而且一旦某个 page table 中的某个 memory region 配置不对，就会导致系统错误。此外，page size 对于 PMA 来说并不是最优选择，会导致地址空间碎片和 TLB 的低效率使用。

RISC-V 则把 PMA 的标准独立出来，并且用一个独立的硬件 PMA checker 来检查 PMA：

+ 大部分情况下，很多 region 的 PMA 是在芯片设计时就已经确定了的，所以可以直接在 checker 中以硬连线的方式实现
+ 对于 runtime 可配置的 PMA，则可以通过一些 memory mapped control register 来实现（比如片上 SRAM 可以动态地划分为 cacheable/uncacheable 区域）

包括虚实地址转化在内，任何访问 physical memory 的行为都会触发 PMA 检查。为了帮助系统 debug，规范强烈建议，尽可能精确地捕获导致 PMA 检查失败的物理地址访问。精确的 PMA 违例包括 instruction，load/store access-faultexception 等。实际中并不能一直捕获到精确异常，比如通过 bus 访问 slave device 时收到的 error response 则是非精确异常。

为了正确地访问设备或者是控制其他硬件单元（比如 DMA）去访问 memory，PMA 对软件来说必须是可读的。因为 PMA 和硬件平台的设计紧密相关，很多 PMA 继承自平台规格，所以软件可以通过访问平台信息的方式来获取 PMA 信息。某些 device，特别是 legacy bus，不支持这种方式获取 PMA，如果对其发起一个不支持的访问，则会返回 error response 或 timeout。通常，平台相关的 machine code 会提取 PMA 信息并通过某种标准表示方式将其转发给上层的非特权软件。 

对于 platform 支持的可配置 PMA，应该提供一个接口，通过该接口向运行在 machine mode 下的 driver 发送请求，实现配置。比如，切换某些 memory region 的 cacheability 时，会涉及到一些 platform 相关的操作，比如只能在 machine mode 下进行的 cache flush。

*常见的 PMA 大概包含下面几方面。*

#### Main memory / IO / empty

对于一个地址段来说，最重要的属性就是它映射的是常规 main memory，还是 I/O 设备，还是空洞。

main memory 拥有一些后文描述的属性，而 I/O 设备的属性会更广泛一些。非 main memory 的 memory，比如 device scratchpad RAM，被归类为 I/O 段。空地址段也会被归类不支持任何访问的 I/O 空间。

#### Supported Access Type

Access Type 描述支持从 8bit 到 long multi-word burst 之间的哪些访问位宽，以及每种访问位宽是否支持非对齐访问。

!!!note
    虽然运行在 RISC-V hart 上的软件不能直接生成对 memory 的 burst 访问，但是该软件可以对 DMA 进行编程来访问 I/O 空间，所以需要知道支持哪些位宽访问。

main memory 永远都支持所有 device 要求的所有 width 下的 read/write 操作，同时可以声明是否支持 execution。

!!!note
    1. 某些平台强制要求所有 main memory 都支持 instruction fetch，而某些平台会禁止从某些地址段 instruction fetch。
    2. 在某些 case 中，processor/device 可能支持一些其他访问位宽，但是必须兼容 main memory 支持的访问位宽。

I/O 空间则可以指定每种位宽下支持的 R/W/E 组合。

对于基于 page 的 virtual memory，I/O 和 memory region 可以声明支持哪些 hardware page table read/write。

!!!note
    类 unix 系统通常要求所有 cacheable main memory 都支持 page table walk。

#### Atomicity

Atomicity PMA 描述地址段支持哪些原子指令，原子指令可以分为 LR/SC 和 AMO 两类。

!!!note
    某些平台可能强制要求 cacheable main memory 必须支持系统中所有 processor 的所有原子指令。

@TODO：补充 AMO，reservability，alignment

#### Memory-Ordering

将地址空间分为 main memory 和 I/O 两种类型的目的是为了支持 FENCE/AMO 中定义的访问顺序。

一个 hart 对 main memory 的访问不仅会被其他 hart 观测到，同时也会被其他可以给 main memory 发送请求的设备（比如 DMA）观测到。main memory 空间要么是 RVWMMO 模型，要么是 RVTSO 模型。

一个 hart 对 I/O 空间的访问不经会被其他 hart 和总线上的 master 设备观测到，还会被目标 slave 设备观测到。

#### Coherenece and Cacheability

coherenece 是针对单个物理地址而言的属性，表示某个 agent 对该地址的访问对系统中的其他 agent 可见。注意，不要混淆 coherence 和内存一致性模型。RISC-V 中不鼓励使用 hardware incoherent region，因为它会导致软件复杂化，性能和功耗恶化。

一个地址段的 cacheability 属性不会改变软件对该地址段的 view，这些 view 不包括其他 PMA 中规定的属性（比如 main memory 和 I/O 空间的划分、访问顺序、支持的访问类型、支持的原子操作、coherence 等）。

一些 platform 支持某些地址段的 cacheability 可配，这种情况下，由某个 machine mode 下的 routine 对 cacheability 进行配置，并在必要时 flush cache。

#### Idempotency

幂等性 idempotency：执行多次和一次的效果一样。

许多 main memory region 都被认为是 idempotent。对 I/O region，read/write 的 idempotent 是分开的：read 具有幂等性，而 write 不具有。

如果访问不具有幂等性，也就是说会产生潜在的副作用，那么 speculative 和 redundant 的访问都必须被规避掉（因为他们都可能会导致多次访问）。

+ main memory 是 idempotency（执行多次和一次效果一样）；I/O 域的 read 是 idempotent 的，而 write 不是

### PMP

为了安全执行以及遏制发生 fault，需要限制 hart 上运行的软件可以访问的物理地址，这个需求可以通过一个可选的 `Physical Memory Protection (PMP)` 单元实现，它可以为每个 hart 提供每个 memory region 的访问属性控制寄存器。PMP 和 PMA 是并列关系，同步进行检查。

虽然 PMP 的访问粒度是和平台相关的，但是标准的 PMP 编码支持的最小 region 大小为 4 Byte。某些 region 的特权属性可以直接用 hardwire 实现，比如某些 region 只有 M-mode 下可访问。

!!!note 
    不同平台对 PMP 的需求不同，有些平台还会额外提供其他的 PMP 指令来增强/代替本小节描述的方案。

当 core 运行在 S/U-mode 时，PMP checker 会检查所有的访问，包括：

- S/U-mode 下的取指
- `mstatus.MPRV = 0` 时 S/U-mode 下的数据访存
- `mstatus.MPRV = 1` 且 `mstatus.MPP` 包含 S/U 时任何 mode 下的数据访存
- S-mode 下的虚拟地址翻译时对 page table 的访问
- (可选地) M-mode 下且 locked region 的访问

事实上，PMP 设置 S/U-mode 下的访问权限（默认无权限），在 M-mode 默认有所有地址的权限。

PMP 违例为精确异常。

!!!note
    PMP 主要检查的是 S-mode 和 U-mode，因为这两种级别只有部分权限，所以地址访问需要做限制。而 M-mode 下 core 必须拥有全部的访问权限，所以 M-mode 不是 PMP 的主要应用场景。

#### PMP CSRs

spec 规定最多支持 64 个 PMP region，implementation 可以选择只实现 0/16/64 个，而且必须优先实现小序号的 PMP entry。每个 region 由一个 8-bit 配置寄存器 `pmpxcfg` + 一个 MXLEN-bit 的地址寄存器 `pmpaddrx` 共同描述。所有 PMP CSR 均为 WARL，且只能在 M-mode 下访问。

##### pmpcfg

为了最小化上下文切换的代价，`pmpxcfg` 是按照小端模式密集存储在一起的。所以可以算出来

+ RV32 需要 16 个 CSR (`pmpcfg0` ~ `pmpcfg15`) 来存储 `pmp0cfg` ~ `pmp63cfg`
+ RV64 需要 8 个偶数下标 CSR `pmpcfg0`, `pmpcfg2` ~ `pmpcfg14` 来存储 `pmp0cfg` ~ `pmp63cfg`，奇数下标 `pmpcfg1`, `pmpcfg3` ~ `pmpcfg15` 是非法的

!!!note
    RV64 不使用奇数下标 pmpcfg 的原因：减小支持多种 MXLEN 的代价。比如，无论是 RV32 还是 RV64，PMP entry 8~11 都在 pmpcfg2 中。

每个 8bit 的 `pmpxcfg` 规定了对应 region 的 L/A/X/W/R 五个属性：

- 当 W/R/X 被置 1 时，表示该 region 允许 write/read/instruction execution。当无权限时，触发对应的 store/load/instruction access fault。
- A 字段表示 `pmpaddrx` 的地址匹配模式，支持 OFF/TOR/NA4/NAPOT 共 4 种模式。
- L 字段表示该 region 被 lock，无法向 `pmpxcfg` 和 `pmpaddrx` 写入新值。

当 MXLEN 发生变化时，`pmpxcfg` 的值保留不变，但是出现在对应的 `pmpcfgy` 的对应 bit 中。比如当 MXLEN 从 64 变化到 32 时，`pmp4cfg` 从 `pmpcfg0[39:32]` 移动到 `pmpcfg1[7:0]`。

!!!tip
    implementation 可以实现 `pmpxcfg` 寄存器，然后根据 MXLEN 用多个 `pmpxcfg` 组合得到 `pmpcfgy`。

##### pmpaddr

PMP 地址寄存器为 CSR `pmpaddr0` ~ `pmpaddr63`：

- RV32：每个 pmpaddr 保存 addr[33:2]，即 34bit 地址
- RV64：每个 pmpaddr 保存 addr[55:2]，即 56bit 地址

因为 PMP region 颗粒度可能大于 4 Byte，所以并不是 pmpaddr 的每个 bit 都会被实现，所以 pmpaddr 为 WARL。

!!!note
    因为 Sv32 page-based 虚拟地址方案支持 34bit 地址空间，所以 RV32 PMP 要支持比 XLEN 更大的地址区间。同理，Sv39 和 Sv48 page-based 虚拟地址方案支持 56bit 地址空间，所以 RV64 PMP 需要覆盖相同地址范围。

虽然 PMP region 的最小粒度为 4 Byte，但是 platform 可以定义更粗的颗粒度。一般来说，PMP region 的颗粒度必须保持一致，为 $2^{G+2}$ Byte。

- 当 $G \geq 1$ 时，NA4 模式不可用
- 当 $G \geq 2$ 且 pmpcfg.A[1] = 1 时，为 NAPOT 模式，读出的 pmpaddr[G-2:0] 为全 1。
- 当 $G \geq 1$ 且 pmpcfg.A[1] = 0 时，为 OFF/TOR 模式，读出的 pmpaddr[G-1:0] 为全 0。pmpaddr[G-1:0] 并不会影响到 TOR 下的地址匹配逻辑。（从这条规则可以推理出下面软件检测 PMP region 粒度的方法）

!!!note
    - 颗粒度 != 容量，所有 region 的颗粒度必须相同，但是大小可以不同。
    - 最小颗粒度决定了 G，也决定了 pmpaddr[G-2:0] 的值，所以硬件可以 hardwire 实现，不需要使用寄存器。
    - 虽然修改 pmpxcfg.A 会影响到 pmpaddrx 的读出结果，但实际上并不会改变底层 pmpaddrx 存储的 bit。特别是，当 pmpxcfg.A 从 NAPOT 改到 TOR，又从 TOR 该回 NAPOT，pmpaddrx[G-1] 都会保持原值不变。
    - 从分类讨论描述可以推断出来，无论哪种地址匹配模式，PMP region 的容量和地址都是对齐的。

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

```
@startuml
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
@enduml
```

failed 的访问会触发对应 exception。单条指令可能会拆分出多个非原子访问序列（比如非对齐访问，访问虚地址 etc），一旦序列中某个访问 failed，即使其他访问 success 且产生了副作用，仍然会触发 exception。

#### Paging

PMP 机制支持基于 page 技术的 Virtual-Memory 系统。当启用 page 时，访问虚拟地址的指令可能会产生多次物理地址访问，包括隐式的查询 page table，PMP 会检查所有的这些物理地址访问。隐式查询 page table 时为 S-mode。

spec 允许支持虚拟地址的 implementation 在实际物理地址访问前投机地进行地址翻译，而且允许把翻译结果缓存起来。从地址翻译到发起物理地址访问，PMP 检查可以发生在这段时间内的任何时候，所以当 PMP CSR 被修改后，M-mode 的软件必须把最新的配置同步到虚拟地址系统已经任何 PMP 翻译缓存中。具体方法：修改 PMP CSR 后使用 rs1 = x0 和 rs2 = x0 的 `SFENCE.VMA` 指令。

如果不支持虚拟系统，则不需要 `SFENCE.VMA` 指令。

## Supervisor-Level ISA

TODO
