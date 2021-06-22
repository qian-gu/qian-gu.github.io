Title: 嵌入式软件开发基本知识
Date: 2021-06-22 14:51
Category: Embedded
Tags: Baremetal
Slug: embedded_software_dev_basic
Author: Qian Gu
Summary: 嵌入式软件开发流程笔记

!!! note
    主要以 GCC 为例，LLVM 的内容以后再补充。

## GCC 简介

`GCC` 一般有两个含义：GNU Compiler Collection 和 GNU C Compiler，这两个含义可以根据上下文分辨出来。顾名思义 GCC 作为 collection 概念时并不是一个单独的程序，而是很多程序的集合，所以一般也叫做“GCC 工具链”。

$$GCC 工具链 = GCC + CRT + Binutils + GDB$$

编译可以分为两类：

+ 本地编译：在一个平台上编译该平台运行的程序
+ 交叉编译：在一个平台上编译其他平台上的程序，主要用于嵌入式系统开发

### 命名规则

下载源码编译的过程略，主要记录一下 GCC 命名规则：arch[-vendor][-os][-(gnu)eabi]

+ arch：表示体系架构，如 arm, riscv64
+ vendor：工具链提供商
+ os：目标操作系统
+ eabi：嵌入式应用二进制接口 embedded application binary interface 

在 RSIC-V 下，几种名字的含义：

+ `riscv64-unknow-linux-gnu-` 作为前缀，表示提供商未知，适用于 RSIC-V 体系结构，默认按照 64bit 编译，使用 linux 下的 glibc 作为 CRT
+ `riscv32-unknow-elf-` 作为前缀，表示提供商未知，适用于 RSIC-V 体系结构，默认按照 32bit 编译，使用 newlib 作为 CRT

!!! warning
    前缀中的数字 32 和 64 与运行在 32/64bit 电脑上无关，而是指没有明确指定 -march 和 -mabi 时默认按照哪种位宽来编译程序。

### 常见编译选项

**`-march`**

因为 RISC-V 是模块化的，所以要指定具体使用那些子集，比如 `-march=rv32imafdc`，`-march=rv64gc` 等。

**`-mabi`**

指定 ABI 调用规则，主要包含整型和浮点两类，比如 `-mabi=ilp32`，`-mabi=lp32d` 等。

!!! warning
    -march 和 -mabi 组合必须相互兼容，否则会报错。比如 -march=rv32imac -mabi=lp32d 这个组合，march 指定了不会使用 F 和 D 子集，但是 mabi 又表示要支持 F 或者 D 子集，相互矛盾。

**`-mcmodel`**

有效值有两个：

+ `medlow`：表示程序寻址范围只能固定在 [-2G, 2G] 之间
+ `medany`：表示程序寻址范围可以是任意的 4G 内

## CRT

C 语言标准主要由两部分组成：C 语法描述 + C 标准库。其中 C 标准库定义了一组标准头文件，每个头文件包含了一些函数、变量、类型声明、宏定义。比如常用的 `printf` 函数就是定义在 `stdio.h` 这个文件中。

C 语言标准只定义了头文件，并不提供实现，所以在编译的时候，我们需要提供一个 C 运行时库（C Runtime Library, `CRT`）。Linux 下最常见的 CRT 是 `glibc` (GNU C Library)，它本身是 GNU 旗下的，后来成为 Linux 的标准 CRT，主要分布在 /lib 和 /usr/lib 目录下，文件名以 .so 结尾。Linux CRT 除了 glibc 之外，还有 uclibc 和 klibc 等，但是 glibc 使用最广泛。在嵌入式系统中常用的是 `newlibc`。

glibc 除了实现 C 标准之外，还封装了操作系统提供的系统服务，即系统调用的服务，所以和操作系统耦合的很紧，作为操作系统的一部分，安装的时候就自带了。

!!! tip
    对于 C++ 来说，最常用的 CRT 是 `libstdc++`，它一般和 GCC 绑定在一起，安装 GCC 的时候会把 libstdc++ 也安装上。libstdc++ 不会直接和系统内核打交道，对于系统级别的事件，libstdc++ 会通过 glibc 与内核通信。

## 软件编译过程

主要包含 4 个步骤：

1. 预处理 preprocessing
2. 编译 compilation
3. 汇编 assembly
4. 链接 linking

### 预处理

完成的工作有：

+ 将 `#define` 删除，展开所有宏定义，处理所有条件编译，比如 `#ifdef`
+ 处理 `#include`，把被包含的文件插入该位置
+ 删除所有注释
+ 添加行号和文件标识
+ 保留所有 `#pragma`

    #!shell
    gcc -E hello.c -o hello.i
    cpp hello.c -o hello.i

可以用 vim 打开看看 hello.i 的内容。

### 编译

完成的工作：对预处理的结果进行词法分析、语法分析、语义分析和优化，产生对应的汇编代码。

    #!shell
    gcc -S hello.i -o hello.s

可以用 vim 打开看看 hello.s 的内容。

### 汇编

对照汇编指令表，将编译结果一一翻译成汇编指令。

    #!shell
    gcc -c hello.s -o hello.o
    as hello.s -o hello.o

汇编的结果是 ELF 格式的可重定向目标文件，没法直接用 vim 打开查看，可以用 `readelf` 来查看相关信息。

### 链接

一般程序都会分成多个源文件，每个源文件都可以编译出对应的目标文件，这些目标文件再经过链接才形成最终的可执行文件。即使程序只有一个源文件，一般都会调用标准库，所以也需要链接器把系统提供的 CRT 代码链接到一起。

    #!shell
    gcc hello.c -o hello
    # 直接使用 ld hello.o -o hello 会报错，因为没有明确指出其需要的依赖库，引导程序和链接脚本

链接分为两类：

+ 静态链接，在编译阶段把依赖库代码复制到可执行程序中，最终的体积比较大

    #!shell
    gcc -static hello.c -o hello
    size hello
    ldd hello

+ 动态链接：在链接阶段只加入一些描述信息，在程序执行的时候，再从系统中把对应代码加载到内存中

    #!shell
    gcc hello.c -o hello.o
    size hello
    ldd hello

### ELF

`ELF`(Executable and Linkable Format) 主要有 3 种：

+ Relocatable 可重定向文件：包含代码和适当的数据，用来和其他目标文件一起创建可执行文件 or 共享目标文件
+ Executable 可执行文件：保存可执行的程序，如 bash
+ Shared 共享文件：共享库 .so 文件

ELF 的文件格式示意图略，常见的几个 section 含义如下：

| section | 用途 |
| ------- | ---- |
| .text   | 已编译程序的指令代码段                |
| .rodata | 只读数据                           |
| .data   | 已初始化的 `全局变量` + `静态局部变量` |
| .bss    | 未初始化的 `全局变量` + `静态局部变量` |
| .debug  | 调试符号表，辅助 debugger            |

可以通过 `readelf` 命令来查看 ELF 文件的信息

#!shell
readelf -a hello

因为 ELF 无法直接用文本编辑器打开，所以一般通过反汇编的方式查看。

### 反汇编

```
#!shell
objdump -D hello > hello.dump
# 用 -S 可以将 C 和汇编混合显示，gcc 需要加上 -g 选项
gcc -g hello.c -o hello
objdump -S hello > hello.dump
```

## 嵌入式软件的特点

前面以 hello world 为例简单说明了 Linux 环境下的编译过程，在这些基础上，嵌入式开发还有一些其他特点：

+ 交叉编译 + 远程调试
+ 需要自己定义引导程序
+ 需要自己定义中断服务程序
+ 主要注意减小代码体积
+ 需要移植 printf
+ 使用 Newlib 作为 CRT

### 交叉编译 + 远程调试

嵌入式平台本身资源很有限，无法将各种开发工具都安装在上面，所以一般都是在 PC 用 GCC 开发编译，最后将编译好的二进制文件下载到嵌入式平台运行。调试的时候同理，用 PC 上的 GDB 进行远程调试。

### 定义引导程序

不能依赖 OS 来做这些“脏活累活”，一般包含初始化硬件、设置异常和中断向量表、复制程序到 SRAM、代码重映射、最后跳转到 main 函数入口这些步骤。

### 定义中断服务程序

### 减小代码体积

常见方法：

+ 使用 `newlib-nano`
+ 正式版本程序不包含 printf 等大型函数
+ 如果一定要用，自己实现简化版 printf
+ 在 C/C++ 语法层次和程序开发层次进行优化

### 移植 newlib

为了适应各种嵌入式系统，newlib 将库函数的实现与 OS、底层硬件分层隔离，newlib 的所有库函数都依赖 20 个桩函数，这 20 个桩函数完成具体 OS 和底层硬件相关的功能。所以移植 newlib 的关键就是找到/实现这些桩函数。

### BSP

上述的这些特点最终会打包成 BSP 的形式来实现，包含了：

+ 底层硬件设备的地址分配信息
+ 底层硬件设备的驱动函数
+ 系统的引导程序
+ 中断和异常服务程序
+ 系统的链接脚本
+ 使用 newlib 时提供桩函数的实现

## SDK

为了方便用户使用，一般 MCU 提供商会进一步打包，提供 SDK 方便用户开发。SDK 不是一个软件，而是一个开发环境，一般包含了：

+ BSP
+ Makefile
+ 示例 software
+ 常用脚本

## 汇编语言程序设计

虽然现在编译器已经很厉害了，绝大数时间我们都是用高级语言开发，但是在某些特殊场合，比如底层驱动、引导程序、高性能算法库等，汇编还是有着重要作用。

一般的 GCC 汇编语法和 C 与汇编的混合编程略，查询 GCC 手册即可。