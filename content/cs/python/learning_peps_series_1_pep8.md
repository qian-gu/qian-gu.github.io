Title: PEP 学习系列 #1 —— PEP8
Date: 2020-04-12 13:55
Category: CS
Tags: PEP, python
Slug: learning_peps_series_1_pep8 
Author: Qian Gu
Series: Learning PEPs
Summary: 翻译 PEP8

[PEP 8 -- Style Guide for Python Code 原文链接][PEP8]

[PEP8]: https://www.python.org/dev/peps/pep-0008/

| item | detail |
| ---- | ------ |
| PEP  |  8     |
| Title | Style Guide for Python Code |
| Author | Guido van Rossum<guido at python.org>, Barry Warsaw<barry at python.org>, Nick Coghlan<ncoghlan at gmail.com> |
| Status | Active |
| Type | Process |
| Created | 05-Jul-2001 |
| Post-History | 05-Jul-2001, 01-Aug-2013 |

## 介绍

本文介绍 Python 主要发布版本中标准库的 code style，对于 CPython 中的 C 代码的 style guide 请查看相关文档 [PEP7][PEP7]。

本文和 [PEP257(docstring 规范)][PEP257] 来源于 Guido 写的原始文章：《python code style》，部分来自于 Barry 的 [GNU Mailman style guide][barry]。

本文随着语言本身的变化不断进化，舍弃了部分规则的同时新加了一些规则。

许多项目都有自己的 coding style guide，如果和本文有任何冲突，应该以该项目自己的 guide 为准。

[PEP7]: https://www.python.org/dev/peps/pep-0007/
[PEP257]: https://www.python.org/dev/peps/pep-0257/
[barry]: http://barry.warsaw.us/software/STYLEGUIDE.txt

## 尽信书，不如无书


Guido 的一个重要见解是：代码更多是用来读而不是写。本文提供的 guideline 的目的是提高代码的可读性，使得广泛的 python 代码保持一致性。正如 [PEP20][PEP20] 所述，“可读性非常重要”。

一篇 style guide 主要内容是一致性。虽然本文的一致性很重要，但是一个项目内的一致性更重要，最重要的是一个 module 或者 function 内部的一致性。

但最重要的是，要知道什么时候不保持一致性，在实际应用时候有些 guide 并不适用，如果有疑问，根据自己的最佳判断，看看其他代码例子然后决定怎么写代码看起来最好。不要羞于发问。

特别注意：不要为了遵守本文而破坏向后的兼容性！

一些可以忽略本 guideline 的情况：

1. 遵守本 guideline 会导致代码的可读性下降，即使对于那些习惯于遵守本文来阅读代码的人来说

2. （可能出于历史原因）为了保持和周边代码的一致性可以忽略本 guideline，虽然这是个清理其他人垃圾的好机会（实现真正的极限编程 Extreme Programming）

3. 代码出现在本规范之前，并且没有其他理由去修改它

4. 代码需要和不支持本规范的旧版本 Python 代码保持一致


[PEP20]: https://www.python.org/dev/peps/pep-0020/

## 代码布局

### 缩进

每级缩进为 4 个空格。

连续行应该按照包围的元素对齐，要么使用 python 圆括号、方括号、花括号的隐式行连接在垂直方向对齐，要么使用 `hanging indent`。使用 hanging indent 的时候应该注意，第一行不应该有任何参数，后续行多一级缩进以便和其他行能清晰地区分开。

    #!python
    # Correct:
    
    # Aligned with opening delimiter.
    foo = long_function_name(var_one, var_two,
                             var_three, var_four)
    
    # Add 4 spaces (an extra level of indentation) to distinguish arguments from the rest.
    def long_function_name(
            var_one, var_two, var_three,
            var_four):
        print(var_one)
    
    # Hanging indents should add a level.
    foo = long_function_name(
        var_one, var_two,
        var_three, var_four)

```
#!python
# Wrong:

# Arguments on first line forbidden when not using vertical alignment.
foo = long_function_name(var_one, var_two,
    var_three, var_four)

# Further indentation required as indentation is not distinguishable.
def long_function_name(
    var_one, var_two, var_three,
    var_four):
    print(var_one)
```

对于后续的行，4 个 space 的规则是可选的，

```
#!python
# Hanging indents *may* be indented to other than 4 spaces.
foo = long_function_name(
  var_one, var_two,
  var_three, var_four)
```

如果 if 语句的条件部分太长以至于要写成多行的形式，要注意，一个双字符的关键字（比如 if）加上一个空格，再加上右括号，会天然形成一个 4 space 的缩进。这会导致条件语句和 if 内部的嵌套语句（本身也是 4 space 缩进）产生视觉冲突。本文没有明确规定如何（是否需要）进一步在视觉上区分条件语句和内嵌语句，可选但是不限于下面几种方式：

```
#!python
# No extra indentation.
if (this_is_one_thing and
    that_is_another_thing):
    do_something()

# Add a comment, which will provide some distinction in editors
# supporting syntax highlighting.
if (this_is_one_thing and
    that_is_another_thing):
    # Since both conditions are true, we can frobnicate.
    do_something()

# Add some extra indentation on the conditional continuation line.
if (this_is_one_thing
        and that_is_another_thing):
    do_something()
```

（也可参考下面关于二元操作符前后断行的讨论）

右括号可以和最后一行第一个非空格字符对齐，

```
#!python
my_list = [
    1, 2, 3,
    4, 5, 6,
    ]
result = some_function_that_takes_arguments(
    'a', 'b', 'c',
    'd', 'e', 'f',
    )
```

也可以和第一行的第一个字符对齐，

```
#!python
my_list = [
    1, 2, 3,
    4, 5, 6,
]
result = some_function_that_takes_arguments(
    'a', 'b', 'c',
    'd', 'e', 'f',
)
```
> 注：`hanging indentation` 是指除了首行之外，其他行都缩进的打印风格。在 python 中，这个术语指的是一个带括号的语句，左括号是该行的最后一个字符，除了右括号，剩余行都会加上缩进

### Tabs 还是 Spaces？

首选空格 space 作为缩进方式。

只有为了和已有代码中的 tab 保持一致才能继续使用 tab。

python 3 不允许 tab 和 space 混合使用，python 2 中的 tab 和 space 混合使用时，应该先统一转换成 space。

如果 python 2 的命令行解释器带了 `-t` 选项，如果有 tab 和 space 混合使用的情况，它会报告 warning，如果带了 `-tt` 选项，则会报告 error。强烈推荐使用这些选项。

### 最大行长度

所有行的最大行长是 79 个字符。

对于基本没有结构化约束的长的文本（docstring和注释），其长度不能超过 72 个字符。

限制编辑器的宽度的好处是可以并列打开多个文件，在 code review 的时候比较两个版本的代码时很方便。

许多工具的默认 warp 功能会破坏代码的视觉结构，使得代码难以理解。选择这些限制的目的就是为了防止 warp 功能设置为 80 个字符的编辑器自动 warp，即使有些编辑器在最后一列放了一个标记来提醒。一些基于 web 的工具甚至都不提供 warp 功能。

一些团队强烈希望更长的行长，如果代码由一个可以达成一致的团队维护，那么可以把限制放宽到 99 个字符，但是注释和 docstring 仍然不超过 72 个字符。

Python 标准库是保守主义，所以要求行长不超过 79（docstring和注释不超过 72）。

对于很长的行，优先选择的方式应该是使用括号隐式的断行，而不是使用 `\` 来断行。

反斜线 `\` 有时候还是有用的，比如较长的 `with` 语句不能使用括号的方式，所以只能选择反斜线。

```
#!python
with open('/path/to/some/file/you/want/to/read') as file_1, \
     open('/path/to/some/file/being/written', 'w') as file_2:
    file_2.write(file_1.read())
```

（对于这种 with 语句，可以参考前面讨论 if 语句的处理方式）

这种情况的另外一个例子是 `assert` 语句。

确保在后续的行中适当地缩进。

### 应该在二元操作符的前还是后断行？

几十年以来，我们一直推荐的是在二元操作符之后断行，但是这样可能会伤害到代码的可读性，原因有两个：运算符一般分布在不同列，并且每个运算符和它的操作数被分开了，放到了操作数的前一行。下面的例子说明了需要读者的眼睛额外做一些工作来分辨那些变量是相加，哪些变量是相减，

```
#!python
# Wrong:
# operators sit far away from their operands
income = (gross_wages +
          taxable_interest +
          (dividends - qualified_dividends) -
          ira_deduction -
          student_loan_interest)
```

为了解决这个可读性的问题，数学家和出版商遵循了相反的约定。Donald Knuth 在他的 *`Computer and Typesetting`* 系列中解释了传统的规则：“虽然段落中的公式总是在二元操作符、关系操作符的后面断开，但是单独显示出来的公式却总是在二元操作符的前面断开。”

遵循数学家的传统通常可以得到可读性更好的代码：

```
#!python
# Correct:
# easy to match operators with operands
income = (gross_wages
          + taxable_interest
          + (dividends - qualified_dividends)
          - ira_deduction
          - student_loan_interest)
```

在 python 代码中，在二元符号之前或之后都可以断行，只要在本地保持一致即可。对于新写的代码，推荐使用 Knuth 的风格。

### 空行

顶层的 `function` 和 `class` 定义前后需要两个空行。

class 内部的 `method` 定义前后需要一个空行。

一组功能相关的 function 可以通过额外的一个空行来区分（谨慎使用）。一组相关的单行代码之间的空行可以省掉（比如一组 dummy implementation）。

在 function 内部（谨慎）使用空行区分逻辑段。

python 接受 `control-L` 作为空格，许多工具把这些字符当作页面分割符，所以你可以用它们来区分文件中的相关段落。注意，一些编辑器和基于 web 的阅读器可能无法识别 control-L，会在其位置显示一个其他符号。

### 源文件的编码格式

python 核心发布版本中的代码总是使用 UTF-8 来编码（python 2 中用 ASCII）。

python 2 中使用 ASCII 的文件和 python 3 中使用 UTF-8 的代码不应该有编码申明。

在标准库中，只有以测试目的或者注释、docstring 中需要提及包含非 ASCII 字符的作者名时，才能使用非默认编码方式；其他情况下，在字符串中优先使用 `\x`，`\u`，`\U`，`\N` 来转义非 ASCII 字符。

对于 python 3.0 和更高版本来说，标准库使用了下面的政策（见 [PEP3131][PEP3131]）：标准库中所有标识符 **必须** 使用 ASCII 标识符，并在尽可能使用英语单词（在很多情况下，缩写和术语是非英语）。除此之外，string literals 和注释必须也使用 ASCII。只有两个例外，

1. 测试非 ASCII 的测试用例

2. 作者的名字

如果作者的名字不是基于拉丁字符，**必须** 提供一个拉丁字母音译。

鼓励具有全球受众的开源项目采取类似的策略。

### Imports

+ `import` 通常应该分开每行一个，

        #!python
        # Correct:
        import os
        import sys

        # Wrong:
        import sys, os

    但是这么写也是 ok 的，

        #!python
        # Correct:
        from subprocess import Popen, PIPE

+ import 必须放在文件的顶部，位于 module 注释和 docstring 的后面，在模块的全局变量/常量的前面。

    import 应该按照下面的顺序分组：

    1. 标准库 import

    2. 相关的第三方库 import

    3. 本地应用/库的特定 import
    
    在每组之间插入一个空行。

+ 推荐使用绝对路径导入，因为当 import 系统配置不正确时（比如 package 内的一个目录以 `sys.path` 结尾），这么做的可读性更好，性能也更好（至少 error 信息更加清晰）。

        #!python
        import mypkg.sibling
        from mypkg import sibling
        from mypkg.sibling import example

    然而，显式的相对路径也是一种可接受的方案，特别是使用绝对路径会导致不必要的复杂 package 布局的情况。

        #!python
        from . import sibling
        from .sibling import example

    标准库中的代码应该避免复杂的 package 布局，并且永远使用绝对路径 import。

    隐式的相对路径 import 永远都不应该使用，在 python 3 中已经删除了它。

+ 当从一个包含 class 的 module 中 import 一个 class 时，一般可以这么写，

        #!python
        from myclass import MyClass
        from foo.bar.yourclass import YourClass

    如果这种拼写方式导致名字冲突，那么可以这么写，

        #!python
        import myclass
        import foo.bar.yourclass

    然后在代码中使用 `myclass.Myclass` 和 `foo.bar.yourcalss.YourClass`。

+ 应该避免使用通配符 `*`（`from <module> import *`），因为这样会使得命名空间中的名字变得不清晰，使很多读者和许多自动化工具产生混淆。有一种情况下可以使用 `*` ，即将内部的接口作为 public API 的一部分重新发布出来。（比如，有一个可选的加速模块，它有某个提前无法知道是否会被重写的端口，使用纯 Python 将其实现的情况）

    当使用这种重新发布名称时，以下关于 public 和 内部接口的规则仍然适用。

### 模块级别的 dunber name

模块级别的 `dunber`（即使那些使用双下划线 `__` 包围的名字），比如 `__all__`，`__author__`，`__version__` 等等，应该放在 module 的 docstring 的后面，任何 `import` 语句之前（`form __future__` 除外）。python 要求 future-import 必须位于除过 docstring 之外的任何代码之前。

```
#!python
"""This is the example module.

This module does stuff.
"""

from __future__ import barry_as_FLUFL

__all__ = ['a', 'b', 'c']
__version__ = '0.1'
__author__ = 'Cardinal Biggles'

import os
import sys
```

注：

`dunber` 指的是 `Double` + `Underscore` 的合体，指那些带双下划线的 method 或 attribute，如 `__init__`、`__main__`、`__verison__` 等。

https://wiki.python.org/moin/DunderAlias

> An awkward thing about programming in Python: there are lots of double underscores. [snip] My problem with the double underscore is that it's hard to say. How do you pronounce __init__? "underscore underscore init underscore underscore"? "under under init under under"? Just plain "init" seems to leave out something important. I have a solution: double underscore should be pronounced "dunder". So __init__ is "dunder init dunder", or just "dunder init".



## string 引用


在 python 中，单引号和双引号字符串是一样的，本文关于这个不会给出建议。选择一个规则并且坚持下去即可。当一个 string 包含单引号或者是双引号时，在内部使用另外一种引号，这样可以避免在代码内部使用反斜线 `\`，提高代码的可读性。

根据 [PEP257][PEP257]，对于三引号 string，永远使用双引号。



## 表达式和语句中的空格


### 一些小问题

避免下面情况中出现的无关空格，

+ 紧跟在括号之后

        #!python
        # Correct:
        spam(ham[1], {eggs: 2})
        
        # Wrong:
        spam( ham[ 1 ], { eggs: 2 } )

+ 在 trailing 逗号和右括号之间

        #!python
        # Correct:
        foo = (0,)
        
        # Wrong:
        bar = (0, )

+ 紧贴在逗号，分号，冒号之前

        #!python
        # Correct:
        if x == 4: print x, y; x, y = y, x
        
        # Wrong:
        if x == 4 : print x , y ; x , y = y , x

+ 然而，`slice` 内部的冒号就像是个二元操作符（把它当作是优先级最低的操作符），所以两边应该有相同数量的空格。在一个扩展 slice 中，所有的冒号必须有相同的间距。例外情况：slice 的一个参数被忽略了，它附带的空格也就被忽略了

        #!python
        # Correct:
        ham[1:9], ham[1:9:3], ham[:9:3], ham[1::3], ham[1:9:]
        ham[lower:upper], ham[lower:upper:], ham[lower::step]
        ham[lower+offset : upper+offset]
        ham[: upper_fn(x) : step_fn(x)], ham[:: step_fn(x)]
        ham[lower + offset : upper + offset]
        
        # Wrong:
        ham[lower + offset:upper + offset]
        ham[1: 9], ham[1 :9], ham[1:9 :3]
        ham[lower : : upper]
        ham[ : upper]

+ 紧跟在（函数调用参数列表）的左括号之后

        #!python
        # Correct:
        spam(1)
        
        # Wrong:
        spam (1)

+ 紧跟在 index 或者是 slice 的左括号之前

        #!python
        # Correct:
        dct['key'] = lst[index]
        
        # Wrong:
        dct ['key'] = lst [index]

+ 为了和其他赋值语句对齐，在赋值语句周围使用多于 1 个空格

        #!python
        # Correct:
        x = 1
        y = 2
        long_variable = 3
        
        # Wrong:
        x             = 1
        y             = 2
        long_variable = 3

### 别的建议

+ 避免尾部空格。因为一般它都是不可见的，这可能会导致困惑：比如，反斜线后面跟着一个空格和一个换行符时，并不算做是一个有效的续行标记。一些编辑器不会保留尾部空格，并且很多项目（比如 CPython 自身）在 commit 之前会有相关检查来滤掉它。

+ 永远在二元操作符两边加上单个空格，比如赋值 `=`，增量赋值 `+=`，`-=`，比较 `==`，`<`，`>`，`！=`，`<>`，`<=`，`>=`，`in`，`not`，`is`，`not`，布尔运算符 `and`，`or`，`not`。

+ 如果使用了具有不同优先级的运算符，考虑在低优先级的运算符周围加上额外的空格。使用自己的判断，但是空格数量不要超过 1 个，并且在二元运算符周围使用相同数量的空格。

        #!python
        # Correct:
        i = i + 1
        submitted += 1
        x = x*2 - 1
        hypot2 = x*x + y*y
        c = (a+b) * (a-b)
        
        # Wrong:
        i=i+1
        submitted +=1
        x = x * 2 - 1
        hypot2 = x * x + y * y
        c = (a + b) * (a - b)

+ 函数注解应该使用正常的冒号规则，如果有 `->`，要在其周围加上空格（参考下文函数注解部分的更多信息）

        #!python
        # Correct:
        def munge(input: AnyStr): ...
        def munge() -> PosInt: ...
        
        # Wrong:
        def munge(input:AnyStr): ...
        def munge()->PosInt: ...

+ `=` 用来标记关键字参数或者是参数默认值时，不要使用空格

        #!python
        # Correct:
        def complex(real, imag=0.0):
            return magic(r=real, i=imag)
        
        # Wrong:
        def complex(real, imag = 0.0):
            return magic(r = real, i = imag)

    当参数有类型注释且有默认值时，要在 `=` 周围加上空格

        #!python
        # Correct:
        def munge(sep: AnyStr = None): ...
        def munge(input: AnyStr, sep: AnyStr = None, limit=1000): ...
        
        # Wrong:
        def munge(input: AnyStr=None): ...
        def munge(input: AnyStr, limit = 1000): ...

+ 复合语句（单行有多个语句）一般是不允许的

        #!python
        # Correct:
        if foo == 'blah':
            do_blah_thing()
        do_one()
        do_two()
        do_three()

    最好不要这样，

        #!python
        # Wrong:
        if foo == 'blah': do_blah_thing()
        do_one(); do_two(); do_three()

+ 有时候 `if`/`for`/`while` 可以和一小块代码放在同一行，但是多行语句时不要这样做，同时避免行长太长导致折叠！

    最好不要这样，

        #!python
        # Wrong:
        if foo == 'blah': do_blah_thing()
        for x in lst: total += x
        while t < 10: t = delay()

    绝对不要这样，

        #!python
        # Wrong:
        if foo == 'blah': do_blah_thing()
        else: do_non_blah_thing()
        
        try: something()
        finally: cleanup()
        
        do_one(); do_two(); do_three(long, argument,
                                     list, like, this)
        
        if foo == 'blah': one(); two(); three()



## 什么时候使用尾部逗号


尾部逗号一般是可选的，除非是在构造单元素的 `tuple` 时它是强制性必须存在的，在 python2 的 `print` 中逗号是语法的一部分。为了清晰起见，推荐用（冗余的）圆括号包围起来：

```
#!python
# Correct:
FILES = ('setup.cfg',)
```

```
#!python
# Wrong:
FILES = 'setup.cfg',
```

使用版本控制系统时冗余的尾部逗号通常非常有用，比如随着时间发展，由值或者是参数组成的 `list`，`import` 的内容不断增多的时候，在最后加上尾部逗号非常有用。一般的写法是每个值一行，然后在最后添加一个元素后面加上尾部逗号，最后在下面的另外一行加上右括号。但是如果元素都在同一行，那么就没有理由加尾部逗号（除非是上面提到的单元素 tuple）：

```
#!python
# Correct:
FILES = [
    'setup.cfg',
    'tox.ini',
    ]
initialize(FILES,
           error=True,
           )
```

```
#!python
# Wrong:
FILES = ['setup.cfg', 'tox.ini',]
initialize(FILES, error=True,)
```



## 注释


和代码相冲突的注释比没有注释更糟糕，在代码改变之后永远第一时间更新相关注释。

注释应该是完整的句子，除非是用标识符开头的语句（永远不要改变标识符的大小写！），其他情况下第一个单词的首字母应该大写。

块注释一般由一段或者是多段的完整句子组成，并且每句都带一个句号。

在多语句的注释中，每句结束后面应该有两个空格，除非是最后一句。

用英语写注释时，遵循 [`Strunk and White`][strunk and white] 风格

如果你是非英语 python 码农，请使用英语写注释，除非你 120% 确保代码永远不会被不说你母语的人读到。

[strunk and white]: https://book.douban.com/subject/3296585/

### 块注释

块注释一般放在代码前面，和代码的缩进同级，块注释中的每一行都以 `#` + 一个空格开头（除非是注释内部的缩进）。

块注释内部的段落用一个以 `#` 开头的空行隔开。

### 行内注释

谨慎地使用行内注释。

行内注释指的是和代码在同一行的注释，行内注释和代码应该用至少 2 个空格隔开，且以一个 `#` + 一个空格开始。

行内注释一般没有必要，事实上还会分散注意力。不要写类似下面的注释，

```
#!python
x = x + 1                 # Increment x
```

但是有时候，这样写是很有用的，

```
#!python
x = x + 1                 # Compensate for border
```

### docstring

docstirng 的规则总结在 [PEP257][PEP257] 内，其内容永远都不会改变。

+ 为所有的 public `module`, `function`, `class`, `method` 写 docstirng。对非 public method 没有必要写 docstirng，但是你应该写个注释描述该 method 的作用。这个注释应该出现在 `def` 行的下面。

+ [PEP257][PEP257] 描述了良好的 docstirng 惯例，要特别注意的是，多行的 docstirng 的结尾 `"""` 应该单独放一行。

        #!python
        """Return a foobang
        
        Optional plotz says to frobnicate the bizbaz first.
        """

+ 对于单行的 docstring，把结尾的 `"""` 放在该行内



## 命名规范


python 库的命名规则有点混乱，我们一直没有完全统一，然而，这里列了一些当前推荐的命名标准。新写的 `module` 和 `package`（包括第三方的 framework）应该遵守下面的标注，但是如果一个已经存在的库有其他的 style，只要内部保持一致性即可。

### 最重要的规则

API 中那些对用户可见的公共接口的名字，应该遵循反映用法而不是内部实现的原则。

### 描述性的：命名风格

有许多不同的命名 style，下面这些可以帮助我们识别出正在使用什么样的 style，而和他们用来做什么没有关系。

下面是一些常见的方式：

+ `b`（单个小写字母）

+ `B`（单个大写字母）

+ `lowercase` 小写

+ `lower_case_with_underscores` 小写带下划线

+ `UPPERCASE` 大写

+ `UPPER_CASE_WITH_UNDERSCORES` 大写带下划线

+ `CapitalizedWords`（或者叫 CapWords，CamelCase —— 驼峰命名法），有时也叫做 StudlyCaps

    注意：在驼峰中使用首字母缩写时，所有字母都要大写，所以 `HTTPServerError` 比 `HttpServerError` 要好

+ `mixedCase`（和驼峰不同之处在于第一个字母小写）

+ `capitalized_Words_With_Underscores`（丑陋！）

还有一种使用短缩写前缀来使一组相关的名字形成一个 group，Pyhton 中这种场景并不多见，这里只是为了全面而提一下。比如，`os.stat()` 函数返回了一个 `tuple`，内部的变量是 `st_mode`, `st_size`, `st_mtime` 之类的名字。（这么做的目的是为了强调和 `POSIX` 系统调用的相关性，以帮助程序员熟悉它）

X11 库里面所有的 public 函数都加了 `X` 前缀，在 python 里，这种风格通常是没有必要的，因为 `attribute` 和 `method` 调用的时候前面一般都会带上 object 前缀，而函数名前面会带上 module 的名字。

除此之外，下面的这种带前缀或后缀下划线 `_` 的格式是可以的（通常和一些惯例结合在一起使用）：

+ `_single_leading_underscore_`，弱“内部使用”标志。比如，`from M import *` 不会导入类似以 `_` 开头的对象

+ `single_trailing_underscore_`，用来避免和 python 内部的关键字相冲突

        #!python
        Tkinter.Toplevel(master, class_='ClassName')

+ `__double_leading_underscore`，用来给 class 的 attribute 命名，调用它时会被矫正（在 class FooBar 中，`__boo` 会变成 `_FooBar_boo`）

+ `__double_leading_and_trailing_underscore__`，“magic” 对象/attribute，存在于用户控制的 `namespcae`，比如，`__init__`，`__import__`，或者 `__file__`。仅仅像文档说明的这样用，永远不要自己发明这种名字。

### 规范性的：命名惯例

#### 避免使用的名字

永远都不要使用小写字母 `l`，大写字母 `O`，大写字母 `I` 作为单字母变量名。

在某些字体中，这些字符会和数字 0/1 混淆不清，如果要使用小写字母 `l`，使用 `L` 代替。

#### 兼容 ASCII

如 [PEP3131][PEP3131] 中所述，标准库中的标识符必须是 ASCII 兼容的。

[PEP3131]: https://www.python.org/dev/peps/pep-3131

#### package 和 module 的名字

`module` 必须使用简短，全小写的名字。如果使用下划线能提高代码的可读性，那么就可以使用。 虽然不鼓励使用下划线，但是 `package` 也必须也用简短、全小写的名字。

如果一个模块的底层实现使用的是 C/C++，并且有个用 python 模块来提供更高层次接口（比如，面向对象），那么这个 C/C++ module 名字必须要有下划线前缀（比如，`_socket`）。 

#### class 的名字

class 的名字一般应该使用 `CapWords` 的惯例。

如果 interface 被文档化了并且主要作为被调用的场景，那么可以换成 function 的命名惯例。

注意，对于内置的名字有个单独的惯例：大部分内置名字一般是单个单词（或者是两个单词连在一起），`CapWords` 之用于 exception 和内置常量。

#### 类型变量的名字

在 [PEP484][PEP484] 中的类型变量名字，相比于短名字，如 `T`, `AnyStr`，`Num`，一般优先使用 `CapWords`。推荐给变量加上后缀 `_co` 或者是 `_contra` 来声明相关的协变量或者是逆变量。

```
#!python
from typing import TypeVar

VT_co = TypeVar('VT_co', covariant=True)
KT_contra = TypeVar('KT_contra', contravariant=True)
```

[PEP484]:https://www.python.org/dev/peps/pep-0484

#### Exception 的名字

因为 exception 应该是个 class，所以使用 class 的规则即可。但是，如果某个 exception 确实是个 error，则应该给它加上 `Error` 后缀。

#### 全局变量名

希望这些变量只会在单个 module 内使用。它的命名规则和 function 一样。

通过 `from M import *` 来使用的 module，应该使用 `__all__` 机制来防止暴露 global 变量，或者使用以前加前缀的规则，比如给这些 global 变量加上单个下划线（表明你想暗示这些变量是 module 内，非 publicc 的）。

#### Function 和 变量 名

function 名应该小写，如果有必要，使用下划线将单词分隔开以提高可读性。

变量名和函数的规则一样。

只有在为了和旧代码（比如 `threading.py`）保持兼容性时，才允许使用 `mixedCase` 风格的名字。

#### Function 和 Method 的参数

永远要把 `self` 作为例化 mehod 的第一个参数。

永远使用 `cls` 作为例化 class 的第一个参数。

如果一个 function 的参数名和关键字相冲突，一般最好在尾部加一个后缀的单下划线，而不是使用缩写或是故意拼写错误。所以 `class_` 比 `clss` 要更好（也许最好的方式是使用一个同义词来避免这种情况）。

#### Mehtod 和 Instance 的名字

使用和 function 一样的命名规则：用下划线把小写单词分隔开以提高可读性。

只有非 public 的 method 和 instance variables 才可以加上前缀下划线。

为了避免和类名相冲突，使用两个前缀下划线来触发 python 的命名矫正规则。

python 会使用 class 的名字来矫正这些名字：如果 class `Foo` 有一个名字为 `__a` 的 attribute，则无法通过 `Foo.__a` 来访问它（用户可以通过 `Foo._Foo__a` 的方式来访问）。一般来说，双下划线前缀只应该用来避免和子类中的名字相冲突的情况。

#### 常量

常量定义一般和 module 同级别，并且全部大写，用下划线隔开单词。比如 `MAX_OVERFLOW` 和 `TOTAL`。

#### 继承的设计

始终要考虑一个 class 的 method 和 instance variables（统称为：`attribute`）应该是 public 还是 non-public。如果有疑问，那么就选择做成 non-public；因为之后将其再改为 public 要比反过来做更容易。

public attribute 是那些你希望和你的 class 不相关的用户可以使用的 attribute，并且你应该保证以后修改时不会发生向后不兼容的情况。non-public attribute 是那些不打算给第三方使用的 attribute，你没必要保证 non-public attribute 以后不会改变或甚至是被删除。

我们不使用术语 `private`，是因为 python 里面的 attribute 并不是真正的 private（为了避免大量不必要的工作）。

基类中还有另外一类 attribute，它们会作为 subclass API 中一部分（通常在别的语言里面叫作 `protected`）。有些 class 被特意设计成被继承形式，一般是为了扩展或者修改原来 class 的行为。当设计这种 class 时，要小心决定哪些 attribute 是 public 的，哪些 attribute 是 subclass 的 API，哪些是真正只有 base class 才会使用的。

遵守以上的思想，这里有一些 pythonic guideline：

+ public attrbute 不应该有前缀下划线
+ 如果你的 public attribute 的名字和保留的关键字冲突了，在属性的最后缀上一个下划线。优先选择这种方法而不是采用缩写或者是错误拼写（但是尽管有这样的规则，对于 class method 作为第一个参数的情况，优先选择用 'cls' 表示 class 类型的变量/参数）

    注意1：对于 class 的 method 的参数命令参考前面的讨论。

+ 对于简单的 public data attribute，最好直接暴露它的名字，而不是再写一个复杂的 accessor/mutator method。如果一个 data attribute 需要增加功能，python 提供了一个方便的途径。这种情况下，使用 property 来隐藏简单的数据访问背后的 功能实现。

    注意1：property 应该只在 new-style 的 class 中实现。

    注意2：虽然有些副作用（比如caching）是可以接受的，但是要尽量尝试让 function 的行为没有副作用

    注意3：property 会让调用者认为访问开销相对较小，所以尽量避免使用 property 来做大开销的计算

+ 如果你的 class 可能会被扩展出 subclass，并且你不希望 subclass 使用一些 attribute，那么考虑用两个下划线前缀、没有下划线后缀的方式给这些 property 命名。这样会触发 python 的命名矫正算法，这个 attribute 的名字前会加上 class 的名字。这样可以避免 subclass 意外使用相同名字时的冲突。

    注意1：只有 class 的名字才会合入到 attribute 名字中，所以如果 subclass 的名字和其 attribute 的名字和父类名字相同，那么还是会有冲突

    注意2：命名矫正在某些情况下很不方便，比如 debug 或者是 `__getattr__()`。但是命名矫正算法的文档很完善，使用起来也很方便。

    注意3：并不是每个人都喜欢命名矫正，尽量避免和潜在的高级调用者产生命名冲突。

### public 和 internal 接口

任何的向后兼容只适用于 public 接口，因此，让用户能清晰地区分出 public 和 内部接口非常重要。

文档化的接口可以认为是 public 接口，除非文档中明确说明该接口是拥有向后兼容豁免权的临时/内部接口。所有没有文档化的接口都应该视为内部接口。

为了更好地支持 introspection，module 应该用 `__all__` 明确声明 public API 的名字。如果没有 public API，那么就把 `__all__` 设置为空 list。

即使合理地设置了 `__all__`，内部接口（package、module、class、function、attribute 或其他名字）还是应该加上单下划线前缀。

如果 namespace（package、module、class）被认为是内部的，那么包含在内的接口也会被认为是内部的。

import 的名字应该永远被认为是实现细节。除非是 module API 的一部分，否则别的 module 不能间接访问这些名字。比如，`os.path` 或者是一个 package 的 `__init__` module。

## 编程建议


+ 代码不能伤害其他 python 的实现（比如 PyPy、Jython、IronPython、Cython、Psyco 等等）

    比如，字符串连接时不要依赖于 CPython 中的高效实现形式 `a += b` 或者是 `a = a + b` 。即使在 Cpython 中这种优化也是很脆弱的（只适用于部分类型），而且如果不使用 `refcouting` 那么就完全不会产生这种优化。库中对性能敏感的部分，应该使用 `''.join()` 的方式。这样可以保证在各种实现中，字符串连接的时间开销是线性的。

+ 和类似 `None` 这样的单例对象的比较，应该永远使用 `is` 或者是 `is not`，永远不要使用等号操作符。

    此外，如果你的目的是 `if x is not None` 那么要小心别写成 `if x`。举例：判断一个默认值是 None 的变量/参数是否被设置成其他值，这个值（比如容器）的类型在 boolean 表达式中可能会是 false！

+ 使用 `is not` 而不是 `not ... is`。虽然两个表达式的功能相同，但是前一种写法的可读性更强：

        #!python
        # Correct:
        if foo is not None:
        
        # Wrong:
        if not foo is None:

+ 当使用丰富的比较实现排序时，最好实现所有的比较符（六个：`__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`），而不是依赖于其他（只在特定比较上验证过的）代码

    为了最小化开销，装饰器 `functools.total_ordering()` 可以提供一个工具来生成缺少的比较操作。

    [PEP207][PEP207] 指出 python 实现了反射机制，所以，解析器可能会把 `y > x` 转换成 `x < y`，把 `y >= x` 转换成 `x <= y`，把 `x == y` 转换成 `x != y`。`sort()` 和 `min()` 可以确保使用 `<` 操作符，`max()` 使用 `>` 操作符。但是，最好实现这六个操作符，这样在其他地方就不会有困惑。

+ 始终使用 `def` 而不是赋值语句来把一个 lambda 表达式绑定到一个标识符上

        #!python
        # Correct:
        def f(x): return 2*x
        
        # Wrong:
        f = lambda x: 2*x

    前一种形式意味着生成的 function 对象是 `f` 而不是通用的 `<lambda>`。这在回溯和 stirng 显示的时候更加有用。赋值语句会消除 lambda 表达式优于显式使用 def 语句的唯一优势。（即 lambda 表达式可以内嵌在一个更大的表达式中）

+ 从 `Exception` 而不是 `BaseException` 中继承 exception，直接从 `BaseException` 中继承得到的 exception 是保留的，捕捉这些异常是大部分情况下一件错误的事情。

    基于需要捕捉 exception 的代码，而不是抛出 exception 的位置代码来设计 exception hierarchies。以编程的角度回答“发生了什么错误?”这个问题，而不是只是说“发生了错误”（内置 exception hierarchies 的例子见 [PEP3151][PEP3151]） 

    应该遵守 class 的命名规则，除非你的 exception 本身就是一个 error，那么就给这个 exception class 名字加上 `Error` 后缀。用于非本地控制或其他形式的非 error exception 不需要特殊的后缀。

+ 适当地使用 exception 链，在 python 3 中，为了不丢失原始的回溯信息，应该使用 `raise X from Y` 来表示明确的替换。

    当故意替换内部 exception 时（在 python 2 中用 `raise X`，在 python 3 中用 `raise X from None`），确保相关的细节被转移到了新的 exception 中（比如把 `KeyError` 转换成 `AttributeError` 时保留属性名，或在新的 exception 中嵌入原始 exception 的文本内容）

+ 在 python 2 中抛出一个 exception 时，使用 `raise ValueError('message')` 而不是以前的形式 `raise ValueError, message`。

    后面这种格式在 python 3 中是非法的。

    使用括号的格式意味着如果 exception 的参数特别长或者包含格式化字符串时不必使用换行符号。

+ 当捕获 exception 时，如果可以尽量加上明确的 exception 名字，而不是写一个光秃秃的 `except:` 块：

        #!python
        # Yes
        try:
            import platform_specific_module
        except ImportError:
            platform_specific_module = None

    一个光秃秃的 `except:` 块会捕捉到 `SystemExit` 和 `KeyboardInterrupt`，导致很难通过 `Control-C` 的方式中断一个程序，而且会掩盖其他问题。如果你想捕获程序的所有异常，使用 `except Exception:`（光秃秃的 `except` 相当于 `except BaseException:`）。

    允许使用使用光秃秃的 except 的两种情况：

    1. exception 处理代码会打印或者记录 log，这样用户至少知道发生了错误

    2. 代码需要做一些清理工作，这种情况下最好使用 `raise.try...finally` 使 exception 可以继续向上传递

+ 当把一个 exception 绑定到一个名字时，优先使用 python2.6 中新加的显式名字绑定：

        #!python
        try:
            process_data()
        except Exception as exc:
            raise DataProcessingFailedError(str(exc))

    这个语法只有 python3 才支持，它可以避免和原来基于逗号的语法之间的歧义。

+ 当捕捉到操作系统的错误时，优先使用 python3.3 中的 explicit exception hierarchy 而不是 `errno` 值。

+ 此外，对于所有的 `try`/`except` 块，`try` 语句中只使用必要的最小化代码，这样可以避免 bug 被掩盖掉：

        #!python
        # Correct:
        try:
            value = collection[key]
        except KeyError:
            return key_not_found(key)
        else:
            return handle_value(value)
        
        # Wrong:
        try:
            # Too broad!
            return handle_value(collection[key])
        except KeyError:
            # Will also catch KeyError raised by handle_value()
            return key_not_found(key)

+ 特定代码的局部资源，使用 `with` 语句来确保这个资源使用完成后被清理干净，下次还能继续使用。也可以用 `try`/`finally` 语句。

+ 除了获取/释放资源，其他时候都应该通过独立的 function 或 method 来调用上下文管理器

        #!python
        # Correct:
        with conn.begin_transaction():
            do_stuff_in_transaction(conn)
        
        # Wrong:
        with conn:
            do_stuff_in_transaction(conn)

    后面这个例子没有提供任何信息来指示 `__enter__` 和 `__exit__` 两个 method 除了在 tansaction 之后关闭连接之外做的其他事情，。在这种情况下，明确指明很重要。

+ 返回语句要保持一致性。要么所有 function 的返回语句都返回一个表达式，要么都不返回。如果有返回语句返回的是表达式，那么不返回值的返回语句应该明确声明 `return None`，并且位于 function 的最后一句
（如果能跑到这一句的话）。

        #!python
        # Correct:
        
        def foo(x):
            if x >= 0:
                return math.sqrt(x)
            else:
                return None
        
        def bar(x):
            if x < 0:
                return None
            return math.sqrt(x)
        
        # Wrong:
        
        def foo(x):
            if x >= 0:
                return math.sqrt(x)
        
        def bar(x):
            if x < 0:
                return
            return math.sqrt(x)

+ 使用 string method 而不是 stirng module。

    string mothod 总是速度更快，而且和 unicode string 共享相同的 API，如果要求兼容 python2.0 以前的版本则可以忽略这条规则。

+ 使用 `''.startswith()` 和 `''.endswith()` 而不是 string 切片来检查前缀/后缀。

    `startwith()` 和 `endswith()` 更加清晰，而且不易出错：

        #!python
        # Correct:
        if foo.startswith('bar'):
        
        # Wrong:
        if foo[:3] == 'bar':

+ 对象类型的比较应该使用 `isinstance()` 而不是直接比较类型：

        #!python
        # Correct:
        if isinstance(obj, int):
        
        # Wrong:
        if type(obj) is type(1):

    如果检查一个对象是否为 string，记得它有可能是个 unicode string！在 python 2 中，`str` 和 `unicode` 有相同的基类 `basestring`，所以你可以这么做：

        #!python
        if isinstance(obj, basestring):

    注意在 python 3 里面，`unicode` 和 `basestring` 都不再存在了（只有 `str`），并且 bytes 对象不再是 string 的一种，它是整数序列。

+ 对于序列（stirngs，list，tupels）来说，空序列的值是 false：

        #!python
        # Correct:
        if not seq:
        if seq:
        
        # Wrong:
        if len(seq):
        if not len(seq):

+ 写 string 时不要依赖结尾的空格，这种空格在视觉上难以区分，而且一些编辑器（比如reindent.py）会删掉他们。

+ 不要使用 `==` 来比较 boolean 值和 `True`/`False`：

        #!python
        # Correct:
        if greeting:
        
        # Wrong:
        if greeting == True:

    更糟糕的情况：

        #!python
        # Wrong:
        if greeting is True:

+ 在 `try...finally` 的最后一个分支中使用流程控制语句 `return`/`break`/`continue`，而且这个语句会跳转到外面，不鼓励这种方式。因为这种语句会隐式地取消所有的正在通过最后一个分支传播的 exception：

        #!python
        # Wrong:
        def foo():
            try:
                1 / 0
            finally:
                return 42

[PEP207]: https://www.python.org/dev/peps/pep-0207
[PEP3151]: https://www.python.org/dev/peps/pep-3151

### 函数注解

随着 [PEP484][PEP484] 的引入，下面的函数注解规则有些变化：

+ 为了前向兼容，python 3 中的函数注解应该优先使用 [PEP484][PEP484] 的语法（在之前的章节中有一些注解的推荐规则）

+ 不再鼓励使用本文以前推荐的实验性注释风格

+ 但是，除了标准库，鼓励使用 [PEP484][PEP484] 中的实验性规则。比如，使用 [PEP484][PEP484] 中的 style 为一个大型第三方库/应用添加注解，检查添加这些注解的容易程度，观察这些注解的出现是否提高了可读性。

+ python 的标准库应该保守地使用这些注解，但是新代码和大型的重构可以使用这种注解。

+ 如果代码想用另外一种方式使用函数注解，推荐在文件顶部添加这样一条注释：

        #!ptyhon
        # type: ignore

    这会告诉 type checker 忽略所有的注解（在 [PEP484][PEP484] 中可以找到更加详细的关于细颗粒度的关闭 type checker 的报错）

+ 和 linter 类似，type checker 是独立可选的工具，python 解释器默认不会报出任何 type checker 的内容，而且不会基于注释改变它们的行为。

+ 用户不想使用 type checker 时可以忽略它们。但是，第三方库的用户可能希望在这些库上运行 type checker，为此，[PEP484][PEP484] 推荐使用 `stub` 文件：相比于 .py 文件，type checker 优先读取 .pyi 文件。stub 文件可以和库一起发布，也可以通过单独的 typeshed repo 发布（通过库的作者许可）

+ 对于需要向后兼容的代码，可以以注释的方式添加类型注解，相关内容见 [PEP484][PEP484]。

[PEP484]: https://www.python.org/dev/peps/pep-0484

### 变量注解

[PEP526][PEP526] 介绍了变量注解，对于变量的注解风格和前面描述的函数注解类似：

+ 对于 module 级别的变量，class 和 instance variables，局部变量，应该在冒号后面加个空格

+ 冒号前面不应该有空格

+ 如果赋值语句有右侧内容，那么等号两边的空格数应该相等

        #!python
        # Correct:
        
        code: int
        
        class Point:
            coords: Tuple[int, int]
            label: str = '<unknown>'
        
        # Wrong:
        
        code:int  # No space after colon
        code : int  # Space before colon
        
        class Test:
            result: int=0  # No spaces around equality sign

+ 虽然 python 3 可以使用 [PEP526][PEP526]，但是对于所有版本的 python，首先以 stub 文件的语法优先选择变量注解。（细节见 [PEP484][PEP484]） 

[PEP526]: https://www.python.org/dev/peps/pep-0526/



## 翻译参考


[PEP8][PEP8]

[Python PEP8 编码规范中文版](https://blog.csdn.net/ratsniper/article/details/78954852)

## 附

Google 推出过开源项目的 coding style 规范，包含了常见编程语言，如 `C++`,  `java`, `Python`, `Shell` 等。因为已经有国内程序员凭热情创建和维护的中文版本，所以就不再翻译了。

[Google Style Guide][google_en]

[Google 开源项目风格指南 (中文版)][google_zh]

[google_en]: https://github.com/google/styleguide
[google_zh]: https://zh-google-styleguide.readthedocs.io/en/latest/
