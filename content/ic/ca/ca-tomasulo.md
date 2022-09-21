Title: CPU 关键技术 —— Tomasulo
Date: 2021-01-13 19:21
Category: IC
Tags: CPU, Tomasolu
Slug: cpu-tomasolu
Author: Qian Gu
Series: CPU 关键技术
Status: draft
Summary: 总结 Tomasolu 算法

## Why need Tomasolu

为了尽可能地获得高性能，人们发明了动态调度算法，比如 scoreboard，但是 scoreboard 无法充分发挥指令的并行性，当前指令的 FU 发生结构冒险时会暂停 issue，导致后续没有结构冒险的指令也无法执行。Tomasolu 算法利用寄存器重命名算法可以避免结构冒险导致的流水线暂停，还可以解决 WAW 和 WAR，一举两得。

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

![renaming](/images/cpu-tomasolu/renaming.png)

## Dynamic Scheduling

调度算法基本可以分为两大类：

+ 静态调度 static scheduling，由软件工具（编译器）规划指令顺序，避免流水线停顿
+ 动态调度 dynamic scheduling，由硬件完成指令重排序，避免流水线停顿

关于这两种方式的优缺点不再赘述，scoreboard 是一种动态调度算法，它可以检测所有类型的冒险，动态地调度不同功能单元执行指令。但是 scoreboard 的问题有两个：

+ 结构冒险会导致流水线暂停
+ 无法消除 WAW 和 WAR，也会导致流水线暂停

比如下面这个例子：

```
#!asm
; structural hazard
fdiv.d  f0 , f2, f4
fadd.d  f10, f0, f8
fsub.d  f12, f8, f14
```

为了解决这个问题，动态调度算法（绝大多数是 Tomasolu 及其变种）做了改进。

+ **最终目标**：**前序指令的阻塞不能影响后序指令的执行**
+ **核心思想**：**把这两类冒险解偶，两类冒险之间相互不影响**
+ **实现方式**：**把译码阶段拆分成两个阶段，发射和读操作数,发射阶段检查结构冒险，读操作数阶段检查数据冒险**

为了防止前序有数据冒险的指令阻塞后续不相关指令，就必须找个临时存储的地方把前序指令保存起来，这样就可以把流水线腾出来执行后序指令，而这个临时存储的地方就是 `保留站`。所以本质上，保留站是一个把指令从有序变成乱序的结构。虽然指令还是顺序发射，但是指令执行是乱序的，自然指令完成也是乱序的。

## What is Tomasulo

Tomasolu 算法是一种硬件动态调度算法，可以实现乱序执行，从而更加充分地使用多个执行单元。它是 Robert Tomasolu 于 1967 在 IBM 发明的，首次使用在 IBM System/360 Model 91 的 FPU 上。他也因为这个发明在 1997 年获得了 Eckert-Mauchly 奖。

Tomasolu 的主要发明包括了三部分，

+ 硬件重命名的方法
+ 给每个执行单元分配一个保留站 (reservation station)
+ 一个广播数据的通用数据总线 (Common Data Bus)

### Common Data Bus

`CDB`(Common Data Bus) 是数据总线，它把保留站和功能单元直接连起来，可以“在提高并行性的同时保持了优先权”。
功能单元访问数据时不再需要涉及寄存器，中间数据不必经过寄存器倒一次手，而是由 CDB 把结果直接广播到总线上，保留站监听总线，得到有效数据后就可以开始执行，避免了寄存器访问的仲裁。

### Reservation Station

`RS` (Reservation Station) 保留站也叫做调度器 (scheduler)，每个功能单元都有自己的保留站，所以它是一种分布式的控制方案，而 scoreboard 是一种集中化管理。当一条指令被发射到保留站时，会同时检查源操作数状态，

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

```
#!text
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

因为每个 register 可能被多个寄存器写入，经过重命名之后需要记录该 register 最终由哪条指令写入，所以每个 register 也需要增加一个字段 Qᵢ 来记录这个信息。

| 符号 | 含义 |
| ---- | ---- |
| Qᵢ | 写入寄存器的 RS 标号（0/blank 表示不需要等待其他 FU 写入新值） |

Register File 的数据结构 `RegisterStat` 如下所示：

```
#!text
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

实际上还需要一张表来记录指令所处的阶段，如下所示。

```
#!text
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

### Stage 1: issue

在发射阶段，如果所有操作数和 RS 都准备好了就可以开始执行指令，否则会暂停执行。寄存器重命名就是在这里实现，这一步可以消除 WAW 和 WAR。具体步骤：

从指令队列头部取出一条新指令，

+ 如果这条这里指令的操作数已经在寄存器中准备就绪，那么
    + 如果对应的 FU 是空闲的，就可以把这条指令发射给它开始执行
    + 否则，没有空闲 FU 意味着结构冒险，暂停本条指令直到该 FU 的 RS 有空闲空间
+ 否则，操作数并没有就绪，那么就使用一个虚拟的值（即 RS 序号）。执行本指令的 FU 必须记录产生真实值的 RS 标号，这样才能跟踪操作数什么时候准备好

```
#!text
// 1. 非 Load/Store 指令
function issue()
    wait until station r empty;         // 指令译码找到执行本指令的 FU，等待它的保留站有空余项 r，表明可以发射本指令到 RS 中
    if (RegisterStat[rs].Qᵢ != 0) {     // 本指令的源操作数 rs 还没有准备好
        RS[r].Qⱼ ← RegisterStat[rs].Qᵢ;     // 在保留站 r 中记录 rs 的产生源头（另一个保留站序号）
    }
    else {                              // 否则，rs 已经准备好
        RS[r].Vⱼ ← Regs[rs];                // 把有效的 rs 更新到 r 的 Vⱼ 字段
        RS[r].Qⱼ ← 0;                       // 同时把 rs 对应 Qⱼ 设置为 0，表示数据已经 ready
    }
    if (RegisterStat[rt].Qᵢ != 0) {          // 对第二个源操作数 rt 相同处理
        RS[r].Qₖ ← RegisterStat[rt].Qᵢ;
    }
    else {
        RS[r].Vₖ ← Regs[rt];
        RS[r].Qₖ ← 0;
    }
    RS[r].Busy <= yes;                  // 把 r 设置为 Busy，占用 FU 等待执行本指令
    RegisterStat[rd].Qᵢ ← r;            // 本指令要写回到 rd，所以把 r 更新到 rd 的 Qᵢ 字段

// 2. Load/Store 指令
    RS[r].A ← imm;                      // 只需要把 rt 相关逻辑修改成对 A 字段的操作即可
```
### Stage 2: execute

在执行阶段，要等到所有数据冒险（RAW）全部解除后才能开始执行。

+ 如果有任何一个源操作数没有 ready，就一直监听 CDB 直到操作数有效
+ 当所有源操作数都是 ready 后，如果指令是条 Load 或 Store，
    + 计算正确的地址，并把结果保存在 RS 中
        + 如果是 Load 指令，memory 单元可访问后马上执行
        + 否则，是 Store 指令，等待写数据有效后再写入 memory
+ 否则，在 ALU 执行本指令：发送到相应的 FU 中

```
#!text
function execute()
    wait until (RS[r].Qⱼ == 0) and (RS[r].Qₖ == 0);  // 一直等到解除 rs 和 rt 的数据冒险才开始执行
    compute result: oprands are in Vⱼ and Vₖ;        // 计算结果，rs 和 rt 的值分别保存在 Vⱼ 和 Vₖ 字段中
```
### Stage 3: write back

在写回阶段，ALU 的结果要写回 rd，Store 指令要把数据写入 memory。

+ 如果是 ALU 指令
    + 如果结果 ready，把结果发送到 CDB 上，由 CDB 广播给相关的 register 和 RS
+ 否则，是 Store 指令，吧数据写入 memory

```
#!text
function write-back()
    wait until execution complete at `r` & CDB available;  // 等待本指令的结果 ready，并且有访问 CDB 的权限
    ∀x (if (RegisterStat[x].Qᵢ == r) {                     // 如果某个寄存器在等待用本指令的结果写入
        regs[x] ← result;                                       // 结果写入该寄存器
        RegisterStat[x].Qᵢ ← 0;                                 // 同时该寄存器的 Qᵢ 状态复位成 0
    });
    ∀x (if (RS[x].Qⱼ == r) {                               // 检查每个 RS 的每一项的 rs 是否在等待本指令的结果
        RS[x].Vⱼ ← result;                                      // 用结果更新该项的 Vⱼ 字段
        RS[x].Qⱼ ← 0;                                           // 同时复位该项的 Qⱼ 字段
    });
    ∀x (if (RS[x].Qₖ == r) {                               // 同上，检查 RS 的 rt 字段是否在等待本指令的结果
        RS[x].Vₖ ← result;
        RS[x].Qₖ ← 0;
    });
    RS[r].Busy ← no;                                       // 指令执行结束，释放 FU 资源
```

## Improvements

## Ref

[Tomasolu wiki](https://en.wikipedia.org/wiki/Tomasolu-algorithm)

[Revervation Station wiki](https://en.wikipedia.org/wiki/Reservation-station)

[Computer Architecture - section 3.4](https://book.douban.com/subject/6795919/)

[ECE252 duke](http://people.ee.duke.edu/~sorin/ece252/lectures/4.2-tomasulo.pdf)