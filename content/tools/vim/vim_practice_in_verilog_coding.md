Title: Verilog coding 中的 Vim 实践
Date: 2020-06-06 15:10
Category: Tools
Tags: Vim
Slug: vim_practice_in_verilog_coding
Author: Qian Gu
Summary: verilog coding 小技巧备忘
Status: draft

有些模块的端口有大量的信号和注释行，如下面的代码所示，

    #!verilog
    module my_module #(
        // clk & rst
        input clk,
        input rst_n,
        // module 1 port
         
        input  wire  [31 : 0]  signal_1   // signal to module 1
        // module 2 port
        
        input  wire  [31 : 0]  signal_2   // signal to module 2
        input  wire  [31 : 0]  signal_3   // signal to module 2
        // module 3 port
        output  wire  [31 : 0]  signal_3   // signal to module 3
        )
        // do something
    endmodule

在集成的时候，把端口信号复制出来后要大批量的重复操作，

+ 删除所有的空白行
+ 删除所有的注释行
+ 删除所有的末尾注释，统一在行尾对齐位置加上括号和逗号

这些操作如果手动完成非常费时费力，而且容易手抖出错。回忆一下手工删除操作的步骤，

1. 挑选出符合条件的行
2. 将其删除

第一个步骤可以用正则表达式完成匹配，第二个步骤可以通过 vim 的替换命令完成，只要将一个行替换成空就能实现删除效果。

而对于统一在行尾对齐位置加括号和逗号的功能，可以通过录制一个 macro 的方式实现。

下面记录一下心得。

## 正则表达式

正则表达式功能非常强大，但是语法也比较琐碎，不容易记住，下面总结几种常见的符号及其含义。

## vim 替换命令

使用 vim 的替换功能，vim 中的替换功能命令的格式是 `:[range]s/from/to/[option]`，其中

+ `[range]` 表示替换范围，常见的全局替换为 `:%`，部分行替换可以先用 visual 模式选中目标范围，然后使用全局替换的命令，或者直接输入行号范围 ``

## 删除空白行

// TODO: insert gif

## 删除注释行

// TODO: insert gif

## 对齐插入括号和分号

在某一行中录制 macro：

    #!vim
    qa                      # start record
    $                       # jump to head of line
    /,                      # find comma
    d$                      # delete all after comma
    A                       # append
    [space to 70]           # append space to column 70
    esc                     # back to normal view
    $                       # jump to head of line
    60l                     # jump to column 60
    A                       # insert
    (),                     # insert 
    esc                     # back to normal view
    q                       # quit record

录完之后，一段 macro 存在寄存器 a 中，要使用的时候，用 visual 模式选中目标行之后输入下面的命令即可，

    #!vim
    :<>normal @a

意思是在选中的行上重复寄存器 a 中的 macro。

上面的例子效果如下所示，

// TODO: insert gif
