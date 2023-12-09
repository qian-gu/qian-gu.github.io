Title: Python 学习笔记 #8 —— Decorator 装饰器
Date: 2020-06-07 22:39
Category: CS
Tags: PEP, python
Slug: python-notes-8-decorator
Author: Qian Gu
Series: Python Notes
Summary: Decorator 学习笔记


[PEP 318 -- Decorators for Functions and Methods 原文链接][PEP318]。

[PEP 3129 -- Class Decorators 原文链接][PEP3129]

[PEP318]: https://www.python.org/dev/peps/pep-0318/
[PEP3129]: https://www.python.org/dev/peps/pep-3129/

-----

## What Decorator

一句话解释 decorator：

**Decorator 是函数调用上的一种“装饰”，这些装饰本质上是一个（高阶）函数，接受一个 callable 对象作为参数，（可选）返回一个 callable 对象，完成对目标的装饰。**

一般来说，作为参数的 callable 对象就是等着被装饰的目标函数，而且这些函数自身也都带有参数，此时 decorator 就是一个高阶函数，返回值是一个闭包函数。

!!! important
    函数式编程的背景知识是理解 Decorator 的关键。

举例如下，

```
#!python
@dec2
@dec1
def func(arg1, arg2, ...):
    pass
```

等价于

```
#!python
def func(arg1, arg2, ...):
    pass
func = dec2(dec1(func))
```

## Why Decorator

为什么需要定义 decorator 呢？一般来说，decorator 是给原函数增加一些额外的“装饰”，比如 log，profiler 等操作。使用 decorator 带来的好处是，

1. 可以将这些事务性的代码和原函数代码隔离开
2. decorator 可以在其他地方复用

使用 decorator **让代码更加优美，也提高代码了的可读性。** 体现了 python 之禅的理念：

>  1. **Beautiful is better than ugly.**
>  2. **Readability counts.**

在引入 decorator 之前，如果想对函数做变换（`transformation`），只能将变换的代码放在函数体的最后，这样写出的代码很笨拙不容易理解。比如将 class 中的 method 定义为静态方法：

```
#!python
def foo(self):
    perform method operation
foo = classmethod(foo)
```

这种方法在函数体很长时可读性就很差，而且为了声明一个函数把同一个名字重复写 3 次的做法也很不 Pythonic，所以 Python 为此专门发明了一种新语法糖：用 `@` 符号表示的 decorator。比如下面这个函数经过了两次变换，

```
#!python
def foo(cls):
    pass
foo = synchronized(lock)(foo)
foo = classmethod(foo)
```

就可以改写成这样的形式，写出来的代码看起来很简洁，也很有高级感。

```
#!python
@classmethod
@synchronized(lock)
def foo(cls):
    pass
```

Decorator 是在 python2.4 中才引入的，实际上在此之前的 python2.2 中就已经有两个 decorator 了：`classmethod()` 和 `staticmethod()`。当时大家都认为很快就会在整个 python 语言中加入这种语法支持。所以你可能会好奇为什么花了这么久的时间大家才达成共识，拖到 python2.4 才完成这项功能。下面列举了一些主要原因，

+ decorator 的位置，几乎每个人都同意把 decorating/transforming 放在函数体的最后是不合适的，但是应该放在哪里却无法达成共识
+ 语法约束，Python 是一门约束非常强的语言以防你“把事情搞砸”（包括视觉上和语法上），最好不要有让新手产生错误理解的语法
+ 大家都不熟悉 decorator 的概念，对于理解线性代数或者是已经掌握了一门其他编程语言的人来说，大部分 Python 代码都是非常直观的。几乎没有人在 Python 之前接触过 decorator 的概念
+ 关于语法的讨论一般来说更加容易引起争论

## Understanding Decorator

如果仅从面向过程/面向对象的角度是很难理解 decorator 语法的，这是因为 decorator 的很多概念实际上来自于函数式编程，所以如果先接受了一些基本的函数式编程的概念，decorator 就很容易理解了。

!!! tip
    FP 中最基本的概念：函数作为一等公民，和变量有同等地位，下面的概念都源自于这个最基本的原理。

下面的代码例子来自于参考资料 [Intermediate Python][Intermediate Python]。

[Intermediate Python]: https://github.com/yasoob/intermediatePython/blob/master/decorators.rst

### Everything is a Object

Python 中万物皆为对象 Object，数字、list、tuple、dict、function、method 这些都是对象，因为函数是对象，而且和变量有同等地位，我们可以创建变量指向同一个对象，自然也可以创建一个函数的引用，通过引用来调用这个函数，

```
#!python
def hi(name="yasoob"):
    return "hi " + name

print(hi())
# output: 'hi yasoob'

# We can even assign a function to a variable like
greet = hi
# We are not using parentheses here because we are not calling the function hi
# instead we are just putting it into the greet variable. Let's try to run this

print(greet())
# output: 'hi yasoob'

# Let's see what happens if we delete the old hi function!
del hi
print(hi())
#outputs: NameError

print(greet())
#outputs: 'hi yasoob'
```

### NestedFunction

因为函数和变量的地位相同，我们可以在函数内定义变量，自然也可以在函数内定义新的函数，

```
#!python
def hi(name="yasoob"):
    print("now you are inside the hi() function")

    def greet():
        return "now you are in the greet() function"

    def welcome():
        return "now you are in the welcome() function"

    print(greet())
    print(welcome())
    print("now you are back in the hi() function")

hi()
#output:now you are inside the hi() function
#       now you are in the greet() function
#       now you are in the welcome() function
#       now you are back in the hi() function

# This shows that whenever you call hi(), greet() and welcome()
# are also called. However the greet() and welcome() functions
# are not available outside the hi() function e.g:

greet()
#outputs: NameError: name 'greet' is not defined
```

### Function as Return Value

因为函数和变量的地位相同，变量可以作为函数的返回值，自然函数也可以作为函数的返回值。（注意，函数名后面加上括号表示调用该函数，不加括号则表示这个函数的引用）

```
#!python
def hi(name="yasoob"):
    def greet():
        return "now you are in the greet() function"

    def welcome():
        return "now you are in the welcome() function"

    if name == "yasoob":
        return greet
    else:
        return welcome

a = hi()
print(a)
#outputs: <function greet at 0x7f2143c01500>

#This clearly shows that `a` now points to the greet() function in hi()
#Now try this

print(a())
#outputs: now you are in the greet() function
```
### Function as Parameter

因为函数和变量的地位相同，变量可以作为函数的参数，自然函数也可以作为函数的参数。

```
#!python
def hi():
    return "hi yasoob!"

def doSomethingBeforeHi(func):
    print("I am doing some boring work before executing hi()")
    print(func())

doSomethingBeforeHi(hi)
#outputs:I am doing some boring work before executing hi()
#        hi yasoob!
```

### Put it All

有了前面的这几个概念，decorator 的理解就非常简单了：

1. 首先 decorator 是一个高阶函数，它可以接收一个（被装饰的函数）函数作为自己的参数
2. 其次 decorator 返回值也是一个函数（闭包函数），它完成对目标的装饰
3. 经过 decorator 装饰之后，调用原函数时，实际上执行的是 decorator 的返回值

!!! note
    因为我们实际调用的是 decorator 的返回值，所以打印原函数的 `--name--` 时得到的就不再是原函数的名字了，这和一般的预期不符，我们希望的效果是“decorator 是透明的”。python 提供了工具 `functool.wraps` 来解决问题，本质上，`wraps()` 也是一个装饰器。

根据这两点，我们就可以写出一个自己的 log decorator 了，

```
#!python
from time import ctime, sleep
from functools import wraps

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print "[" + ctime() + "]" + func.--name-- + " was called"
        return func(*args, **kwargs)
    return wrapper


@log
def add(a, b):
    return a + b

@log
def sub(a, b):
    return a - b


add(1, 2)
sleep(1)
sub(7, 2)
```

上面代码中的 log 函数是一个 decorator，只有一个参数 func，接收被装饰的函数名，它的返回值是定义在自己内部的 wrapper 函数；因为 wrapper 函数用到了上层 log 函数的变量 func，所以它是一个闭包函数。func 自带的参数通过 wrapper 的 `args` 和 `kwargs` 传递到内部。这段代码运行结果如下，

```
#!text
[Fri Jun 12 23:07:12 2020]add was called
[Fri Jun 12 23:07:13 2020]sub was called
```

### Decorator with Arguments

前面的这个 log 例子中的 decorator 不带参数，无法区分装饰的目标，统一把 log 输出到 stdout 中。如果我们想把不同操作的 log 保存在不同文件中，该怎么做呢？显然 decorator 必须要能够再接收一个额外的参数，实际上直接给 log 函数增加新参数是不行的，我们只能采用一种曲线救国的方式：

**在 decorator 外面再包一层函数，这个函数的功能是接收参数并且返回我们想要的实现装饰功能的(闭包)函数。**一般带参数的 decorator 的形式如下，

```
#!python
@decomaker(deco-args)
def foo(): pass
```

这段代码等价于

```
#!python
foo = decomaker(deco-args)(foo)
```

这种形式看起来依然比较难理解，实际等效于下面的形式，首先 decomaker 使用 deco-args 作为参数，返回闭包函数赋值给 deco，然后 deco 对 foo 进行装饰。

```
#!python
deco = decomaker(deco-args)
foo = deco(foo)
```

所以 log 的例子修改如下，

```
#!python
from time import ctime, sleep
from functools import wraps

def log-to-file(log-file='operator.log'):
    def log-decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log-string = "[" + ctime() + "] " + func.--name-- + " was called"
            print log-string
            with open(log-file, 'a') as opened-file:
                opened-file.write(log-string + '\n')
            return func(*args, **kwargs)
        return wrapper
    return log-decorator


@log-to-file('add.log')
def add(a, b):
    return a + b

@log-to-file('sub.log')
def sub(a, b):
    return a - b


add(1, 2)
sleep(1)
sub(7, 2)
```

log-to-file 是一个有参 decorator，接收一个名为 log-file 的参数，并返回 log-decorator 函数。运行之后会在显示 log 记录的同时把记录写入到对应的两个文件中。

## Decorator Class

前面介绍的语法是 function 装饰 function，实际上 decorator 也可以写成 class 的形式，class 作为 decorator 只需要实现下面两点即可，

+ 一个 `--init--` 方法，用来接收被 decorated 的函数名
+ 一个 `--call--` 方法，实现装饰效果

!!! tip
    实际上成为 decorator 的要求只有一个：它必须接受一个 callable 对象作为参数，并且返回一个 callable 对象。根据这个约束，上面两点就很容易理解了。

    根据这个约束，可以推测出一个事实：如果 func 本身不需要参数而且 decorator 本身也不需要的参数，那么 decorator 也不需要写成返回闭包函数的形式，下面的代码也能正常运行。

        #!python
        def dec(func):
            print "decorating " + func.--name--
            return func

        def dec2(func):
            print "decorating again " + func.--name--
            return func

        @dec2
        @dec
        def say-hello():
            print "hello"
        
        say-hello()

    不过这种 decorator 的限制比较强，自身和目标函数都不能带参数，可能实用性不大，但是可以帮助我们理解 decorator 的概念。因为一般函数都 decorator 都是带参数的，所以就像前面的例子表现的一样 decorator 大部分情况下都是一个返回闭包的高阶函数。

    关于这个约束，实际上接收 callable 对象作为参数是必须的，返回 callable 对象则不一定，如果这个 decorator 设计成不需要后续再串接其他 decorator，那么返回值就不必是 callable 对象，如内建的 properity 等。

用 class 实现 decorator 的好处是保持用法不变的同时代码更加清晰，而且可以通过继承扩展出新的 decorator。继续以 log 装饰器为例，首先我们把它改造成 class 形式，

```
#!python
from time import ctime, sleep

class BasicLog(object):
    """A basic log class."""
    def --init--(self, func):
        self.func = func

    def --call--(self, *args, **kwargs):
        log-string = "[" + ctime() + "] " + self.func.--name-- + " was called"
        print log-string
        return self.func(*args, **kwargs)


@BaiscLog
def add(a, b):
    return a + b

@BasicLog
def sub(a, b):
    return a - b


add(1, 2)
sleep(1)
sub(7, 2)
```

这个 BasicLog 的效果和最开始的 log decorator 效果是一样的，不过看起来更清晰一点，后期扩展也更容易。显然，这个 BasicLog 无法接收参数，所以也不能根据不同操作保存到不同 log 文件中。我们改造一下它，让它可以接收参数。需要注意的是：无法在 BasicLog 的基础上直接通过简单的继承构造出一个新的 decorator，而应该做如下修改：

+ `--init--` 不再接收 func 参数，而是接收 class 参数
+ `--call--` 接收 func 参数并实现装饰效果

这里的改动类似于 function 形式的 decorator，无参数时 `--call--` 就是需要返回的闭包函数，它直接完成装饰工作；有参数时，`--init--` 用来接收其他参数，而 `--call--` 变成了一个原来闭包函数的 wrapper，它负责接受 func 参数，定义在 `--call--` 内部的闭包函数 deco 完成真正的装饰工作。

修改后的新 decorator 如下，

```
#!python
from time import ctime, sleep

class FileLog(object):
    """A log class for writing log into files."""
    def --init--(self, file-name='operator.log'):
        self.-file-name = file-name

    def --call--(self, func):
        @wraps(func)
        def deco(*args, **kwargs):
            log-string = "[" + ctime() + "] " + func.--name-- + " was called"
            print log-string
            with open(self.-file-name, 'a') as opened-file:
                opened-file.write(log-string + '\n')
            return func(*args, **kwargs)
        return deco

@FileLog(file-name='add.log')
def add(a, b):
    return a + b

@FileLog(file-name='sub.log')
def sub(a, b):
    return a - b

add(1, 2)
sleep(1)
sub(7, 2)
```

## Build-in Decorator

1. @propority
    
    可以把 class 的 method 伪装成属性，本来 `Foo.func()` 的调用方法就变成了 `Foo.func` 形式，可以让调用者写出简短的代码，同时又能保证对参数的检查等操作。

2. @staticmethod
3. @calssmethod

!!!note
    这三个内置 decorator 的返回结果都不是 callable 对象，所以它们只能放在 decorator 的最外层，后面有个相关例子。

## Class Decorator

Decorator 不仅可以装饰 function，它也可以装饰 class。

在 python2.4 引入 decorator 的时候，只能用于 function 或者是 method，class 是无法使用 decorator 的。几乎可以确定地说，decorator 能实现的功能用 metaclass 同样可以实现，但是 metaclass 的方式太过晦涩，由于 Guido 的坚持反对，直到在 PEP3129 中讨论了 class 的 decorator 之后，在 python3.0 中最终加入 class decorator。

Class decorator 的设计目标和语法和 function decorator 完全相同，唯一的区别就是你在“装饰” class 对象。语法如下，

```
#!python
class A:
  pass
A = foo(bar(A))


@foo
@bar
class A:
  pass
```

随便写个 class 然后直接用前面的 log 函数进行装饰，代码如下，

```
#!python
from time import ctime
from functools import wraps

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print "[" + ctime() + "] " + func.--name-- + " was called"
        return func(*args, **kwargs)
    return wrapper

@log
class People(object):
    """Class for general people."""
    def --init--(self, name):
        self.-name = name

    def get-name(self):
        print "My name is " + self.-name

    def change-name(self, new-name):
        self.-name = new-name
        print "Change name to " + self.-name

Jack = People('Jack')
Jack.get-name()
Jack.change-name('Tom')
Jack.get-name()
```

运行结果如下

```
#!text
[Fri Jun 12 23:16:27 2020] People was called
My name is Jack
Change name to Tom
My name is Tom
```

运行结果和我们的预期不符，只有例化对象时调用了 log 进行装饰，调用其他方法时却没有调用。

最无脑的解决方法是给每个方法前面都加上装饰，虽然这样修改之后结果如我们预期，但是这种方法违反了 DRY 原则，每个方法都要手动加上装饰，以后新增方法也要添加，如果不需要 log 功能又要逐行删掉所有的装饰语句，这很不 pythonic。我们期望的效果是：只在 class 的定义处只做一次装饰声明，实现对内部所有方法的装饰。

修改方法一：根据前面的思路对于 class 的 decorator，显然输入参数是一个 class，最终返回的也是一个 class，只需要在函数内部对输入 class 的 `--getattribute--` 方法进行特殊定义即可。

```
#!python
from time import ctime
from functools import wraps

def new-log(cls):

    orig-getattribute = cls.--getattribute--

    def new-getattribute(self, name):
        print "[" + ctime() + "] " + name + " was called"
        return orig-getattribute(self, name)

    cls.--getattribute-- = new-getattribute

    return cls

@new-log
class People(object):
    """Class for general people."""
    def --init--(self, name):
        self.-name = name

    def get-name(self):
        print "My name is " + self.-name

    def change-name(self, new-name):
        self.-name = new-name
        print "Change name to " + self.-name

Jack = People('Jack')
Jack.get-name()
Jack.change-name('Tom')
Jack.get-name()
```

方法二：要修改一个 class 的行为，除了上面的方法之外还有一种就是给原始 class 包一层，只需要修改 wrapper class 的 `--getattr--` 方法即可通过代理和授权实现 decorator 的效果。代码如下，

```
#!python
from time import ctime
from functools import wraps

def new-log(cls):
    class NewCls(object):
        """Decorated new class."""
        def --init--(self, *args, **kwargs):
            super(NewCls, self).--init--()
            self.origin-inst = cls(*args, **kwargs)
    
        @staticmethod
        def log(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print "[" + ctime() + "] " + func.--name-- + " was called"
                return func(*args, **kwargs)
            return wrapper

        def --getattr--(self, s):
            return self.log(getattr(self.origin-inst, s))

    return NewCls
   

@new-log
class People(object):
    """Class for general people."""
    def --init--(self, name):
        self.-name = name

    def get-name(self):
        print "My name is " + self.-name

    def change-name(self, new-name):
        self.-name = new-name
        print "Change name to " + self.-name

Jack = People('Jack')
Jack.get-name()
Jack.change-name('Tom')
Jack.get-name()
```

运行结果如下，

```
#!text
[Fri Jun 12 23:20:51 2020] get-name was called
My name is Jack
[Fri Jun 12 23:20:51 2020] change-name was called
Change name to Tom
[Fri Jun 12 23:20:51 2020] get-name was called
My name is Tom
```

## Caveats

这部分内容来自于参考链接 [详解Python的装饰器][ref1]，非常有意思，搬运过来记录一下。

[ref1]: https://www.cnblogs.com/cicaday/p/python-decorator.html

第一个例子如下，

```
#!python
def html-tags(tag-name):
    print 'begin outer function.'
    def wrapper-(func):
        print "begin of inner wrapper function."
        def wrapper(*args, **kwargs):
            content = func(*args, **kwargs)
            print "<{tag}>{content}</{tag}>".format(tag=tag-name, content=content)
        print 'end of inner wrapper function.'
        return wrapper
    print 'end of outer function'
    return wrapper-

@html-tags('b')
def hello(name='Toby'):
    return 'Hello {}!'.format(name)

hello()
hello()
```

这段代码的运行结果如下，

```
#!text
begin outer function.
end of outer function
begin of inner wrapper function.
end of inner wrapper function.
<b>Hello Toby!</b>
<b>Hello Toby!</b>
```

这个结果说明一旦一个函数被装饰过，那么以后就再也无法调用原函数了，原函数名指向的是被装饰过的函数，而且是最里层的那个闭包函数。所以尽量把逻辑都写在最里层的闭包内，以防出现与预期不符的结果。

第二个例子，

```
#!python
class Car(object):
    def --init--(self, model):
        self.model = model

    @logging  # 装饰实例方法，OK
    def run(self):
        print "{} is running!".format(self.model)

    @logging  # 装饰静态方法，Failed
    @staticmethod
    def check-model-for(obj):
        if isinstance(obj, Car):
            print "The model of your car is {}".format(obj.model)
        else:
            print "{} is not a car!".format(obj)

"""
Traceback (most recent call last):
...
  File "example-4.py", line 10, in logging
    @wraps(func)
  File "C:\Python27\lib\functools.py", line 33, in update-wrapper
    setattr(wrapper, attr, getattr(wrapped, attr))
AttributeError: 'staticmethod' object has no attribute '--module--'
"""
```

这个例子证明了 `@staticmethod` 返回的 staticmethod 对象不是 callable 的，所以无法再继续传递给其他 decorator。解决方法也很简单，调整一下顺序将 staticmethod 放在最后就好了。

## Using 3rd Lib

[decorator.py][decorator.py] 和 [wrapt][wrapt] 都是帮助我们写 decorator 的第三方包，使用它们的好处是一方面可以减少函数嵌套的层数，像前面带参数的 decorator 要嵌套定义 3 层，看起来有点难懂；另一方面可以帮我们解决函数签名等问题。详细内容直接看官方文档即可。

[decorator.py]: https://github.com/micheles/decorator

[wrapt]: https://pypi.org/project/wrapt/

## Example

[PEP318][PEP318] 和 [Python Decorator Library][library] 中列举了很多可以直接使用的 decorator 例子，具体使用方法直接看原文即可。

[library]: https://wiki.python.org/moin/PythonDecoratorLibrary

## Design Decorator

这部分是扩展阅读。PEP318 提到了很多设计 decorator 时的考虑因素和对比取舍，了解这些背景知识可以增加我们对 Python 的理解。下面是一些内容的翻译和笔记。

### Name Choice

很多人抱怨 decorator 这个名字，因为它和实际的用法并不一致，之所以选择这个名字，很可能是借鉴了编译器领域的术语，可能以后会换成一个更加合适的名字。

### Goals

Decorator 的设计目标包括，

+ 这种语法应该能适用于任何 wrapper，包括用户自定义的函数以及已经存在的内建函数 `classmethod()`、`staticmethod()`，这个要求也意味着 decorator 的语法要能支持传参
+ 能支持多个 wrapper 嵌套
+ 语法要足够明显，至少要让新手写代码时可以安全地忽略它的存在
+ 一旦解释就应该很容易记住 "that ...[is] easy to remember once explained."
+ 方便未来扩展
+ 容易书写，代码会经常使用这种语法
+ 不会增加快速浏览代码的难度，应该很容易搜索
+ 不要使其他工具难以支持
+ 允许将来的编译器做优化，未来会有一个 python 的 JIT 编译器，所以需要把 decorator 放在函数定义的前面
+ 从函数的结尾处挪到函数的开头，more in your face

### Current Syntax

```
#!python
@dec2
@dec1
def func(arg1, arg2, ...):
    pass
```

等价于

```
#!python
def func(arg1, arg2, ...):
    pass
func = dec2(dec1(func))
```

这样就不需要像原来那样再定义一个同名的变量，多做一次赋值。decorator 就在函数声明的附近，`@` 符号可以明确表明这里有一些新语法。

Decorator 的顺序设计是为了和数学中的函数规则相匹配，比如 $(g \circ f)(x)$ 和 $g(f(x))$ 是等价的，在 python 中，`@g @f def foo()` 会翻译成 `foo=g(f(foo))`。

decorator 语法允许调用一个返回 decorator 的函数，

```
#!python
@decomaker(argA, argB, ...)
def func(arg1, arg2, ...):
    pass
```

这段代码等价于

```
#!python
func = decomaker(argA, argB, ...)(func)
```

之所以允许一个函数返回 decorator，部分原因是 @ 符号可以看作是一个表达式（虽然在语法上仅限于作用在函数上），所以任何时候调用都会返回这个表达式。

### Syntax Alternatives

实际上在确定最终的语法之前，还有很多变种语法，下面列举了几大类，从中可以看到 python 设计的思路和决策取舍，增加对 python 的理解。

1. Decorator Location

    一种写法如下，把 decorator 放在 def 和函数名，或者是函数名和参数表之间，其缺点是无法使用 `def foo(` 来 grep 寻找函数定义，而且有多个 decorator 时代码会变得非常笨重。

        #!python
        def @classmethod foo(arg1,arg2):
            pass
        
        def @accepts(int,int),@returns(float) bar(low,high):
            pass
        
        def foo @classmethod (arg1,arg2):
            pass
        
        def bar @accepts(int,int),@returns(float) (low,high):
            pass

    另外一种写法是把 decorator 放在参数表和行尾的冒号之间，

        #!python
        def foo(arg1,arg2) @classmethod:
            pass
        
        def bar(low,high) @accepts(int,int),@returns(float):
            pass

    Guido 总结了下面几个理由来反对这种写法，

    + 隐藏了关键信息
    + 如果参数表和 decorator 都很长，很容易忘记两者之间的转化
    + decorator 在行中间，cut/copy 重用很麻烦

    还有一种写法把 decorator 放在函数体内部的开头 docstring 的位置，这种写法的主要问题是要先“偷窥”一下函数内部才能确定 decorators，而且 decorator 在函数运行的时候并不会被执行。

        #!python
        def foo(arg1,arg2):
            @classmethod
            pass
        
        def bar(low,high):
            @accepts(int,int)
            @returns(float)
            pass
    
    还有一种写法是产生一个新的代码块，这种写法的问题是 decorated 和 undecorated 函数的缩进不一样。

        #!python
        decorate:
            classmethod
            def foo(arg1,arg2):
                pass
        
        decorate:
            accepts(int,int)
            returns(float)
            def bar(low,high):
                pass

2. Syntax forms

    + 使用 `@decorator` 方式
    
            #!python
            @classmethod
            def foo(arg1,arg2):
                pass
            
            @accepts(int,int)
            @returns(float)
            def bar(low,high):
                pass
    
        主要的反对意见是之前的 Python 中没有用到 @ 符号（IPython 和 Leo 中用到了），而且  @ 符号没有实际含义。
    
    + 使用 `|decorator` 方式
     
            #!python
            |classmethod
            def foo(arg1,arg2):
                pass
            
            |accepts(int,int)
            |returns(float)
            def bar(low,high):
                pass
    
        这种语法的好处是 IPython 和 Leo 不会冲突，缺点是 `|` 符号和大写字母 `I`、小写字母 `i` 很像。
    
    + 使用 list 语法
    
            #!python
            [classmethod]
            def foo(arg1,arg2):
                pass
            
            [accepts(int,int), returns(float)]
            def bar(low,high):
                pass
    
        主要问题是 list 语法是有实际含义的，而且这种写法无法很清楚地表明这就是一个 decorator。
    
    + 使用其他括号的 list 语法，<...>, [[...]] 等
    
            #!python
            <classmethod>
            def foo(arg1,arg2):
                pass
            
            <accepts(int,int), returns(float)>
            def bar(low,high):
                pass
    
        两个方括号的写法只能表明 decorator 不是一个 list，而 <> 的方式解析起来很麻烦，而且容易和大于、小于号产生歧义。
    
    + 使用 `decorator()` 函数
    
        这个函数其实是一个使用内省机制实现操作内部函数的 magic function，Guido 坚决反对这种用法，因为不引入新语法，这种写法看起来“魔力值”会非常高，

        > Using functions with "action-at-a-distance" through sys.settraceback may be okay for an obscure feature that can't be had any other way yet doesn't merit changes to the language, but that's not the situation for decorators. The widely held view here is that decorators need to be added as a syntactic feature to avoid the problems with the postfix notation used in 2.2 and 2.3. Decorators are slated to be an important new language feature and their design needs to be forward-looking, not constrained by what can be implemented in 2.3.

    + 使用新的关键字/ block

        这种写法用到了新的关键字 `using`，而且 block 看起来是个普通的代码块，但实际上它并不是，如果在 block 内尝试写语句则会报错，这会让使用者非常困扰。Guido 拒绝了这种方案，

        > ... the syntactic form of an indented block strongly suggests that its contents should be a sequence of statements, but in fact it is not -- only expressions are allowed, and there is an implicit "collecting" of these expressions going on until they can be applied to the subsequent function definition. ...

        > ... the keyword starting the line that heads a block draws a lot of attention to it. This is true for "if", "while", "for", "try", "def" and "class". But the "using" keyword (or any other keyword in its place) doesn't deserve that attention; the emphasis should be on the decorator or decorators inside the suite, since those are the important modifiers to the function definition that follows. ...

3. Why @

    Javadoc 和 Java1.5 用到了  @ 符号作为标记，这种用法和 python 非常相似。之前的 Python 版本不支持  @ 符号意味着这些代码无法在旧版本的 python 上运行，所以也就不会导致微妙的语法错误，这也意味着 decorator 的声明不再有歧义。即使这样仍然有人认为 @ 符号的选用太过随意，提议用其他符号来代替，比如 |, [|...|], *[...]*, <...> 等等。

## Summary

Decorator 是一个高阶函数，可以在不影响目标函数的前提下，对其进行装饰，实现一些增强/辅助效果。Decorator 可以是 function 形式也可以是 class 形式，它修饰的对象可以是 function 也可以是 class。

## Ref

[Python 核心编程](https://book.douban.com/subject/3112503/)

[Intermediate Python][Intermediate Python]

[Python修饰器的函数式编程](https://coolshell.cn/articles/11265.html)

[详解Python的装饰器][ref1]

[Advanced Uses of Python Decorators](https://www.codementor.io/@sheena/advanced-use-python-decorators-class-function-du107nxsv)

[Python Decorator Library][library]

[Python Cookbook][cookbook]

[cookbook]: https://book.douban.com/subject/26381341/

