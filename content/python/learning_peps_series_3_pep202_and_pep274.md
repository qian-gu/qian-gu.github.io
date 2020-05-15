Title: PEP 学习系列之 3 —— PEP202 & PEP274
Date: 2020-05-10 19:15
Category: Python
Tags: PEP, python
Slug: learning_peps_series_3_pep202_and_pep274
Author: Qian Gu
Series: Learning PEPs
Summary: List & Dict Comprehensions 学习笔记

## 为什么需要 Comprehensions

如果想用从一个 list 中挑选出一部分满足条件的元素组成一个新的 list，该怎么做？

+ 方法一：最直观简单的方法，写一个 `for` 循环，然后从中挨个挑选出符合条件的元素
+ 方法二：使用函数式编程中的 `map()`/`filter()`

方法一虽然简单但是很臃肿，方法二在 FP 世界里面可能是最优写法，但是不适合混合到指令式编程的世界中，所以出现了 `list comprehensions`， 它提供了另外一种更加简洁的实现方法。（**Simple is better than complex.**）

## List Comprehensions

[PEP 202 -- List Comprehensions 原文链接][PEP202]。

[PEP202]: https://www.python.org/dev/peps/pep-00202/

List Comprehensions 就是运用于 List 对象的 Comprehensions。

###  Examples

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

### 以数学的角度理解 list comprehensions

下面这个集合表示从自然数中挑选出符合条件 `x > 5` 且 `x < 10` 的所有元素，

$$new\_list = \{x | x \in N, x > 0, x < 10\}$$

下面是 Python 的实现版本，

```
#!python
new_list = [x for x in N if x > 0 and x < 10]
```

对比一下 python 版本的代码就可以知道两者非常相似，只不过 python 用 for 和 if 语句来描述数学中的条件表达式。尤其是 python 中有集合 `set` 的概念，set 也是可以写成 comprehensions 形式的，这个时候就和数学就完全等价了。

### 如何写 list comprehensions

因为 list comprehensions 本质是 for 和 if 的简洁写法，所以我们可以总结出一个模板，只要满足这个模板的 for 循环就可以改成写 list comprehensions。

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

### 小结

无论是单层还是嵌套的 for 循环，改成 list comprehensions 的方法其实方法非常简单，就是把普通的 for 循环调整了顺序，将循环内的语句写在了最前面，剩余部分按原顺序写就可以了。

+ 上面的语法只适用于一个元素（the Right One）
+ 不允许写成 `[x, y for ...]` 形式，但是可以写成一个 tuple 元素的形式 `[(x, y) for ...]`
+ 允许嵌套形式 `[...  for x... for y...]`，就像嵌套循环一样，最后一个 index 是变化最快的


## Dict Comprehensions

[PEP 274 -- Dict Comprehensions 原文链接][PEP274]。

[PEP274]: https://www.python.org/dev/peps/pep-00274/

dict comprehensions 和 list comprehensions 非常相似，不同之处是用 `{}` 而不是 `[]`。同时，关键字 `for` 前面的部分表达式改成了用冒号隔开的 key-value 对。

###  Examples

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

## Ref

[Python List Comprehensions: Explained Visually](https://treyhunner.com/2015/12/python-list-comprehensions-now-in-color/)

[用数学思维理解Comprehension](https://www.jianshu.com/p/dd85d2cd89d1)