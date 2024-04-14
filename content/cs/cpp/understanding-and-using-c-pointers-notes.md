Title: 深入理解 C 指针读书笔记
Date: 2024-04-14 16:55
Category: CS
Tags: C, pointer
Slug: understanding-and-using-c-pointers-notes
Author: Qian Gu
Summary: 总结 C 指针用法

[TOC]

## 第一章 认识指针

> 理解指针的关键在于理解C程序如何管理内存。归根结底，指针包含的就是内存地址。不理解组织和管理内存的方式，就很难理解指针的工作方式。

### 指针和内存

| 内存类型             | 作用域                | 生命周期           |
| -------------------- | --------------------- | ------------------ |
| 全局内存             | 整个文件              | 应用程序的生命周期 |
| 静态内存             | 声明它的函数内部      | 应用程序的生命周期 |
| 自动内存（局部内存） | 声明它的函数内部      | 函数执行时间内     |
| 动态内存             | 由引用该内存的指针决定| 直到内存释放       |

> 指针变量包含内存中别的变量、对象或函数的地址。对象就是内存分配函数（比如malloc）分配的内存。指针通常根据所指的数据类型来声明。对象可以是任何C数据类型，如整数、字符、字符串或结构体。然而，指针本身并没有包含所引用数据的类型信息，指针只包含地址。

#### 为什么要精通指针？（指针的用途）

> + 写出快速高效的代码
> + 为解决很多类问题提供方便的途径
> + 支持动态内存分配
> + 使表达式变得紧凑和简洁
> + 提供用指针传递数据结构的能力而不会带来庞大的开销
> + 保护作为参数传递给函数的数据

> 用指针可以写出快速高效的代码是因为指针更接近硬件。也就是说，编译器可以更容易地把操作翻译成机器码。指针附带的开销一般不像别的操作符那样大。

> 紧凑的表达式有很强的表达能力，但也比较晦涩，因为很多程序员并不能完全理解指针表示法。紧凑的表达式应该用来满足特定的需要，而不是为了晦涩而晦涩。

#### 声明指针

```c
// 星号两边的空格无关紧要，下面的几个声明是等价的。空白符的使用是个人喜好
int *pi;
int* pi;
int * pi;
int*pi;
```

> 星号将变量声明为指针。这是一个重载过的符号，因为它也用在乘法和解引指针上。

> 指针的实现中没有内部信息表明自己指向的是什么类型的数据或者内容是否合法

> 尽管不经过初始化就可以使用指针，但只有初始化后，指针才会正常工作。

任何变量都有两个熟悉：valu 和 address，指针变量的 value = 被指向对象的地址。

!!!Warning
    指针变量的类型是 **指针**，如 `int *` 和 `char *` 等。虽然有些系统中，`int*` 和 `int` 都是 32bit 数据，但是它们的类型不同，所以不能直接把 `int` 变量赋值给 `int *` 指针。但是可以强转后赋值，即 `int *pi = (int *)num`。

!!!Warning
    为了避免解引用未初始化的指针导致错误，声明指针变量时尽快初始化是一个好习惯。

#### 如何阅读声明

**倒过来读。**

```c
// 1. pci 是一个变量;
// 2. pci 是一个指针变量
// 3. pci 是一个指向整数的指针变量
// 4. pci 是一个指向整数常量的指针变量
const int *pci;
```

#### 地址操作符 `&`

因为指针保存的 value 是地址，所以 可以用地址操作符来给指针赋值：

```c
int num;
int *pi = &num;
```
 
对于 `int *pi` 来说，

| 变量  | 含义                                                                   |
| ----- | ---------------------------------------------------------------------- |
| `pi`  | 任何变量，直接引用表示取该变量的 value，即指针变量 pi 指向的变量的地址 |
| `&pi` | 任何变量，地址操作符返回该变量的 address，取指针变量 pi 自身的地址     |

#### 间接引用操作符 `*`
 
`*` 返回指针变量指向的对象的 value，这个过程叫做指针解引用。

```c
int num = 5;
int *pi = &num;
printf("%p\n", *pi);  // print 5
// 解引用的结果既可以当左值，又可以当右值。
*pi = 200;
printf("%p\n", *pi);  // print 200
```

#### 指向函数的指针

指针指向的对象可以是函数：

```c
// 指针变量的名称为 foo
// 被指向的对象（函数）没有形参，也没有返回值
void (*foo)();
```

#### null 的概念

几个近似但不同的概念：

| 术语           | 含义                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------ |
| null 概念      | 通过 null 指针常量来支持的一种抽象，这个常量可以是也可以不是 0，C 程序员不需要关心实际的内部表示 |
| null 指针常量  | null 指针没有指向任何内存区域，两个 null 指针总是相等的。每个类型的指针都有对应的 null 指针类型  |
| NULL 宏        | 把整数常量 0 强转为 void 指针，即 `#define NULL ((void *)0)`                                     |
| ASCII 字符 NUL | 全 0 的字节                                                                                      |
| null 字符串    | C 语言的字符串是必须以 0 结尾的字符序列，NUL 字符串是空字符串，不包含任何字符                    |
| null 语句      | 只有一个分号的语句                                                                               |

!!!Warning
    null 指针和未初始化的指针不是一回事，未初始化的指针可能包含任何值，null 指针则不会指向任何内存地址。任何时候都不能解引用 null 指针，因为它指向的不是合法地址。

!!!Warning
    不能直接把 int 变量赋值给指针，但是一个例外情况是**可以把常数 0 直接赋值给任何指针**，但是不能赋值其他常数。

```c
// valid assignment
pi = 0;
pi = NULL;
// invalid assignment
pi = 100;
pi = num;
```

Q：用不用 NULL？

A：取决于个人喜好，NULL 比 0 的含义更加清晰，提醒正在使用指针

#### void 指针

```c
void *pv;
```

+ void 指针具有和 char* 指针相同的形式和内存对齐方式
+ void 指针永远都不会和其他类型的指针相等，但是两个赋值为 NULL 的 void 指针是相等的

通用指针，用来存放任何数据类型的引用。任何类型的指针都可以转成 void 指针，然后再转回到原来的类型。转回后的结果和原始指针的 value 是相等的。

```c
int num;
int *pi = &num;
printf("Value of pi: %p\n", pi);  // Value of pi: 100
void *pv = pi;
pi = (int *)pv;
printf("Value of pi: %p\n", pi);  // Value of pi: 100
```

!!!Warning
    + void 指针只能用来作为数据指针，不能用作函数指针
    + 一旦指针被转为 void 指针后，就可以再次被转为其他任意类型的指针，所以要小心使用

#### 全局和静态指针

全局/静态指针声明时就会被自动初始化为 NULL：

```c
int *globalpi;

void foo() {
  static int *staticpi;
}

int main()
{
}
```

### 指针的长度和类型

+ 数据指针的长度通常都是一样的，和指针类型无关
+ 函数指针长度可能和数据指针长度不同

使用指针时常用的四种预定义类型：

+ `size_t`
+ `ptrdiff_t`
+ `intptr`
+ `uintptr_t`

#### size_t

+ 含义：C 中任何对象可以达到的最大长度
+ 用途：用于安全地表示长度。
+ 用法：是 `sizeof` 的返回值类型，也是 `malloc` 和 `strlen` 函数的参数
+ 声明：实现相关，一般出现在一个或多个标准头文件中，如 `stdio.h` 和 `stdlib.h`。一般 32 位系统上是 32，64 位系统上是 64

```c
#ifndef __SIZE_T
#define __SIZE_T
typedef unsigned int size_t;
#endif
```

!!!Warning
    `size_t` 可以用来存放指针，但是假定 `size_t` 和指针一样长不是个好主意。`intptr_t` 是更好的选择。

#### intptr_t  和 uintptr_t

+ 用途：存放指针地址
+ 用法：提供一种可移植且安全的方法声明指针，且和系统中使用的指针长度相同。把指针转化成整数时很有用
+ 一般来说，`intptr_t` 比 `uintptr_t` 更灵活

!!!Warning
    + 避免把指针转化成整数。如果指针是 64bit，整数只有 32bit 时会丢失信息
    + 使用 `intptr_t` 和 `uintptr_t` 时，必须先强转才能赋值。

```c
int num
uintptr_t *pi = &num;  // error
uintptr_t *pi = (uintptr_t *)&num;  // okay
```

### 指针操作符

| 操作符               | 名称                           | 含义                   |
| -------------------- | ------------------------------ | ---------------------- |
| `*`                  |                                | 声明指针               |
| `*`                  | 解引用                         | 得到指向对象的 value   |
| `->`                 | 指向                           | 得到指针指向结构的字段 |
| `+`                  | 加                             | 指针加法               |
| `-`                  | 减                             | 指针减法               |
| `==`, `!=`           | 相等、不相等                   | 指针比较               |
| `>`, `>=`, `<`, `<=` | 大于、大于等于、小于、小于等于 | 指针比较               |
| (数据类型)           | 转换                           | 转化指针类型           |

#### 指针算术运算

数据指针可以执行以下几种算术运算：

| 算术运算                | 结果                                                                                                           |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- |
| l_ptr = r_ptr + integer | <p>参与指针算术运算的整数的单位是 `sizeof(ptr)`，</p>l_ptr 的 value = r_ptr 的 value + integer * sizeof(r_ptr) |
| ptr - int               | <p>参与指针算术运算的整数的单位是 `sizeof(ptr)`，</p>l_ptr 的 value = r_ptr 的 value - integer * sizeof(r_ptr) |
| ptr - ptr               | 它们之间相差的 “单位” 的数量，`ptrdiff_t` 是指针差值的可移植方式                                               |
| ptr 和 ptr 比较         | 一般没有用途，特殊情况：指针和数组元素比较，判断数组元素的相对顺序，和指针差值类似，结果的正负号表示前后顺序   |

### 指针常见用法

+ 多层间接引用
+ 常量指针

#### 多层间接引用

即指针套娃，常见例子：双重指针，如 `argv` 给 main 函数传参。

    #!c
    char *titles[] = {"A Tale of Two Cities", "Wuthering Heights", "Don Quixote", "Odyssey", "Moby-Dick", "Hamlet", "Gulliver's Travels"};
    char **bestBooks[3];
    char **englishBooks[4];
    
    bestBooks[0] = &titles[0];
    bestBooks[1] = &titles[3];
    bestBooks[2] = &titles[5];
    
    englishBooks[0] = &titles[0];
    englishBooks[1] = &titles[1];
    englishBooks[2] = &titles[5];
    englishBooks[3] = &titles[6];
    printf("%s\n", *englishBooks[1]); // Wuthering Heights

间接引用没有层数限制，但是层数过多会让人迷惑，难以维护。

#### 常量与指针

| 指针     | 被指向的对象 | 示例                                 | 类型                                   | 指针 value 可修改 | 被指向对象 value 可修改 |
| -------- | ------------ | ------------------------------------ | -------------------------------------- | ----------------- | ----------------------- |
| 非 const | 非 const     | `int *pci`                           | 普通指针                               | Y                 | Y                       |
| 非 const | const        | `const int *pci` 或 `int const *pci` | 指向 const 的指针                      | Y                 | N                       |
| const    | 非 const     | `int *const cpi`                     | const 指针                             | N                 | Y                       |
| const    | const        | `const int *const cpci`              | 指向 const 对象的 const 指针，很少用到 | N                 | N                       |

!!!Note
    const 和数据类型关键字的顺序不重要，但是 const 和 * 的顺序非常重要！

示例：

    #!c
    const int *pci;  // 指向 const 的指针，两者等价
    int const *pci;
    
    int *const cpi;  // 指针是 const

    #!c
    int num = 5;
    const int limit = 500;
    int *pi;
    const int *pci;  // 从右向左读：pci 是一个普通指针，指向对象的类型为 int 常量
                     // 1. pci 可以被修改指向其他对象
                     // 2. 可以解引用 pci 以读取被指向对象的 value
                     // 3. 不能解引用 pci 来修改被指向对象的 value
    
    pi = &num;
    pci = &limit;
    
    pci = &num;  // legal
    *pci = 200;  // illegal
    
    #!c
    int num;
    int *const cpi = &num;  // 从右向左读：cpi 是一个常数，它的类型是指针，指向对象的类型为 int
                            // cpi 的 value 必须被初始化，指向的对象必须是非常量的 int
                            // cpi 的 value 初始化后就不能再修改，因为 cpi 是个 const
                            // cpi 指向的对象的 value 可以被修改
    
    *cpi = limit;  // legal
    *cpi = 25;     // legal
    
    const int limit = 500;
    int *const cpi = &limit  // Warning: limit 是 const，被非 const 的 cpi 指向后，可能会被 *cpi 非法修改

## 第二章 C 的动态内存管理

内存类型：

+ 静态内存：栈 `stack`
+ 动态内存：堆 `heap`

### 动态内存分配

具体可用的函数取决于系统，大部分系统的 stdlib.h 文件中都有如下函数：

| 函数                  | 功能                                                    |
| --------------------- | ------------------------------------------------------- |
| `void malloc(size_t)` | 从 heap 分配内存                                        |
| `realloc()`           | 在之前分配的基础上，重新分配为更大（小）的部分          |
| `calloc()`            | 从 heap 分配内存并清零， `calloc` = `malloc` + `memset` |
| `free()`              | 释放空间到 heap                                         |

+ malloc 只分配空间，不初始化
+ 成功后返回首字节的地址
+ 分配内存时用 sizeof 操作符提高移植性
+ 每次申请时，堆管理器会额外分配空间来管理
+ 初始化静态/全局变量时不能调用 malloc 函数
  + 静态变量的解决方法：可以先声明再赋值 `static int *pi; pi = malloc(sizeof(int));`
  + 全局变量无解：全局变量必须在函数和可执行代码外部声明，赋值必须出现在函数中
+ reallocate 如果是空间变小，直接归还多余空间；如果空间变大，则重新开辟并复制旧内存
+ C99 引入了变长数组 (VLA），数组长度可以 runtime 决定

!!!Note
    + 在编译器看来，初始化操作符 `=` 和赋值操作符 `=` 不一样
    + VLA 有 runtime 开销，而且一旦函数退出，立即释放内存
    + VLA 的长度不能改变，一旦分配就固定了，如果长度需要可变，需要使用 `realloc`


malloc 必须和 free 对称使用，防止内存泄漏。通常的做法是把被释放的指针赋值为 NULL。两种常见的内存泄露：

1. 丢失内存地址

        #!c
        // 变长数组 VLA
        void compute(int size) {
          char *buffer[size];
        }
        // 内存泄漏
        int *pi = (int *)malloc(sizeof(int));
        *pi = 5;
        pi = (int *)malloc(sizeof(int));

2. 忘记调用 free

### 迷途指针

迷途指针：内存已经释放，还在引用原始内存的指针。

迷途指针造成的问题：

+ 如果访问内存，行为不可预期
+ 如果内存为不可访问，则是段错误
+ 潜在的安全隐患

迷途指针的例子：

    #!c
    // 1. 访问已释放的内存
    int *pi = (int*)malloc(sizeof(int));
    *pi = 5;
    free(pi);
    *pi = 10;  // pi 迷途指针：已释放
    
    int *p1 = (int*)malloc(sizeof(int));
    *p1 = 5;
    int *p2;
    p2 = p1;
    free(p1);
    *p2 = 10;  // p2 迷途指针：空间已通过 p1 释放
    
    
    // 2. 访问无效的局部变量
    int *pi;
    {
      int tmp = 5;
      pi = &tmp;
    }
    *pi = 10;  // pi 迷途指针：tmp 已失效

如何处理迷途指针：

+ 释放指针后设置为 NULL（无法解决多个指针的问题）
+ 写一个特殊函数代替 free
+ 第三方检测工具
+ 垃圾回收（非标准技术，不属于语言的一部分）
+ 异常处理

## 第三章 指针和函数

+ 指针指向数据，作为函数参数：把数据传递给函数，允许函数对其进行修改
+ 指针指向函数，动态控制程序执行流

### 程序的栈和堆

> 程序栈是支持函数执行的内存区域，通常和堆共享。也就是说，它们共享同一块内存区域。程序栈通常占据这块区域的下部，而堆用的则是上部。

> 程序栈存放栈帧（stack frame），栈帧有时候也称为活跃记录（activation record）或活跃帧（activation frame）。栈帧存放函数参数和局部变量。

> 调用函数时，函数的栈帧被推到栈上，栈向上“长出”一个栈帧。当函数终止时，其栈帧从程序栈上弹出。栈帧所使用的内存不会被清理，但最终可能会被推到程序栈上的另一个栈帧覆盖。

> 动态分配的内存来自堆，堆向下“生长”。随着内存的分配和释放，堆中会布满碎片。尽管堆是向下生长的，但这只是个大体方向，实际上内存可能在堆上的任意位置分配。

栈帧由以下几种元素组成：

+ 返回地址：函数完成后要返回的程序内部地址
+ 局部数据存储：为局部变量分配的内存
+ 参数存储：为函数参数分配的内存
+ 栈指针和基指针：运行时系统用来管理栈的指针

> 栈指针通常指向栈顶部。基指针（帧指针）通常存在并指向栈帧内部的地址，比如返回地址，用来协助访问栈帧内部的元素。这两个指针都不是C指针，它们是运行时系统管理程序栈的地址。如果运行时系统用C实现，这些指针倒真是C指针。

> 系统在创建栈帧时，将参数以跟声明时相反的顺序推到帧上，通常，接下来会推入函数调用的返回地址，然后是局部变量。推入它们的顺序跟其在代码中列出的顺序相反。

比如

    #!c
    float average(int *arr, int size) {
      int sum;
      for (int i = 0; i < size; i++) {
        sum += arr[i];
      }
      return (sum * 1.0f) / size;
    }

+ 推入 stack frame 的顺序是：size，arr，return_address，sum，地址依次变小（因为 stack 是“向上”生长，栈的实际生长方向跟实现相关）
+ for 语句块中的 i 没有被包含到 stack frame 中。C 语言把语句块当成微型函数，在合适的时机将其推入栈或弹出栈
+ 精确的地址可能会变化，不过顺序一般不变。这一点很重要，因为它可以解释参数和变量内存分配的相对顺序
+ 将栈帧推到程序栈上时，系统可能会耗尽内存，这种情况称为栈溢出，通常会导致程序非正常终止
+ 要牢记每个线程通常都会有自己的程序栈。一个或多个线程访问内存中的同一个对象可能会导致冲突

### 通过指针传递和返回数据

好处：

+ 不用把对象声明为全局可访问，就可以让多个函数访问所引用的对象
+ 不需要复制对象

> 要在函数中修改数据，就要用指针传递数据。

> 传递参数（包括指针）时，传递的是它们的值。也就是说，传递给函数的是参数值的一个副本。当涉及大型数据结构时，传递参数的指针会更高效。

> 传递对象的指针意味着不需要复制对象，但可以通过指针访问对象。

#### 修改实参

必须用指针的形式，不能使用值传递的方式：

    #!c
    void swapWithPointers(int *pnum1, int *pnum2) {
      int tmp;
      tmp = *pnum1;
      *pnum1 = *pnum2;
      *pnum2 = tmp;
    }
    
    
    void swap(int num1, int num2) {
      int tmp;
      tmp = num1;
      num1 = num2;
      num2 = tmp;
    }
    
    int main() {
      int n1 = 5;
      int n2 = 10;
      // num1 和 num2 是实参 n1 和 n2 的副本，在 swap() 中修改形参 num1 和 num2 不会改变 n1 和 n2 的值 
      swap(n1, n2);
      // pnum1 和 pnum2 是实参 &n1 和 &n2 的副本，
      // 在 swapWithPointers() 中操作 *pnum1 和 *pnum2 实际就是在操作 n1 和 n2，因为是同一个地址
      swapWithPointers(&n1, &n2);
      return 0;
    }

#### 只读实参

如果希望参数对函数是只读的，那么就可以传递指向常量的指针：

    #!c
    void passingAddressOfConstants(const int *num1, int *num2) {
      *num2 = *num1;
    }

#### 返回指针

从函数返回指针可能的问题：

+ 返回未初始化的指针
+ 返回指向无效地址的指针
+ 返回局部变量的指针
+ 返回指针但是没有释放内存

#### 传递指针的指针

传递指针时，传递的是指针的 value。实际操作的是实参指针的副本，形参指针。如果想修改实参指针，就需要传递指针的指针。

### 函数指针

#### 声明

    #!c
    // 最右边的括号里面是被指向函数的形参表，此例子为空
    // 最左边是被指向函数的返回值，此例子为 void
    // 中间是变量的名称，此例子为 foo
    // * 表示本变量是一个指针变量
    // 如果去掉第一对括号，就变成了函数原型的声明，这个括号让这个声明变成了一个名为 foo 的函数指针，* 表示这是个指针
    void (*foo)();
    
    // 一些其他例子
    int (*f1)(double);  // 传入 double，返回 int
    void (*f2)(char*);  // 传入 char 指针，返回 void
    double *(*f3)(int, int);  // 传入两个 int，返回 double 指针
    
    // 注意区分下面两个
    int *f4();  // f4 是一个函数，传入 void，返回 int*
    int (*f5)();  // f5 是一个函数指针，传入 void，返回 int

#### 使用

+ 函数指针的 value 是被指向函数的地址
+ 函数名和数组名类似，保存的就是该对象的起始地址，所以可以直接把函数名赋值给函数指针，就像直接把数组名赋值给数据指针一样
+ 也可以对函数名/数组名取地址，但是没必要，编译器会忽略取地址符号
+ 一般为了方便，会为函数指针定义一个 typedef
+ 函数指针和其他类型一样，可以作为形参，也可以作为返回值
+ 函数指针和其他类型一样，可以作为数组的类型
+ 函数指针还可以参与比较运算
+ 不同类型的函数指针之间可以转化，类似于数据指针之间的转换
+ 函数指针不能和数据指针之间转换
+ 函数指针转换时不能用 `void *`，而应该用 `typedef void (*fptrBase)()`，即一个形参和返回值都为 void 的函数

!!!Warning
    使用函数指针时必须小心，因为 C 不会检查参数传递是否正确。

例子：

    #!c
    int square(int num) {
      return num * num;
    }
    
    // 声明函数指针
    int (*fptr)(int);
    
    // 使用函数指针
    // 方式1：直接把函数名赋值给函数指针
    fptr = square;
    // 方式2：取地址符号，没必要
    fptr = &square;
    
    int n = 5;
    printf("%d squared is %d\n", n, fptr(n));

    #！c
    // 定义 typedef 方便使用函数指针
    typedef int (*funcptr)(int);
    
    funcptr fptr2;
    fptr2 = square;
    printf("%d squared is %d\n", n, fptr2(n));

    #!c
    int add(int num1, int num2) {
      return num1 + num2;
    }
    
    int substract(int num1, int num2) {
      return num1 - num2;
    }
    
    typedef int (*fptrOperation)(int, int);
    
    // 函数指针作为形参
    int compute(fptrOperation operation, int num1, int num2) {
      return operation(num1, num2);
    }
    
    printf("%d\n", compute(add, 5, 6));
    printf("%d\n", compute(substract, 5, 6));

    #!c
    // 函数指针作为返回值
    fptrOperation select(char opcode) {
      switch(opcode) {
        case '+': return add;
        case '-': return substract;
      }
    }
    
    int evaluate(char opcode, int num1, int num2) {
      fptrOperation operation = select(opcode);
      return operation(num1, num2);
    }
    
    printf("%d\n", evaluate('+', 5, 6));
    printf("%d\n", evaluate('-', 5, 6));

    #!c
    // 函数指针数组:
    // 数组的名字为 operations，类型为 operation，数组的长度为 128，所有元素都被初始化为 NULL
    typedef int (*operation)(int, int);
    operation operations[128] = {NULL};
    
    // 不使用 typedef 的等效声明
    int (*operations[128])(int, int) = {NULL};
    
    // 数组长度为 128，下标和 ASCII 码的前 128 个字符对应，所以可以用下面的方式给数组的元素赋值
    operations['+'] = add;
    operations['-'] = substract;
    
    int evaluateArray(char opcode, int num1, int num2) {
      operation op;
      op = operations[opcode];
      return op(num1, num2);
    }
    
    printf("%d\n", evaluateArray('+', 5, 6));
    printf("%d\n", evaluateArray('-', 5, 6));

    #!c
    // 函数指针比较
    fptrOperation fptr = add;
    if (ptr == add) {
      printf("fptr points to add function\n");
    } else {
      printf("fptr does not point to add function\n");
    }

    #!c
    // 函数指针的转换
    typedef void (*fptrBase)();
    typedef int (*fptrToSingleInt)(int);
    typedef int (*fptrToTwoInts)(int, int);
    int add(int, int);
    
    fptrBase basePointer;
    fptrToSingleInt fptrFirst = add;
    basePointer = (fptrBase)fptrFirst;
    fptrFirst = (fptrToTwoInts)basePointer;
    
    printf("%d\n", fptrFirst(5, 6));

## 第四章 指针和数组

### 数组概述

> 数组是能用索引访问的同质元素连续集合。这里所说的连续是指数组的元素在内存中是相邻的，中间不存在空隙，而同质是指元素都是同一类型的。

> C99 标准引入了变长数组，在此之前，支持变长数组的技术是用realloc函数实现的。

> C 并没有强制规定边界，用无效的索引访问数组会造成不可预期的行为。

> 数组名字只是引用了一块内存。

> 对数组做 sizeof 操作会得到为该数组分配的字节数，要知道元素的数量，只需将数组长度除以元素长度

    #!c
    int vector[5];
    
    printf("%d\n", sizeof(vector)/sizeof(int));  // 5
    
    // 2 行 3 列
    int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};

### 指针表示法和数组

> 数组表示法和指针表示法在某种意义上可以互换。不过，它们并不完全相同。

> 单独使用数组名字时会返回数组地址。我们可以把地址赋给指针。

> 数组表示法可以理解为“偏移并解引用”，`vector[2]` 表示从 vector 开始，向右偏移 2 个位置，然后解引用这个位置获取其值，其中 vector 是指向数据开始位置的指针。

> 几种等价的写法：`&vector[10]` == `vecotr + 10` == `&pv[10]` == `pv + 10`。

数组和指针的差别：

    #!c
    int vector[5] = {1, 2, 3, 4, 5};
    int *pv = vecotr;

+ `vector[i]` 和 `*(pv + i)` 结果相同，但是生成的汇编代码不同，大部分情况下可忽略：`vector[i]` 的汇编是从 vector 开始移动 i 个位置，取出内容；`*(pv + i)` 的汇编是从 vector 地址开始，在地址上加 i 后取出该地址的值
+ sizeof 对数组和指针返回的结果不同：sizeof(vector) = 20，sizeof(pv) = 4
+ pv 是一个左值，左值可修改；vector 是个右值，不能修改

        #!c
        int vector[5] = {1, 2, 3, 4, 5};
        int *pv = vector;  // 把 vector[0] 的地址赋值给 pv，即 pv 指向 vector 的第一个元素，而不是数组本身
        int *pv = &vector[0];  // 和上面等价
        
        // 注意：返回的是整个数组的指针，pv 是个指针，指向的对象是 int [5]
        int *pv = &vecotr;
        
        *(pv + i) == pv[i];  // pv[i] 即对 pv 的 value 加上 i 之后，对新地址解引用返回被指向的对象的 value

### 传递一维数组

> 将一维数组作为参数传递给函数实际是通过值来传递数组的地址，这样信息传递就更高效，因为我们不需要传递整个数组，从而也就不需要在栈上分配内存。通常，这也意味着要传递数组长度，否则在函数看来，我们只有数组的地址而不知道其长度。

> 除非数组内部有信息告诉我们数组的边界，否则在传递数组时也需要传递长度信息。如果数组内存储的是字符串，我们可以依赖NUL字符来判断何时停止处理数组。一般来说，如果不知道数组长度，就无法处理其元素。

> 我们可以使用下面两种表示法中的一种在函数声明中声明数组：数组表示法和指针表示法。

    #!c
    // 方式一：数组表示法
    void display(int arr[], int size) {
      for (int i = 0; i < size; i++) {
        printf("%d\n", arr[i]);  // 等价于
        printf("%d\n", *(arr + i));
      }
    }
    
    int vector[5] = {1, 2, 3, 4, 5};
    display(vector, 5);
    
    // 方式二：指针表示法
    void display(int *arr, int size) {
      for (int i = 0; i < size; i++) {
        printf("%d\n", arr[i]);  // 等价于
        printf(%d\n", *(arr + i));
      }
    }

### 指针数组

指针数组：数组元素的类型为指针，即一系列的指针形成的数组。

    #!c
    int* arr[5];  // arr 是数组名，数组每个元素的类型为 int *，即 int 指针
    for (int i = 0; i < 5; i++) {
      arr[i] = (int*)malloc(sizeof(int));
      *arr[i] = i;
    }

### 指针和多维数组

    #!c
    int matrix[2][5] = {{1, 2, 3, 4, 5}, {6, 7,8, 9, 10}};
    // (*pmatrix) 表示 pmatrix 是一个指针，指向的对象类型是 int [5]，因为 pmatrix 本身就是指针（和数组等价），所以 pmatrix 指向的是二维数组，数组的第二维的大小是 5
    int (*pmatrix)[5] = matrix;
    print("%d\n", *(pmatrix + 1));  // 6
    // matrix[i][j] 表示第 i 行第 j 列个元素，地址为 matrix + i*sizeof(row) + j*sizeof(element)
    print("%d\n", matrix[0][1]);  // 2
    
    // pmatrix 是一个数组，数组长度为 5，元素类型为 int*
    int *pmatrix[5];

### 传递多维数组

多维数组作为函数参数时，在声明函数时需要决定两件事情：

+ 使用 数组表示法 or 指针表示法
+ 如何传递数组的形态，即数组的维度和每一维度的大小

例子：

    #!c
    // 两种方法都需要指定列数，因为编译器要知道每行的大小。多维数组，除了第一维，其他维度都需要指定大小
    // 数组表示法
    int display2DArray(int arr[][5], int rows);
    // 指针表示法
    int display2DArray(int (*arr)[5], int rows);
    // 调用示例
    display2DArray(matrix, 2);
    
    // 错误：语法合法，但是和预期效果不同，表示 arr 是个一维数组，数组长度是 5，元素类型是 int*
    int display2DArray(int *arr[5], int rows);

## 第五章 指针和字符串

### 字符串基础

> 字符串是以ASCII字符NUL结尾的字符序列。ASCII字符NUL表示为\0。字符串通常存储在数组或者从堆上分配的内存中。不过，并非所有的字符数组都是字符串，字符数组可能没有NUL字符。

> C中有两种类型的字符串：
>
> + 单字节字符串：由 `char` 数据类型组成的序列
> + 宽字节字符串：由 `wchar_t` 数据类型组成的序列。`wchar_t` 数据类型用来表示宽字符，要么是16位宽，要么是32位宽。主要用来支持非拉丁字符集。

> 字符串的长度是字符串中除了NUL字符之外的字符数。为字符串分配内存时，要记得为所有的字符再加上NUL字符分配足够的空间。

!!!Warning
    `NULL` 和 `NUL` 不同，`NULL` 用来表示特殊指针，通常定义为 `((void*)0)`，而 `NUL` 是一个 char，定义为 `\0`。两者不能混用。

> **字符常量**是单引号引起来的字符序列。字符常量通常由一个字符组成，也可以包含多个字符，比如转义字符。在C中，它们的类型是int。char的长度是1，而字符字面量的长度是4。这个看似异常的现象乃语言设计者有意为之。

#### 字符串声明

三种方式：

+ 字面量：双引号引起来的字符序列，通常用于初始化，位于字符串字面量池中
+ 字符数组：`char header[32]`
+ 字符指针：`char *header`

!!!Warning
    不要把**字符串字面量**和单引号引起来的字符搞混，后者是**字符字面量**。

#### 字符串字面量池

> 定义字面量时通常会将其分配在字面量池中，这个内存区域保存了组成字符串的字符序列。多次用到同一个字面量时，字面量池中通常只有一份副本。这样会减少应用程序占用的内存。通常认为字面量是不可变的，因此只有一份副本不会有什么问题。不过，认定只有一份副本或者字面量不可变不是一种好做法，大部分编译器有关闭字面量池的选项，一旦关闭，字面量可能生成多个副本，每个副本拥有自己的地址。

> 字符串字面量一般分配在只读内存中，所以是不可变的。字符串字面量在哪里使用，或者它是全局、静态或局部的都无关紧要，从这个角度讲，字符串字面量不存在作用域的概念。

#### 字符串初始化

> 初始化字符串采用的方法取决于变量是被声明为字符数组还是字符指针，字符串所用的内存要么是数组要么是指针指向的一块内存。

1. 字符数组

    + 用字符字面量初始化
    + 用 `strcpy` 函数初始化
    + 逐字符赋值

    !!!Warning
        不能把字符串字面量的地址赋值给数组名字，下面的例子是错误的。`char header2[]; header2 = "Media Player";`

    例子：
  
        #!c
        // 方法1 字符字面量：数组长度为 13，保持 12 个字符 + 结尾的 NUL
        char header[] = "Media Player";
        // 方法 2 strcpy 函数
        char header[13];
        strcpy(header, "Media Player");
        // 方法 3 逐字符赋值
        header[0] = 'M';
        header[1] = 'e';
        header[12] = '\0';

2. 字符指针

    + 用字符字面量初始化
    + 用 `strcpy` 函数初始化
    + 逐地址赋值

    例子:

        #!c
        // 注意要用 strlen 而不是 sizeof，另外要算上结尾符 NUL。strlen 返回字符串的长度，sizeof 返回数组/指针的长度
        char *header = (char*)malloc(strlen("Media Player")+1);
        // 方法 1 字符字面量
        char *header = "Media Player";
        // 方法 2 strcpy 函数
        strcpy(header, "Media Player");
        // 方法 3 逐地址赋值
        *(header + 0) = 'M';
        *(header + 1) = 'e';
        *(header + 12) = '\0';

字符串可以在内存中的多个位置：

    #!c
    // “Chapter” 在字符串字面量池中
    // 全局内存中开辟一个指针，指向字符串字面量池中的 "Chapter\0" 字符串
    char* globalHeader = "Chapter";
    // 全局内存中开辟了一块独立空间，保存的内容是 "Chapter\0"
    char globalArrayHeader[] = "Chapter";
    
    void displayHeader() {
      // 全局内存中开辟一个指针，指向字符串字面量池中的 "Chapter\0" 字符串
      static char* staticHeader = "Chapter";
      // stack 中开辟了一个指针，指向字符串字面量池中的 "Chapter\0" 字符串
      char* localHeader = "Chapter";
      // 全局内存中开辟了一块独立空间，保存的内容是 "Chapter\0"
      static char staticArrayHeader[] = "Chapter";
      // stack 中开辟了一块独立空间，保存的内容是 "Chapter\0"
      char localArrayHeader[] = "Chapter";
      // stack 中开辟了一个指针，指向 heap 空间的 "Chapter\0"
      char* heapHeader = (char*)malloc(strlen("Chapter")+1);
      strcpy(heapHeader, "Chapter");
    }

### 标准字符串操作

+ 比较 `int strcmp(const char *s1, const char *s2);`
+ 复制 `char* strcpy(char *s1, const char *s2);`
+ 拼接`char* strcat(char *s1, const char *s2);`

### 传递字符串

#### 参数声明

和字符串声明类似，声明字符串作为函数参数时也有两种选择：

+ char 数组

        #!c
        size_t stringLength(char string[]);

+ char 指针

    在参数列表中，把参数声明为char指针

        #!c
        // 字符串参数类型用 char* 声明
        size_t stringLength(char* string);

#### 传递参数

+ 参数声明方式不影响传参方式，参数用字符数组方式声明，也可以用字符指针传参
+ 如果需要保护传入的字符串，可以用 `const char* string` 来声明

例子：

    #!c
    char simpleArray[] = "simple string";
    char *simplePtr = (char*)malloc(strlen("simple string")+1);
    strcpy(simplePtr, "simple string");
    
    // 以数组方式传递
    // 方式 1：传递数组名（数组名和指针等效，指向第一个元素的地址）
    stringLength(simpleArray)
    // 方式 2：对数组名取地址，冗余且会有 warning
    stringLength(&simpleArray)
    // 方式3：对数组第一个元素取首地址，冗余
    stringLength(&simpleArray[0]));
    
    // 以指针方式调用，只需要传递指针名
    stringLength(simplePtr)

最典型的例子：给 main 传递参数：argc 表示参数的个数，argv 是个一维数组，数组元素类型为字符串指针，每个指针引用一个命令行参数。

    #!c
    int main(int argc, char** argv) {
        for (int i = 0; i < argc, i++) {
            printf("argv[%d] %s\n", i, argv[i]);
        }
    }
    
    // 可等价声明为
    int main(int argc, char *argv[]) {
    }

### 返回字符串

函数返回字符串，实际返回的是字符串的地址，所以需要关注的问题是如何返回合法的地址。可以返回以下三种对象之一：

+ 字面量
+ 动态分配的内存：被调函数 malloc，调用者 free
+ 局部字符串变量：可能会被破坏，避免这种用法

例子：

    #!c
    // 对象 1：字面量
    char returnALiteral() {
        return "Boston Processing Center";
    }
    
    // 对象 2：动态分配内存，blanks 动态申请，由调用者负责释放
    char* blanks(int number) {
        char* spaces = (char*)malloc(number+1);
        return spaces;
    }
    char *tmp = blanks(5);
    free(tmp);
    
    // 对象 3：局部字符串变量
    char* blanks(int number) {
        char spaces[32];
        return spaces;
    }

### 函数指针和字符串的例子

需求：

+ 写一个 sort 函数对字符串进行排序，排序算法不限
+ sort 排序比较字符串时有两种方式，直接比较 or 忽略大小写比较

实现：

+ 为每一种比较方式写一个函数，compare 和 compareIgnoreCase
+ sort 通过函数指针选择具体的比较方式，好处是只需要一份 sort 代码就可以实现任意排序方式，不需要硬编码具体的比较函数名
+ 字符串作为参数传递给 sort 和 compare，compareIgnoreCase 等函数

例子：

    #!c
    // 比较方式 1：直接比较
    int compare(const char* s1, const char* s2) {
        return strcmp(s1, s2);
    }
    // 比较方式 2：忽略大小写
    int compareIgnoreCase(const char* s1, const char* s2) {
        char* t1 = stringToLower(s1);
        char* t2 = stringToLower(s2);
        int result = strcmp(t1, t2);
        // stringToLower 中申请动态内存，调用者用完后主动释放，避免内存泄漏
        free(t1);
        free(t2);
        return result;
    }
    char *stringToLower(const char* string) {
        // 形参为 const，所以本地为变量申请空间，需要调用者负责释放
        char *tmp = (char*)malloc(strlen(string)+1);
        char *start = tmp;
        while (*string != 0) {
            *tmp++ = tolower(*string++);
        }
        *tmp = 0;
        return start;
    }
    
    // 申明函数指针
    typedef int (fptrOperation)(const char*, const char*);
    
    // 基于冒泡排序的 sort 函数
    void sort(char *array[], int size, fptrOperation operation) {
        int swap = 1;
        while (swap) {
            swap = 0;
            // 相邻字符串比较并排序
            for (int i = 0; i < size-1; i++) {
                if (operation(array[i], array[i+1]) > 0) {
                    // 一旦需要交换顺序，标记 swap 重新再遍历一遍所有字符串
                    swap = 1;
                    char *tmp = array[i];
                    array[i] = array[i+1];
                    array[i+1] = tmp;
                }
            }
        }
    }
    
    // 打印结果
    void displayNames(char* names[], int size) {
        for (int i = 0; i < size; i++) {
            printf("%s  ", names[i]);
        }
        printf("\n");
    }
    
    // 构造测试用例
    char *names[] = {"Bob", "Ted", "carol", "Alice", "alice"};
    // 测试 1
    sort(names, 5, compare);
    displayNames(names, 5);
    // 测试 2
    sort(names, 5, compareIgnoreCase);
    displayNames(names, 5);

## 第六章 指针和结构体

### 声明结构体

结构体有两种声明方式：

+ 简单声明

        #!c
        strcut _person {
            char *firstName;
            char *lastName;
            char *title;
            unsigned int age;
        }

+ 使用 typedef

        #!c
        typedef struct _person {
            char *firstName;
            char *lastName;
            char *title;
            unsigned int age;
        } Person; 

        // 直接例化
        Person person;
        person.firstName = (char*)malloc(strlen("Emily")+1);
        // 通过指针例化
        Person *ptrPerson;
        ptrPerson = (Person*)malloc(sizeof(Person));
        pterPerson->firstName = (char*)malloc(strlen("Emily")+1);

### 结构体对齐

> 为结构体分配内存时，分配的内存大小至少是各个字段的长度和。不过，实际长度通常会大于这个和，因为结构体的各字段之间可能会有填充。某些数据类型需要对齐到特定边界就会产生填充。
> 这些额外内存的分配意味着几个问题：
>
> + 要谨慎使用指针算术运算
> + 结构体数组的元素之间可能存在额外的内存

填充的气泡可能在结构体的内部，也可能在结构体的尾部。

### 释放结构体

!!!Warning
    C 语言中，系统不会自动为结构体内部的指针分配内存，类似的，结构体消失时，也不会自动释放结构体内部指针指向的内存。在 Person 例子中，用户必须自己初始化和释放 firstName, lastName，title。

例子：

    #!c
    void initializePerson(Person *person, const char *fn, const char *ln,
        const char *title, uint age) {
            person->firstName = (char*)malloc(strlen(fn)+1);
            strcpy(person->firstName, fn);
            person->lastName = (char*)malloc(strlen(ln)+1);
            strcpy(person->lastName, ln);
            person->title = (char*)malloc(strlen(title)+1);
            strcpy(person->title, title);
            person->age = age;
    }
    
    void deallocatePerson(Person *person) {
        free(person->firstName);
        free(person->lastName);
        free(person->title);
    }

### 避免 malloc/free 开销

> 重复分配然后释放结构体会产生一些开销，可能导致巨大的性能瓶颈。解决这个问题的一种办法是为分配的结构体单独维护一个表。当用户不再需要某个结构体实例时，将其返回结构体池中。当我们需要某个实例时，从结构体池中获取一个对象。如果池中没有可用的元素，我们就动态分配一个实例。这种方法高效地维护一个结构体池，能按需使用和重复使用内存。

    #!c
    #define LIST_SIZE 10
    
    // 用指针数组表示资源池，每个元素指向一块动态申请的内存，用来存放结构体
    Person *list[LIST_SIZE];
    
    // NULL 表示该位置没有被使用，可以被获取
    // 资源池一开始不动态申请，只有在需要才申请，一旦申请后就循环使用（get 和 return），
    // 循环使用时 get 和 return 不会再动态申请和释放。
    void initializeList() {
        for (int i = 0; i < LIST_SIZE; i++) {
            list[i] = NULL;
        }
    }
    
    // 返回第一个 NULL，如果都被占用，就临时分配一个空间
    Person *getPerson() {
        for (int i = 0; i < LIST_SIZE; i++) {
            if (list[i] != NULL) {
                Person *ptr = list[i];
                list[i] = NULL;
                return ptr;
        }
        Person *person = (Person*)malloc(sizeof(Person));
        return person;
    }
    
    // 将结构体返回给 list 中第一个 NULL 位置，如果资源池已满，就直接释放掉
    Person *returnPerson(Person *person) {
        for (int i = 0; i < LIST_SIZE; i++) {
            if (list[i] == NULL) {
                list[i] = person;
                return person;
            }
            deallocatePerson(person);
            free(person);
            return NULL;
    }
    
    // 使用示例
    initializeList();
    Person *ptrPerson;
    ptrPerson = getPerson();
    initializePerson(ptrPerson, "Ralph", "Fitsgerald", "Mr.", 35);
    displayPerson(*ptrPerson);
    returnPerson(ptrPerson);

这种方法的问题：list 长度固定，无法灵活适配变长的需求，可能会频繁申请或浪费空间。可以用更加复杂的管理策略来管理 list 的长度。

### 指针和结构体

> 指针可以为简单或复杂的数据结构提供更多的灵活性。这些灵活性可能来自动态内存分配，也可能来自切换指针引用的便利性。内存无需像数组那样是连续的，只要总的内存大小对就可以。

几种可以用指针实现的常用数据结构：

+ 链表
+ 队列：一般用链表实现
+ 栈：一般用链表实现
+ 树：基于链表，每个 node 有多个 next

## 第七章 安全问题和指针误用

> 因为C的某些特性，用C写安全的应用程序跟用其他语言有所不同。比如说，C不会阻止程序员越过数组边界写入，这样会导致内存损坏，也会引发安全风险。此外，误用指针通常也是很多安全问题的根本原因。

### 指针的声明和初始化问题

+ 不正确的指针声明

        #!c
        // ptr1 类型是 int*, ptr2 类型是 int
        int* ptr1, ptr2;
        // 正确写法
        int *ptr1, *ptr2;
        // 每个变量声明独占一行更好，或者用宏定义
        #define PINT int*
        PINT ptr1, ptr2;
        // 更好的方法是用 typedef
        typedef int* PINT;
        PINT ptr1, ptr2;

+ 使用前未初始化（野指针）

    处理野指针的 3 种方法：

    + 总是用 NULL 初始化指针
    + 用 assert 函数
    + 用第三方工具

### 指针的使用问题

> 很多安全问题聚焦的是缓冲区溢出的概念，覆写对象边界以外的内存就会导致缓冲区溢出。下面几种情况可能导致缓冲区溢出：
> + 访问数组元素时没有检查索引值
> + 对数组指针做指针算术运算时不够小心
> + 用gets这样的函数从标准输入读取字符串
> + 误用strcpy和strcat这样的函数。

+ 测试 NULL

    一定要检查 malloc 的返回值。

        #!c
        float *vector = malloc(20 * sizeof(float));
        if (vector == NULL) {
            // 分配失败
        } else {
            // 正常处理
        }

+ 错误使用解引用

        #!c
        // 正确，pi 指向 num
        // 星号把 pi 声明为指针，而不是解引用
        int num;
        int *pi = &num;
        // 错误，把 num 的地址赋值给 pi 指向的内存，但是 pi 还没有被初始化
        // 星号对 pi 解引用
        int num;
        int *pi;
        *pi = &num;

+ 迷途指针：引用已释放的空间
+ 越界访问数组
+ 错误计算数组长度

    将数组传递给函数时，一定要同时传递数组长度。这个信息帮助函数避免越过数组边界。不能简单依靠 NUL，因为外部传入的数组内容可能不正确。

        #!c
        // strcpy 允许缓冲区溢出，所以 name 中保存的是 8 个字符 Alexande，没有结尾的 NUL
        char name[8];
        strcpy(name, "Alexander");

+ 错误使用 sizeof

    试图检查指针边界但方法错误，sizeof 返回的是 byte 大小。
    
        #!c
        int buffer[20];
        // 错误，sizeof(buffer) 返回值为 20 * 4byte = 80
        for (int i = 0; i < sizeof(buffer); i++) {
        }
        // 正确
        for (int i = 0; i < sizeof(buffer)/sizeof(int); i++) {
        }

+ 一定要匹配指针类型
+ 有界指针（限制指针的有效区域）

    C 没有对有界指针提供直接支持，不过程序员可以显式地确保这个机制。

        #!c
        #define SIZE 32
        char names[SIZE];
        char *p = name;
        if (name != NULL) {
            if (p > name && p < name+SIZE) {
                // 有效
            } else {
                // 无效，错误分支
            }
        }

    C++ 智能指针提供了一种模仿指针同时支持边界检查的方法。

+ 字符串的安全问题

    + 如果使用strcpy和strcat这类字符串函数，稍不留神就会引发缓冲区溢出
    + gets函数从标准输入读取一个字符串，并把字符保存在目标缓冲区中，它可能会越过缓冲区的声明长度写入。如果字符串太长的话，就会发生缓冲区溢出

+ 指针算术运算和结构体

    只对数组使用指针算术运算，因为数组肯定分配在连续的内存块上。不应该将它们用在结构体内，因为结构体的字段可能分配在不连续的内存区域。

    !!!Warning
        即使结构体内部全部对齐，虽然通常分配在一起，但也有可能分配在离散地址上。更好的做法是不要用指针算术运算，而是将指针直接指向结构体的字段，最保险的做法是根本不用指针。

    例子：

        #!c
        typedef struct _item {
            int partNumber;
            int quantity;
            int binNumber;
        } Item;

        // 危险做法，通常不会出错，但不一定
        Item part = {12345, 35, 107};
        int *pi = part.partNumber;
        pi++;
        printf("Quantity: %d\n", *pi);

        // 更好的方法，不用指针运算
        pi = &part.quantity;
        printf("Quantity: %d\n", *pi);

        // 最好的做法，不用指针
        printf("Quantity: %d\n", part.quantity);

+ 函数指针的问题

    + 错误 1：只使用函数名，实际表示该函数的地址
    + 错误 2：函数和函数指针的签名不同，可以编译但是输出不确定

    例子：

        #!c
        int foo(int);

        // 错误 1：只有函数名时，表示函数地址，一般不会为 0，所以条件永远为真
        if (foo == 0) {
        }
        // 类似错误：省略了值的比较
        if (foo) {
        }
        // 正确
        if (foo()) {
        }

        // 错误 2：add 和 fptrCompute 签名不同，一个两个形参，一个三个形参
        int add(int, int, int);
        int (*fptrCompute)(int, int)

### 内存释放问题

+ 重复释放：释放后总是将其置为 NULL
+ 清除敏感数据：用完马上覆写，因为一般 OS 不会清零内存，会直接分配给别的程序

### 使用静态工具

+ 编译器 `-Wall`
+ 其他工具，提供比编译器更强的诊断功能

## 第八章 其他重要内容

### 指针类型转化

> 在指针与整数之间来回转换和在指针与void指针之间来回转换不同。

> 有时候容易将句柄和指针搞混。句柄是系统资源的引用，对资源的访问通过句柄实现。不过，句柄一般不提供对资源的直接访问，指针则包含了资源的地址。

### 别名、强别名和 restrict 关键字

#### 别名

别名：如果两个指针引用同一内存地址，我们称一个指针是另一个指针的别名。别名可以修改指向对象的 value，所以编译器无法优化，每次引用时必须执行机器级别的 ld 和 st，频繁 ld/st 会很低效。在某些情况下，编译器还必须关心操作执行的顺序。

### 强别名

强别名：不允许一种类型的指针成为另一种类型的指针的别名。需要关闭强别名的代码可能意味着差劲的内存访问实践，如果可能的话，花些时间解决这些问题，而不是关闭强别名。

!!!Warning
    + 编译器并非总能准确地报告别名相关的警告，有时候会漏报，有时候会虚报，最终还是要靠程序员定位别名问题。
    + 编译器总是假定char指针是任意对象的潜在别名，所以，大部分情况下可以安全地使用。不过，把其他数据类型的指针转换成char指针，再把char指针转换成其他数据类型的指针，则会导致未定义的行为，应该避免这么做。

#### restrict 关键字

> C编译器默认假设指针有别名，用restrict关键字可以在声明指针时告诉编译器这个指针没有别名，这样就允许编译器产生更高效的代码。很多情况下这是通过缓存指针实现的，不过要记住这只是个建议，编译器也可以选择不优化代码。如果用了别名，那么执行代码会导致未定义行为，编译器不会因为破坏强别名假设而提供任何警告信息。

> 新开发的代码应该尽量对指针声明使用restrict关键字，这样会产生更高效的代码，而修改已有代码可能就不划算了。

### 线程和指针

> 线程之间共享数据会引发一些问题。常见的问题是数据损坏。

> 指针是在另一个线程中引用数据的常见方式，很多时候会用互斥锁保护数据。

> 大家普遍认可的定义是如果一个线程的事件导致另一个线程的函数调用，就称为回调。将回调函数的指针传递给线程，而函数的某个事件会引发对回调函数的调用。

### 面向对象

> C不支持面向对象编程，不过，借助不透明指针，我们也可以使用C封装数据以及支持某种程度的多态行为。

> 不透明指针用来在C中实现数据封装。一种方法是在头文件中声明不包含任何实现细节的结构体，然后在实现文件中定义与数据结构的特定实现配合使用的函数。数据结构的用户可以看到声明和函数原型，但是实现会被隐藏（在．c/.obj文件中）。
>
> 只有使用数据结构所需的信息会对用户可见，如果太多的内部信息可见，用户可能会使用这些信息，从而产生依赖。一旦内部结构发生变化，用户的代码可能就会失效。

#### 不透明指针实例

需求：

+ 定义一个链表，实现对链表的封装
+ 链表支持 4 个操作，获取链表，删除链表，添加节点，删除头节点

链表在头文件中声明：

    #!c
    //link.h
    
    // Data 声明为 void*，这样允许处理任何类型的数据
    typedef void *Data;
    // 声明 typedef，但是结构体 _linkedList 的定义在 .c 文件中，对用户隐藏
    typedef struct _linkedList LinkedList;
    
    // 链表支持的 4 个操作
    // 1. 获取一个 LinkedList 实例
    LinkedList* getLinkedListInstance();
    // 2. 传入实例指针，删除链表实例
    void removeLinkedListInstance(LinkedList* list);
    // 3. 将 Data 插入到链表头部
    void addNode(LinkedList*, Data);
    // 4. 删除链表头结点
    Data removeNode(LinkedList*);

链表在源文件中实现：

+ 我们不允许用户看到链表内部结构以及使用链表内部结构，并且会对用户隐藏结构体的任何变化。
+ 只有四个支持函数的签名对用户是可见的，否则，用户就无法利用或修改实现细节。我们封装了链表结构及其支持函数，从而减轻了用户的负担。

代码：

    #!c
    // link.c
    
    #include <stdlib.h>
    #include "link.h"
    
    // 定义结点
    typedef struct _node {
        Data* data;
        struct _node* next;
    } Node;
    
    // 定义链表，只需要头指针
    struct _linkedList {
        Node* head;
    };
    
    // 4 个操作的实现
    
    LinkedList* getLinkedListInstance() {
        LinkedList* list = (LinkedList*)malloc(sizeof(LinkedList));
        list->head = NULL;
        return list;
    }
    
    void removeLinkedListInstance(LinkedList* list) {
        Node *tmp = list->head;
        while (tmp != NULL) {
            free(tmp->data);  // 潜在的内存泄露，解决方法：传递一个释放数据的成员函数
            Node *current = tmp;
            tmp = tmp->next;
            free(current);
        }
        free(list);
    }
    
    void addNode(LinkedList* list, Data data) {
        Node *node = (Node*)malloc(sizeof(Node));
        node->data = data;
        if (list->head == NULL) {
            list->head = node;
            node->next = NULL;
        } else {
            node->next = list->head;
            list->head = node;
        }
    }
    
    Data removeNode(LinedList* list) {
        if (list->head == NULL) {
            return NULL;
        } else {
            Node *tmp = list->head;
            Data *data = tmp->data;
            list->head = list->head->next;
            free(tmp);
            return data;
        }
    }

使用实例：用前面章节的 Person 结构体来创建并使用链表:

+ 我们只能在 link.c 文件中创建 _linkedList 结构体的实例，这是因为如果没有完整的结构体声明就无法使用 sizeof 操作符。比如说，如果你试图在 main 函数中为这个结构体分配内存，会得到一个语法错误。
+ 类型不完整是因为编译器看不到 link.c 文件中的实际定义。它只能看到 _linkedList 结构体的类型定义，而看不到结构体的实现细节。

        #!c
        #include "link.h"
        
        int main() {
            LinkedList* list = getLinkedListInstance();
            Person *person = (Person*)malloc(sizeof(Person));
            initializePerson(person, "Peter", "Underwood", "Manager", 36);
            addNode(list, person);
            person = (Person*)malloc(sizeof(Person));
            initializePerson(person, "Sue", "Stevenson", "Developer", 28);
            addNode(list, person);
            
            person = removeNode(list);
            displayPerson(person);
            person = removeNode(list);
            displayPerson(person);
            
            removeLinkedListInstance(list);
        }

### C 中的多态

> C++这类面向对象语言的多态是建立在基类及派生类之间继承关系的基础上的。C不支持继承，所以我们得模拟结构体之间的继承。

> 结构体的变量分配顺序对这种技术的工作原理影响很大。当我们创建一个派生类/结构体的实例时，会先分配基类/结构体的变量，然后分配派生类/结构体的变量。

!!!Important
    理解从类实例化来的对象如何分配内存是理解面向对象语言中继承和多态工作原理的关键。我们在C中使用这种技术时，这一点仍然适用。

> 当对一个类/结构体执行函数时，其行为取决于它所作用的对象是什么。比如说，对Shape调用打印函数就会显示一个Shape，对Rectangle调用打印函数就会显示Rectangle。在面向对象编程语言中这通常是通过虚表（或者VTable）实现的。

+ strcut 和 class 等效，可以包含数据和函数指针，函数指针相当于 class 的成员函数，只是 struct 没有访问保护，都是 public
+ 从 base struct 中派生出来的 struct 通过给函数指针赋值，实现重载，进而实现多态

## 读书感悟

+ 大量使用 struct 对变量进行封装
+ 大量使用（数据 + 函数）指针提供灵活的操作，而且可以简化代码
+ 大量使用 typedef 对类型进行重命名，以简化代码

