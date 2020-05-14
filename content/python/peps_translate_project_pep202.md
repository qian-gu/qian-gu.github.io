Title: PEP 翻译计划系列 —— PEP202
Date: 2020-05-10 19:15
Category: Python
Tags: PEP, python
Slug: peps_translate_project_pep202
Author: Qian Gu
Series: PEP translate project
Summary: PEPs 翻译系列 PEP202

[PEP 202 -- List Comprehensions 原文链接][PEP202]。

[PEP202]: https://www.python.org/dev/peps/pep-00202/

| item | detail |
| ---- | ------ |
| PEP  |  202   |
| Title | List Comprehensions |
| Author | barry at python.org (Barry Warsaw) |
| Status | Final |
| Type | Standards Track |
| Created | 13-Jul-2000 |
| Python-Version | 2.0 |
| Post-History |  |

## Introduction

本文描述了一种 python 语法扩展 proposal：列表解析式（list comprehensions）。

<br>

## The Proposed Solution

本文提议允许程序员可以用 `for` 和 `if` 关键字来有条件地构造一个 list，就像在 `for` 和 
`if` 语句中的做法一样。

_如果想用从一个 list 中挑选出一部分满足条件的元素组成一个新的 list，该怎么做？最简单的方法
是写一个 `for` 循环，然后从中挨个挑选出符合条件的元素。但是这种写法很臃肿，所以出现了 
`list comprehensions`。_

<br>

## Rationale

list comprehensions 提供了另外一种更加简洁的选择，以实现当前使用 `map()`/`filter()` 或
者是嵌套循环的效果。

<br>

##  Examples

```
#!bash
>>> print [i for i in range(10)]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> print [i for i in range(20) if i%2 == 0]
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

>>> nums = [1, 2, 3, 4]
>>> fruit = ["Apples", "Peaches", "Pears", "Bananas"]
>>> print [(i, f) for i in nums for f in fruit]
[(1, 'Apples'), (1, 'Peaches'), (1, 'Pears'), (1, 'Bananas'),
 (2, 'Apples'), (2, 'Peaches'), (2, 'Pears'), (2, 'Bananas'),
 (3, 'Apples'), (3, 'Peaches'), (3, 'Pears'), (3, 'Bananas'),
 (4, 'Apples'), (4, 'Peaches'), (4, 'Pears'), (4, 'Bananas')]
>>>> print [(i, f) for i in nums for f in fruit if f[0] == "P"]
[(1, 'Peaches'), (1, 'Pears'),
 (2, 'Peaches'), (2, 'Pears'),
 (3, 'Peaches'), (3, 'Pears'),
 (4, 'Peaches'), (4, 'Pears')]
>>> print [(i, f) for i in nums for f in fruit if f[0] == "P" if i%2 == 1]
[(1, 'Peaches'), (1, 'Pears'), (3, 'Peaches'), (3, 'Pears')]
>>> print [i for i in zip(nums, fruit) if i[0]%2==0]
[(2, 'Peaches'), (4, 'Bananas')]
```

<br>

## Reference Implementation

list comprehensions 在 Python release2.0 中变成了语法中的一部分。

<br>

## BDFL Pronouncements

+ 上面的语法只适用于一个元素（the Right One）
+ 不允许写成 `[x, y for ...]` 形式，但是可以写成一个 tuple 元素的形式 `[(x, y) for ...]`
+ 允许嵌套形式 `[...  for x... for y...]`，就像嵌套循环一样，最后一个 index 是变化最快的

 <br>

------------

<br>

## 什么是 list comprehensions

list comprehensions 是 python 中的一种语法糖（`syntactis suger`），它可以将一个 list 
按照一定的条件转换成另外一个 list。可以把它看成是函数式编程中 `map()` 和 `filter()` 的语法
糖，

```
#!bash
>>> doubled_odds = map(lambda n: n * 2, filter(lambda n: n % 2 == 1, umbers))
>>> doubled_odds = [n * 2 for n in numbers if n % 2 == 1]
```

### 以数学的角度理解 list comprehensions

下面这个集合表示从自然数中挑选出符合条件 `x > 5` 且 `x < 10` 的所有元素，

$$new\_list = \{x | x \in N, x > 0, x < 10\}$$

对比一下 python 版本的代码就可以知道两者非常相似，只不过 python 用 if 语句来描述数学中的
条件表达式。

```
#!python
new_list = [x for x in N if x > 0 and x < 10]
```

尤其是 python 中有集合 `set` 的概念，set 也是可以写成 comprehensions 形式的，这个和数学
就完全等价了。

## 如何写 list comprehensions

### 模板

因为 list comprehensions 本质是 for 和 if 的简洁写法，所以我们可以总结出一个模板，只要满
足这个模板的 for 循环就可以改成写 list comprehensions。

```
#!pyton
for item in old_list:
    if condition(item):
        new_list.append(func(item))
```

可以改写成下面的形式

```
#!python
new_list = [func(item) for item in old_list if condition(item)]
```

### 循环嵌套的 list comprehensions

循环嵌套的 list comprehensions 例子：将矩阵展平，

```
#!python
for row in matrix:
    for n in row:
        flattened.append(n)
```

可以写成

```
#!python
flattend = [n for row in matrix for n in row]
```

**总结：**

无论是单层还是嵌套的 for 循环，改成 list comprehensions 的方法其实方法非常简单，就是把普
通的 for 循环调整了顺序，将循环核心的语句写在了最前面，剩余部分按原顺序写就可以了。

### 提高 list comprehensions 的可读性

因为 python 支持在括号之间断行，所以前面的例子，可以该写成下面的形式以提高可读性：

```
#!python
new_list = [
    func(itme)
    for item in old_list
    if condition(itme)
]
```

```
#!python
flattend = [
    n
    for row in matrix
    for n in row
]
```

<br>

## Ref

[Python List Comprehensions: Explained Visually](https://treyhunner.com/2015/12/python-list-comprehensions-now-in-color/)

[用数学思维理解Comprehension](https://www.jianshu.com/p/dd85d2cd89d1)