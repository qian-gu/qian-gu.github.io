Title: Python 学习笔记 #3 —— Docstring 风格
Date: 2020-04-26 19:20
Category: CS
Tags: PEP, python
Slug: python-notes-3-docstring-style
Author: Qian Gu
Series: Python Notes
Summary: 翻译 PEP257 -- Docstring Conventions

[PEP 257 -- Docstring Conventions 原文链接][PEP257]

[PEP257]: https://www.python.org/dev/peps/pep-0257/

| item | detail |
| ---- | ------ |
| PEP  |  257   | 
| Title | Docstring Conventions |
| Author | David Goodger <goodger at python.org>, Guido van Rossum <guido at python.org> |
| Status | Active |
| Type | Informational |
| Created | 29-May-2001 |
| Post-History | 13-Jun-2001 |

----

## 摘要

本文描述了 Python docstrings 的语法和惯例。

## 基本原理

本文的目的是在 high-level 的层次对 docstrings 结构进行标准化：应该包含哪些内容，以及如何表述（docstrings 内部不需要任何的标记性语法）。本文的内容是惯例，而不是严格的语法或法律。

> "A universal convention supplies all of maintainability, clarity, consistency, and a foundation for good programming habits too. What it doesn't do is insist that you follow it against your will. That's Python!"
>
>    —Tim Peters on comp.lang.python, 2001-06-16

如果你违法了这些惯例，最差的结果也只不过是你的作品看起来比较丑陋。但是一些软件（比如 [Docutils][docutils] 系统）会感知到 docstrings，所以遵守这些惯例可以让你获得最好的结果。

[docutils]: docutils.sourceforge.net

## 标准

### Docstrings 是什么

docstrings 是一个字符串，是 `module`, `function`, `class`, `method` 中的第一个语句，这些字符会变成该 object 的特殊属性 `--doc--`。

所有的 module 都应该有 docstrings，module 中所有可以导出的 function 和 class 也都应该有 docstrings。class 的 public method（包括 `--init--` 构造器）也应该有 docstrings。一个 package 可以在自己目录下面 `--init--.py` 文件的 docstrings 中进行描述。

Python 文件中其他位置的字符串也可以成为文档的一部分，它们无法被 Python 的字节码编译器识别，runtime 的时候也无法访问（也就是说，没有赋值给 `--doc--` 属性），但是有两种类型的 docstrings 可以被软件工具识别出来：

1. 在 module, class, `--init--` 方法的顶层，简单赋值语句后面的字符串，叫做 “attribute docstrings”
2. 在 docstrings 之后紧跟着出现的字符串，叫做 “additional docstrings”

关于这两种 docstrings 的详细描述请参考 [PEP258 "Docutils Design Specification"][PEP258]。

为了保持一致性，永远使用三个双引号 `"""triple double quotes"""` 包围 docstrings。如果在 docstrings 中使用到了反斜线，请使用 `r"""raw triple double quotes"""`，对于使用 Unicode 字符的情况，请使用 `u"""Unicode triple quoted string"""`。

docstrings 有两种形式：单行、多行。

[PEP258]: https://www.python.org/dev/peps/pep-0258/

### 单行 Docstrings

单行 docstrings 显而易见，就是只有一行。举例，

```
#!python
def kos-root():
    """Return the pathname of the KOS root directory."""
    global -kos-root
    if -kos-root: return -kos-root
    ...
```

注意：

+ 即使是单行的情况，仍然使用三双引号，方便以后扩展成多行的情况
+ 开头和结尾的引号在同一行，这样看起来要美观一些
+ docstrings 前后没有空行
+ docstrings 用一个以句号结尾的短语，它用命令性的方式规定了 function/method 的效果（比如“Do this”，“Return that”），而不是描述性的方式（比如，不要写成这样 "Returns the pathname..."）
+ 单行的 docstrings 不应该是 function/method 的参数的重新声明（可以通过内省实现），不要写成这样

        #!python
        def function(a, b):
        """function(a, b) -> list"""

    这种类型的 docstrings 只适合于 C 函数（比如内建函数），因为 C 没有内省机制。然而内省无法决定返回值的类型，所以要在 docstrings 中进行说明。所以 docstrings 应该优先选择下面的方式，

        #!python
        def function(a, b):
        """Do X and return a list."""

### 多行 Docstrings

多行 docstrings 的结构分为 2 段，第一段是一个类似于单行 docstrings 的总结行，第二段是更详细的描述，两段之间用一个空行隔开。总结行可能会被自动化索引工具使用到，所以让它的长度保持在一行内，并且用空行和其他部分隔开非常重要。总结行可以放在开头引号的同一行，也可以放到下一行。整个 docstrings 和引号的缩进保持一致（见下面的例子）。

class 的 docstrings 的后面要插入一（多）个空行。一般来说 class 的 methods 之间会通过一个空行进行隔离，docstrings 也需要一个空行来和第一个 method 进行隔离。

一个脚本（作为一个单独的程序）的 docstrings 应该可以当作 Usage message 来使用，当使用不正确的参数（或者是表示 help 的 -h 参数）调用脚本时打印出这些内容。这种 docstrings 应该包含脚本的功能、命令行语法、环境变量、文件等信息。Usage message 可以非常详细（内容长达几个全屏），达到可以指导一个新用户正确使用本脚本命令，这个信息也可以作为高级用户查询所有选项和参数的快速参考。

一个 module 的 docstrings 应该列出所有可以被导出的 class，exception 和 function 以及其他 objects，每个对象都有一个单行的总结性描述（这些总结比 docstrings 的总结行更简洁）。

一个 package 的 docstrings（比如，`--init--.py` 的 docstrings）也应该列出可以导出的 module 和 subpackage。

一个 function/method 的 docstrings 应该总结它的行为，描述它的参数，返回值，副作用，抛出的 exception，调用时的约束。同时应该指出可选参数，无论 keyword 参数是不是接口的一部分，都应该进行描述。

一个 class 的 docstrings 应该总结它的行为，列出 public method 和 instance varibale。如果它本身的设计目的是子类化，并且针对 subclass 留有额外的接口，那么这个额外接口应该在 docstrings 中单独列出来。构造器应该在 `--init--` 方法的 docstrings 中描述，其他的 method 都在自己的 docstrings 中进行描述。

如果一个 subclass 的大部分行为都继承自另外一个 class，那么它的 docstrings 应该提到这一点并且总结两者的不同之处。用动词 `override` 来说明 subclass 的方法重写了 superclass 的同名方法；用动词 `extend` 来表示 subclass 的方法调用了 superclass 的同名方法，并且添加了自己额外的功能。

在 docstrings 中涉及到 function/method 的参数时不要用 Emacs 的大写惯例。Python 对大小写敏感而且参数的名字可以用作是 keyword 参数，所以 docstrings 应该使用正确的参数名字。最好按照每行一个参数的形式列出来。举例，

```
#!python
def complex(real=0.0, imag=0.0):
    """Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """
    if imag == 0.0 and real == 0.0:
        return complex-zero
    ...
```

除非是所有内容都可以在一行内完全放下，否则把结尾的引号单独放在一行，这样 Emacs 的 `fill-paragraph` 命令就可以使用了。

### 处理 Docstrings 的缩进

docstrings 工具可以对 docstrings 的第二行及以后的行进行整体的缩进删除，删除的长度是后面这些行中的最小缩进，也就是说后面这些行的缩进最小化。第一行 docstrings 的任何缩进都是没有用的，会被删除。后续行的缩进也会被保留下来。应该删掉 docstrings 开头和结尾的空行。

因为代码比描述更准确，这里贴出来这个规则（算法）的实现，

```
#!python
def trim(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)
```

下面这个例子中的 docstrings 包含两个换行符号，所以一共有 3 行，第一行和最后一行是空行，

```
#!python
def foo():
    """
    This is the second line of the docstring.
    """
```

在命令行中运行一下看看，

```
#!text
>>> print repr(foo.--doc--)
'\n    This is the second line of the docstring.\n    '
>>> foo.--doc--.splitlines()
['', '    This is the second line of the docstring.', '    ']
>>> trim(foo.--doc--)
'This is the second line of the docstring.'
```

一旦经过 trim 处理， 下面这两种 docstring 是等效的，

```
#!python
def foo():
    """A multi-line
    docstring.
    """

def bar():
    """
    A multi-line
    docstring.
    """
```

## 参考

参考阅读

[PEP 256 -- Docstring Processing System Framework](https://www.python.org/dev/peps/pep-0256/)

[PEP 258 -- Docutils Design Specification](https://www.python.org/dev/peps/pep-0258/)

## 附：实践

使用 [flake8-docstrings][flake8-docstrings] 工具来帮助自己检查 docstrings 是否符合规范。

[flake8-docstrings]: https://github.com/PyCQA/flake8-docstrings

