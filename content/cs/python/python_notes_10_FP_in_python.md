Title: Python 学习笔记 #10 —— Python 中的 FP
Date: 2020-06-21 11:19
Category: CS
Tags: PEP, python
Slug: python_notes_10_fp_in_python
Author: Qian Gu
Series: Python Notes
Summary: 学习 Python 中的函数式编程

## Functional Programming

函数式编程是一种编程范式，和面向过程、面向对象并列。大家都知道世界观和方法论，用中国古话就是道和术。就编程而言解决一个问题的方法有很多，不同方法的具体实现就是术，但是我们可以对这戏方法进行归类，归类的依据就是道，也就是编程范式：

+ 面向过程：一切问题都可以通过一些数据（变量）和一些操作（函数）进行处理，只需要按照步骤处理数据就可以解决问题，其中数据和操作是相互独立没有关系的，典型例子是 C 语言

+ 面向对象：数据和操作是有关联的，它们都是一个类（对象）的属性，根据问题建模出若干对象，在对象之间进行交互就能解决问题，典型例子是 C++

+ 函数式编程：源自于数学中的函数，基本上数学中函数有什么特点，编程语言中的函数就有相同特点，比如函数是一等公民，引用透明，没有副作用等

函数式编程本身是一个大而广的问题，而且 Python 不是也不大可能成为一种函数式编程语言，但是它有很多函数式编程的特点。函数式编程是一种思想，很多老手都无法准确定义什么是函数式编程，这里只是简单写写学习笔记。

## Lambda

`lambda` 函数的主要用途是定义特殊的函数，

+ 首先它必须很小，小到只有一行表达式
+ 其次它只会别调用一次（实际上因为 lambda 函数是匿名函数，没有函数名自然其他地方也无法调用）

```
#!text
lambda  [arg1 [, arg2, ... argN]: expression
```

把一个常规函数转换成 lambda 函数的方法很简单：把 def 替换成 lambda，并且省略掉函数名和参数的括号，以及 return 关键字。可以通过下面的变形来理解 lambda 函数，

```
#!python
def add(x, y): return x+y

lambda x, y: x+y
```

## High-order Function

高阶函数在学习 decorator 时已经接触过了，可以接收 function 作为参数，或者返回值的函数就是高阶函数，典型例子就是各种 decorator。

Python 中的所有函数都是”一等公民“，一等公民是指具有下面一项或几项特点的对象，

+ runtime 时创建
+ 可以赋值给一个变量或者是数据结构中的一个元素
+ 可以作为参数进行传递
+ 可以作为函数的返回值

因此 Python 中的所有函数都可以作为高阶函数来使用。

## Filter, Map, Reduce

这几个高阶函数都定义在 functools 模块中。

### Filter

`filter` 函数顾名思义，就像一个过滤器一样，把符合条件的东西（数据）过滤出来，它接收两个参数，第一个参数是过滤函数；第二个参数是 `iterable` 对象，也就是待处理的数据对象。

```
#!text
filter(function, iterable)
```

举例说明，

```
#!python
def odd(n):
    return n % 2

nums = range(6)
print filter(odd, nums)
# [1, 3, 5]
```

odd 是个过滤函数，如果数据是奇数则返回 1，偶数返回 0，也就是说会把奇数过滤出来。如果 odd 函数只在这里使用一次的话，可以结合前面的 lambda 函数写出更简洁的代码，

```
#!python
nums = range(6)
print filter(lambda n: n % 2, nums)
# [1, 3, 5]
```

仔细观察一下 filter 函数就会发现它的功能和 list comprehension 非常相似，都是迭代一个 `iterable` 对象并筛选出符合条件的数据。所以上面的例子可以用 list comprehension 重写成下面的样子，

```
#!python
print [num for num in range(6) if num % 2]
```

显然 list comprehension 的版本更加简洁，更加 `Pythonic`。

### Map

`map` 函数和 filter 函数类似，不同之处在于做映射而不是过滤。它也接收两个参数，第一个参数是映射函数，第二个参数是 `iterable` 对象，也就是待处理的数据对象。

```
#!text
map(function, iterable)
```

举例说明，将上面的挑选奇数的例子改成求平方，

```
#!python
def square(n):
    return n ** 2

nums = range(6)
print map(square, nums)
# [0, 1, 4, 9, 16, 25]
```

同理也可以写出 lambda 形式和 list comprehension，

```
#!python
# using lambda
nums = range(6)
print map(lambda n: n**2, nums)
# [0, 1, 4, 9, 16, 25]

# list comprehension
print [num**2 for num in range(6)]
# [0, 1, 4, 9, 16, 25]
```

### Reduce

`reduce` 函数顾名思义，就是把一个 `iterable` 对象归并缩减成一个单一的值。它的语法规则也 filter，map 类似。

```
#!text
reduce(function, iterable)
```

举例说明，将前面例子中的函数改为求和。普通模式的代码略，下面是 lambda 方式，

```
#!python
# lambda
nums = range(6)
print reduce(lambda m, n: m + n, nums)
# 15
```

!!! note
    map 和 reduce 函数非常有名，Google 大牛 Jeff Dean 的著名论文 [MapReduce: Simplified Data Processing on Large Clusters](https://research.google/pubs/pub62/) 介绍了 map/reduce 的基本思想，而之前非常火的大数据处理框架 Hadoop 底层实现的一个组件就是 map/reduce。大数据处理一般需要很多太计算机分布式计算，而 FP 天然就支持并行处理，不需要锁和同步，所以应用很广泛。

## Partial Function Application

3 个容易混淆的概念，

+ 数学的偏函数：定义域上部分有定义的函数，也就是说定义域中某些值没有映射值
+ 柯里化 `curring`，它指把一个有多参数的函数分解成一系列单参数的函数的过程
+ 部分函数应用 partial function application, PFA，函数调用的结果，在调用时只提供了部分参数

经典例子，

```
#!python
from functools import partial

def power(base, exponent): 
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print square(3)
# 9
print cube(3)
# 27
```

实际上，partial 接收的参数有 3 个，

```
#!python
partical(func, *args, **kw_args)
```

一般创建 PFA 固定参数时都是采用关键字的方式，比如上面例子中固化 exponent 参数。在实际调用 square 时，会把位置参数放到 `*args`, `**kw_args` 的左边（必须符合 Python 的参数定义约束）。所以上面的例子实际上等价于，

```
#!python
kw1 = {’exponent‘: 2}
kw2 = {'exponent': 3}
square = power(3, **kw1)
cube = power(3, **kw2)
```

但是如果下面这个例子中，我们就想固化中间的参数怎么办？显然调用 sum2 时只能通过关键字的方式传参。

```
#!python
def sum4(num1, num2, num3, num4):
    print 'num1 = ', num1
    print 'num2 = ', num2
    print 'num3 = ', num3
    print 'num4 = ', num4
    return num1 + num2 + num3 + num4

sum2 = paritcal(sum4, num2=2, num3=3)
sum2(1, 4)
# TypeError: sum() got multiple values for keyword argument 'num2'
sum2(num1=1, num4=4)
# num1 = 1
# num2 = 2
# num3 = 3
# num4 = 4
# 10
```

如果固化参数时没有用关键字，那么实际上就是按顺序固化

```
#!python
sum3 = partical(sum4, 1, 3)
sum3(2, 4)
# num1 = 1
# num2 = 3
# num3 = 2
# num4 = 4
# 10
```

可以看到 PFA 和待默认参数的函数很类似，但是 PFA 更灵活，原始函数不必提供参数默认值，而且可以得到很多偏函数调用，每个都能选择给不同参数默认值。

## Practice

只使用这几个简单函数就可以把所有面向过程的代码都改写成 FP 的形式，但是转换出来的代码新手比较难理解，这很不 Pythonic（具体参考[这篇文章][article1]），我们也不应该这么做。Python 本身没有专门设计成一门函数式编程语言，在可预见的将来可以也不会变成函数式语言，Python 能流行起来很大的原因就是它的语法非常接近自然语言有很高的可读性，一方面 Python 在一直吸取 FP 的要素，比如 list comprehension 等语法，另外一方面虽然 FP 的代码更接近抽象层，但是实际上能习惯看数学表达式的人本来就不多而且 FP 目前也没有大面积推广，显然 Python 类似自然语言的语法可读性更好。如果呆板地为了 FP 而舍弃 Python 自身的精髓显然是一件非常愚蠢的事情。

那么在 Python 中到底应该怎么运用 FP 呢？这里有两篇博客介绍了一些经验。

[Best Practices for Using Functional Programming in Python][article2]

[A practical introduction to functional programming][article3]

+ 尽可能地写 pure function
+ 尽可能地避免使用 mutability 对象
+ 有限地使用 class，改用 module 来代替 class（待讨论）
+ 不要滥用 lambda 和 high-order function
+ 必要时使用 generator

[article1]: https://debugtalk.com/post/python-functional-programming-getting-started/
[article2]: https://kite.com/blog/python/functional-programming/
[article3]: https://maryrosecook.com/blog/post/a-practical-introduction-to-functional-programming

## Summary

函数式编程是美丽而纯粹的，Python 是一门多范式编程语言并且支持 FP。事实上很多大牛 Python 程序猿都非常反感 Python 中的 FP，因为它很不 Pythonic。个人认为到底要不要在 Python 中使用 FP 取决于实际应用，不能削足适履强行套用，也不能无脑抵制。核心思想还是 The Zen of Python，有时候简单地使用 lambda, PFA 可以简化代码，提高可读性；在不影响可读性的情况下尽量将函数写出 pure 形式也可以提高代码的健壮性。

## Ref

[Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)

[Python 核心编程](https://book.douban.com/subject/3112503/)

[Python Cookbook](https://book.douban.com/subject/26381341/)

[函数式编程 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1016959663602400/1017328525009056)

[Best Practices for Using Functional Programming in Python][article2]

[A practical introduction to functional programming][article3]

[Learn Functional Python Syntax in 10 Minutes [Tutorial]](https://hackernoon.com/learn-functional-python-in-10-minutes-to-2d1651dece6f)

