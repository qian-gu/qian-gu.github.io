Title: 《Verilog and SystemVerilog gotchas》笔记
Date: 2020-12-17 22:13
Category: IC
Tags: Verilog, SystemVerilog
Slug: verilog_and_systemverilog_gotchas_notes
Author: Qian Gu
Summary: 读书笔记

!!! note
    1. 这本书非常老，第一作者 Sutherland 已经去世了。虽然有对应的中文翻译版本，但是翻译和校对的质量很差，语句不同顺，笔误满天飞，可能看英文版理解起来更通顺一些
    2. 只记录了 Design 相关的陷阱，Verfication 相关的陷阱没有记录

## 关于作者

Stuart Sutherland 是 Verilog 和 SV 标准的起草者，也是业界培训大佬，写了很多著名的书和培训教程。

Q：什么是陷阱？

A：符合语法规则，但是结果并不符合预期，比如常见的 C 语言中 `if(a=b)` 把比较写成了赋值。

产生陷阱的原因：

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
| 笔误和忘记声明会导致工具自动推断出未声明的隐式 wire，可能导致功能错误 | 高级编辑器 or 使用 `.name` 或 `.*` 方式连接端口 |
| 自动推断的内部隐式 wire 只有 1bit，可能导致位宽不匹配 | 工具会报端口位宽不匹配 |
| 多个文件使用 $unit 可能会导致命名冲突 | 使用 package 代替 $unit |
| 枚举类型 import 并不能导入其定义的标签 | 明确 import 标签 or 使用 `*` 通配符 |
| 使用 `*` import 多个 package 可能导致命名冲突 | 对于重复的标识符使用明确的 import 声明 |
| case 的数据类型（进制、符号）不匹配时可能产生功能错误 | 增加 default 分支 or 使用 unique case |
| 定义常数时位宽范围不正确，V/SV 自动截断 or 填充规则可能不符合预期 | lint 工具检查 or 写代码时明确匹配位宽和数值 |
| 位宽不匹配的赋值语句，扩展规则取决于表达式的类型和语句右侧的数据，可能和预期不符 |  |

## RTL 建模中的陷阱

## 运算符陷阱

## 常见的编程陷阱

## 面向对象和多线程编程陷阱

## 随机化、覆盖率和断言类陷阱

## 工具兼容性陷阱

