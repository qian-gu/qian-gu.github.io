Title: Python 学习笔记 #9 —— Function Arguments 函数参数
Date: 2020-06-13 16:24
Category: CS
Tags: PEP, python
Slug: python_notes_9_function_arguments
Author: Qian Gu
Series: Python Notes
Summary: 函数参数小结


## Positional Argument

最普通常见的参数，函数调用时必须按照定义顺序准确传递，而且数量也必须一样，不能多也不能少。位置参数还有一种传参方式：通过关键字。如果在函数调用时给出参数名，这样就不必按照定义顺序传参了，因为解释器可以自己根据参数名进行传递。

```
#!python
def add(a, b):
    return a+b

add(1, 2)
add(a=1, b=2)
add(b=2, a=1)
```

## Default Argument

如果定义函数时给参数默认值，那么在调用函数时可以传递也可以不传递这个参数，不传递时使用默认值。默认参数的好处是，

+ 帮助开发者更好的控制用户行为
+ 帮助用户更轻松的调用函数

默认参数可以让用户不必再操心每个繁琐的参数，当没有那么多必须操心的参数时，生活也不再那么复杂。而且一般默认值是精心选择过的“最佳值”，用户一开始时可以不必面对繁琐的选项，随着时间流逝用户逐渐变成了专家，自然就能在需要时给默认参数传递新的值。

!!! important
    显然默认参数在调用时不是必需的，有一个规则：所有的**必需参数**都要在默认参数的前面！原因很简单，如果这两类参数混合在一起，那么解释器就无法确定用哪个值来匹配哪个参数。

```
#!python
def add2(a, b=1):
    return a+b

add2(1, 2)
add2(1)
```

结合关键字参数和默认参数，就可以实现“跳过缺失参数”的效果，

```
#!python
def add3(a, b=1, c=2):
    return a+b+c

add3(1, c=3)
```

默认参数并没有看上去的那么简单。首先，对默认参数的赋值只会在函数定义的时候绑定一次。

```
#!python
def spam(a, b=x):
    print(a, b)

x = 42
spam(1)
# 1 42
x = 23
spam(1)
# 1 42
```

其次，给默认参数赋的值应该是不可变对象，如果默认值是可变容器的话，应该用 None 作为默认值。

```
#!python
def add_end(L=[]):
    L.append('END')
    return L

add_end()
add_end()
```

连续调用两次就会发现问题。修改方法也很简单，将默认值改成 `None` 即可。

```
#!python
def add_end(L=None):
    if L is None:
        L = []
    L.append('END')
    return L
```

和 C++ 中的 const 一样，使用不变对象的好处有很多，首先它不会有修改数据导致错误的情况，其次多任务时也不必加锁，同时读取也没有关系。由这个例子就可以推出一个规则，如果一个变量可以定义为不变对象，那么尽量设计成不变对象。

---------

有时候函数需要处理的参数数量是可变的，显然最简单的方法就是通过容器（`tuple`， `list`，`dict`）来传递参数。

```
#!python
def sum(numbers):
    sum = 0
    for number in numbers:
        sum += number
    return number

sum([1, 2, 3])
sum((1, 2, 3))
```

这种方式的问题在于：调用函数时必须先组装出一个容器对象，而利用变长参数则可以直接省去组装过程。因为普通参数有 positional 和 keyword 两种参数类型，所以变长参数也可以分为两类：变长位置参数、关键字参数。

----------------

## var_positional Argument

与普通位置参数对应的就是变长位置参数 var_positional argument，定义非关键字参数的方法很简单，只需要在参数名前面加上一个 `*` 即可，

```
#!python
def sum(*numbers):
    sum = 0
    for number in numbers:
        sum += number
    return number

sum(1, 2, 3)
sum(1)
sum()
```

实际调用时就不再需要组装的步骤，直接将参数挨个传递进去即可。如果已经有了一个 tuple 或者 list 对象，将其一一拆开传递进去是合法的，但是这样做太繁琐，可以直接在对象前面加上一个星号，将其转换成变长位置参数，这种写法是非常常见的。实际上星号后面的参数无论本身就是一个 tuple 还是 list，都会转化成一个 tuple 传递给函数，显然 tuple 内的元素可以是任意多个。

```
#!python
nums = [1, 2, 3]
sum(nums[0], nums[1], nums[2])
sum(*nums)
```

## var_keyword Argument

与普通关键字参数对应的就是变长关键字参数 var_keyword argument，一个函数可以接收一个 `dict` 对象作为普通参数，也可以将其定义为变长关键字参数。定义方法就是在参数名前面加上两个 `*`，

```
#!python
def person(name, age, **kw):
    print('name:', name, 'age:', age, 'other:', kw)

person('Michael', 30)
person('Bob', 35, city='Beijing')
person('Adam', 45, gender='M', job='Engineer')
```

同理，可以将 dict 拆开后传递，也可以将 dict 转换成变长关键字参数，

```
#!python
extra = {'city': 'Beijing', 'job': 'Engineer'}
person('Jack', 24, city=extra['city'], job=extra['job'])
person('Jack', 24, **extra)
```

而且可以验证，上面例子中的 `**kw` 是 `extra` 的一份拷贝，操作 kw 不会影响 extra。

```
#!python
def change(name, age, **kw):
    for key in kw.keys():
        kw[key] = 'hello'
    print(kw)

extra = {'city': 'Beijing', 'job': 'Engineer'}
person('Jack', 24, **extra)
print(extra)
```

## Keyword-only Argument

[PEP 3102 -- Keyword-Only Arguments 原文链接][PEP3102]

[PEP3102]: https://www.python.org/dev/peps/pep-3102/

`keyword-only arguments` 是 Python 3 中引入的新传参方式，在函数调用时必须以关键字的方式传递否则会报错。

我们已经知道普通的 position arguments 可以按照位置隐式地传递，也可以通过关键字的方式显式地传递，而且 Python 支持可变参数 var_positional arguments，但是前提是 position arguments 必须全部放到 var_positional arguments 的前面（左边）。这个约束有时候并不是我们想要的，如前所述如果一个函数既想要一组  var_positional arguments 也想要几个可选的 keyword 参数，那么只能通过定义 keyword argument 的方式进行传递，然后在函数内部从这个 dict 中提取出 keyword。这样做有时候不太方便，而且有时候出于安全或者是提高代码可读性的考虑，我们想定义只能通过 keyword 方式传参的参数，因此引入了 keyword-only 参数。

定义 keyword-only 参数的方法很简单，只要稍微改动一下之前的规则，允许常规参数出现在变长位置参数的后面即可，这时候这个常规参数就是 keyword-only 参数了，它必须通过关键字的方式进行传递：
 
```
#!python
def person(name, age, *args, city, job):
    print(name, age, args, city, job)
```

如果一个函数本身不需要接收可变参数，按照前面的规则就必须给它传递一个冗余的可变参数，但是这样做很不安全，所以进一步修改一下规则，把这个冗余的可变参数名省略掉只剩下一个单独的星号，如下面的形式即可。

```
#!python
def person(name, age, *, city, job):
    print(name, age, city, job)
```

keyword-only 参数也可以有默认值，如果它带有默认值，那么调用函数时可以不传递新参数，否则必须传参。

## Positional-only Arguments

[PEP 570 -- Python Positional-Only Parameters ][PEP570]

[PEP570]: https://www.python.org/dev/peps/pep-0570/

PEP 570 中还提出了一个新的符号 `/` 来定义 positional-only 参数，与 `*` 的作用刚好相反，`/` 之前的参数全部都是 positional-only，即只能通过 position 的方式传参，不能通过关键字的方式。这个提议针对 Python 3.8 及以后的版本，目前在 accept 阶段，还没到 final 阶段，所以暂时先不讨论。

## Summary

综上，Python 中一共有 5 种参数，

+ 位置参数
+ 默认参数
+ 可变参数
+ 关键字参数
+ keyword-only 参数

这五种参数的定义顺序有严格要求，有两条约束必须遵守，

+ 可变参数 `*args` 必须作为最后一个位置参数出现
+ 关键字参数 `**kw_args` 必须作为最后一个参数出现

结合这两条就可以知道，keyword-only 参数只能出现在 `*args` 和 `**kw_args` 之间，所以函数的参数必须是下面的顺序：

```
#!python
def func(positional, default, *args, keyword_only, **kw_args)
```

需要注意的是，如果调用函数时存在 `**args` 惨素而且忽略了 default 参数，那么 `**args` 会填到 default 寄存器的位置中。

```
#!python
def show_param(a, b, c=3, *args, d, **kw_args):
    print("a = ", a, '\nb = ', b, '\nc = ', c, '\n*args = ', args, '\nd = ', d, '\n**kw_args', kw_args)

args = (4, 5)
kw_args = {"param1": 6, "param2": 7}
show_param(1, 2, *args, d=3, **kw_args)
# a =  1 
# b =  2 
# c =  4 
# *args =  (5,) 
# d =  3 
# **kw_args {'param1': 6, 'param2': 7}
```

虽然 Python 支持各种方式的参数，但是实际应用中最好尽量减少参数组合，提高代码可读性。

## Ref

[Python 核心编程](https://book.douban.com/subject/3112503/)

[Python Cookbook](https://book.douban.com/subject/26381341/)

[函数的参数 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1016959663602400/1017261630425888)
