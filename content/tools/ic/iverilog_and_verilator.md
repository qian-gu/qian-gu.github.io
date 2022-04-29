Title: 开源 IC 工具/库 —— iverilog、verilator 和 gtkwave
Date: 2022-04-16 10:43
Category: Tools
Tags: iverilog, verilator, gtkwave
Slug: iverilog_verilator_and_gtkwave
Author: Qian Gu
Status: draft
Series: Open IC Tools & Library
Summary: 总结 iverilog、verilator 和 gtkwave 的常用使用方法

## iverilog

[iverilog][iverilog] 是 vcs 的平替，可以做一些基本的仿真，优点：

- 安装包非常小巧
- 支持全平台
- 代码开源

!!! note
     一般的项目可以为其写 fusesoc 的 core 文件，每次写的时候复制以前的 core 文件相关内容即可。下面内容全是来自 [iverilog user guide][iverilog user guide] 和 iverilog 的 man 和 help，主要目的是备忘，为一些临时实验性质的不值得写 core 文件的项目，提供快速查阅。

[iverilog]: http://iverilog.icarus.com/
[iverilog user guide]: https://iverilog.fandom.com/wiki/User_Guide

### install

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

### use

iverilog 主要包含两个工具：

- `iverilog`：编译器
- `vvp`：仿真运行引擎

假设有一个 counter.sv 模块和 tb_counter.sv，那么

```
#!bash
iverilog -o my_design counter.sv tb_counter.sv
vvp my_design
```

然后就可以用 gtkwave 打开波形文件了。

iverilog 的常用参数：

- `-c file` 指定 filelist
- `-s top` 指定 top module
- `-I includedir` 指定 include 目录
- `-o filename` 指定编译结果的文件名

!!! warning
     iverilog 对 sv 语法的支持比较弱，很多 sv 的新语法都不支持。相比之下 verilator 的支持力度更好。

## verilator
 
[verilator][verilator] 号称是 the fastest verilog/systemverilog simulator。

[verilator]: https://www.veripool.org/verilator/

### install

方式一：直接用 apt 安装，好处是省心，但是缺点是可能获取的不是最新稳定版本。

```
#!bash
sudo apt-get install verilator
```

方式二：从源码编译，好处是可以获得最新的稳定版本，缺点就是稍微麻烦一点。首先下载源码，安装编译所依赖的工具，然后

```
#!bash
autoconf
./configure
make
sudo make install
```

### use

verilator 的特殊之处：

- 把 dut 编译成 c++ 模型（即 `verilating` 过程，输出的模型叫做 `verilated module`）
- testbench 用 c++ 写，而不是 sv（即一个 c++ 的 wrapper，包含了 `main` 函数，其中例化了 `verilated dut`）
- 使用 C++ 编译器把 testbench 和 verilator 的库函数编译成可执行文件
- 运行可执行文件，完成仿真

一个简单的 dut 例子：

```
#!cpp
#include "Vcounter.h"
#include "verilated_vcd_c.h"
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
    vluint64_t time = 0;
    top->clk = 0;
    top->rst_n = 0;
    time++;
    top->rst_n = 1;
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
- testbench 必须调用 `eval()`，每次 eval 被调用一次，就会执行一次 `always @(posedge clk)`，计算相应的组合逻辑，更新寄存器的值

然后使用下面的命令编译：

```
#!bash
verilator main.cpp counter.sv -Wall -top-module counter --cc --trace --exe
```

- `-Wall` 打开所有 warning
- `-Wno-fatal` 忽略非 fatal 的 warning
- `--top-module` 指定 top module
- `--cc` 表明是 c++
- `--trace` 生成 trace 波形
- `--exe` 生成可执行文件

运行 `obj_dir` 下面的可执行文件，可以进行仿真，生成波形。

## gtkwave

[gtkwave][gtkwave] 是 verdi 的平替，安装和使用都非常简单：

[gtkwave]: https://github.com/gtkwave/gtkwave

```
#!bash
sudo apt-get install gtkwave
gtkwave wave.vcd
```