Title: 可配置设计
Category: IC
Date: 2015-04-17
Tags: configurable design
Slug: configurable-design
Author: Qian Gu
Summary: 总结可配置设计

[Verilog 编程艺术][book1] 的可配置设计一章 学习笔记。

[book1]: https://book.douban.com/subject/26612391/
## Configurable design
* * *

> 我们做设计的时候，就要考虑做成可以灵活配置的设计，不管是小模块，还是大模块，这样便于以后维护和移植。可配置模块的设计方法如下：
>
> 1. 使用 parameter 和 `define
> 
> 2. 使用 for 语句生成多条语句
> 
> 3. 使用 generate、for、if 等语句生成多条语句和多个实例化
> 
> 4. 通过工具或脚本生成配置参数
> 
> 5. 通过工具或脚本直接生成 Verilog 代码

书里面总结了上面的这些方法，以前总结过另外一篇博客：Verilog 中的参数化建模，里面总结了 条件编译、`define、parameter、localparam 的用法和区别。

[Reuse Methodology Manual for System-on-a-Chip Designs][book2] 是一本很经典的书，里面有全面详细的可重用设计的方法，有时间了看了再补上。

[book2]: https://book.douban.com/subject/2125482/

## Paramter

可配置设计最基本的方法，将配置选项放到端口参数上。

**优点：** user 直接在例化时传递参数，无需修改 submodule 的源代码

**约束：** 必须从 top 一级一级传递下去，每次修改 submodule 内的所有模块都需要同步修改

**缺点：** 参数数量多时 parameter list 冗长，修改不灵活

## define

主要用于条件编译，比如条件定义是否包含某组端口或者例化某个 submodule。

**优点：** 一处定义，处处使用

**缺点：** define 作用域问题

## Generate if/for

generate if 在 module 内部可以代替 define，但是无法在端口定义上无法代替 define。

generate for 或者是 for loop 在 module 内部可以实现参数化设计，典型例子是实现参数化的 N-1 mux。同理，当 case 分支的数量为参数化且每个分支内都可以写成统一的参数化形式时，就可以可以用 for 来代替 case。

```
#!systemverilog
// N-1 mux
always-comb begin
    dout = '0;
    for (int i = 0; i < N; i++) begin
        if (sel[i]) dout = din[i];
    end
end
```

## Package

SV 引入的新方法，将公有定义放到 package 中，供 module 内部使用。

**优点：** 公共定义几种在一个文件中，方便管理

**缺点：** 修改可配置参数，要修改 submodule 的源代码

## Package + Port Parameter

综合 Package 和 Port Paramter 的优点，具体方式：

- 在 package 中将 meta 和 generated 参数各自定义成一个 struct
- 在 package 中给出 default meta 和 default generated
- 每个 module 端口使用 struct 参数（解决 parameter list 冗长问题）
- 在 top 中计算重载过的 generated 参数

**优点：** 避免了冗长的 parameter list，且 parameter 定义集中在一起，方便管理；无作用域问题

**缺点：** parameter 仍然要层层传递，但 parameter list 仅包含 meta 和 generated，相对较少

```
#!systemverilog
// foo-pkg.sv
package foo-pkg;

    // meta paramter
    typedef struct packed {
        int     Length;
        int     Width;
    } cfg-t;

    // generated paramter
    typedef struct packed {
        int     Area;
        int     Perimeter;
    } gen-cfg-t;

    localparam cfg-t DefaultCfg = '{
        Length: 16,
        Width:  8 
    };

    localparam gen-cfg-t GenCfg = '{
        Area: DefaultCfg.Length * DefaultCfg.Width,
        Perimeter: (DefaultCfg.Length + DefaultCfg.Width)*2
    };

endpackage
```

```
#!systemverilog
// for-top.sv
module foo-top
    import foo-pkg::*;
#(
    parameter cfg-t Cfg = DefaultCfg
) (
    // port list
);

    localparam gen-cfg-t GenCfg = '{
        Area: Cfg.Length*Cfg.Width
        Perimeter: (Cfg.Length + Cfg.Width)*2
    }; 

    bar #(
        .Cfg(Cfg),
        .GenCfg(GenCfg)
    ) BAR (
        // port list
    );

endmodule
```

!!! note

     写了个小实验 module 测试了一下这种用法，verilator 编译是没有问题的，但是 iverilog 对 sv 的支持实在是太差了，编译会报错。

## Scripts

有些复杂且规律的模块，如 meory wrapper 等可以用脚本自动化生成。包括某些顶层的配置，也可以用 make 等工具自动化生成相关配置文件和代码。

### Adnes

Andes 的配置工具提供一个友好清晰的图形界面，点击相关配置后就会生成 config.inc 文件，其中包含了根据配置生成的 define 和 parameter，然后被每个 sv 文件所包含。

### Sifive

Sifive 提供一个基于网页的图形化配置界面，同样可以生成相关配置文件和代码。

### WestDegitial

WestDegital 的开源 risc-v core 使用 config/Make 的方式，首先运行 config 文件，通过命令行参数的方式进行自定义配置，会自动生成相关配置文件，包括：

```
#!text
snapshots/default
├── common-defines.vh                       # `defines for testbench or design
├── defines.h                               # #defines for C/assembly headers
├── pd-defines.vh                           # `defines for physical design
├── perl-configs.pl                         # Perl %configs hash for scripting
├── pic-map-auto.h                          # PIC memory map based on configure size
└── whisper.json                            # JSON file for swerv-iss
```

## Ref

[Verilog 编程艺术][book1]
