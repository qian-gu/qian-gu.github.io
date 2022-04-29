Title: CPU 关键技术 —— Scoreboard
Date: 2021-01-13 19:21
Category: IC
Tags: CPU, scoreboard
Slug: cpu_scoreboard
Author: Qian Gu
Series: CPU 关键技术
Status: draft
Summary: 总结 Scoreboard 细节

## Why need Scoreboard

流水线是 CPU 设计中的基本概念，为了获得尽可能高的性能，人们发明了各种技术使得流水线保持在全速运行状态。其中最关键的就是**动态调度技术**。如[《计算机体系结构》][arch]介绍，

> 现在体系结构的主要矛盾不在运算部件，CPU 中用于做加、减、乘、除的部件只占 CPU 面积的很小一部分，CPU 中的大部分面积被用来给运算部件提供足够的指令和数据。

[arch]: https://book.douban.com/subject/27190711/

Scoreboard 是一种非常古老的动态调度算法，发明于 1964 年，最早用在的 CDC 6600 计算机上。Scoreboard 可以使得 CPU 乱序执行（Out-of-Order Execution），从而提高 CPU 的性能。

## What is Scoreboard

### Hazard

乱序执行的基本原理就是：**硬件让不受其他指令影响的指令尽可能早执行，尽早结束，这样才能获取到最高性能。**但是乱序执行的前提是要保证功能正确，如果功能都不正确，那么这一切都没有意义。保证功能正确意味着要解决两大问题：

| 问题 | 含义 |
| ----- | ---- |
| 资源冒险（`structual hazard`） | 计算单元一次只能执行一条指令，同时计算多条指令结果不正确 |
| 数据冒险（`data hazard`） | 计算开始前源操作数必须是 ready 状态，计算结果也要在合适的时间写入寄存器 |

根据读写关系数据冒险可以分为 3 种：

+ `RAW` (Read-After-Write)：读源操作数的时间不能太早，要等数据准备好再读，避免读到无效数据
+ `WAW` (Write-After-Write)：写回执行结果的时间不能太早，要等到前序指令把旧值写入后再写入新值，避免被旧值覆盖
+ `WAR` (Write-After-Read)：写回执行结果的时间不能太早，要等到前序指令把旧值读走后再写入新值，避免覆盖仍然有用的旧值

产生 WAW 和 WAR 的根本原因就是因为寄存器数量太少了（RV32I 只有 32 个通用寄存器），前后指令流要复用同一个寄存器。假设有无数个寄存器可用，那么自然就不存在数据冒险的问题。

!!! tip
    1. 数据冒险不包含 RAR(Read-After-Read) 的原因很简单：RAR 对结果的正确性没有任何影响
    2. 这三种数据冒险中，RAW 被称为“真数据冒险”，因为另外两种冒险实际上并不是真正的数据依赖，而是“名字相关”，即只是因为使用同一个寄存器名而导致的相关性
    3. WAW 和 WAR 可以通过**寄存器重命名**技术进行规避，而 RAW 是无法规避的，只能进行流水线停顿。为了减少停顿，一般通过动态调度降低性能损失：
        + 数据旁路 Data Bypass Forward：把前序的结果尽可能早地传递给后续需要用它的指令，减少等待时间
        + 执行后续无关指令，直接消灭等待
    3. `Tomasulo 算法` 可以通过 `保留站` 和 `ROB` 实现寄存器重命名，达到上述两个效果

这几种数据依赖关系贯穿于整个流水线的多个阶段：

+ **发射 Issue**：检查本条指令要读写哪些寄存器，并记录下相关信息。为了保证 WAW，发射本条指令有两个条件必须满足：第一个是前序要写回相同寄存器的指令执行结束后才能发射本条指令；第二个是相关功能单元不是 busy 状态
+ **读操作数 Read Operands**：在把指令成功发射给相关功能单元之后，还需要准备好源操作数。为了保证 RAW，读取源操作数必须要等到前序写对应寄存器的指令执行结束后在进行
+ **执行 Execution**：操作数准备就绪后功能单元开始执行，在执行结束时会通知 scoreboard
+ **写回 Write Back**：执行结束后的结果也不能马上写入到目标寄存器，因为要保证 WAR，即要等到前序要读目标寄存器的指令把数据读走之后才能把新值写入寄存器

### Scoreboard Algorithm

Scoreboard 是一种集中式的控制逻辑，可以同时识别资源冒险和数据冒险，其核心思想是：**记录每一条指令需要用到的寄存器序号和功能单元的状态，持续跟踪，直到数据依赖解除后才把指令发射到相关功能单元。当功能单元执行完毕，结果写回到寄存器后更新相关状态，为后续指令做准备。**

为了实现这个目的，scoreboard 维护了 3 张表：

| 表格 | 功能 |
| ----- | ----- |
| **指令状态表 Instruction Status** | 记录每条指令的状态，指示处于流水线的哪个 stage |
| **功能单元状态表 Functional Unit Status** | 记录每个功能单元的状态，表的深度 = 功能单元的数量，每个 entry 记录包含 9 个字段<ul><li>Busy[FU]：记录该 FU 的状态</li><li>Op[FU]：记录该 FU 执行的操作</li><li>Fᵢ[FU]：记录该 FU 要写入的寄存器号</li><li>Fⱼ[FU]：记录该 FU 读取的第一个源操作数 src1</li><li>Fₖ[FU]：记录该 FU 读取的第二个源操作数 src2</li><li>Qⱼ[FU]：记录产生该 FU src1 的功能单元</li><li>Qₖ[FU]：记录产生该 FU src2 的功能单元</li><li>Rⱼ[FU]：记录该 FU 的 src1 是否 ready 的状态</li><li>Rₖ[FU]：记录该 FU 的 src2 是否 ready 的状态</li></ul> |
| **寄存器状态表 Register Status** | 记录每个寄存器的状态，指示哪个功能单元会写入本寄存器 |

第一张表用来判断指令的执行状态，当一条指令走完所有 stage，就可以从表格中删除，为其他指令腾出空间。第二张和第三张表格配合在一起，记录了所有的冒险。因为每条指令的源操作数可能是前一条指令的结果，所以必须记录本条指令的源操作数是谁产生的，即 Qⱼ[FU] 和 Qₖ[FU]；而本条指令的结果也可能是后续指令的源操作数，所以也必须记录目的寄存器的内容是由本条指令产生的，即 Result[dst]。

算法伪代码如下：

**发射阶段**

```
#!text
// 在发射阶段：
// 1. 等待解除 结构冒险 和 数据冒险 WAW + WAR
// 2. 发射当前指令
// 3. 用当前指令的信息更新 FU 的状态表

function issue(op, dst, src1, src2)
    wait until (!Busy[FN] AND !Result[dst]);    // 确认 FU 并且等待解除所有冒险
    Busy[FU] ← Yes;                             // 设置 FU 的状态为 busy
    Op[FU] ← op;                                // 记录 FU 执行的具体操作
    Fᵢ[FU] ← dst;                               // 记录 FU 的 目的寄存器序号
    Fⱼ[FU] ← src1;                              // 记录 FU 的 源寄存器 1 序号
    Fₖ[FU] ← src2;                              // 记录 FU 的 源寄存器 2 序号
    Qⱼ[FU] ← Result[src1];                      // 查表、记录产生 src1 的 FU 名称，如果为 0 表示不需要任何 FU 写这个寄存器
    Qₖ[FU] ← Result[src2];                      // 差表、记录产生 src2 的 FU 名称，如果为 0 表示不需要任何 FU 写这个寄存器
    Rⱼ[FU] ← Qⱼ[FU] == 0;                       // 记录 src1 是否 ready
    Rₖ[FU] ← Qₖ[FU] == 0;                       // 记录 src2 是否 ready
    Result[dst] ← FU;                           // 在寄存器状态表中记录 dst 寄存器的值是由当前 FU 产生的
```

**读操作数**

```
#!text
// 在读操作数阶段：
// 1. 等待解除所有 RAW
// 2. 把数值从源寄存器中读出来
// 3. 设置源寄存器的状态为 No（Yes 表示寄存器有新值待读出；No 表示寄存器还未写入新值；读出后设置为 No）

function read_oprands(FU)
    wait until (Rⱼ[FU] AND Rₖ[FU]);     // 等待解除 RAW
    Rⱼ[FU] ← No;                        // 读出数据后把对应的源寄存器状态设置为 No，表示数据已被读出
    Rₖ[FU] ← No;
    Qⱼ[FU] ← Null;                      // RAW 已解除，不再需要记录源操作数的产生源头，复位
    Qₖ[FU] ← Null;
```

**执行阶段**

```
#!text
// 在执行阶段：FU 执行具体操作

function execute(FU)
    // Execute whatever FU must do
```

**写回阶段**

```
#!text
// 在写回阶段：
// 1. 等待解除所有 WAR
// 3. 设置 FU 的 busy 状态为 No，为后续指令做准备

function write_back(FU)
    wait until (∀f {(Fⱼ[f]≠FₖFU] OR Rⱼ[f]=No) AND (Fₖ[f]≠Fᵢ[FU] OR Rₖ[f]=No)})  // 等待解除所有 WAR，即所有活跃指令都不需要读当前要写入的目标寄存器
    foreach f do
        if Qⱼ[f]=FU then Rⱼ[f] ← Yes;       // 如果某个 FU 要用到当前结果，将它的 ready 设置为 Yes 表明数据已经准备好
        if Qₖ[f]=FU then Rₖ[f] ← Yes;
    Result[Fᵢ[FU]] ← 0;                     // 目标寄存器的值已写入，为后序指令解除 RAW 和 WAW
    Regfile[Fᵢ[FU]];                        // 执行结果写回目标寄存器
    Busy[FU] ← No;                          // 复位 FU 的 busy 状态，为后序指令做准备
```

## Other Techniques

一般来说 scoreboard 都是顺序发射，如果当前指令用到的功能单元处于 busy 状态，Scoreboard 会暂停 issue stage，此时即使有空闲的功能单元也无法执行后续指令，必须要等到解决当前指令的结构冒险。也就是说 scoreboard 只能检查数据冒险，但是无法消除。下面这个例子中，因为前面的 fadd.d 依赖于 fdiv.d，而 fdiv.d 执行时间较长，所以会出现流水线暂停，导致和前序指令之间没有任何数据冒险的 fsub.d 也会被阻塞住。

```
#!asm
; structural hazard
fdiv.d  f0 , f2, f4
fadd.d  f10, f0, f8
fsub.d  f12, f8, f14
```

一些寄存器重命名技术，比如 Tomasolu 算法，可以避免上述结构冒险导致的流水线暂停的同时还能消除 WAW 和 WAR，一举两得，获得潜在的性能提升。

## Ref

[Scoreboard wiki](https://en.wikipedia.org/wiki/Scoreboarding)

[Computer Architecture Appendix C.7](https://book.douban.com/subject/6795919/)