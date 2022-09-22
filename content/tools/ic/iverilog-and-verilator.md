Title: 开源 IC 工具/库 —— iverilog、verilator 和 gtkwave
Date: 2022-04-16 10:43
Category: Tools
Tags: IC-tools, iverilog, verilator, gtkwave
Slug: iverilog-verilator-and-gtkwave
Author: Qian Gu
Series: Open IC Tools & Library
Summary: 总结 iverilog、verilator 和 gtkwave 的常用使用方法

## Iverilog

[iverilog][iverilog] 是 vcs 的平替，可以做一些基本的仿真，优点：

- 安装包非常小巧
- 支持全平台
- 代码开源

!!! note
     一般的项目可以为其写 fusesoc 的 core 文件，每次写的时候复制以前的 core 文件相关内容即可。下面内容全是来自 [iverilog user guide][iverilog user guide] 和 iverilog 的 man 和 help，主要目的是备忘，为一些临时实验性质的不值得写 core 文件的项目，提供快速查阅。

[iverilog]: http://iverilog.icarus.com/
[iverilog user guide]: https://iverilog.fandom.com/wiki/User-Guide

### Installation

方式一：直接用 apt 安装，好处是省心，但是可能获取的不是最新稳定版本。

```
#!bash
sudo apt-get install iverilog
```

方式二：从源码编译，好处是可以获得最新的稳定版本，缺点就是稍微麻烦一点。首先下载源码，安装编译所依赖的工具，然后

```
#!bash
./configure
make
sudo make install
```

### Usage

iverilog 主要包含两个工具：

- `iverilog`：编译器
- `vvp`：仿真运行引擎

假设有一个 counter.sv 模块和 tb-counter.sv，那么

```
#!bash
iverilog -o my-design counter.sv tb-counter.sv
vvp my-design
```

然后就可以用 gtkwave 打开波形文件了。

iverilog 的常用参数：

- `-c file` 指定 filelist
- `-s top` 指定 top module
- `-I includedir` 指定 include 目录
- `-o filename` 指定编译结果的文件名

!!! warning
     iverilog 对 sv 语法的支持比较弱，很多 sv 的新语法都不支持。相比之下 verilator 的支持力度更好。

## Verilator
 
[verilator][verilator] 号称是 the fastest verilog/systemverilog simulator。是仿真器 4 巨头之一，其他 3 个分别是，

- vcs
- modelsim
- nc-sim

这 3 个因为是闭源的，通常被叫做 3 巨头。

verilator 文档和手册中说大部分 simulator 都必须兼容 IEEE-1364 和 IEEE-1800 标准，所以必须采用事件驱动的方式，因此无法对 blocks 进行重排序，也无法进行网表的优化。而这些正好是 verilator 速度更快的原因。

!!! note
    实际使用中，影响 verilator 速度的因素非常多，最主要的有优化掉所有 `UNOPTFLAT` 这个 warning 以及使用多线程。其中多线程要确保 CPU core 的数量一定比线程数大，否则性能会严重恶化。

[verilator]: https://www.veripool.org/verilator/

### Installation

方式一：直接用 apt 安装，好处是省心，但是缺点是可能获取的不是最新稳定版本。

```bash
sudo apt-get install verilator
```

方式二：从源码编译，好处是可以获得最新的稳定版本，缺点就是稍微麻烦一点。

```bash
autoconf
./configure
make
sudo make install
```

一般用 apt 或者默认的编译安装，则不需要再手动设置任何环境变量，如果安装时选择了自定义目录，那么就要设置相应的环境变量了。

### Usage

一个简单的 dut 例子：

```cpp
#include "Vcounter.h"
#include "verilated-vcd-c.h"
#include "verilated.h"
#include <iostream>

using namespace std;

int main(int argc, char **argv, char **env)
{
    Verilated::commandArgs(argc, argv);
    // dump wave
    Verilated::traceEverOn(true);
    VerilatedVcdC *tfp = new VerilatedVcdC;
    Vcounter *top = new Vcounter;
    top->trace(tfp, 0);
    tfp->open("wave.vcd");
    // set simulation time
    vluint64-t time = 0;
    top->clk = 0;
    top->rst-n = 0;
    time++;
    top->rst-n = 1;
    while (time < 100) {
        if (time % 2) {
            top->clk = 1;
        } else {
            top->clk = 0;
        }
        top->en = 1;
        top->eval();
        tfp->dump(time);
        cout << "time = " << time << ", cnt = " << int(top->cnt) << endl;
        time++;
    }
    top->final();
    tfp->close();
    delete top;
    cout << "Simulation Finished!" << endl;
    return 0;
}
```

说明：

- `xxx` 模块会被编译成 `Vxxx`，所以要 `include "Vxxx.h"`，使用时也是通过 `new Vxxx` 来动态申请一个对象
- wrapper 必须调用 `eval()`，每次 eval 被调用一次，就会执行一次 `always @(posedge clk)`，计算相应的组合逻辑，更新寄存器的值

然后使用下面的命令编译：

```bash
verilator main.cpp counter.sv -Wall -top-module counter --cc --trace --exe --build
```

一些常见的参数：

- `-Wall` 打开所有 warning
- `-Wno-fatal` 关闭 warning 导致 fatal 退出仿真
- `--top-module` 指定 top module
- `--cc` 生成 c++ 模型
- `--trace` 生成 trace 波形
- `--exe` 在 Makefile 中生成可执行文件的 target
- `--build` 在 verilation 后自动生成可执行文件

运行 `obj-dir` 下面的可执行文件，可以进行仿真，生成波形。

[完整的 example][dic_template]

[dic_template]: https://github.com/qian-gu/dic_template

### Dive into Verilator

1. verilator 本质上是一个 compiler，把 tb/dut（.v 和 .sv 文件）编译成 .h 和 .cpp，并提供一个 runtime lib，这个库默认安装在 `/usr/local/share/verilator/include` 下面。编译过程叫做 `verilating`，输出的模型叫做 `verilated module`
2. 需要用户提供一个包含 `main()` 函数的 C++ wrapper 来例化 verilated model
3. 经过 verilation 后调用 C++ 编译器将 verilated model 编译为可执行文件，运行可执行文件，完成仿真
4. verilating 时会生成两个 makefile，分别是 `V{top}.mk` 和 `V{top}-classes.mk`。其中 `V{top}-classes.mk` 会根据命令行参数给一些 verilator 预定义的变量赋值。`V{top}.mk` 作为顶层的 makefile 会自动 include 生成的 `V{top}-classes.mk` 和 `$VERILATOR-ROOT/include/verilated.mk` 文件。举个例子，如果命令行加了 `--trace` 选项，那么 `V{top}-classes.mk` 中会包含一行 `VM-TRACE = 1`，然后通过 `verilated.mk` 和 `V{top}.mk` 最终传递给 g++ 参数 `-DVM-TRACE=1`，所以我们就可以直接在 wrapper 中使用 `#if VM-TRACE` 来开启 trace 功能了
5. 如果在调用 verilator 时加上 `--exe`，那么 verilator 会在 `V{top}.mk` 中加入 link target，方便用户后续手动 build。否则 `V{top}.mk` 中不包含 link target
6. 如果在调用 verilator 时加上 `--exe` 和 `--build`，那么 verilator 会自动 build，无需用户再手动调用
7. verilator 支持很多命令行参数，详细说明见手册
8. 大型设计会消耗大量的时间（10+ mins）和内存空间（100+ GB），为了解决这个问题，支持分 hierarchy 做 verilating。比如从一个多核的大型 SoC 中把 core 剥离出来单独做verilating，然后再整合到一起。具体用法见文档
9. verilator 支持多线程仿真

!!! note
    dump 波形的功能既可以在 `sim-main.cpp` 中用 verilator 提供的 dump 功能，也可以在 `tb-top.sv` 中使用 sv 语法 `$dumpfile` 和 `$dumpvars`。后者会更好一些，因为即使切换成 vcs 等其他仿真器，dump 功能也是可以正常工作的。无论哪种方式，都必须在命令行中加上 `--trace` 选项。

### Coverage

 verilator 提供了 coverage 工具，支持 line/function/toggle，需要 `sim-main.cpp` 和命令行参数配合使用，具体见 [dic-template][dic-template]和 `examples/make-trace-c`。

 1. 在 `sim-main.cpp` 中加入收集覆盖率的代码（见 dic-template/tb/sim-main.cpp），
 2. 使用 `verilator` 编译、运行仿真，覆盖率收集结果在 `coverage.dat` 文件中
 3. 使用 `verilator-coverage` 配合命令行参数分析 `coverage.dat` 文件（见 dic-template/Makefile），分析结果输出到 `coverage.info` 文件中，info 文件可以被 `lcov` 读取并使用 `genhtml` 生成 HTML 报告，然后这些报告可以导入到 codecov.io 网站上

### Code Profiling

因为 verilator 输出的是 C++ 文件，所以可以支持用 GNU gprof 做性能分析，同时 verilator 提供了 prof 工具，可以将 C++ 的分析结果反标到 verilog/sv。（具体使用方式见 [dic-template][dic-template]）

1. 给 `verilator` 命令行加上 `--prof-cfunc` 选项
2. 编译、运行仿真后会输出 `gmont.out` 文件
3. 用 `gprof` 分析 `gmont.out` 和 `Vtb-top`，结果输出到 `grpof.out` 中
4. 用 `verilator-profcfunc` 分析 `gprof.out`，将性能分析结果反标到 Verilog/sv 代码

### Execution Profiling

统计 verilated model 的运行时间并进行可视化，对于性能优化来说非常有用。verilator 通过下面方式实现：

1. 给 `verilator` 命令行加上 `--prof-exec` 选项
2. 编译、运行仿真后会输出 `profile-exec.dat` 文件
3. 用 `verilator-gantt` 分析 `profile-exec.dat`，输出 `profile-exec.vcd` 文件
4. 用 gtkwave 分析波形

## Gtkwave

[gtkwave][gtkwave] 是 verdi 的平替，安装和使用都非常简单：

[gtkwave]: https://github.com/gtkwave/gtkwave

```
#!bash
sudo apt-get install gtkwave
gtkwave wave.vcd &
```
