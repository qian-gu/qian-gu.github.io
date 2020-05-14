Title: PEP 翻译计划系列 —— PEP274
Date: 2020-05-10 23:51
Category: Python
Tags: PEP, python
Slug: peps_translate_project_pep274
Author: Qian Gu
Series: PEP translate project
Summary: PEPs 翻译系列 PEP274

[PEP 274 -- Dict Comprehensions 原文链接][PEP274]。

[PEP274]: https://www.python.org/dev/peps/pep-00274/

| item | detail |
| ---- | ------ |
| PEP  |  274   |
| Title | Dict Comprehensions |
| Author | Barry Warsaw <barry at python.org> |
| Status | Final |
| Type | Standards Track |
| Created | 25-Oct-2001 |
| Python-Version | 2.7, 3.0 (originally 2.3) |
| Post-History | 29-Oct-2001 |

## Abstract

PEP202 介绍一种叫做 list comprehensions 的语法扩展，本文提出了一种类似的扩展叫做 
`dictionary comprehension`，简称为 `dict comprehension`，用法也和 list comprehension
类似，只是结果是一个 dictionary 对象而不是 list 对象。

<br>

## Resolution

本文本来是为 Python2.3 所写，但是后来因为 `dict()` 的构造函数部分已经包含了相关内容，所以
最后就撤销了。

然而，Python2.7 和 3.0 引入了这个 feature，同时还有 `set comprehensions`。在 
2012-04-19，本文的状态更新为 Accepted，同时更新了 Python-Version 字段。因为现在的版本已
经解决了所有问题，所以 Open Questions 章节被删除了。

<br>

## Proposed Solution

dict comprehensions 和 list comprehensions 非常相似，不同之处是用 `{}` 而不是 `[]`。
同时，关键字 `for` 前面的部分表达式改成了用逗号隔开的 key-value 对，这种表示方法是为了提醒
你 list comprehensions 也适用于 dictionaries。

<br>

## Rationale

有时候你有些按照元素对的形式排列的数据，而且你想把他们变成一个 dict。在 Python2.2 中，
`dict()` 构造函数可以接受 `(key, value)` 形式的参数 sequence 来构造出一个 dict。但是有
时候这么做很不方便或者性能不高。对于一些常用操作，把一个 list 转换成一个 set 时，可以
用一种更好的语法来使得代码清晰。

就像 list comprehensions，可以用一个 for 循环来实现，dict comprehensions 可以提供比传
统 for 循环更加简洁的语法。

<br>

## Semantics

dict comprehensions 的语法实际上可以用 python2.2 来证明，把一个 list comprehensions 
传参给一个 dict 的构造函数，

```
#!python
>>> dict([(i, chr(65+i)) for i in range(4)])
```

在语法上它和下面是等价的，

```
#!python
>>> {i: chr(65+i) for i in range(4)}
```

但是用 dict 构造函数的方式有两个缺点。第一，它没有 dict comprehensions 方式清晰；第二，
它要求程序员先构造一个 list，代价可能比较大。

<br>

##  Examples

```
#!python
>>> print {i : chr(65+i) for i in range(4)}
{0 : 'A', 1 : 'B', 2 : 'C', 3 : 'D'}
```

```
#!python
>>> print {k : v for k, v in someDict.iteritems()} == someDict.copy()
1
```

```
#!python
>>> print {x.lower() : 1 for x in list_of_email_addrs}
{'barry@zope.com'   : 1, 'barry@python.org' : 1, 'guido@python.org' : 1}
```

```
#!python
>>> def invert(d):
...     return {v : k for k, v in d.iteritems()}
...
>>> d = {0 : 'A', 1 : 'B', 2 : 'C', 3 : 'D'}
>>> print invert(d)
{'A' : 0, 'B' : 1, 'C' : 2, 'D' : 3}
```

```
#!python
>>> {(k, v): k+v for k in range(4) for v in range(4)}
... {(3, 3): 6, (3, 2): 5, (3, 1): 4, (0, 1): 1, (2, 1): 3,
   (0, 2): 2, (3, 0): 3, (0, 3): 3, (1, 1): 2, (1, 0): 1,
   (0, 0): 0, (1, 2): 3, (2, 0): 2, (1, 3): 4, (2, 2): 4, (
   2, 3): 5}
```

<br>

## Implementation

所有实现细节都在 Python2.7 和 3.0 中解决了。