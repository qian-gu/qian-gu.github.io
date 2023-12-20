Title: 《Verilog and SystemVerilog gotchas》笔记
Date: 2021-04-25 22:13
Category: IC
Tags: Verilog, SystemVerilog
Slug: verilog-and-systemverilog-gotchas-notes
Author: Qian Gu
Summary: 读书笔记，总结常见“语法坑”

!!! note
    1. 这本书[《Verilog and SystemVerilog gotchas》][book]非常老，第一作者 Sutherland 已经去世了。虽然有对应的中文翻译版本，但是翻译和校对的质量很差，语句不同顺，笔误满天飞，可能看英文版理解起来更通顺一些
    2. 只记录了 Design 相关的陷阱，Verfication 相关的陷阱没有记录

[book]:https://book.douban.com/subject/2859647/

## 关于作者

Stuart Sutherland 是 Verilog 和 SV 标准的起草者，也是业界培训大佬，写了很多著名的书和培训教程。

Q：什么是陷阱 `Gotcha`？

A：符合语法规则，但是结果并不符合预期，比如常见的 C 语言中 `if(a=b)` 把比较写成了赋值。

Verilog/SV 产生陷阱的原因：

+ 继承自 C/C++ 的陷阱
+ 松散的类型操作，即操作符可以执行任意类型的数据
+ 允许良莠不齐的模型设计（可综合 and 不可综合）

Verilog 的标准：

+ Verilog-1995 (`IEEE Std 1364-1995`)
+ Verilog-2001 (`IEEE Std 1364-2001`)
+ Verilog-2005 (`IEEE Std 1364-2005`)

SV 的标准：

+ IEEE Std 1800-2005
+ IEEE Std 1800-2009（合并 IEEE 1364-2005 和 IEEE 1800-2005）
+ IEEE Std 1800-2012

## 声明以及字符表述类陷阱

| 陷阱 | 如何避免 |
| ------- | ----- |
| VHDL 大小写不敏感，而 V/SV 大小写敏感 | 良好的 coding style |
| 笔误和忘记声明会自动推断出隐式 wire，可能导致功能错误 | 高级编辑器 / 使用 `.name` 或 `.*` 方式连接端口 |
| 自动推断出的内部隐式 wire 只有 1bit，可能导致位宽不匹配 | 工具会报端口位宽不匹配 |
| 多个文件使用 $unit 一起综合可能会导致命名冲突 | 使用 package 代替 $unit |
| var 可以在任何地方声明，但是必须先声明后使用 | coding style 约束所有声明放在最前面 |
| 枚举类型 import 并不能导入 label | 明确导入每个 label / 使用 `*` 通配符导入 |
| 使用通配符 `*` 导入多个 package 可能出现命名冲突 | 使用显式的 import 导入 |
| case 的数据类型（进制、符号）不匹配时可能产生功能错误 | 某些场景下可以使用 unique case |
| 带 base 的常数默认是 unsigned，不带 base 的常数默认是 signed | 小心使用 |
| 定义常数时位宽范围不正确，截断/填充规则可能不符合预期 | lint 工具检查 / 写代码时明确匹配位宽和数值 |
| 位宽不匹配的常数赋值语句，截断/扩展规则取决于等号右侧常数的类型，可能和预期不符 | 小心使用 |
| `data = 'b1` 并不能设置 data 为全 1 | 使用 SV 语法 `data = '1` |
| 笔误可能导致 `{}` 和 `'{}` 混淆使用，不会有语法问题但是功能不正确 | 小心使用 / lint 工具 |
| module 端口位宽不匹配可能导致出错 | 注意工具 warning / 使用 `.name` 或 `.*` 方式连接端口 |
| input/output 端口可以反向使用而且不会报错 | 使用 logic 代替所有的 wire/reg |
| real 类型无法作为端口传递 | Verilog 必须使用系统函数 / SV 需要特别声明 |

## RTL 建模中的陷阱

| 陷阱 | 如何避免 |
| ------- | ----- |
| `always *` 可能推断不出所调用的 function 用到的所有信号 | 使用 `always_comb` |
| array 如何添加到敏感列表中？ | 使用 `always_comb` |
| vector 和 posedge/negedge 配合时，只会处理 LSB | 避免使用，如果一定要用 vector 必须先转化成 1bit 信号 |
| posedge/negedge 只被敏感列表中表达式的结果触发，不受操作数的影响 | 使用 `always_comb` |
| 不恰当的 begin...end 可能导致时序逻辑功能错误 | `always_ff` 不需要 begin...end，只有内部 if...else 需要 |
| 有些信号可能在 reset 块中会被不小心漏掉，导致功能错误 | lint、coverage 等工具报错 |
| 时序逻辑误用阻塞赋值，组合逻辑误用非阻塞赋值 | lint 工具报错 / `always_comb`、`always_ff` |
| 组合逻辑块中语句的顺序错误可能导致仿真和实际硬件行为不一致 | 写代码时小心 |
| `parallel_case` 使用不当导致仿真和硬件行为不一致 | 增加 default 分支 / `unique case`、`priority case` |
| 粘贴复制导致的重复条件分支，只会执行第一个分支，导致与设计意图不符 | lint 工具 / `unique case` |
| 不恰当使用 `unique` 导致功能不正确 | 关注 warning |
| 使用 2-state 信号建模可能导致仿真出错 | 避免使用 2-state 信号 / 使用 `always_comb`, `always_ff` |
| 内部 X 态可能并不会传播到端口上，导致错误未被发现 | 使用 SVA |
| Verilog 允许 net 多驱动，可能出现功能错误 | lint 工具 / 使用 SV 的 `always_comb` |

## 运算符陷阱

| 陷阱 | 如何避免 |
| ------- | ----- |
| SV 不允许在条件语句中包含赋值语句 | 小心使用 |
| 有些操作符是 context-determined，有些操作符是 self-determined | 理解操作符的含义 |
| 设计者错误理解赋值语句的 bit 扩展规则 | 理解 loosely type，小心使用 |
| 有符号运算是 context-determined | 使用时确认右边的操作数类型 |
| 从 signed 部分选择的结果是 unsigned 类型，可能与意图不符 | 使用 `$signed()` 或 `signed'()` |
| 自增/自减是阻塞赋值，错误使用 | 仅在组合逻辑中使用自增/自减 |
| 错误认为前自增/后自增相同 | 理解含义，谨慎使用 |
| 仿真中的求值短路可能导致仿真和硬件行为不一致 | 避免使用对操作数产生副作用的建模方式 |
| 把 `~` 和 `!` 的作用视为相同（实际不同） | 逻辑判断中永远不要使用 `~` |
