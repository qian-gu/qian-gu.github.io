Title: Python 学习笔记 #6 —— Iterator 迭代器
Date: 2020-05-24 22:47
Category: CS
Tags: PEP, python
Slug: python-notes-6-iterator
Author: Qian Gu
Series: Python Notes
Summary: Iterator 学习笔记

## What is Iterator

[PEP 234 -- Iterators 原文链接][PEP234]。

[PEP234]: https://www.python.org/dev/peps/pep-0234/

Sequence 是 python 中的一种数据结构，它们的成员是有序排列的，可以通过下标来访问特定元素，比如字符串、list、tuple 等都是 sequence。很多时候我们需要对 sequence 进行顺序访问，最简单的方法是写一个 for 循环，通过计数的方式实现迭代。但是计数的方式很原始也不高效，所以 python 提供了 iterator 来迭代 sequence。Iterator 在 Python 中使用非常广泛，它不仅对 sequence 的支持是无缝的，它还能迭代那些具有 sequence 的行为但实际上并不是 sequence 的对象，比如 dict 的 keys 以及 file。

Iterator 实际上是一个实现了工厂模式的对象，它通过 `next()` 方法来获取元素，而不是通过 index 计数来实现。for 循环只要调用 iterator 的 next 方法，就能获得 sequence 中的下一项，当迭代完所有的 item 后，再次调用会返回一个 `StopIteration` 的异常，这个异常并不代表发生了错误，而是告诉调用者，迭代已经完成了。

## Iteratable vs Iterator

**含有 `--iter--()` 或 `--getitem--()` 方法的对象称为“可迭代对象”：`Iteratable`**

可以用 `isinstance()` 判断一个对象是否为 `Iteratable` 对象，

```
#!python
from collections import Iterable

isinstance([], Iterable)  # True
isinstance({}, Iterable)  # True
isinstance('abc', Iterable) # True
isinstance(100, Iterable)  # False
isinstance(x for x in range(10), Iterable)  # True
```

**实现了 `next()` 方法的对象称为迭代器：`Iterator`**

可以用 `isinstance()` 判断一个对象是否为 `Iterator` 对象，

```
#!python
from collections import Iterator

isinstance([], Iterator)  # False
isinstance({}, Iterator)  # False
isinstance('abc', Iterator)  # False
isinstance(100, Iterator)  # False
isinstance(x for x in range(10), Iterator)  # True
```

**`lsit`, `dict`, `str` 等都是 `Iterable`，但不是 `Iterator`，可以用 `iter()` 得到其对应的 `Iterator`**

实际上，python 的 for 循环作用于 Iterable 时，会自动调用 `iter()` 来得到对应的 Iterator，然后不断调用 next 获取其中的元素，

```
#!python
for i in seq:
    do-something-to(i)
```

Python 在底层实现时，会自动替换成下面的方式，

```
#!python
fetch = iter(seq)
while True:
    try:
        i = fetch.next()
    except StopIteration:
        break
    do-something-to(i)
```

结论：**对于 `Iterable` 对象，我们可以直接用 for 循环来迭代。**

## Why Iterator

翻译自 PEP234：

+ 提供了一种可扩展的 iterator 接口
+ 加强了 list 的迭代性能
+ dict 的迭代性能巨大提升
+ 迭代功能的底层实现是真正的迭代，而不是用随机访问来模拟
+ 兼容目前已有的所有用户自定义的 class、模拟 sequence 和 dict 的扩展对象、甚至那些只实现了 `{--getitee--, keys, valus, itmes}` 的 mappings
+ 迭代那些非 sequence 对象的代码可以更加简洁，可读性更高

## Construct Iterator

如何得到一个迭代器呢？

### BIT

对于 Python 内建数据类型，比如容器，只需要用内建函数 `iter()` 就可以得到对应的迭代器，具体有两种调用方式：

```
#!python
iter(obj)
iter(func, sentinel)
```

+ `iter(obj)`，返回一个迭代器
+ `iter(func, sentinel)`，iter 会重复调用 func，直到迭代返回值为 sentinel 时停止迭代

### Delegate

如果是一个自定义容器，内部包含一个 list、tuple、dict 等可迭代对象，那么可以直接在自定义容器中定义一个 `--iter()--` 方法，将迭代请求委托到容器内容对象上。

```
#!python
class Node(object):
    def --init--(self, value):
        self.-value = value
        self.-children = []

    def --iter--(self):
        return iter(self.-children)
```

### Implement Iterator Protocal

有时候内建类型的迭代协议无法满足我们的需求，这个时候可以自行实现迭代协议。只要一个 class 实现了下面两个方法，就可以当作迭代器来使用，

+ 一个 `--iter()--` 方法，返回值是 `self`
+ 一个 `next()` 方法，返回一个 item 或者是 StopIteration 异常

这两个方法分别对应了前面区分过的两种协议，

+ 任意一个实现了 `--iter()--` 或 `--getitme--()` 的对象，都可以用 for 循环来迭代 —— **Iterable 对象**
+ 任意一个实现了 `next()` 的对象都可以当作是 iterator —— **Iterator 协议**

迭代的概念本身只涉及第二种协议，容器类的对象一般都支持第一种协议。目前 iterator 要求这两种协议都支持，支持第一种协议的目的是为了让 iterator 同时也是 Iterable，这样它的行为和 sequence 类似，特别是在用 for 循环中使用 iterator 的场景。

**example：**

定义一个产生随机 sequence 的 class，然后使用 for 循环迭代该对象，

```
#!python
#! /usr/bin/env python

from random import choice

class RandSeq(object):
    def --init-- (self, seq):
        self.data = seq

    def --iter-- (self):
        return self

    def next(self):
        return choice(self.data)

seq = RandSeq(('rock', 'paper', 'scissors'))

for item in seq:
    print item
```

也可以像前面介绍的一样，用 `isinstance()` 来检查，说明我们的 RandSeq 类既是一个 Iterable 也是一个 Iterator。

```
#!python
isinstance(seq, Iterable)  # True
isinstance(seq, Iterator)  # True
```

### Generator

Generator 是一种特殊的 iterator，最典型的例子就是 Fibonacci 数列。可以直接根据需要写一个 generator 直接调用，

```
#!python
def frange(start, stop, increment):
    x = start
    while x < stop:
        yiled x
        x += increment

for n in frange(0, 4, 0.5)
    print(n)
```

如果 generator 涉及到比较复杂的控制（比如暴露属性等），可以把 generator 函数扩展成 class 形式。比如前面的 RandSeq 例子可以扩展出更加复杂的功能，然后将 `--iter--` 内部的 return 改为 yield 即可。

## Using Iterator

### Sequence

```
#!python
>>> myTuple = (123, 'xyz', 45.67)
>>> i = iter(myTuple)
>>> i.next()
123
>>> i.next()
'xyz'
>>> i.netx()
45.67
>>> i.next()
Traceback (most recent call last):
  File "<stdin>, line 1, in <module>
StopIteration
```

### Dict

+ dict 内部实现了一个 `sq-contaisn` 的函数，它实现了 `has-key()` 相同的功能，所以可以这么写，

```
#!python
if k in dict: ...

# equivalent to
if dict.has-key(k): ...
```

+ dict 内部还实现了一个 `tp-iter` 的函数，可以产生一个针对所有 keys 的高效迭代器。所以可以这么写，

```
#!python
for k in dict: ...

# equivalent to, but much faster than
for k in dict.keys(): ...
```

只要不违反“禁止修改 dict 内容”的约束，就可以这么用。

+ dict 实际上有 3 种 iterator，`for x in dict` 实际上是 `for x in dict.iterkeys()` 的缩写

```
#!python
for key in dict.iterkeys(): ...

for value in dict.itervalues(): ...

for key, value in dict.iteritems(): ...
```

### File

file 对象内部实现了 `tp-iter` 方法，所以访问文件内容的代码可以写得更简洁，

```
#!python
for line in myFile:
    print line

# as a shorthand for
for line in iter(file.readline, ""):
    print line

# equivalent, but faster than
while 1:
    line = file.readline()
    if not line:
        break
    print line
```
### Restrictions

!!! note
    在用 iterator 时，sequence/dict 的内容是不能被修改的。

sequence 中除了 list，其它（tuple 和 string）都是不可变的，所以只需要注意 list 的情况即可。对于 dict，只允许对一个已经存在的 key 设置它的值，其他操作（增加/删除/`update()`）都是不允许的。原因就是 iterator 和实际对象是绑定在一起的，一旦修改了原对象，效果会马上体现出来。

```
#!python
# legal
myDict = {'a': 1, 'b': 2, 'c': 3}
for key in myDict:
    myDict[key] = myDict[key] + 1

# illegal
for key in myDict:
    del myDict[key]
```

实际上，在 python 的迭代器出现之前，这个限制就已经存在了，比如 C++ 也有类似的约束。

## Special Iterator

### Reversed Iterator

获得一个反向迭代器的方式：

+ 调用 BIF `reversed()`
+ 实现 `--reversed--()` 方法
+ 将对象转化为 list 对象
+ 使用 generator

直接使用 `reversed()` 的问题在于待处理的对象必须是大小确定的，如果一个对象大小不固定而且又没有实现 `--reversed--()` 方法，那么直接将其转化为 list 对象可能会占用大量内存，更优的做法是在 `--reversed--()` 中定义一个 generator。

### Using `itertools`

Python 内建的工具包，可以产生一系列各种各样的 iterator，比如无穷迭代器 `count()`, `cycle()`, `repeat()`，有限长度的 `accumulate()`, `compress()`, `chain()` 等。

```
#!python
from itertools import count

counter = count(10)
next(counter)  # 10
next(counter)  # 11
```

`itertools` 常见的 iterator 有：

+ 生成切片： `itertools.islice()`
+ 丢弃部分数据： `itertools.dropwhile()`
+ 产生所有排列组合： `itertools.permutations()`
+ 一次性迭代不同容器内的元素： `itertools.chain()`

**总结：遇到看似复杂的迭代任务，不要着急自己写复杂的 for index 循环或者是 iterator，而是应该首先看看 `itertools` 里面是否提供了相关功能，往往有惊喜。**

### `enumerate()`

如果想在迭代对象时，同时知道对应的索引，该怎么办？

或许你会想在 iterator 的基础上，再加一个计数器，在每次 for 循环中不断自增，类似这样，

```
#!python
my-list = ['a', 'b', 'c']

idx = 1
for val in my-list:
    print idx, val
    idx = idx + 1
```

但是这种写法很丑陋，最优雅的答案是用内建函数 `enumerate()`，它的返回值是一个 `enumerate` 对象，本质上就是个迭代器，返回一个由 index 和 value 组成的 tuple。

[PEP 279][PEP279] 介绍了这个函数的实现原理，如下

```
#!python
def enumerate(collection):
    'Generates an indexed series: (0, coll[0]), (1, coll[1]) ...'
    i = 0
    it = iter(collection)
    while 1:
        yield (i, it.next())
        i += 1
```

使用方法：

```
#!python
for idx, val in enumerate(my-list):
    print idx, val
```

[PEP279]: https://www.python.org/dev/peps/pep-0234/

### `zip()`

如果想同时迭代多个对象，每次迭代分别从中取出一个元素，应该怎么办？

最优雅的方式是用 `zip()` 函数，zip 函数的返回值是一个 iterator，所以可以直接在 for 循环中使用，

```
#!python
a = [1, 2, 3]
b = ['a', 'b', 'c']

for i in zip(a, b)
    print i
```

## Ref

[PEP 234 -- Iterator][PEP234]

[PEP 279 -- The enumerate() built-in function][PEP279]

[Python 核心编程](https://book.douban.com/subject/3112503/)

[Python Cookbook](https://book.douban.com/subject/26381341/)

[迭代器 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1016959663602400/1017323698112640)

[Iterables vs. Iterators vs. Generators](https://nvie.com/posts/iterators-vs-generators/)

[完全理解Python迭代对象、迭代器、生成器](https://foofish.net/iterators-vs-generators.html)
