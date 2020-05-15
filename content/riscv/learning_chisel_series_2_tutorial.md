Title: 学习 chisel 系列之 2： Chisel Tutorial
Date: 2020-05-10 14:56
Category: RISC-V
Tags: chisel
Slug: learning_chisel_series_2_chisel_tutorial
Author: Qian Gu
Series: Learning Chisel
Summary: 官方教程 chisel_tutorial 学习笔记
Status: draft

[chisel 环境安装][install_chisel]成功之后，就可以正式开始 chisel 的学习之旅了。

[install_chisel]: https://qiangu.cool/riscv/learning_chisel_series_1_install.html

## Chisel Tutorial

[Chisel Tutorial][tutorial] 是官方提供的教程，阅读 wiki，走完整个流程，就能掌握
chisel 的基本语法了。

[tutorial]: https://github.com/ucb-bar/chisel-tutorial

## Doc generattion

Tutorial 下面的 `doc` 目录里面包含了一篇 chisel 入门论文，只要按照 Makefile 中的提示把所有的依赖包都安装好，就可以生成最终的 [pdf 论文][paper]了。

[paper]: 

## Wiki

Wiki 部分的笔记如下。

### wire

用 `val` 声明一个变量，只要这个变量不是用 `Reg` 类型来赋值，那么它就会被解释成一个 verilog 中的 `wire`，因此这个变量也可以随意赋值给其他变量，就像 verilog 中的 `wire` 的行为一样。

chisel 的一个强大功能是可以根据输入信号自动推断其他信号的位宽，所以它能节省广大硅农的很多时间，而且自动推断不会产生眼花手抖等情况，bug率也大幅下降，妈妈再也不用担心我的代码位宽不匹配了XD。

### reg

verilog 中声明一个 `reg`，实际最终综合出来的可能是一条线 `wire`，也有可能是一个真正的寄存器 `register`，这是 verilog 语法的历史问题导致的。即使是很多老手，也经常声明错。

chisel 和 verilog 的不同之处在于，如果一个 `Reg` 变量，那么它一定会综合出一个上升沿触发的寄存器。chisel中声明寄存器的方法有好几种，

1. 声明类型时不传递参数，在后面的语句中赋值（适合有条件赋值）
2. 用 `RegNext()`声明的同时传参，那么在每个时钟上升沿都会采样该值（适合无条件打拍）

```
#!scala
// method 1
val x = Reg(UInt())
when (a > b) { x:= y}
  .elsewhen (b > a) {x := z}
  .otherwise {x := w}

// method 2
val y = io.x
val z = RegNext(y)
```

需要注意的是，如果是用 `when` 语句有条件的赋值，那么要保证等号两边的数据类型和宽度相匹配，对于无条件复制则无须这么做，因为编译器会根据右边的变量自动推断左边的寄存器类型和位宽。

## reset

需要注意的是，前面的代码没有声明 clk 和 reset 信号，因为编译器会自动隐式地生成一个时钟信号和一个同步复位信号。

像 `val x = Reg(UInt())` 这种方式声明的寄存器是不带复位信号的，如果我们想指定复位的初始值，可以有两种方式，

1. 用 `RegInit()`
2. 在后续赋值中对寄存器进行初始化，chisel 自动隐式地生成的复位信号名字叫 `reset`，我们可以直接在代码中使用这个信号，但是为了把它转换成一个 Bool 类型的变量，需要显式地添加 `toBool` 来转换。

```
#!scala
// method 1: using RegInit()
val x = RegInit(0.(1.W))

// method 2: using reset.toBool
when(reset.toBool) {
	x := 0.U
} .elsewhen(io.enable) {
	x := y
}
```

下面用一个4bit的shift register实例来说明，

版本一：使用 `RegInit()` 的代码，

```
#!scala
package examples

import chisel3._

class ResetShiftRegister extends Module {
  val io = IO(new Bundle {
    val in    = Input(UInt(4.W))
    val shift = Input(Bool())
    val out   = Output(UInt(4.W))
  })
  // Register reset to zero
  val r0 = RegInit(0.U(4.W))
  val r1 = RegInit(0.U(4.W))
  val r2 = RegInit(0.U(4.W))
  val r3 = RegInit(0.U(4.W))
  when (io.shift) {
    r0 := io.in
    r1 := r0
    r2 := r1
    r3 := r2
  }
  io.out := r3
}
```

版本二：使用 `reset.toBool` 的代码如下，

```
#!scala
package examples

import chisel3._

class EnableShiftRegister extends Module {
  val io = IO(new Bundle {
    val in    = Input(UInt(4.W))
    val shift = Input(Bool())
    val out   = Output(UInt(4.W))
  })
  val r0 = Reg(UInt())
  val r1 = Reg(UInt())
  val r2 = Reg(UInt())
  val r3 = Reg(UInt())
  when(reset.toBool) {
    r0 := 0.U(4.W)
    r1 := 0.U(4.W)
    r2 := 0.U(4.W)
    r3 := 0.U(4.W)
  } .elsewhen(io.shift) {
    r0 := io.in
    r1 := r0
    r2 := r1
    r3 := r2
  }
  io.out := r3
}
```

两个版本生成的 rtl 是一样的，核心部分如下，

```
#!verilog
module ResetShiftRegister(
  input        clock,
  input        reset,
  input  [3:0] io_in,
  input        io_shift,
  output [3:0] io_out
);
  /* some code */
  always @(posedge clock) begin
    if (reset) begin
      r0 <= 4'h0;
    end else begin
      if (io_shift) begin
        r0 <= io_in;
      end
    end
    if (reset) begin
      r1 <= 4'h0;
    end else begin
      if (io_shift) begin
        r1 <= r0;
      end
    end
    if (reset) begin
      r2 <= 4'h0;
    end else begin
      if (io_shift) begin
        r2 <= r1;
      end
    end
    if (reset) begin
      r3 <= 4'h0;
    end else begin
      if (io_shift) begin
        r3 <= r2;
      end
    end
  end
endmodule
```

### bit  with inference

chisel 可以根据信号的连接，自动分析信号的位宽，所以我们可以省掉 verilog 中繁琐的位宽声明。


## Ref
