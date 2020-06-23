Title: Python 学习笔记 #2 —— PEP8 实践
Date: 2020-04-19 14:56
Category: CS
Tags: PEP8, python, Sublime Text
Slug: python_notes_2_pep8_in_practice
Author: Qian Gu
Series: Python Notes
Summary: 总结实际 coding 中遵循 PEP8 时用到的工具和插件

## PEP8 & PCQA

[PEP8][PEP8] 之前已经介绍过了，这里有[中文翻译（前一篇博客）][pep8_zh]。

[PCQA][PCQA] 是 Python Code Quality Authority 的缩写，它是一个松散的组织，聚集了各地的开发者，大家以在线协作的方式，为广大 python 码农提供各种 automatic style and quality reporting 工具，方便大家做项目时可以在不同项目都能保持代码风格一致。

PCQA 源自于 `Ian Cordasco` 在把 `Flake8` 迁移到 Git 时发出的一封邮件，大家积极提议把项目迁移到 `GitLab` 上，所以他在 `GitLab` 和 `GitHub` 上都建了一个 group 来专门维护 `Flake8` 和 `flake8-docstrings`。后来其他人开发维护的各种 lint 工具也源源不断地加入，PCQA 逐渐壮大。

在 [PCQA 的 GitHub 主页][pcqa-github] 上可以看到很多工具，很多常见的 linter 和 formatter 工具大部分来自于 PCQA，下文会经常看到 PCQA 的身影。

[PEP8]: https://www.python.org/dev/peps/pep-0008/
[pep8_zh]: http://guqian110.github.io/posts/python/python_notes_1_pep8.html
[PCQA]: https://meta.pycqa.org/en/latest/code-of-conduct.html
[pcqa-github]: https://github.com/PyCQA



## Linter

### pycodestyle

PCQA 荣誉出品，[pycodestyle][pycodestyle] 原名叫 `pep8`，后应 python 之父的[要求][rename]，后来改名为 `pycodestyle`。

> This package used to be called pep8 but was renamed to pycodestyle to reduce confusion. Further discussion can be found in the issue where Guido requested this change, or in the lightning talk at PyCon 2016 by @IanLee1521: slides video.

安装和使用方法直接看 [pycodestyle Github 主页][pycodestyle]，或者在命令行中查询。

    #!bash
    pycodestyle -h

关于配置，pycodestyle 的 [文档][pycodestyle_doc] 里面有详细介绍，如果想自定义忽略某些检查项，则根据文档查阅这些检查项对应错误代码，在配置文件中添加忽略选项即可。

**pycodestyle 是一个非常基础、应用非常广泛的工具，很多 lint 工具底层都依赖于它！**

[pycodestyle]: https://github.com/PyCQA/pycodestyle
[rename]: https://github.com/PyCQA/pycodestyle/issues/466
[pycodestyle_doc]: https://pep8.readthedocs.io/en/latest/index.html

### pyflakes

PCQA 荣誉出品，[pyflakes Github 主页][pyflakes] 介绍到 pyflakes 的设计原则非常简单：

> it will never complain about style, and it will try very, very hard to never emit false positives.

它通过解析每个源文件的 syntax tree，而不是通过 import 的方式来检查代码，所以很安全没有副作用，速度也会比 [pylint][pylint] 和 [Pychecker][pychecker] 快很多。但是付出的代价就是它能检查的类型有限。

pyflakes 的使用方法也非常简单，没有命令行参数，像下面这样直接调用即可，

    #!bash
    pyflakes my_file.py

所以 pyflakes 只是检查语法错误，而不检查 code style，如果想要语法检查 + style 检查，那么可以使用下面介绍的 [flake8][flake8]。

[pyflakes]: https://github.com/PyCQA/pyflakes
[pylint]: https://www.pylint.org/
[pychecker]: http://pychecker.sourceforge.net/
[flake8]: https://gitlab.com/pycqa/flake8

### flake8

PCQA 荣誉出品，[flake8][flake8] 实际上是一个集成工具，它集成了

+ PyFlakes
+ pycodestyle
+ Ned Batchelder's McCabe script

通过一个单条的 `flake8` 命令可以启动这三个命令进行检查。

    #!bash
    flake8 my_file.py

详细用法可以通过 help 选项查看或者阅读 [flake8 的文档][flake8-doc]。

flake8 流行的一个重要原因是它提供扩展功能，官方已经为 flake8 开发了很多插件。比如 [flake8-docstirngs][flake8-docstrings] 基于 PEP257 检查文档的 docstrings。

每个插件的安装方法直接参考该插件的文档即可，安装完之后就可以像前面一样直接使用了。下面几个是常用插件：

+ [pep8-naming][pep8-naming]
+ [flake8-bugbear][flake8-bugbear]
+ [flake8-import-order][flake8-import-order]
+ [flake8-commas][flake8-commas]
+ [flake8-docstrings][flake8-docstrings]

[flake8-doc]: http://flake8.pycqa.org/en/latest/index.html
[flake8-docstrings]: https://github.com/PyCQA/flake8-docstrings
[pep8-naming]: https://github.com/PyCQA/pep8-naming
[flake8-bugbear]: https://github.com/PyCQA/flake8-bugbear
[flake8-import-order]: https://github.com/PyCQA/flake8-import-order
[flake8-commas]: https://github.com/PyCQA/flake8-commas
[flake8-docstrings]: https://github.com/PyCQA/flake8-docstrings

### pylint

PCQA 荣誉出品，提到 [pylint][pylint]，必须先引用官网的一句话，

> It's not just a linter that annoys you!

pylint 会检查代码语法错误，coding style（默认的检查标准和 PEP8 非常相似），它还能建议代码应该如何重构，它还会根据检查结果对你的代码打分 XD。

不过 pylint 的检查非常严格，而且运行速度也要慢一些，所以很多人更喜欢用 flake8 等其他工具。

[pylint]: https://github.com/PyCQA/pylint

--------

*上面的工具的使用流程都是一样的：*

1. *写代码*
2. *命令行调用工具检查*
3. *根据检查结果逐个修改代码*
4. *迭代 1~3 直到没有 error 和 warning*

*如果经常改动代码，这个过程会重复很多次，依然会很繁琐，所以下面介绍的几个工具可以提供自动化处理，减轻工作量。*

-------

## Formatter

### autopep8

来自于一个日本程序猿之手，[autopep8][autopep8] 依赖于 pycodestyle，安装和使用说明直接看 Github 主页即可。通过命令行使用起来稍微有点繁琐，后面小节中有介绍使用 sublime 插件实现一键调用。

[autopep8]: https://github.com/hhatto/autopep8

### yapf

首先必须说明 [yapf][yapf] 并不是 Google 的官方产品，仅仅是恰好代码所属权是 Google。

下面内容是一段官方文档的翻译：

目前大部分的 python formatter 工具的机制是根据 lint 结果把 error 信息逐个修掉。这么做有很明显的局限性，比如某些代码虽然遵循了 PEP8，但是并不代表它的 coding style 是良好的。

yapf 才用了另外一种思路，它基于 [clang-format][clang-format] 工具，使用算法提取代码，尽最大努力将其 format 成最佳 style，即使有时候代码并没有违背规范。它终结了 formatting 的圣战：如果项目中有代码改动，将整个 codebase 用 yapf 过一遍，那么所有代码的风格就会保持一致，在 code review 的时候就不再有无意义的争吵。

yapf 的终极目标是产生的代码和（遵循规范的）程序猿写出的代码一样，它可以替你完成维护代码中的一些繁琐的事情。

安装和使用方法见官方主页。

[yapf]: https://github.com/google/yapf
[clang-format]: https://clang.llvm.org/docs/ClangFormat.html

### black

查看资料说 [black][black] 和 yapf 类似，但是限制条件比较多，没有太多的自定义选项，所以优点是省心。因为基于 python3，目前我还在使用 python 2.7，所以暂时记录一下，以后切换成 python 3 了再补坑。

[black]: https://github.com/psf/black



## Practice in Sublime

sublime 有很多 linter 和 formater 插件，下面总结一下。

### SublimeLinter

[SublimeLinter][SublimeLinter] 是一个 sublime 的插件，可以提供一个框架，配合扩展插件完成各种语法和规则的 lint 检查。

SublimeLinter 官方出品的扩展插件命名为 `SublimeLinter-xxx` 的格式，第三方的插件则命名为 `SublimeLinter-contrib-xxx` 的格式，比如

+ 集成 `iverilog` 的插件 [Sublime​Linter-contrib-iverilog][Sublime​Linter-contrib-iverilog]
+ 集成 `verilator` 的插件 [Sublime​Linter-contrib-verilator][Sublime​Linter-contrib-verilator]
+ 集成 `modelsim` 的插件 [Sublime​Linter-contrib-modelsim][Sublime​Linter-contrib-modelsim]

下面介绍的插件都是官方出品的插件。

[SublimeLinter]: https://github.com/SublimeLinter/SublimeLinter
[Sublime​Linter-contrib-iverilog]: https://packagecontrol.io/packages/SublimeLinter-contrib-iverilog
[Sublime​Linter-contrib-verilator]: https://packagecontrol.io/packages/SublimeLinter-contrib-verilator
[Sublime​Linter-contrib-modelsim]: https://packagecontrol.io/packages/SublimeLinter-contrib-modelsim

### Sublime​Linter-pep​8 / Sublime​Linter-pycodestyle

如前文所述，因为 `pep8` 已经改名叫 `pycodestyle`，所以 sublimlinter 也弃用了 [Sublime​Linter-pep​8][Sublime​Linter-pep​8]，而是使用 [Sublime​Linter-pycodestyle][Sublime​Linter-pycodestyle] 为 sublimelinter 提供与 [pycodestyle][pycodestyle] 的集成接口。

安装完之后就可以看到效果了，根据提示修改代码即可。

[Sublime​Linter-pep​8]: https://packagecontrol.io/packages/SublimeLinter-pep8
[Sublime​Linter-pycodestyle]: https://packagecontrol.io/packages/SublimeLinter-pycodestyle

### Sublime​Linter-pyflakes

[Sublime​Linter-pyflakes][Sublime​Linter-pyflakes] 为 sublimelinter 提供与 [pyflakes][pyflakes] 的集成接口，安装完之后也可以看到效果。

[Sublime​Linter-pyflakes]: https://packagecontrol.io/packages/SublimeLinter-pyflakes

### SublimeLinter-flake8

[Sublime​Linter-flake8][Sublime​Linter-flake8] 为 sublimelinter 提供与 [flake8][flake8] 的集成接口，安装完之后也可以看到效果。

因为 flake8 已经在底层集成了 pycodestyle 和 pyflake，所以只安装 SublimeLinter-flake8 即可，没有必要安装把这三个插件都安装了，这样会有很多重复提示。

[Sublime​Linter-flake8]: https://packagecontrol.io/packages/SublimeLinter-flake8

### AutoPEP8

[AutoPEP8][AutoPEP8_plugin] 为 sublime 提供与 [autopep8][autopep8] 的集成接口，可以一键调用 autopep8 检查代码是否符合 PEP8 规范，使用起来特别方便，目前安装量有 117K。

**注意：AutoPEP8 不是完整的 linter，严格说应该属于 formatter，只能实现 PEP8 规范中的部分功能。**

安装完成后可以通过快捷键 `ctrl + 8` 或者是 `shift + ctrl + 8` 直接使用。

+ `ctrl + 8`：会生成一个 patch 文件，可以预览改动
+ `shift + ctrl + 8`：直接修改目标文件

[AutoPEP8_plugin]: https://packagecontrol.io/packages/AutoPEP8

### Py​Yapf Python Formatter

[PyYapf][PyYapf] 为 sublime 提供与 yapf 集成的接口，安装之后可以通过快捷键或者是 `ctrl + shift + p` 在 sublime 内调用 yapf。

[PyYapf]: https://packagecontrol.io/packages/PyYapf%20Python%20Formatter



## Summary

综上，python 有众多 linter 和 formatter 工具，很多工具之间的功能大部分都是重复的，选择一个用着顺手的即可。因为我使用 sublime text 作为主力编辑器，所以 PEP8 实践的最佳方案是：

| item | solution |
| ---- | -------- |
| editor | sublime |
| linter | sublimelinter-flake8 |
| formatter | PyYapf |
