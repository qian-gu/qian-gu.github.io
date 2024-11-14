Title: 计算机体系结构 —— Issue
Date: 2021-01-13 19:21
Category: IC
Tags: CPU, issue, Scoreboard, Tomasulo
Slug: ca-issue
Author: Qian Gu
Series: 计算机体系结构
Status: draft
Summary: 总结指令发射关键技术

[TOC]

## In-Order vs Out-of-Order Execution

**顺序执行**：只有一条 pipeline，所有指令必须按照程序序流过完整的 pipeline（如经典 5 级流水）。

缺点：前序指令发生阻塞时，后续的不相关指令因为 pipeline stall 无法执行，性能变差。

解决方法：绕过前序发生阻塞的指令，继续执行后序指令，即乱序执行。核心思想是 **硬件让不受其他指令影响的指令尽可能早执行，尽早结束，这样才能获取到最高性能。**

如何实现乱序执行：

- pipeline 必须有多条，是后续指令绕行的必要条件
- 动态调度必须维护数据正确性，遵守所有的数据冒险和结构冒险

## Dynamic Scheduling

调度算法基本可以分为两大类：

+ 静态调度 static scheduling，由软件工具（编译器）规划指令顺序，避免流水线停顿
+ 动态调度 dynamic scheduling，由硬件完成指令重排序，避免流水线停顿

流水线是 CPU 设计中的基本概念，为了获得尽可能高的性能，人们发明了各种技术使得流水线保持在全速运行状态。其中最关键的就是**动态调度技术**。如[《计算机体系结构》][arch]介绍，

> 现在体系结构的主要矛盾不在运算部件，CPU 中用于做加、减、乘、除的部件只占 CPU 面积的很小一部分，CPU 中的大部分面积被用来给运算部件提供足够的指令和数据。

Scoreboard 和 Tomasulo 都属于动态调度算法。无论哪种方法，为了保证数据正确性，都必须解决以下两类冒险。

[arch]: https://book.douban.com/subject/27190711/

### Hazard

| 类型 | 含义 |
| ----- | ---- |
| 资源冒险（`structual hazard`） | 计算单元一次只能执行一条指令，同时计算多条指令结果不正确 |
| 数据冒险（`data hazard`） | 计算开始前源操作数必须是 ready 状态，计算结果也要在合适的时间写入寄存器 |

根据读写关系数据冒险可以分为 3 种：

+ `RAW` (Read-After-Write)：读源操作数的时间不能太早，要等数据准备好再读，避免读到无效数据
+ `WAW` (Write-After-Write)：写回执行结果的时间不能太早，要等到前序指令把旧值写入后再写入新值，避免被旧值覆盖
+ `WAR` (Write-After-Read)：写回执行结果的时间不能太早，要等到前序指令把旧值读走后再写入新值，避免覆盖仍然有用的旧值

产生 WAW 和 WAR 的根本原因就是因为寄存器数量太少了（RV32I 只有 32 个通用寄存器），前后指令流要复用同一个寄存器。假设有无数个寄存器可用，那么自然就不存在 WAW、WAR 的问题。

!!! tip
    1. 数据冒险不包含 RAR(Read-After-Read) 的原因很简单：RAR 对结果的正确性没有任何影响
    2. 这三种数据冒险中，RAW 被称为“真数据冒险”，因为另外两种冒险实际上并不是真正的数据依赖，而是“名字相关”，即只是因为使用同一个寄存器名而导致的相关性
    3. WAW 和 WAR 可以通过**寄存器重命名**技术进行规避，而 RAW 是无法规避的，只能进行流水线停顿。为了减少停顿，一般通过动态调度降低性能损失：
        + 数据旁路 Data Bypass Forward：把前序的结果尽可能早地传递给后续需要用它的指令，减少等待时间
        + 执行后续无关指令，直接消灭等待
    3. `Tomasulo 算法` 可以通过 `保留站` 和 `ROB` 实现寄存器重命名，达到上述两个效果

## Scoreboard

Scoreboard 是一种非常古老的动态调度算法，发明于 1964 年，最早用在的 CDC 6600 计算机上。Scoreboard 可以使得 CPU 乱序执行（Out-of-Order Execution），从而提高 CPU 的性能。

Scoreboard 在整个流水线的多个阶段遵守数据冒险和结构冒险：

+ **发射 Issue**：检查本条指令要写哪些寄存器，并记录下相关信息。为了保证 结构冒险和 WAW，发射本条指令有两个条件必须满足：
    + 前序要写回相同寄存器的指令执行结束
    + 相关功能单元不是 busy 状态
+ **读操作数 Read Operands**：在把指令成功发射给相关功能单元之后，还需要准备好源操作数。为了保证 RAW，读取源操作数必须要等到前序写对应寄存器的指令执行结束后再进行
+ **执行 Execution**：操作数准备就绪后功能单元开始执行，在执行结束时会通知 scoreboard
+ **写回 Write Back**：执行结束后的结果也不能马上写入到目标寄存器，因为要保证 WAR，即要等到前序要读目标寄存器的指令把数据读走之后才能把新值写入寄存器

### Scoreboard Algorithm

Scoreboard 是一种集中式的控制逻辑，可以同时识别资源冒险和数据冒险，其核心思想是：**记录每一条指令需要用到的寄存器序号和功能单元的状态，持续跟踪，直到数据依赖解除后才把指令发射到相关功能单元。当功能单元执行完毕，结果写回到寄存器后更新相关状态，为后续指令做准备。**

为了实现这个目的，scoreboard 维护了 3 张表：

| 表格 | 功能 |
| ----- | ----- |
| **指令状态表 Instruction Status** | 记录每条指令的状态，指示处于流水线的哪个 stage |
| **功能单元状态表 Functional Unit Status** | 记录每个功能单元的状态，表的深度 = 功能单元的数量，每个 entry 记录包含 9 个字段<ul><li>Busy[FU]：记录该 FU 的状态</li><li>Op[FU]：记录该 FU 执行的操作</li><li>Fᵢ[FU]：记录该 FU 要写入的寄存器号</li><li>Fⱼ[FU]：记录该 FU 读取的第一个源操作数 src1 的寄存器号</li><li>Fₖ[FU]：记录该 FU 读取的第二个源操作数 src2 的寄存器号</li><li>Qⱼ[FU]：记录产生该 FU src1 的功能单元</li><li>Qₖ[FU]：记录产生该 FU src2 的功能单元</li><li>Rⱼ[FU]：记录该 FU 的 src1 是否 ready 但未被读取的状态</li><li>Rₖ[FU]：记录该 FU 的 src2 是否 ready 但未被读取的状态</li></ul> |
| **寄存器状态表 Register Status** | 记录每个寄存器的状态，指示哪个功能单元会写入本寄存器 Result[dst] |

第一张表用来判断指令的执行状态，当一条指令走完所有 stage，就可以从表格中删除，为其他指令腾出空间。第二张和第三张表格配合在一起，记录了所有的冒险。因为每条指令的源操作数可能是前一条指令的结果，所以必须记录本条指令的源操作数是谁产生的，即 Qⱼ[FU] 和 Qₖ[FU]；而本条指令的结果也可能是后续指令的源操作数，所以也必须记录目的寄存器的内容是由本条指令产生的，即 Result[dst]。

算法伪代码如下：

**1. 发射阶段**

    #!text
    // 在发射阶段：
    // 1. 等待解除 结构冒险 和 数据冒险 WAW
    // 2. 发射当前指令
    // 3. 用当前指令的信息更新 FU 的状态表
    
    function issue(op, dst, src1, src2)
        wait until (!Busy[FU] AND !Result[dst]);    // 确认 FU 无结构冒险和 WAW 冒险
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

**2. 读操作数**

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

**3. 执行阶段**

    #!text
    // 在执行阶段：FU 执行具体操作
    
    function execute(FU)
        // Execute whatever FU must do

**4. 写回阶段**

    #!text
    // 在写回阶段：
    // 1. 等待解除所有 WAR
    // 3. 设置 FU 的 busy 状态为 No，为后续指令做准备
    
    function write_back(FU)
        wait until (∀f {(Fⱼ[f]≠Fᵢ[FU] OR Rⱼ[f]=No) AND (Fₖ[f]≠Fᵢ[FU] OR Rₖ[f]=No)})  // 遍历 scoreboard entry，等待解除所有 WAR，即所有活跃指令都不需要读当前要写入的目标寄存器
        foreach f do
            if Qⱼ[f]=FU then Rⱼ[f] ← Yes;       // 遍历 scoreboard，如果某个 FU 要用到当前结果，将它的 ready 设置为 Yes 表明数据已经准备好
            if Qₖ[f]=FU then Rₖ[f] ← Yes;
        Result[Fᵢ[FU]] ← 0;                     // 目标寄存器的值已产生
        Regfile[Fᵢ[FU]] ← computed value;       // 执行结果写回目标寄存器
        Busy[FU] ← No;                          // 复位 FU 的 busy 状态

### Scoreboard Summary

特点：

- 发射阶段：解决结构冒险 和 WAW 时面向 FU 的思路，深度为 FU 的数量
- 读操作数阶段：解决 RAW 时面向 FU，检查改 FU entry 的 source1 和 source2 标记
- 写回阶段：解决 WAR 时面向 register，Result[dst] 的深度为 RF 的数量
- out-of-order dispatch，execution, complete, in-order issue

优点：

- 允许乱序执行
- 实现简单

缺点：

- scoreboard 无法消除 WAR 和 WAW
- 结构冒险会 stall 所有 pipeline，因为是 in-order issue，所以一旦发生 stall，后续任何类型的指令都无法继续发射
- 每个 FU 只能发射一条指令，无法 pipeline（因为每个 FU 在 scoreboard 中只有一条 entry）
- scoreboard 的 write-back 不是顺序的，对程序调试提出挑战

一般来说 scoreboard 都是顺序发射，如果当前指令用到的功能单元处于 busy 状态，Scoreboard 会暂停 issue stage，此时即使有空闲的功能单元也无法执行后续指令，必须要等到解决当前指令的结构冒险。也就是说 scoreboard 只能检查冒险，但是无法消除。下面这个例子中，因为前面的 fadd.d 依赖于 fdiv.d，而 fdiv.d 执行时间较长，所以会出现流水线暂停，导致和前序指令之间没有任何数据冒险的 fsub.d 也会被阻塞住。

    #!asm
    ; structural hazard
    fdiv.d  f0 , f2, f4
    fadd.d  f10, f0, f8
    fsub.d  f12, f8, f14

一些寄存器重命名技术，比如 Tomasulo 算法，可以避免上述结构冒险导致的流水线暂停的同时还能消除 WAW 和 WAR，一举两得，获得潜在的性能提升。

## Register Renaming

分析数据冒险 WAW 和 WAR 的产生原因，就可以知道是因为前后两条指令要操作同一个寄存器，而更深层次的根本原因就是因为 ISA 规定的 register 太少，所以不同指令不得不复用相同寄存器。假设如果有无数个寄存器可用，一条新的指令需要写回结果，给它分配一个新的寄存器即可,那么就不存在 WAW 和 WAR 了。现实中我们不可能真的有无数个寄存器，但是我们可以退而求其次，假设我们实际上的寄存器数量比 ISA 规定的多，那么在条件满足的情况下硬件上“偷偷把指令使用的寄存器重命名成另外一个寄存器”，让软件看不到这一细节，那么就能在不改变任何软件的前提下，解决 WAR 和 WAW。

所以寄存器重命名的核心思想就是：**把指令中的寄存器标号看作是位置 locations，而不是名字 names**：

+ locations 比 names 多
+ 动态地把 names 映射到 locations 上
+ 映射表 map table 保存了具体的映射关系
    + 写寄存器：分配新 location，并且在映射表 map table 中记录相关信息
    + 读寄存器：在 map table 中查找最近一次该 name 映射的 location
    + 小细节：必须在合适的时间点回收映射表项，即 de-allocate

下面是一个 renaming 的例子：

![renaming](/images/ca-issue/renaming.png)

!!!note
    rename 的两种实现方式：

    - GPR 和 PRF 隔离开
    - GPR 和 PRF 混合在一起，任意一个 PRF 在不同时刻都有可能是 GPR

    tomasulo 中 GPR 和 RS 在物理上是分离的，且 RS 充当了类似 PRF 的效果，所以属于第一种 rename 方案，但并不彻底：

    - WAW：把 new value 写入 GPR，old value 广播给需要的 FU
    - WAR：因为 issue 时就把 rs 读取出来了，所以不会发生

## Tomasulo

为了解决 scoreboard 的缺点，动态调度算法（绝大多数是 Tomasulo 及其变种）做了改进。

+ **最终目标**：**前序指令的阻塞不能影响后序指令的执行**
+ **核心思想**：**把这两类冒险解偶，两类冒险之间相互不影响**
+ **实现方式**：**把译码阶段拆分成两个阶段，发射和读操作数,发射阶段检查结构冒险，读操作数阶段检查数据冒险**

为了防止前序有数据冒险的指令阻塞后续不相关指令，就必须找个临时存储的地方把前序指令保存起来，这样就可以把流水线腾出来执行后序指令，而这个临时存储的地方就是 `保留站 RS`。所以本质上，保留站是一个把指令从有序变成乱序的结构。虽然指令还是顺序发射，但是指令执行是乱序的，自然指令完成也是乱序的。

Tomasulo 算法是一种硬件动态调度算法，可以实现乱序执行，从而更加充分地使用多个执行单元。它是 Robert Tomasulo 于 1967 在 IBM 发明的，首次使用在 IBM System/360 Model 91 的 FPU 上。他也因为这个发明在 1997 年获得了 Eckert-Mauchly 奖。

Tomasulo 的主要发明包括了三部分，

+ 硬件重命名的方法
+ 给每个执行单元分配一个保留站 (reservation station)
+ 一个广播数据的通用数据总线 (Common Data Bus)

![tomasulo](https://upload.wikimedia.org/wikipedia/commons/f/f8/Tomasulo_Architecture.png)

### Common Data Bus

`CDB`(Common Data Bus) 是数据总线，它把保留站和功能单元直接连起来，可以“在提高并行性的同时保持了优先权”。
功能单元访问数据时不再需要涉及寄存器，中间数据不必经过寄存器倒一次手，而是由 CDB 把结果直接广播到总线上，保留站监听总线，得到有效数据后就可以开始执行，避免了寄存器访问的仲裁。

### Reservation Station

`RS` (Reservation Station) 保留站也叫做调度器 (scheduler)，保留的是已发射出来的指令和数据。每个功能单元都有自己的保留站，所以它是一种分布式的控制方案，而 scoreboard 是一种集中化管理。当一条指令被发射到保留站时，会同时检查源操作数状态，

+ 如果寄存器中的源操作数已经准备好了，那么直接把源操作数写入到 RS 中（Vⱼ 和 Vₖ）
+ 如果寄存器中的源操作数还没有准备好，那么在保留站中存下产生这个数的 RS 序号（Qⱼ 和 Qₖ）

这样，RS 中就保存了所有的必要信息。只需不断监听 CDB，等待数据 ready 后把数据更新到 RS 中，然后就可以真正发射给功能单元开始执行。

保留站的数据结构 `RS` 本质上是一张表，每个 entry 是保留站的一项记录，可以记录一条指令的信息。每一个 entry 包含下面 7 个字段：

| 符号 | 含义 |
| ---- | ---- |
| Op | 要执行的操作 |
| Qⱼ, Qₖ | 产生源操作数的 RS 标号（0/blank 表示数据已经 ready，保存在 Vⱼ, Vₖ 中） |
| Vⱼ, Vₖ | 源操作数的值 |
| Busy | 1 = 被占用, 0 = 没有被占用 |
| A | Load / Store 的内存地址 |

示意图如下：

```text
                Reservation Station(RS)
  +------+------+------+------+------+------+------+
  |  Op  |  Qⱼ  |  Vⱼ  |  Qₖ  |  Vₖ  | Busy |  A   |
  +------+------+------+------+------+------+------+
1 |      |      |      |      |      |      |      |
  +------+------+------+------+------+------+------+
2 |      |      |      |      |      |      |      |
  +------+------+------+------+------+------+------+
3 |      |      |      |      |      |      |      |
  +------+------+------+------+------+------+------+
4 |      |      |      |      |      |      |      |
  +------+------+------+------+------+------+------+
5 |      |      |      |      |      |      |      |
  +------+------+------+------+------+------+------+
```

需要保存字段 A 的原因是有些指令并不是寄存器寻址，而是使用立即数，比如 RISC-V 中的 I 类型指令（比如 Load / Store 指令)，所以要分配一个字段来保存这个立即数。

显然，因为保存了操作数，而且要把所有执行单元的结果和所有已保存的的地址做比较，所以硬件开销很大，无法做得很深。

!!!note
    RS 的作用和 scoreboard 的 entry 类似，都是面向 FU 的，记录该 FU 执行的指令信息，所以两者的字段很多都是相同的。不同之处：

    - scoreboard 中每个 FU 只有一条 entry，tomasulo 中每个 FU 都有一个多 entry 的 RS
    - scoreboard 的 Vⱼ 和 Vₖ 保存寄存器编号，tomasulo 中的 Vⱼ 和 Vₖ 保存 value
    - scoreboard 的 Qⱼ 和 Qₖ 记录的是 FU，又因为每个 FU 只记录一条 entry，所以 scoreboard 无法做到重命名；而 tomasulo 的 Qⱼ 和 Qₖ 记录的是 RS 序号，实际上就是在做 rename，即用 RS 编号而不是寄存器编号标记数据来源

因为每个 register 可能被多个寄存器写入，经过重命名之后需要记录该 register 最终由哪条指令写入，所以每个 register 也需要增加一个字段 Qᵢ 来记录这个信息。

| 符号 | 含义 |
| ---- | ---- |
| Qᵢ | 写入寄存器的 RS 标号（0/blank 表示不需要等待其他 FU 写入新值） |

Register File 的数据结构 `RegisterStat` 如下所示：

```text
     RegisterStat
   +------+-------+
   |  Qᵢ  | value |
   +------+-------+
r0 |      |       |
   +------+-------+
r1 |      |       |
   +------+-------+
r2 |      |       |
   +------+-------+
r3 |      |       |
   +------+-------+
```

!!!note
    该结构和 scoreboard 中的相同。

实际上还需要一张表来记录指令所处的阶段，如下所示。当一条指令完成所有阶段，就可以从表中删除。

```text
                      Record Buffer
+-------------+-------+---------+--------------+---------+
| Instruction | Issue | Execute | Write Result |  Commit |
+-------------+-------+---------+--------------+---------+
|             |       |         |              |         |
+-------------+-------+---------+--------------+---------+
|             |       |         |              |         |
+-------------+-------+---------+--------------+---------+
|             |       |         |              |         |
+-------------+-------+---------+--------------+---------+
|             |       |         |              |         |
+-------------+-------+---------+--------------+---------+
|             |       |         |              |         |
+-------------+-------+---------+--------------+---------+
```

!!!note
    该结构和 scoreboard 中的相同。

### Tomasulo Algorithm

!!!note
    因为 tomasulo 的 RS 直接记录了源操作数的 value，所以相比于 scoreboard 调度步骤中少了读操作数这一步。

**1. issue**

在发射阶段，所有指令 in-order issue 到 RS 中，判断能否发送的唯一条件就是 RS 是否有空闲的 entry。寄存器重命名就是在这里实现，这一步可以消除 WAW 和 WAR。具体步骤：

当 RS 有空闲 entry 时，从指令队列头部取出一条新指令发射到 RS 中，

+ 如果这条指令的操作数已经在寄存器中准备就绪，那么复制该 value 到 RS entry 中，标记该数据已 ready
+ 否则，操作数并没有就绪，那么使用标记产生该源操作数的 RS 序号（执行本指令的 FU 必须记录产生真实值的 RS 标号，这样才能跟踪操作数什么时候准备好）

伪代码如下：

    #!text
    // 1. 普通计算指令
    function issue()
        wait until station r empty;             // 指令译码找到执行本指令的 FU，等待它的保留站有空余项 r，表明可以发射本指令到 RS 中
        // step1. 检查源操作数 rs1，更新 RS 对应 entry
        if (RegisterStat[rs1].Qᵢ != 0) {         // 本指令的源操作数 rs1 还没有准备好
            RS[r].Qⱼ ← RegisterStat[rs1].Qᵢ;        // 在保留站 r 中记录 rs1 的产生源头（另一个保留站序号）
        }
        else {                                  // 否则，rs1 已经准备好
            RS[r].Vⱼ ← RegisterStat[rs1].Value;     // 把有效的 rs1 更新到 r 的 Vⱼ 字段
            RS[r].Qⱼ ← 0;                           // 同时把 rs1 对应 Qⱼ 设置为 0，表示数据已经 ready
        }
        // step2. 检查源操作数 rs2，更新 RS 对应 entry（过程同 rs1）
        if (RegisterStat[rs2].Qᵢ != 0) {
            RS[r].Qₖ ← RegisterStat[rs2].Qᵢ;
        }
        else {
            RS[r].Vₖ ← RegisterStat[rs2].Value;
            RS[r].Qₖ ← 0;
        }
        RS[r].Busy ← yes;                   // 把 r 设置为 Busy，占用 FU 等待执行本指令
        // step3. 本指令要写回到 rd，所以把 r 更新到 rd 的 Qᵢ 字段
        RegisterStat[rd].Qᵢ ← r;
    
    // 2. Load 指令: 读取 address(rs1 + imm) 的数据到 rd
    function issue()
        wait until buffer r empty;
        // step1. load 指令 rs1 操作和普通指令相同
        if (RegisterStat[rs1].Qᵢ != 0) {
            RS[r].Qⱼ ← RegisterStat[rs1].Qᵢ;
        }
        else {
            RS[r].Vⱼ ← RegisterStat[rs1].Value;
            RS[r].Qⱼ ← 0;
        }
        // step2. load 指令无 rs2，无操作
        // step3. load 指令需要记录 imm
        RS[r].A ← imm;
        RS[r].Busy ← yes;
        // step4. load 指令有 rd，需要记录 rd 由本 entry 产生
        RegisterStat[rd].Qᵢ ← r;

    // 3. Store 指令：保存 rs2 数据到 address(rs1 + imm)
    function issue()
        wait until buffer r empty;
        // step1. store 指令 rs1 操作和普通指令相同
        if (RegisterStat[rs1].Qᵢ != 0) {
            RS[r].Qⱼ ← RegisterStat[rs1].Qᵢ;
        }
        else {
            RS[r].Vⱼ ← RegisterStat[rs1].Value;
            RS[r].Qⱼ ← 0;
        }
        // step2. store 指令 rs2 操作和普通指令相同
        if (RegisterStat[rs2].Qᵢ != 0) {
            RS[r].Qₖ ← RegisterStat[rs2].Qᵢ;
        }
        else {
            RS[r].Vₖ ← RegisterStat[rs2].Value;
            RS[r].Qₖ ← 0;
        }
        // step3. store 指令需要记录 imm
        RS[r].A ← imm;
        RS[r].Busy ← yes;
        // step4. store 指令无 rd

**2. execute**

在执行阶段，不断监听 CDB 来获取最新的 rs1/rs2，等到所有数据冒险（RAW）全部解除后才能开始执行。

+ 如果有任何一个源操作数没有 ready，就一直监听 CDB 直到操作数有效
+ 当所有源操作数都是 ready 后，如果指令是条 Load 或 Store，
    + 计算正确的地址
        + 如果是 Load 指令，memory 单元可访问后马上执行
        + 否则是 Store 指令，等待写数据有效后再写入 memory
+ 否则为普通指令，在 ALU 执行本指令：发送到相应的 FU 中

伪代码如下：

    #!text
    // 1. 普通计算指令
    function execute()
        wait until (RS[r].Qⱼ == 0) and (RS[r].Qₖ == 0);  // 等待所有 rs（rs1 和 rs2）都解除数据冒险后，才开始执行
        compute result: oprands are in Vⱼ and Vₖ;        // 计算结果，rs1 和 rs2 的值分别保存在 Vⱼ 和 Vₖ 字段中

    // 2. Load 指令
    function execute()
        wait until (RS[r].Qⱼ == 0) and (r is head of load-store queue);  // 等待所有 rs（rs1）都解除数据冒险且读写保序后，才开始执行
        read from Mem[RS[r].Vⱼ+RS[r].imm];                               // 读取数据

    // 3. Store 指令
    function execute()
        wait until (RS[r].Qⱼ == 0) and (RS[r].Qₖ == 0) and (r is head of load-store queue);  // 等待所有 rs（rs1 和 rs2）都解除数据冒险且读写保序后，才开始执行
        Mem[RS[r].Vⱼ+RS[r].imm] = RS[r].Vₖ;                                                  // 保存数据

**3. write back**

在写回阶段，ALU 的结果要写回 rd，Store 指令要把数据写入 memory。

+ 如果是 ALU 指令
    + 如果结果 ready，把结果发送到 CDB 上，由 CDB 广播给相关的 register 和 RS
+ 否则，是 Store 指令，把数据写入 memory

伪代码如下：

    #!text
    // 1. 普通指令 or Load 指令
    function write_back()
        wait until execution complete at `r` & CDB available;  // 等待本指令的结果 ready，并且有访问 CDB 的权限
        // step1. 遍历 RegisterStat，用 result 更新 RegisterStat
        ∀x (if (RegisterStat[x].Qᵢ == r) {                     // 如果某个寄存器在等待用本指令的结果写入
            RegisterStat[x].Value ← result;                         // 结果写入该寄存器
            RegisterStat[x].Qᵢ ← 0;                                 // 同时该寄存器的 Qᵢ 状态复位成 0
        };
        // step2. 遍历 RS，用 result 更新 rs1（如果匹配上）
        ∀x (if (RS[x].Qⱼ == r) {                               // 检查每个 RS 的每一项的 rs1 是否在等待本指令的结果
            RS[x].Vⱼ ← result;                                      // 用结果更新该项的 Vⱼ 字段
            RS[x].Qⱼ ← 0;                                           // 同时复位该项的 Qⱼ 字段
        };
        // step3. 遍历 RS，用 result 更新 rs2（如果匹配上）
        ∀x (if (RS[x].Qₖ == r) {                               // 同上，检查 RS 的 rs2 字段是否在等待本指令的结果
            RS[x].Vₖ ← result;
            RS[x].Qₖ ← 0;
        };
        RS[r].Busy ← no;                                       // 指令执行结束，释放 FU 资源

    // 2. Store 指令
    function write_back()
        wait until execution complete at `r`;  // 等待本指令的结果 ready
        RS[r].Busy ← no;

### Tomasulo Summary

优点：

- RS 可以缓冲多条指令，平稳了发送速度的波动
- register 只写最新的 value，减少无谓的中间写，解决了 WAW 问题
- RS 直接保存源操作数的 value，解决了 WAR 问题

缺点：

- RS 可能同时多条指令都 ready，需要仲裁选择一条执行
- 可能会有 FU 同时产生结果，但是只有一条 CDB，所以写回时仲裁 or 多条 CDB（代价大）
- 无法实现精确异常（精确异常必须 in-order commit）

## ROB

为了解决 tomasulo 无法实现精确异常的问题，设计人员提出了 ROB(ReOrder Buffer)，目的是让乱序执行的指令被顺序地提交，这个设计理念已经成为乱序处理器的基石，可以说没有 ROB 就没有现代的乱序处理器。

ROB 的核心思想是记录下程序序，一条指令执行完成后不会马上 commit，而是先到 buffer 中等待，等前序指令都 commit 完毕，才可以 commit 本指令。想象一个 FIFO，指令在发射时入队，在 commit 时出队，通过这个 FIFO 就可以实现指令的按序 commit。

ROB 对 tomasulo 的增强：

1. 新增了一个 ROB 模块
2. CDB 不再直接写入 GPR，而是写入 ROB
3. 发射指令时需要从 ROB 中读取 rs1/rs2

## Ref

[Scoreboard wiki](https://en.wikipedia.org/wiki/Scoreboarding)

[Computer Architecture Appendix C.7](https://book.douban.com/subject/6795919/)

[Tomasulo wiki](https://en.wikipedia.org/wiki/Tomasulo%27s_algorithm)

[Revervation Station wiki](https://en.wikipedia.org/wiki/Reservation-station)

[Computer Architecture - section 3.4](https://book.douban.com/subject/6795919/)

[ECE252 duke](http://people.ee.duke.edu/~sorin/ece252/lectures/4.2-tomasulo.pdf)
