Title: 开源 IC 工具/库 —— verible
Date: 2025-05-29 01:17
Category: Tools
Tags: IC-tools, verible
Slug: verible
Author: Qian Gu
Series: Open IC Tools & Library
Summary: 总结 verible 的常用使用方法

## Verible

[verible][verible] 是一个由 Chips Alliance 开发的 SystemVerilog 开发者工具套件，包括解析器、风格检查器、格式化工具和语言服务器。Verible 的主要任务是解析 SystemVerilog（IEEE 1800-2017），适用于多种应用场景，如开发者工具。它支持解析未经预处理的源文件，适用于单文件应用，如风格检查和格式化。此外，Verible 还可以适应解析预处理的源文件，这是真实编译器和工具链所需要的。

[verible]: https://github.com/chipsalliance/verible

### Installation

从源码编译要安装一大堆工具，最省事的方法是从 github 上下载最新 release 的二进制文件，下载后把路径添加到 `$PATH` 变量即可。

```bash
export PATH=$HOME/.local/verible/bin:$PATH
```

命令行能自动补全则说明安装成功。

### Formatter

可以通过 `--helpfull` 选项查看 formatter 支持的选项，大部分都顾名思义，其中有个别选项含义有点模糊，记录如下。

`--column_limit` 看名字似乎是 format 自动 wrap 代码到最大列，实际上并不是。这个 flag 设置了 formatter 生效的最大列宽，当代码列宽超过这个值时就会停止 format，不再对后续 line 做 format。所以还是需要我们自己手动 wrap 或者依靠编辑器自动换行。

虽然不能自动插入换行，但是 formatter 可以自动删除冗余的换行，把多行合并成一行（所谓的换行是冗余的，就是删除多行之间的换行后合并成的一行仍然没有超过 column_limit）。如果多行合并后超出了 column_limit，则完全不进行合并。比如一个 assign 语句分成了 3 行写，每行的列宽分别为 70，5，10，且设置的 column_limit 为 80，那么因为 70+5+10 > 80，即使 70+5 < 80，也并不会合并前两行。

`--line_break_penalty`：

`--over_column_limit_penalty`：

`--wrap_spaces`：

`--named_parameter_alignment`：子模块例化时 parameter 传参括号的对齐位置。

`--named_parameter_indentation`：子模块例化时 port 括号的对齐位置。

`--port_declarations_right_align_packed_dimensions`：packed array port 向右对齐，即最低维度对齐。（很有用）

`--port_declarations_right_align_unpacked_dimensions`：unpacked array port 向右对齐，即最低维度对齐。（很有用）

`--try_wrap_long_lines`

和其他工具的集成：

- vs code：插件 SystemVerilog and Verilog Formatter
- vim：neoformat
