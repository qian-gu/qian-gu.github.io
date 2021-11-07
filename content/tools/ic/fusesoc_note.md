Title: Fusesoc 小结
Date: 2021-10-30 16:25
Category: Tools
Tags: IC_tools, fusesoc
Slug: fusesoc_summary
Author: Qian Gu
Summary: 记录 fusesoc 用法

最近看到很多开源项目都在用 fusesoc 来管理，花了半天时间学习了一下，简单记录一下笔记。

# What is Fusesoc

[Fusesoc][fusesoc] 是一个用 python 写的 HDL 管理工具，用一句话解释就是：**HDL 版的 pip**，它主要解决 IP core 重用时复杂繁琐的常规性工作，更轻松地实现下面目标：

- 重用已有的 IP core
- 为 compile-time 和 run-time 生成配置文件
- 在多个 simulator 上跑回归
- 在不同平台间移植设计
- 让别人复用你的设计
- 配置 CI

一个设计中包含多个 core，而且可能会有不同的 target，比如仿真、lint、综合等，而且每个 target 也会有多种工具可用，fusesoc 的目标就是把这些设置通过一个配置文件管理起来，使得支持 fusesoc 的 IP 相互之间可以轻松地复用。

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

即 IP core 设计本身，比如一个 FIFO，它的代码可以保存在本地，也可以保存在远程。每个 core 都有一个 `.core` 文件来描述它，fusesoc 就是通过这个文件来查找、确定某个 core。

一个 core 可以依赖于另外一个 core，比如一个 FIFO core 依赖于一个 SRAM core。

SoC 中有很多 IP core，我们只需要指定 top level 的 core 即可，剩下的依赖分析和解决都交给 fusesoc 来完成即可，当 fusesoc 整理出完整的 filelist 后，就会将后续工作交给真正的 EDA 工具来完成。毕竟，fusesoc 只是一个工程管理工具。

### `tool flow`

显然不同的工具需要不同的命令来调用，fusesoc 的目标就是对用户隐藏这些工具之间的差异，尽量简化调用过程。

!!! note

    实际上是将 IP core 用户的工作量转嫁给了 IP core 的提供者，因为一个 IP 要想让别人复用自己的设计，就要提供对应的 .core 文件，提供者在这个文件里描述每一种 target 下每种 tool 使用哪些文件，传入什么样的参数等等。

### `target`

对于同一个 IP，我们可以做不同的任务，比如仿真、综合、lint等，这些任务对应的 filelist 和参数传递等也不相同，fusesoc 把这些相关配置叫做 target，一般来说常规的任务有 `sim`， `synth`，`lint` 等。

### `build stage`

fusesco 把 build 过程分为 3 个 stage:

- `setup`：把所有 IP 攒到一起，解决依赖问题后把结果交给 tool flow 进行处理
- `bulid`：运行 tool flow 直到输出期望的文件
- `run`：执行 build 阶段的输出，对于 sim 来说就是运行仿真，对于 lint 来说就是调用 lint 工具，对于 FPGA flow 来说就是用生成 bitstream 对 FPGA 进行编程

## Building

Build 过程就是 fusesoc 调用 tool flow 产生一些输出，然后执行这些输出文件。所以 target 和 tool flow 不同时，fusesoc 执行的任务也不同。fusesoc 执行 build 分为两步：

1. 为 IP 写 `.core` 文件
2. 使用 `fusesoc run` 命令来调用 fusesoc

下面记录两个实验。

# Example 1

参考官方的 `tests/userguide/blinky`，写了一个 counter 的实验例子。

首先新建一个目录 `cores/counter`，在下面完成 counter 的 rtl 和 tb，以及 `.core` 文件，目录结构如下

```
#!text
cores/counter
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

```
#!yaml
# counter.core
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
    + core 文件内容需要遵守 user guide 中的 `CAPI2` 部分的语法规则

使用下面的命令就可以完成 build

```
#!bash
fusesoc --cores-root=cores run --target=sim --setup --build --run qian:examples:counter
```

我们用 `--cores-root` 指定 core 的搜索目录，用 `--target=sim` 指定执行 sim flow，`--setup --build --run` 指定执行完整的 build 3 个步骤，最后的 `qian:examples:counter` 是我们在 .core 文件中为 counter 起的名字。

fusesoc 执行完成后会产生一个 build 目录，在 `build/qian_examples_counter_1.0.0/sim-icarus` 下就可以看到结果了，用 `gtkwave sim.vcd` 可以看波形。

!!! note

    + fusesoc 读取 core 文件后，解析生成 build 下的 makefile， 使用它来调用 EDA 工具
    + 因为 iverilog 对 sv 的支持不完整，所以如果设计使用的 sv，先确认 iverilog 的版本及对 sv 的支持程度（使用源码本地编译可以得到最新的 iverilog）

# Example 2

一种更常见的场景是我们想复用别人的设计，比如说我们想设计一个 counter_blinky 的 core，它依赖于我们刚才写 counter 和 fusesoc 官方 library 中的 blinky 模块。

因为要使用 fusesoc 的官方 library，所以第一步就是添加这个 library，下面这个命令会 clone 对应的 repo，并产生一个 `fusesoc.conf` 文件，这个文件里面保存了描述 `fusesoc-cores` 这个 library 的配置信息。

```
#!shell
fusesoc library add fusesoc-cores https://github.com/fusesoc/fusesoc-cores
```

!!! note

    这个 repo 仅仅是 core 文件，并不包含相应的设计文件，设计文件的路径在 core 文件内的 `provider` 部分描述。在 build 时 fusesoc 会自动从相应的地址下载设计文件，并且保存在 `~/.cache` 目录下。

完成下载后，使用 `fusesoc core list` 就可以查看该 library 中包含了哪些 core，并且可以看到对应 core 的状态为 empty 还是 downloaded，empty 表示还没下载该 core 的设计文件。如果设计需要用到某个 core，则 fusesoc 在 build 过程中会自动下载，我们也可以手动下载：

```
#!bash
fusesoc fetch fusesoc:utils:blinky:0
```

下载好要用的 blinky core 后我们就可以开始写自己的 counter_blinky 了，在 counter 平级新建一个 counter_blinky 的目录如下：

```
#!text
cores/counter_blinky
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

```
#!yaml
# counter_blinky.core
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

同理，用下面的命令进行 build：

```
#!bash
fusesoc --cores-root=cores run --target=sim --setup --build --run qian:examples:counter_blinky
```

然后就可以到 build 下查看波形，进行 debug 了。

## Custom

前面这个实验过程中自动生成了一个 `fusesoc.conf` 文件，所以可以做一个合理的猜测：fusesoc 的行为取决于 conf 文件，所以我们可以通过对 conf 文件的修改，实现自定义配置。

```
[main]
cores_root = ~/workspace/cores
build_root = ~/workspace/build
cache_root = ~/workspace/remote
```

因为我们已经在 conf 文件里面指定的 cores_root 路径包含了本地设计文件，所以我们下面的命令中就不需要手动指定了

```
#!bash
fusesoc --config fusesoc.conf run --target=sim --setup --build --run qian:examples:counter_blinky
```

同时，build 完成后可以看到自动下载的 blinky 保存到了我们指定的 `remote` 目录下面。

运行时提示 cores_root 这个选项已经被弃用了，应该使用添加 library 的方式，查看 `fusesoc library add -h` 后再实验一下：

```
#!bash
fusesoc library add mycores ~/workspace/cores
fusesoc library list
```

可以看到已经成功添加了本地目录 `~/workspace/cores` 为本地 provider，打开 `fusesoc.conf` 可以看到相关的记录。以后使用这个目录下的 core 就不再需要在命令行手动指定路径了。

## More

Fusesoc 的这个想法显然是从 `pip`， `npm` 借鉴过来的，现在硬件开源领域越来越多地借鉴软件领域的成功经验，比如 RISC-V、 fusesoc、硬件敏捷开发、chisel/spanil HDL、chipalliance 等等，如果将来硬件开发能像软件一样蓬勃发展，想想都是一件激动人心的事情。
