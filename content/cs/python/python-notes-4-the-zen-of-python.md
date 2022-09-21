Title: Python 学习笔记 #4 —— Python 之禅
Date: 2020-05-10 14:36
Category: CS
Tags: PEP, python
Slug: python-notes-4-the-zen-of-python
Author: Qian Gu
Series: Python Notes
Summary: 学习 Python 之禅

著名的 python 之禅，[PEP 20 -- The Zen of Python 原文链接][PEP20]。

[PEP20]: https://www.python.org/dev/peps/pep-0020/

| item | detail |
| ---- | ------ |
| PEP  |  20    |
| Title | The Zen of Python |
| Author | tim.peters at gmail.com (Tim Peters) |
| Status | Active |
| Type | Informational |
| Created | 19-Aug-2004 |
| Post-History | 22-Aug-2004 |

## Abstract

很久之前，Python 先驱 Tim Peters 将 BDFL（Benevolent director for life，仁慈的终身独裁者，特指 Python 之父 Guido van Rossum）的 Python 设计指导原则总结成 20 条格言，只记录下了其中的 19 条。

## The Zen of Python

网上有很多不同版本的翻译，有些语言风趣幽默，有些正经严肃。我个人更喜欢严肃的翻译，因为幽默的翻译有时候需要特定的语境和背景只是才能理解，反而增加了理解难度。下面的翻译一些是我按照自己的理解写的，有些是网上别人的翻译（因为出处已经无法找到了，所以只能感谢原作者的分享了）。文学水平太低做不到 `达雅`，只能争取做到 `信`，尽量不要误导大家。

1. **Beautiful is better than ugly.**

    优美胜于丑陋

    PEP8 中提到，Python 的理念是代码更多时候是用来读的，所以以编写 `优美` 的代码为目标，`if a == 0 and b == 1 or c == True:` 要比 `if a == 0 && b == 1 || c == True:` 更加优美。优美的代码包含的内容非常广泛，PEP8 提供了一些如何写出优美代码的建议。

2. **Explicit is better than implicit.**

    显式胜于隐式

    代码应该清晰易懂，比如良好的命名可以提高代码的可读性。几个不好的例子，

    + 太宽泛： `my-list`
    + 太冗长： `list-of-machine-learning-data-set`
    + 太模糊： `I`, `o`, `O`, `a`, `b`, `c`

    关于命名可以参考 PEP8.

3. **Simple is better than complex.**

    简单胜于复杂

    选择最简单实现方案，python 有很多功能强大的内置 method，合理利用它们可以减少你的代码量，删繁就简只保留核心代码。一个直观例子是用 `enumerate()` 来迭代容器，另外一个例子是用 `zip()` 快速创建字典。减少代码量不仅仅可以提高可读性，还意味着出错的概率更低，而且代码的性能更好（因为通常库实现更加高效）。

4. **Complex is better than complicated.**

    复杂胜于凌乱

    如果复杂不可避免，也要避免晦涩的实现。复杂和晦涩的区别，我理解就是复杂是可以通过分解来理解，但是晦涩特指那种非常难理解的语法、不符合常规思维的实现方式。

5. **Flat is better than nested.**

    扁平胜于嵌套

    代码尽量少嵌套，降低理解难度。

6. **Sparse is better than dense.**

    间隔胜于紧凑

    适当的间隔和空行能提高可读性，同参考 PEP8.

7. **Readability counts.**

    可读性很重要

    同参考 PEP8，两个例子：

    + 使用下划线对很长的数字分组，`money = 1-000-000`
    + f-string 可以大幅提高代码的可读性， `print(f"I have {money} dollars.")`

8. **Special cases aren't special enough to break the rules.**

    规则至高无上，没有什么特例可以打破规则


9. **Although practicality beats purity.**

    但是实用性胜过代码的纯粹性

    与前一句相矛盾，提醒我们掌握它们之间的平衡。

10. **Errors should never pass silently.**

    不要默许任何错误

    默许的错误会导致隐患，使用异常处理以尽量写出健壮的代码。

11. **Unless explicitly silenced.**

    除非你确定要这么做

    在某些情况下，小错误是可以容忍的，和前一条组合在一起，避免走极端。

12. **In the face of ambiguity, refuse the temptation to guess.**

    面对歧义，拒绝猜测的诱惑

    避免写含糊不清的代码。

13. **There should be one-- and preferably only one --obvious way to do it.**

    应该有且只有一个最优解决方案 —— 最显而易见的实现方案

    python 的语法非常灵活，库也非常强大，所以同一个问题可以有非常多种不同实现方式，那么最优方案应该是那个最直观的解决方案。不要走标新立异的路线，用最显而易见的方法，花费最少的时间解决问题，珍惜自己的生命，也珍惜读者（代码维护者）的生命。

    > life is short, you need pyhton.

14. **Although that way may not be obvious at first unless you're Dutch.**

    虽然一开始并不容易，除非你是 Pyhton 之父

15. **Now is better than never.**

    现在开始做胜过永远拖延

    拒绝拖延症！

16. **Although never is often better than *right* now.**

    但是不假思索地的行动还不如拖延

    行动前要仔细思考，制定计划。

17. **If the implementation is hard to explain, it's a bad idea.**

    如果实现方案很难向别人解释，那么它就是个坏方案

    小黄鸭调试法。

18. **If the implementation is easy to explain, it may be a good idea.**

    反之亦然，良好的实现方案应该清晰容易理解

    好方案的一个共同特点就是清晰易懂，因为它们抓住了问题的关键点，从而可以用简单的方法高效地解决问题 —— `奥卡姆剃刀`。

19. **Namespaces are one honking great idea -- let's do more of those!**

    命名空间是一个绝妙的理念，我们要多加利用

    给变量起名字是一门艺术，尤其是大工程多人协同工作时，难免会有命名冲突，因为好名字是大家有共识的，使用命名空间可以让你不再有命名冲突的烦恼。

## Easter Egg

在解释器中用下面的命令就可以看到原文。

```
#!python
import this
```

## Ref

[Python之禅](https://liuwynn.github.io/2019/04/24/Python%E4%B9%8B%E7%A6%85/)

[《Python之禅》的翻译和解释](https://blog.csdn.net/lanphaday/article/details/2151918)

[怎样让你写的 Python 代码更优雅？](https://www.infoq.cn/article/e5FEa0D6JFADgKkHVyuE)
