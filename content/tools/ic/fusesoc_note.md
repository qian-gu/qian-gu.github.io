Title: Fusesoc 小结
Date: 2021-10-30 16:25
Category: Tools
Tags: IC_tools, fusesoc
Slug: fusesoc_summary
Author: Qian Gu
Series: Open IC Tools & Library
Summary: 记录 fusesoc 用法

最近看到很多开源项目都在用 fusesoc 来管理，花了半天时间学习了一下，简单记录一下笔记。

!!! note

    下面的内容作为学习笔记，主要节选翻译自 Fusesoc 的官方文档，最新的完整内容见官网。

# What is Fusesoc

[Fusesoc][fusesoc] 是一个用 python 写的 HDL 管理工具，用一句话解释就是：**HDL 版的 pip + make**，它主要解决 IP core 重用时复杂繁琐的常规性工作，更轻松地实现下面目标：

- 重用已有的 IP core
- 为 compile-time 和 run-time 生成配置文件
- 在多个 simulator 上跑回归
- 在不同平台间移植设计
- 让别人复用你的设计
- 配置 CI

一个设计中包含多个 core，而且可能会有不同的 target，比如仿真、lint、综合等，而且每个 target 也会有多种工具可用，fusesoc 的目标就是把这些 dirty job 管理起来，使得支持 fusesoc 的 IP 相互之间可以轻松地复用。

Fusesoc 还有以下特点：

- **非入侵**：因为 fusesoc 本质上是用特定的描述文件来描述 IP core，这个描述文件不会影响到 IP 本身
- **模块化**：可以为你的工程创建一个 end-to-end 的 flow
- **可扩展**：想支持任何一种新的 EDA 工具时，只需要增加 100 行左右的内容来描述它的用法即可（命令 + 参数）
- **兼容标准**：兼容其他工具的标准格式
- **资源丰富**：标准库目前包含 100 多个 IP（包括 CPU，peripheral, interconnect, SoC 和 util），还可以添加自定义库
- **开源免费**：既可以管理开源项目，也可以用到公司内部项目
- **实战验证**：许多开源项目实际使用验证过

因为 fusesoc 本身是一个 python package，所以我们可以直接用 pip 来安装：

```
#!bash
pip3 install fusesoc
fusesoc --version
```

[fusesoc]: https://github.com/olofk/fusesoc

# How to use

## Concept

要使用 fusesoc 首先就要理解它定义的几个概念，然后就可以用 `fusesoc -h` 来看具体的命令行选项和用法了。

### `core`

工程管理的第一个问题就是解决依赖。

就像 pip 管理 package 一样，fusesoc 以 `core` 作为基本单元。core 指的就是 IP core 设计本身，比如一个 FIFO。每个 core 都有一个 `.core` 文件来描述它，fusesoc 就是通过这个文件来查找、确定某个 core。

一个 core 可以依赖于另外一个 core，比如一个 FIFO core 依赖于一个 SRAM core。SoC 中有很多 IP core，我们只需要指定顶层 core 即可，剩下的依赖分析都交给 fusesoc 来完成即可。一般 core 有两种组织方式：

- core 代码和 .core 文件保存在一个 repo 下
- core 代码和 .core 文件分两个 repo

fusesoc standard library 就是按照第二种方式管理的，标准库只是 .core 文件的集合，每个 .core 文件内描述了 core 代码在服务器上的路径。

### `core library`

当我们指定顶层 core 后，它依赖的底层 core 代码甚至是底层 .core 文件都不在本地，fusesoc 是如何解决依赖的呢？答案就是 `core library`。与软件类似，fusesoc 根据配置文件 `fusesoc.conf` 中的 core library 信息来查找所有的 core，所以我们使用某个 core 的第一步就是“安装”包含这个 core 的 library。以 fusesoc 标准库为例：

```
#!shell
fusesoc library add fusesoc-cores https://github.com/fusesoc/fusesoc-cores
# show all libraries
fusesoc library list
# show all cores
fusesoc core list
```

如果这个 library 是远程库（如标准库），这个命令会将其 clone 到当前目录下；如果这个 library 是本地库，则会将其路径添加到配置文件中。

如前面所述，有些 library 可能采用和标准库类似的组织方式，library repo 并不包含 core 代码，而仅仅是 .core 文件集合。所以 `fusesoc library add` 命令只是 clone 了 .core 文件，对应的 core 代码并没有下载下来，我们可以看到 `fusesoc core list` 显示 core 状态是 empty。在 build 过程中 fusesoc 会根据 .core 文件中 `provider` 字段的地址将 core 代码 clone 到 `~/.cache/` 目录下面。

!!! note

    如后面 custom 部分所述，我们可以修改配置文件，指定 clone 和 build 的路径。

### `fusesoc.conf`

fusesoc 查找 fusesoc.conf 文件的顺序：

1. 首先在当前目录找
2. 然后在 `$XDG_CONFIG_HOME/fusesoc` 下找
3. 最后在 `/etc/fusesoc` 下找

也可以直接通过命令行选项 `--config` 指定使用某个 fusesoc.conf 文件。

fusesoc 查找 core 的顺序：

当 fusesoc 查找到 fusesoc.conf 后，根据文件中 `[main]` 的 `cores_root` 字段来搜索所有的合法 core 文件，并将其加入内存数据库中。`cores_root` 字段可以添加多个目录，用空格隔开。也可以通过命令行参数 `--cores-root` 指定搜索目录。fusesoc 查找 core 时按照目录列表顺序搜索，且命令行指定目录位于目录列表的最后。当遇到同名（相同 VLNV，Vender-Library-Name-Version） core 时，后解析到的会覆盖之前的。可以利用这个机制来实现同名 core 的重载：

- 用 `cores_root` 字段内容顺序来指定某个 lib 重载另外一个 lib 的同名 core
- 用命令行参数 `--cores-root` 来指定 lib 路径

### `build system`

解决依赖后，工程管理的第二个问题就是调用 EDA 工具。

fusesoc 内部的 `build system` 从顶层 core 文件开始分析，解决所有依赖后整理出完整的 filelist，然后将后续工作交给真正的 EDA 工具来完成。毕竟，fusesoc 只是一个工程管理工具。显然不同的 EDA 工具用法是不一样的，如何将整理好的 filelist 根据目标调用不同的 EDA 工具，传递该工具的特定参数，这个过程是和 EDA 工具强绑定的。比如：

- 如果想调用 verilator 跑仿真：build system 会创建一个 makefile，然后调用 verilator
- 如果想为 Xilinx 生成 bit：build system 会创建一个 vivado 工程文件，然后调用 vivado 完成综合-布局布线-生成 bit

这些 dirty job 都由 fusesoc 帮我们做了，而且 fusesoc 本身是可扩展的，可以轻松支持新的 EDA 工具。`build system` 包含 3 个概念：`tool flow`， `target`，`build stage`。

### `tool flow`

`tool flow` 就是某个特定的 EDA 工具分析运行的过程。verilator 和 vcs，vivado 都是一种 tool。显然不同 tool 需要不同的命令来调用，fusesoc 的目标就是对用户隐藏这些工具之间的差异，尽量简化调用过程。

!!! note

    实际上是将 IP core 用户的工作量转嫁给了 IP core 的提供者，因为一个 IP 要想让别人复用自己的设计，就要提供对应的 .core 文件，提供者在这个文件里描述每一种 target 下每种 tool 使用哪些文件，传入什么样的参数等等。

### `target`

对于同一个 IP，我们可以做不同的任务，比如仿真、综合、lint等，这些任务对应的 filelist 和参数传递等也不相同，fusesoc 把这些相关配置叫做 `target`，一般来说常规的任务有 `sim`， `synth`，`lint` 等。

### `build stage`

fusesco 把 build 过程分为 3 个 stage:

- `setup`：把所有 IP 攒到一起，解决所有依赖问题
    - 从顶层 core 开始生成一棵依赖树
    - 把调用 `generator` 生成的 core 添加到依赖树中
    - 解析依赖树，生成一个 flattened 描述，将其写入一个 EDAM 文件
    - 调用某个特定的 tool flow
- `bulid`：运行 tool flow 直到输出期望的文件
- `run`：执行 build 阶段的输出，对于 sim 来说就是运行仿真，对于 lint 来说就是调用 lint 工具，对于 FPGA flow 来说就是用生成 bitstream 对 FPGA 进行编程

## Building

Build 过程就是 fusesoc 调用 tool flow 产生一些输出，然后执行这些输出文件。所以 target 和 tool flow 不同时，fusesoc 执行的任务也不同。fusesoc 执行 build 分为两步：

1. 为 IP 写 `.core` 文件
2. 使用 `fusesoc run` 命令来调用 fusesoc

下面记录两个实验。

# Example 1

参考官方的 `tests/userguide/blinky`，写了一个 counter 的实验例子。

首先新建一个目录 `~/workspace/mycores/counter`，在下面完成 counter 的 rtl 和 tb，以及 `.core` 文件，目录结构如下

```
#!text
~/workspace/mycores/counter
├── counter.core
├── rtl
│   └── counter.sv
└── tb
    └── tb_counter.sv

2 directories, 3 files
```

其中 counter.sv 和 tb_counter.sv 内容很简单

```
#!systemverilog
// counter.sv
module counter #(
  parameter DW = 8
) (
  input  logic            clk,
  input  logic            rst_n,
  input  logic            en,
  output logic [DW-1 : 0] cnt
);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        cnt <= '0;
    end else if (en) begin
        cnt <= cnt + 1'b1;
    end
  end

endmodule
```

```
#!systemverilog
// tb_counter.sv
`timescale 1ns / 1ns

module tb_counter;

  parameter DW = 8;
  parameter FREQ = 1_000_000;

  localparam PERIOD = 1_000_000_000 / FREQ;
  localparam HALF_PERIOD = PERIOD / 2;

  logic            clk = 1'b1;
  logic            rst_n = 1'b1;
  logic            en = 1'b0;
  logic [DW-1 : 0] cnt;

  counter #(
    .DW(DW)
  ) U_COUNTER (
    .clk,
    .rst_n,
    .en,
    .cnt
  );

  always #(HALF_PERIOD) clk = ~clk;

  initial begin
    $dumpfile("sim.vcd");
    $dumpvars;
    clk = 1;
    rst_n = 1'b0;
    #(2*PERIOD);
    rst_n = 1'b1;

    #(3*PERIOD);

    en = 1'b1;

    #(10*PERIOD);

    en = 1'b0;

    #(20*PERIOD);

    $display("Testbench finshed OK");
    $finish;

  end

endmodule
```

counter.core 文件：

```
#!yaml
CAPI=2:

name: qian:examples:counter:1.0.0
description: Counter, a example core

filesets:
  rtl:
    files:
      - rtl/counter.sv
    file_type: systemVerilogSource

  tb:
    files:
      - tb/tb_counter.sv
    file_type: systemVerilogSource

targets:
  default: &default
    filesets:
      - rtl
    toplevel: counter
    parameters:
      - DW

  sim:
    <<: *default
    description: Simulate the design
    default_tool: icarus
    filesets_append:
      - tb
    toplevel: tb_counter
    tools:
      icarus:
        iverilog_options:
          - -g2012

parameters:
  DW:
    datatype    : int
    description : counter width
    paramtype   : vlogparam
```

!!! note

    + core 文件的语法是 YAML，fuesesoc 的 user guide 里面提供了一个快速入门的教程：[Learn X in Y minutes](https://learnxinyminutes.com/docs/yaml/)
    + core 文件内容需要遵守 user guide 中的 `CAPI2` 的语法规则

在 `~/workspace` 目录下面使用执行：

```
#!bash
fusesoc --cores-root=mycores run --target=sim --setup --build --run qian:examples:counter
```

我们用 `--cores-root` 指定 core 的搜索目录，用 `--target=sim` 指定执行 sim flow，`--setup --build --run` 指定执行完整的 build 3 个步骤，最后的 `qian:examples:counter` 是我们在 .core 文件中为 counter 起的名字。

fusesoc 执行完成后会产生一个 build 目录，在 `build/qian_examples_counter_1.0.0/sim-icarus` 下就可以看到结果了，用 `gtkwave sim.vcd` 可以看波形。

!!! note

    + fusesoc 读取 core 文件后，解析生成 build 下的 makefile， 使用它来调用 EDA 工具
    + 因为 iverilog 对 sv 的支持不完整，所以如果设计使用的 sv，先确认 iverilog 的版本及对 sv 的支持程度（使用源码本地编译可以得到最新的 iverilog）

# Example 2

一种更常见的场景是我们想复用别人的设计，比如说我们想设计一个 counter_blinky 的 core，它依赖于我们刚才写 counter 和 fusesoc 官方 library 中的 blinky 模块。

要使用 fusesoc 的官方 library，所以第一步就是添加这个 library：

```
#!shell
fusesoc library add fusesoc-cores https://github.com/fusesoc/fusesoc-cores
```

这个命令会 clone 指定的 library 到当前目录下，并产生一个 `fusesoc.conf` 文件，里面保存了这个 library 的配置信息。完成下载后，使用 `fusesoc core list` 就可以查看该 library 中包含了哪些 core，并且可以看到对应 core 的状态为 empty 还是 downloaded，empty 表示还没下载该 core 的设计文件。如果设计需要用到某个 core，则 fusesoc 在 build 过程中会自动下载，我们也可以手动下载：

```
#!bash
fusesoc fetch fusesoc:utils:blinky:0
```

下载好要用的 blinky core 后我们就可以开始写自己的 counter_blinky 了，在 counter 平级新建一个 counter_blinky 的目录如下：

```
#!text
~/workspace/mycores/counter_blinky
├── counter_blinky.core
├── rtl
│   └── counter_blinky.sv
└── tb
    └── tb_counter_blinky.sv

2 directories, 3 files
```

其中 counter_blinky.sv 和 tb_counter_blinky.sv 的内容：

```
#!systemverilog
// counter_blinky.sv
counter_blinky #(
  parameter DW = 8,
  parameter clk_freq_hz = 1_0000_000
) (
  input  logic            clk,
  input  logic            rst_n,
  input  logic            en,
  output logic [DW-1 : 0] cnt,
  output logic            q
);

  counter #(
    .DW(DW)
  ) U_COUNTER (
    .clk,
    .rst_n,
    .en,
    .cnt
  );

  blinky #(
    .clk_freq_hz(clk_freq_hz)
  ) U_BLINKY (
      .clk,
      .q
  );

endmodule
```

```
#!systemverilog
// tb_counter_blinky.sv
`timescale 1ns / 1ns

module tb_counter_blinky;

  parameter DW = 8;
  parameter FREQ = 1_000_000;

  localparam PERIOD = 1_000_000_000 / FREQ;
  localparam HALF_PERIOD = PERIOD / 2;

  logic            clk = 1'b1;
  logic            rst_n = 1'b1;
  logic            en = 1'b0;
  logic [DW-1 : 0] cnt;
  logic            q;

  counter_blinky #(
    .DW(DW),
    .clk_freq_hz(10)
  ) U_COUNTER_BLINKY (
    .clk,
    .rst_n,
    .en,
    .cnt,
    .q
  );

  always #(HALF_PERIOD) clk = ~clk;

  initial begin
    $dumpfile("sim.vcd");
    $dumpvars;
    clk = 1;
    rst_n = 1'b0;
    #(2*PERIOD);
    rst_n = 1'b1;

    #(3*PERIOD);

    en = 1'b1;

    #(100*PERIOD);

    en = 1'b0;

    #(20*PERIOD);

    $display("Testbench finshed OK");
    $finish;

  end

endmodule
```

counter_blinky.core 文件：

```
#!yaml
CAPI=2:

name: qian:examples:counter_blinky:1.0.0
description: Counter_blinky, a example core with dependencies

filesets:
  rtl:
    files:
      - rtl/counter_blinky.sv
    file_type: systemVerilogSource
    depend:
      - qian:examples:counter
      - fusesoc:utils:blinky:0

  tb:
    files:
      - tb/tb_counter_blinky.sv
    file_type: systemVerilogSource

targets:
  default: &default
    filesets:
      - rtl
    toplevel: counter_blinky
    parameters:
      - DW
      - clk_freq_hz

  sim:
    <<: *default
    description: Simulate the design
    default_tool: icarus
    filesets_append:
      - tb
    toplevel: tb_counter_blinky
    tools:
      icarus:
        iverilog_options:
          - -g2012

parameters:
  DW:
    datatype    : int
    description : counter width
    paramtype   : vlogparam
  clk_freq_hz:
    datatype    : int
    description : frequency in hz
    paramtype   : vlogparam
```

用下面的命令进行 build：

```
#!bash
fusesoc --cores-root=mycores run --target=sim --setup --build --run qian:examples:counter_blinky
```

然后就可以到 build 下查看波形，进行 debug 了。

# Custom

我们可以通过对 fusesoc.conf 文件的修改，实现自定义配置。

```
[main]
cores_root = ~/workspace/mycores
build_root = ~/workspace/build
cache_root = ~/workspace/remote
```

conf 文件里面加入这些配置后，因为 `cores_root` 已经包含了本地目录，所以我们下面的命令中就不需要手动指定了：

```
#!bash
fusesoc --config fusesoc.conf run --target=sim --setup --build --run qian:examples:counter_blinky
```

同时，build 完成后可以看到自动下载的 blinky 保存到了我们指定的 `cache_root` 目录下面。

运行时提示 cores_root 这个选项已经被弃用了，应该使用添加 library 的方式，查看 `fusesoc library add -h` 后再实验一下：

```
#!bash
fusesoc library add mycores ~/workspace/mycores
fusesoc library list
```

可以看到已经成功添加了本地目录 `~/workspace/mycores` 为本地 library，打开 `fusesoc.conf` 可以看到相关的记录。以后使用这个目录下的 core 就不再需要在命令行手动指定路径了。

# More

Fusesoc 的这个想法显然是从 `pip`， `npm` 借鉴过来的，现在硬件开源领域越来越多地借鉴软件领域的成功经验，比如 RISC-V、 fusesoc、硬件敏捷开发、chisel/spanil HDL、chipalliance 等等，如果将来硬件开发能像软件一样蓬勃发展，想想都是一件激动人心的事情。
