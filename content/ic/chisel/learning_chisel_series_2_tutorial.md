Title: 学习 chisel 系列 #2： Chisel Syntax Summary
Date: 2020-05-10 14:56
Category: IC
Tags: chisel
Slug: learning_chisel_series_2_chisel_syntax_summary
Author: Qian Gu
Series: Learning Chisel
Summary: chisel_tutorial 和 chisel3 的 wiki学习笔记
Status: draft

[chisel 环境安装][install_chisel]成功之后，就可以正式开始 chisel 的学习之旅了。下面是我总结的 chisel 语法笔记。

[install_chisel]: https://qiangu.cool/riscv/learning_chisel_series_1_install.html

## Chisel Tutorial & Chisel3

[Chisel Tutorial][tutorial] 是官方提供的教程，阅读 wiki，走完整个流程，就能掌握一部分 chisel 的基本语法了。

[tutorial]: https://github.com/ucb-bar/chisel-tutorial

Tutorial 下面的 `doc` 目录里面包含了一篇 chisel 入门论文，只要按照 Makefile 中的提示把所有的依赖包都安装好，就可以生成最终的 [pdf 论文][paper]了。

[paper]: 

[Chisel3][chisel3] 官方的 wiki 页面详细介绍了 chisel3 的语法。

[chisel3]: 

---------

## Scala 和 Chisel

因为 Chisel 是 Scala 的方言，所以它本质是还是 scala 代码，但是 scala 是一门功能强大的复杂语言，融合了指令式编程、面向对象编程、函数式编程，有很多高级和复杂的概念，学习 scala 的所有特性固然对 chisel 有帮助，但是因为 chisel 只限定于硬件描述领域，所以实际上有些 scala 的特性一般是用不到的，所以如果为了快速入门 chisel，scala 的部分主题是可以跳过的，总结如下表：

| Scala 功能 | Chisel 是否用到 | Chisel 主要用途 |
| --------- | -------------- | -------------- |
| 集合（Array、List、Tuple、Map、Set | Y | 构建寄存器组等 |
| 内建控制结构 | Y | 重复逻辑、连线 |
| Class 多态 | N | - |
| Class 继承 | Y | 电路本身没有继承关系，主要用来扩展接口 |
| 特质 | Y | 提取电路公共属性，用来快速修改/删除电路功能 |
| 模式匹配 | Y | 快速裁剪、参数化配置电路 |
| 类型参数化 | N | 阅读 Chisel 源码，理解语言的机制，设计电路不会用到 |
| 抽象成员 | N | 理解 Chisel API，设计电路不会用到 |
| 隐式定义 | Y | 和模式匹配配合实现快速裁剪、配置，Chisel 高级功能的重点 |
| 

## 变量

### wire

用 `val` 声明一个变量，只要这个变量不是用 `Reg` 类型来赋值，那么它就会被解释成一个 verilog 中的 `wire`，因此这个变量也可以随意赋值给其他变量，就像 verilog 中的 `wire` 的行为一样。

verilog 中声明一个 `reg`，实际最终综合出来的可能是一条线 `wire`，也有可能是一个真正的寄存器 `register`，这是 verilog 语法的历史问题导致的。即使是很多老手，也经常声明错。

chisel 和 verilog 的不同之处在于，如果一个 `Reg` 变量，那么它一定会综合出一个上升沿触发的寄存器。chisel中声明寄存器的方法有好几种，

1. 声明类型时不传递参数，在后面的语句中赋值（适合有条件赋值）
2. 用 `RegNext()`声明的同时传参，那么在每个时钟上升沿都会采样该值（适合无条件打拍）

```scala
// method 1
val x = Reg(UInt())
when (a > b) { x:= y}
  .elsewhen (b > a) {x := z}
  .otherwise {x := w}

// method 2
val y = io.x
val z = RegNext(y)
```

需要注意的是，如果是用 `when` 语句有条件的赋值，那么要保证等号两边的数据类型和宽度相匹配，对于无条件赋值则无须这么做，因为编译器会根据右边的变量自动推断左边的寄存器类型和位宽。

## 控制语句

### for loop

```
#!scala
// exclusive n
for (i <- 0 until n) {
	...
}

// include n
for (i <- 0 to n) {
	...
}
```

### if-elseif-if

```
#!scala
if (<condition1>) {
	...
	} else if (<condition2>) {
		...
	} else {
		...
	}
```

### when

```
#!scala
// when clause
when (<condition1>) {...}
.elsewhen (<condition2) {...}
.elsewhen (<condition3) {...}
.otherwise {...}

// unless clause
unless (<condition) {...}
```

### Assignments and Re-assignments

这是 chisel 的独特语法，在 chisel 中第一次定义变量时，必须使用 `=` 来告诉 chisel 生成这样一个硬件资源，之后如果想改变这个硬件的值，即重新赋值则必须使用 `:=`。

在电路中重新赋值的操作是没有意义的，因为一旦电路中任意两个节点之间只需要声明一次即可，之后source就会每时每刻都在驱动着destination。那么就会有个问题，

`Q：为什么 chisel 会出现重新赋值的语法？`

原因是 chisel 和 verilog 的编译顺序不一样，它是顺序编译的。如果某个变量的赋值出现在定义的后面，就需要重新赋值。

一个最简单的例子就是 top 层的 I/O 信号，因为在端口上声明输出信号时我们并不知道它的值是多少，要在模块中计算更新才知道最终输出。

### Bit Extraction

和 verilog 类似，提取 bit 位的语法不同而已，`[:]` 改成了 `(,)`。

```
#!scala
val x_to_y = value(x, y)
val x_of_value = value(x)
```

### Bit Concatenation

和 verilog 的 bit 拼接不同，chisel 使用 `Cat()` 函数来实现 bit 拼接，和 bit 提取一样，高位部分是第一个参数，低位部分是第二个参数。`Cat()` 函数的实现在 chisel 的 util 包，不在 core 内，所以需要先 import 才能使用。

```
#!scala
import chisel3.util.Cat
// or import all the utility definitions 
// import chisel3.util._

val A = UInt(32.W)
val B = UInt(32.W)
val bus = Cat(A, B)
```

### Bit Inference

很多运算结果的位宽会比操作数更宽，比如加法和乘法，在传统的 verilog 编码中，硅农们必须手动指定每个 reg/wire 的位宽。相比之下，chisel 的一个强大功能是可以自动推断信号的位宽，所以它能节省广大硅农的很多时间，而且自动推断不会产生眼花手抖等情况，bug率也大幅下降，妈妈再也不用担心我的代码位宽不匹配了XD。

常见的 bit 位宽推断如下，

| Operation | Result Bit Width |
| --------- | ---------------- |
| Z = X + Y | max(Width(X), Width(Y)) |
| Z = X - Y | max(Width(X), Width(Y)) |
| Z = X | Y | max(Width(X), Width(Y)) |
| Z = X ^ Y | max(Width(X), Width(Y)) |
| Z = ~X | Width(X) |
| Z = Mux(C, X, Y) | max(Width(X), Width(Y)) |
| Z = X * Y | Width(X) + Width(Y) |
| Z = X << n | Width(X) + n |
| Z = X >> n | Width(X) -n |
| Z = Cat(X, Y) | Width(X) + Width(Y) |
| Z = Fill(n, x) | Width(X) + n |

## 复位 reset

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

## UInt Class

UInt（无符号整数类型）等价于 verilog 中的 unsigned 类型，UInt 运算的操作数类型必须也是 UInt 类型，支持的常见运算有，

| Operand | Operation | Ooutput Type |
| ------- | --------- | ------------ |
| + | Add | UInt |
| - | Subtract | UInt |
| * | Multiply | UInt |
| / | UInt Divide | UInt |
| % | Modulo | UInt |
| ~ | Bitwise Negation | UInt |
| ^ | Bitwise XOR | UInt |
| & | Bitwise AND | UInt |
| | | Bitwise OR | UInt |
| === | Equal | Bool |
| =/= | Not Equal | Bool |
| > | Greater | Bool |
| < | Less | Bool |
| >= | Greater or Equal | Bool |
| <= | Less or Equal | Bool |

大部分运算符和 verilog 都是相同的，不同之处是 `|`、`===` 和 `=/=` 操作。

## Bool Class

Bool 类用来表示逻辑表达式的结果，可以在 `when` 之类的条件语句中使用，

```
#!scala
val change = io.a == io.b
when (change) {
	//...
} .otherwise {
	//...
}

val true_value  = true.B
val false_value = flase.B
```

## Casting Between Types

chisel 要求赋值表达式的两边数据类型是一致的。如果直接把一个 Bool 类型的变量赋值给一个 UInt 类型会报错，正确做法是显式地进行转换，

```
#!scala
val io = IO(new Bundle{
	val in = Input(UInt(2.W))
	val out = Ouptut(UInt(1.W))
})
io.out := (in === 0.U).asUInt
```

常见的类型转换：

+ `asUInt()`
+ `asSInt()`
+ `asBool()`

## Moudule Instantiation

chisel 中例化一个 module class 就等价于例化一个 verilog 的 module，具体方法就是 `Module` 调用 `new` 来创建一个新的 module，并把它赋值给一个 `val`，以便我们做端口连接。

```
#!scala
class Adder4 extends Module {
	val io = IO(new Bundle {
		val A    = Input(UInt(4.W))
		val B    = Input(UInt(4.W))
		val Cin  = Input(UInt(1.W))
		val Sum  = Input(UInt(4.W))
		val Cout = Input(UInt(1.W))
		})
    // Adder for bit 0
	val Adder0 = Module(new FullAdder())
	Adder0.io.a := io.A(0)
	Adder0.io.a := io.B(0)
	Adder0.io.cin := io.Cin
	val s0 = Adder0.io.sum
	// other bits ...
}

```

## Vec Class

`Vec` 类等价于 verilog 中的寄存器组，语法如下，

```
#!scala
val myVec = Vec(Seq.fill( <number of elements> ) { <data type})
```

有点类似 C++ 中的 vector，需要指明内部存放的数据类型，但是还需要额外指定 vector 的长度，举例如下，

```
#!scala
val ufix_vec10 := Vect(Seq.fill(10) { UInt(5.W) })
val reg_vec32 = Reg(Vec(Seq.fill(32) { UInt() }))
```

给 vec 中的元素赋值或访问特定元素的方法，也和 verilog 类似，只不过是用 `()`，

```
#!scala
val reg5 = reg_vec(5)
reg_vec32(0) := 0.U
```

还能用 vec 来例化一组 module，此时语法稍微有点不一样，因为 module 的数据类型和内置的 primitive 类型不一样，应该用 module 的 io Bundle，

```
#!scala
val FullAdders = Vec(Seq.fill(16) { Module(new FullAdder()).io })
```

## Parameterization

chisel 也可以实现 verilog 的参数化，

```
#!chisel
class FIFO(width: Int, depth: Int) extends Module {...}

val fifo1 = Module(new FIFO(16, 32))
val fifo2 = Module(new FIFO(width = 16, depth = 32))
val fifo3 = Moudle(new FIFO(depth = 32, width = 16))
```

## Built In Primitives

和 verilog 类似，chisel 中也定义了很多原语，这些原语和编译器绑定在一起，可以直接使用，比如 `Reg`, `UInt`, `Bundle`, `Mem` 和 `Vec` 等。

`Mux` 原语，有三个输入，`select` 信号是 Bool 类型，`A` 和 `B` 可以是任意类型，任意宽度的信号，只要他们的类型一致即可。当 select 为 `true` 时输出 `A`，反之 select 是 `flase` 时输出 `B`。

```
#!chisel
val out = Mux(select, A, B)
```

## Writing Scala Testbenches

模板：

+ 使用 `poke` 设置输入
+ 使用 `step` 控制仿真的进度
+ 使用 `expect` 或者是 `peek` 检查输出
+ 不断重复直到所有的 test case 全部验证通过

chisel 的 testbench 可以做简单的检查，跑基本的测试，但是对于比较大的设计，因为 chisel 本身的不完备，testbench 会变得非常复杂，速度也很很慢。所以官方建议用 C++ 的 emulator 或者是 verilog 的一套工具进行严谨的测试。

## Creating Your Own Project

如果是自己创建项目，需要按照 sbt 的规则创建目录，很麻烦。推荐使用官方提供的模板 [chisel template][tempalte]，在其基础上修改是最省事的。

[template]: https://github.com/freechipsproject/chisel-template

## Memory

只读 memory 可以用 `Vec` 实现，

```
#!scala
val numbers = Vec(0.U, 1.U, 2.U, 3.U)
```

可读可写的 memory 用原语 `Mem`实现，

```
#!scala
// asynchronous read
val CombMem = Mem(<size>, <type>)

// synchromous read
val SeqMem = SyncReadMem(<size>, <type>)

// adding write ports
when (<write condiation>) {
	<memory name>( <write address> ) := <write data>
}

// asynchronous read ports
when (<read condition>) {
	<read data 1> := <memory name>( <read address 1>)
	...
	<read data N> := <memory name>( <read address N>)
}

// synchromous read ports
val read_port = Reg(UInt(32.W))
when (re) {
	read_port := myMem(raddr)
}
```

注意：chisel 中 `Mem` 不能指定初始化值。


## def

```
#!scala

```

## Ref

[Chisel Tutorial Wiki][tutorial]

[Chilse3 Wiki][chisel3]
