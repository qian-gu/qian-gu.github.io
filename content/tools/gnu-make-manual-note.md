Title: GNU Make Manual 笔记
Date: 2023-03-26 20:23
Category: Tools
Tags: Makefile, GNU Make
Author: Qian Gu
Slug: gnu-make-manual-note
Summary: 总结 Make 知识点，为中小工程写出专业的符合 GNU Make 惯例的 Makefile。

[TOC]

## GNU Make Notes

按照 GNU Make Manual 的章节顺序记录，一些基本且重要的点，可以覆盖日常使用，支撑中小项目使用，细节查 Manual。

### An Introduction to Makefiles

1. rule 的一般格式

        #!text
        <target> : <prerequisites>
                <recipe>

    术语：`target`, `prerequisites`， `recipe` 和 `rule`。

2. Make 的原理是检查 prerequisites 的时间戳是否比 target 的更新，如果是则执行 recipe。所以 Make 不限于编译程序，还可以用来做其他事情。但是 make 为编程特意提供了一些 implicit rules 和 variables，方便使用。

3. 如果没有指定 target 名称，默认情况下 make 以 Makefile 中第一个（不以 . 开头的）target 作为 `default goal`。

### Writing Makefiles

1. 一个 Makefile 中包含 5 部分：explicit rules，implicit rules，variable definitions，directives，comments

2. 默认情况下按照 `GNUmakefile`，`makefile`，`Makefile` 的顺序查找 makefile，推荐文件名为 `Makefile`，因为更醒目且通用。

3. 遇到 `include` 时会暂停读取当前文件，转而读取被 include 的文件，在读取 incldue 文件时 make 会尝试自动 rebuild 这个被 include 的文件。

4. 使用 include 的场景

    + 多个子程序由各自的 makefile 管理，这些 makefile 共享的规则可以单独放在一个文件里，被 include 使用（比如 systemc 的 examples）。
    + 自动生成的依赖文件单独存放，由主 makefile 通过 include 使用，这种方式比直接写到 makefile 的方式更整洁。

5. make 程序读取 makefile 的步骤分为两步：
    + 第一阶段：读取所有 makefile（包括 include），初始化变量，推导 implicit rules，所有的 target 和 prerequisites 建立一个依赖图
    + 第二阶段：判断哪个 target 是 goal，并判断 goal 是否需要更新，如果是的话，运行 recipe

6. variable 和 function 展开有两种方式：

    + 立即（immediate）展开：用 `:=` 定义，展开发生在第一阶段
    + 延后（deferred）展开：用 `=` 定义，展开发生在第二阶段
    + Conditional Directives 是立即展开的
    + 所有类型的 rule 都按照下面的规则展开

            #!make
            immediate : immediate ; deferred
                deferred

        即 target 和 prerequisites 是立即展开的，recipe 是延后展开的。

### Writing Rules

1. 第一个 rule 被当作 default goal，所以一般是 build 整个程序/多个程序的命令。

2. prerequisites 有两类，语法为 `target : normal-prerequisites | order-only-prerequisites`

      order-only prerequisites 的目标是满足一种特定场景：在 build target 前必须先build order-only prerequisites，但是 order-only prerequisites 的更新不触发 target 的更新。典型例子：编译文件放在 build 目录下，但是 build 目录在执行 make 时并不一定存在，同时 build 目录的更新不应该触发 target 的重新 build

        #!make
        OBJDIR := objdir
        OBJS := $(addprefix $(OBJDIR)/,foo.o bar.o baz.o)
        
        $(OBJDIR)/%.o : %.c
        $(COMPILE.c) $(OUTPUT_OPTION) $<
        
        all: $(OBJS)
        
        $(OBJS): | $(OBJDIR)
        
        $(OBJDIR):
            mkdir $(OBJDIR)

      !!!warning
          Manual 中的这个例子虽然可以工作，但是根据 Smith 的文章可以知道这种方式不是最优的，因为这种写法违反了规则 2：`$@` 和 `$<` 的 stem 应该完全一致。更推荐的写法是：在 build 目录下工作，并且通过 vpath 查找 src 文件的路径，此时 obj 和 src 的 stem 就可以做到相同。How?

3. 文件名可以用通配符 `*` 和 `%` ，文件名的展开时刻取决于出现的位置：

    + target 和 prerequisites 中的通配符由 make 在第一阶段展开
    + recipe 中的通配符由 shell 展开
    + 其他位置（variable 和 function）的通配符必须用 wildcard 函数展开

4. `VPATH` 和 `vpath` 都是为 target 和 prerequisites 搜索设计的，如果在当前目录下找不到 target/prerequisites 文件时，会从 VPATH/vpath 指定的目录中去寻找

    !!!warning
        vpath 只能对 make 的 target/prerequisites 起作用，无法传递给 makefile 中的 variables 或 functions。

            #!make
            srcs = $(wildcard *.c)
            vpath %.c src/

        只能查找当前路径下的 c 文件，无法匹配到 src/ 目录下的 c 文件。

5. 通过 VPATH/vpath 找到的文件是带完整路径的，因为写 recipe 时并不能确定搜索结果，所以必须使用自动变量 `$^` 或 `$<` 来表示搜索结果

        #!make
        VPATH = src:../headers
        
        foo.o : foo.c defs.h hack.h
            cc -c $(CLFAGS) $< -o $@

6. 强制 target（没有 prerequisites 且没有 recipe 的 target）作用和伪目标相同，推荐使用伪目标的方式

7. `empty target`（target 文件确实存在，但是内容为空）是 phony target 的变种，主要目的是用 target 的时间戳记录上次执行 recipe 的时间。

8. 一个 prerequisites 可以对应多个 target 文件（用空格分开），表示他们有相同的 prerequisites。如果想根据 prerequisites 根据 target 变化，则应该使用 static pattern rules。

9. 一个 target 也可以出现在多个 rule 中，对应多个 prerequisites。这种情况下所有 prerequisites 会被合并到一起，但是只能有一个 rule 提供 recipe，如果有多个，则使用最后一个 recipe 且打印错误信息。

    !!!note
        自动产生依赖时，makefile 中给出了 .d 文件的 recipe，同时生成的 .d 文件自身只给出 targt 和 prerequisites，但是没有 recipe，所以这种情况下，相当于给 .d 和 .o 文件添加了一些额外的 prerequisites，并不会引起错误。

10. `static pattern rule` 可构造 prerequisites 相似，但不相同的 rules，所以比 multiple target rule 更通用（“targets 必须具有相同的 prerequisites" 这个约束放松为 "targets 和 prerequisites 具有相同的 stem"）。

        #!make
        objects = foo.o bar.o
        
        all: $(objects)
        
        $(objects): %.o: %.c
            $(CC) -c $(CFLAGS) $< -o $@

    static pattern rule + filter 在大工程中很有用，可以对 target 中某一类型文件的 recipe 进行定义。比如 object 列表包含了所有目标文件，格式可能包含 .o 和 .elc，那么可以用静态模式 + filter 实现两类目标文件 recipe 的定义：

        #!make
        objs = foo.elc bar.o lose.o
        
        $(filter %.o, $(objs)): %.d: %.c
            $(cc) -c $(CFLAGS) $< -o $@
        
        $(filter %.elc, $(objs)): %.elc: %.el
            emacs -f batch-byte-compile $<

    实现对 .elc 和 .o 文件 recipe 的定义。

11. `implicit rule` 也可以实现和 static pattern rule 类似的功能，但是两者还是有区别的

    + static pattern rule 的作用范围是显式指定的，implicit rule 的作用范围是符合 rule 的所有 target
    + static pattern rule 更优的两种场景
        + 想对某些文件重载默认的 implicit rule
        + 不确定目录下是否存在某些文件满足隐含模式，从而产生不确定的影响，此时采用 static pattern rule 可以消除这种不确定性

    !!!note
        规则模式要求 target 和 prerequisites 的 stem 同名，所以如果编译结果放到 build 目录下，那么规则模式不适用，因为 target 的 stem 为 `xxx/foo.o` ，搜索不到对应的 prerequisite `xxx/build/foo.cpp`（源文件为 `xxx/src/foo.cpp`）

12. `double colon rules`（允许 target 出现在多个 rule 中，且每个 rule 有不同的 recipe）可以提供一种根据不同 prerequisite 执行不同 recipe 更新同一个 target 的机制，一般很少用到。

13. Manual 中给出了一种利用 include 自动 rebuild 的特性[自动维护依赖关系的方法][manual-automatic-prerequisites]，但是这个方法有 3 个缺点：

    + 效率问题：如果某个 .c 文件被修改了，因为 prerequisite(.c 文件) 时间戳更新且 rules 存在，所以对应的 .d 文件在 include 时每次都会 rebuild，但是 rebuild 这个 .d  文件并不是必须的，因为无论是否更新 .d 文件，.c 文件的修改都意味着 .o 文件必然要被更新
    + 烦人的 warning：如果新增了一个文件 or 第一次 build，因为不存在对应的 .d 文件，所以会报 warning
    + 如果重命名/删除了某个 prerequisite 文件（比如程序员在重命名/删除某个 .h 文件时忘记同步更新相关的 .c 文件），这个机制会出错。因为 .d 文件里面还记录着这个无效的依赖关系，此时只能手动删除所有相关的 .d 文件（这个错误应该是在更新 .o  文件时由 compiler 报错, 而不是由 make 报错）

    所以需要一个[更加健壮的自动生成 dependency 的方法][automatic-dependency]：

    + 解决第一个问题：.d 文件的更新实际上是为下次 make 准备的，只需要保证下次 make 时 dependency list 是最新的即可，所以 .o 和 .d 文件可以在同一个 rule 下更新
    + 解决第二个问题：用 wildcard 来匹配所有 .d 文件，避免不存在的文件 include 报错
    + 解决第三个问题：利用 make 处理 `rules without recipes or prerequisite` 的机制，修改 .d 文件的内容，把每个 prerequisite 文件都列为 target 即可

    这个方法依然有问题：如果用户在没有修改任何 .c 文件的前提下不小心删除了某个 .d 文件，那么修改 .h 文件并不会触发更新 .o 文件。解决方法：把 .d 作为 .o 的 prerequisites 的一部分，并且为其提供一个 empty rule 避免 rebuild。最终版本：

        #!makeile
        OBJDIR := obj
        
        DEPDIR := $(OBJDIR)/.deps
        DEPFLAGS = -MT $@ -MMD -MP -MF $(DEPDIR)/$*.d
        
        COMPILE.c = $(CC) $(DEPFLAGS) $(CFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -c
        
        $(OBJDIR)/%.o : %.c $(DEPDIR)/%.d | $(DEPDIR)
                $(COMPILE.c) $(OUTPUT_OPTION) $<
        
        $(DEPDIR): ; @mkdir -p $@
        
        DEPFILES := $(SRCS:%.c=$(DEPDIR)/%.d)
        $(DEPFILES):
        include $(wildcard $(DEPFILES))

[manual-automatic-prerequisites]: https://www.gnu.org/software/make/manual/make.html#Automatic-Prerequisites
[automatic-dependency]: https://make.mad-scientist.net/papers/advanced-auto-dependency-generation/

### Write Recipe in Rules

1. recipe 用 `@` 开头可以取消 echoing

2. recipe 的每一行都由一个新的 shell 子进程执行，同一行包含多个命令时，用分号 `;` 隔开组成一个完整的 shell 命令；如果想把完整的 shell 命令分成多行写，在行尾加反斜杠 `\` 进行连接。

3. make 使用 `/bin/sh` 作为默认 shell，不会继承环境变量设置的 shell，可以在 makefile 中通过变量 `SHELL` 进行指定

4. recipe 用减号开头，忽略此命令返回的失败值，比如 `-rm *.o`

5. 递归调用时，用 `$(MAKE)` 代替 `make`

6. 上层 makefile 可以通过 `export VARIABLE = value` 的方式把变量传递给子 makefile

### How to Use Variables

1. 除了 recipe 和用 `=` 或 `define` 定义的，其他形式的 variables 和 functions 都是在 makefile 被读取时（即第一阶段）展开的。

2. 传统做法是 variable 大写，但是 GNU make manual 推荐 makefile 内部使用的变量小写，只有控制 implicit rule 或用户可以通过命令行重载的变量大写。

3. 变量引用是一个严格的字符替换过程，shell 中的变量引用可以是 `$foo` 的形式，但是 makefile 必须是 `$(foo)` 或者 `${foo}`

4. 变量赋值有两种方式

    + 递归展开式变量：用 `=` 赋值，变量只有在被引用时才会递归展开。优点是可以先使用，后定义；缺点是展开时可能存在无限循环导致错误，另外一个缺点是如果变量中包含函数（如 wildcard）会在变量每次展开时都触发函数，导致执行速度变慢
    + 简单展开式变量：用 `:=` 或 `::=` 定义，变量在定义时被展开，即变量被定义后就是一个字符串，不包含其他任何变量的引用.优点是简化程序因为其行为和大部分编程语言中的变量类似。

5. 变量替换：`$(VAR:.A=.B)`

6. 引用未定义的变量时，会被当做空字符串。

7. 可以通过命令行对变量进行重载，使用 override 关键字可以让你修改用户通过命令行传进来的变量的值。应用场景例子：不管用户是否在命令行中有无指定，在 makefile 中确保包含 `-g` 选项 `override CFLAGS += -g`。

8. `target specific variables` 是只对特定 target 起作用的变量，语法 `<target>: <variable-assignment>`。

9. `pattern specific variables` 是只对特定 pattern 起作用的变量，语法 `<pattern>: <variable-assignment>`。

### Conditional Parts of Makefiles

1. 语法 `ifeq`, `ifneq`, `ifdef`, `ifndef`, `else`, `endif`。

### Functions for Transforming Text

1. 语法 `$(FUNCTION ARGUMENTS)` 只能调用 make built-in 函数，用户自定义函数只能通过 `call` 调用。

2. 字符替换相关函数

    + `$(subst from, to, text)`
    + `$(patsubst pattern, replacement, text)`
    + `$(strip string)` 去掉头尾空白符，合并中间空白符
    + `$(findstring find, in)`
    + `$(filter pattern..., text)`
    + `$(filter-out pattern..., text)`
    + `$(sort list)`
    + `$(word n, text)`
    + `$(wordlist s, e, text)`
    + `$(words text)`
    + `$(firstword names...)`
    + `$(lastword names...)`

3. 文件名相关函数

    + `$(dir names…)`
    + `$(notdir names…)`
    + `$(suffix names…)`
    + `$(basename names…)`
    + `$(addsuffix suffix,names…)`
    + `$(addprefix prefix,names…)`
    + `$(join list1,list2)`
    + `$(wildcard pattern)`
    + `$(realpath names…)`
    + `$(abspath names…)`

### How to Run make

1. 一些 GNU 的典型 PHONY target 名字：`all`, `clean`, `mostlyclean`, `distclean`, `realclean`, `clobber`, `install`, `print`, `shar`, `dist`, `TAGS`, `check`, `test`。

2. `-n` 参数：只打印但不执行 recipe

3. `-W` 参数配合 `-n`，查看修改某个文件带来的影响

4. `make -k` 忽略错误，继续编译，让一次编译过程多抛出一些错误

### Using Implicit Rules

1. 使用 `implicit rules` 的方法：rules 不包含 recipe，或者甚至不写 rules

2. 每个 implicit rule 包含一个 target pattern 和 prerequisite pattern

3. 多个 implicit rule 可能拥有相同的 target pattern，比如 .o 文件可以由 .c 或者是 .s 编译得到

4. 一般来说，make 会为没有 recipe 的 target 和 double-colon rule 自动搜索 implicit rule。

5. 作为 prerequisite 的文件会被当做没有 recipe 的 target 来对待

    !!!warning
        明确给出 prerequisite 并不会影响到 implicit rule 的搜索，比如 `foo.o: foo.p` 如果目录下存在 `foo.c` 那么会使用 foo.c 而非 foo.p 来编译出 foo.o，因为 .c 对应的 implicit rule 排在搜索结果的更前面。

7. 如果不想对某个 target 使用 implicit rule，那么使用空命令（recipe 是一个分号）

8. `$(LD)` 使用的 flag 有两种：`$(LDFLAGS)` 指向 `-L` 参数；`$(LDLIBS)` 指向 `-l` 参数。

9. `pattern rule` 和普通 rule 类似，但是 target 中包含 % 符号，用来匹配文件名模式。

10. pattern rule 中 target 和 prerequisite 的 stem 必须相同，但是 prerequisite 并不是必须包含 stem，比如 `%.o: define.h` 说明所有 .o 文件都依赖 define.h 这个头文件。

11. pattern rule 也可以有多个 target pattern（即这些 target 的 stem 相同，文件后缀名不同），这些 targets 会被当做整体来对待，一旦某个 target 被更新，其他 target 也被当做最新（即不更新），比如 `%.o, %.x: %.c` 用 make foo.o foo.x 执行后，只生成 foo.o 不生成 foo.x 而且提示 foo.x 已经是最新了（实际上 foo.x 不存在）。

12. implicit rule 就是 make 内置的 pattern rule，比如

        #!make
        %.o : %.c
            $(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

    所以用户可以用 pattern rule 的方式自定义一个 implicit rule。

14. 重载 implicit rule 的方法：使用 implicit rule 相同的 target 和 prerequisite，但是不同的 recipe；如果留空 recipe 就是屏蔽这个 implicit rule。

    注意下面两个的区别：
    
        #!make
        # using implicit rule by omitting recipe in common rule
        foo.o: foo.c
        
        # cancel implicit rule by omitting recipe in pattern rule
        %.o: %.c

13. pattern rule 因为要对文件名进行匹配，所以 recipe 中就不能写具体的文件名，而需要一个特殊的变量来表示，也就是 automatic variables，比如 `$@` `$^` `$<` `$?`。

### Makefile Conventions

1. 用 automake 可以帮助你写出符合 GNU makefile 规范的 makefile。

2. 每个 makefile 都要包含一行 `SHELL = /bin/sh`，避免从环境变量继承来的 SHELL 为其他值（对于 GNU make 来说不存在这个问题，GNU make 中的 SHELL 不会从环境变量继承）。

3. 明确指定你想要的 suffixs，避免不同 make 程序的 suffix 和 implicit rule 不兼容的问题

        #!make
        .SUFFIXES:
        .SUFFIXES: .c .o

4. 小心处理 recipe 中的路径。当需要处理指定目录的文件时，要明确给出路径，因为 `./` 指向的是 build 目录（GNU 惯例）而非 src 或其他目录。

5. configure 和 makefile 脚本中使用给定的工具。

6. dist target 中可以用 gzip。

7. 每个工具尽量用它的通用选项。

8. 尽量不要在 recipe 中创建软连接，因为有些操作系统不支持软连接。

9. 用内置变量调用编译器等工具，比如 `$(CC)` 表示 cc。

10. 如果确定只是用于某种特殊 OS，那么就可以使用其他工具，上述为了通用性做的约束可以放松。

11. 命令应该用变量来表示，比如 `$(CC)` ，这样可以方便用户修改相应变量就可以替换工具/选项。

12. 对于一般性工具，比如 ln，rm，mv 等则不需要为其定义变量，因为用户也没有替换为其他工具的需求。

13. 参数也应该用变量表示，变量的命名方式就是 `PROGRAM-NAME + FLAGS`，比如 `$(CFLAGS)`，`$(LDFLAGS)` 等。

14. 把 `$(CFLAGS)` 放在命令行的最后，以确保设置的 `$(CFLAGS)` 不会被其他变量重载。

15. 凡是调用 `$(CC)` 的地方都需要加上 `$(CFLAGS)`，包括编译和链接。

16. 每个 makefile 都要定义一个 `INSTALL` 变量，表示安装命令。

17. 每个 makefile 要定义两个变量 `INSTALL_PROGRAM`（默认值为 INSTALL）和 `INSTALL_DATA = $(INSTALL) -m 644` 作为程序和数据的安装命令，比如 `$(INSTALL_PROGRAM) foo $(bindir)/foo` 把 foo 安装到 `$(bindir)/foo`。

18. 安装目录也最好用一个变量 DESTDIR 定义，方便修改安装路径。比如

        #!shell
        # makefile recipe
        $(INSTALL_PROGRAM) foo $(DESTDIR)/$(bindir)/foo

        # shell command
        make DESTDIR=/tmp/stage install

19. `DESTDIR` 应该只用在 `install*` 和 `uninstalll*` target 中。

20. 不应该在 Makefile 中定义 `DESTDIR`，这样就可以安装到默认目录。

21. DESTDIR 在 package creation 中很常用，可以让用户指定安装目录（比如可能没有权限安装到默认目录），所以强烈推荐使用（但不强制）。

22. GNU 为安装定义了一系列标准 variable 和标准 target。

## Rules of Makefiles

GNU Make 目前的维护者 Paul Smith 的规则：

1. 使用 GNU make

    不要为写可移植的 makefile 而苦恼，而是使用可移植的 make 程序。

2. 每个非伪目标的 recipe 必须更新和 target 完全同名的文件

    也就是说每个 recipe 更新的文件是 `$@`，而不是 `../$@` 或 `$(notdir $@)` 等形式。

3. 在 CWD 下 build target 是最容易的方式

    VPATH 的用途是在 build 目录下定位 src 文件，而不是反过来在 src 目录下定位 object 文件。

4. 遵循 Least Repetition 原则

    用 variable，pattern rules，automatic variables 和 GNU make function 等技术避免重复写文件名。

5. 每个以 tab 开头的非连续行都是 recipe 的一部分，反之亦然

    每个不以 tab 开头的非连续行，都会按照 makefile 的语法解析。

6. 目录不应该作为 normal prerequisites 的一部分

    因为 GNU make 会把目录当成普通文件一样对待，所以如果目录新增/删除了文件就会产生不期望的
    rebuild，正确做法是把目录作为 order-only prerequisite。

## Makefile Tempalte

!!!info
    大项目使用 GNU autotool，本模板适用于中小项目。

目标：

+ 一份通用模板，可以快速适配到不同（中小）项目中
+ 自动提取所有源文件和依赖
+ 自动化编译
  + 任何源文件被修改，自动编译
  + 任何头文件被修改，自动编译包含该头文件的源文件
  + 自动链接更新后的目标文件

```make
############################### Customise #####################################
CURDIR := $(shell pwd)
src_dir := $(CURDIR)/src
inc_dir := $(CURDIR)/include
build_dir := $(CURDIR)/build
target := out

############################### Variables #####################################

CXX := g++
CXXFLAGS := -g -Wall -O3 -I$(inc_dir)
LDFLAGS ?=
LDLIBS ?=

depdir := $(build_dir)/.deps
DEPFLAGS = -MT $@ -MMD -MP -MF $(depdir)/$*.d

COMPILE.c = $(CXX) $(DEPFLAGS) $(CXXFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -c

srcs := $(foreach dir, $(src_dir), $(wildcard $(dir)/*.cpp))
objs := $(addprefix $(build_dir)/, $(addsuffix .o, $(notdir $(basename $(srcs)))))

vpath %.cpp $(src_dir)
vpath %.h $(inc_dir)

############################### Rules #########################################

.PHONY: all rebuild clean

all: $(build_dir)/$(target)

rebuild: clean all

$(build_dir)/$(target): $(objs)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(LDLIBS) $^ -o $@

$(build_dir)/%.o: %.cpp $(depdir)/%.d | $(depdir)
	$(COMPILE.c) $(OUTPUT_OPTION) $<

$(depdir): ; @mkdir -p $@

DEPFILES := $(addprefix $(depdir)/, $(addsuffix .d, $(notdir $(basename $(srcs)))))
$(DEPFILES):
include $(wildcard $(DEPFILES))

clean:
	rm -rf $(build_dir)
```

模板说明：

+ 使用小写定义简单展开式变量，指定项目的路径（根目录，src 目录列表，include 目录列表）
+ 使用 vpath 指定头文件和源文件的搜索目录
+ 使用 order-only prerequisite 自动创建 build 目录，保持项目目录整洁
+ 因为 .o 和 .cpp 分别在 build 和 src 子目录下，无法使用 implicit rule（要求两者的 stem 必须一样），所以明确写 pattern rule

## Reference

1. 最重要的、最全面的、最权威的自然是[官方手册][GNU make manual]
2. GNU Make 当前维护者 Paul Smith 的[文章][Smith]
3. 陈浩大神写的教程[跟我学 Makefile][how-to-write-makefile]，大概就是 manual 的中文简化版
3. 一份比较全面的 [Makefile Coding Style Guide][coding-style-guide]


[GNU make manual]: https://www.gnu.org/software/make/manual/html_node/index.html
[how-to-write-makefile]: https://seisman.github.io/how-to-write-makefile/
[Smith]: https://make.mad-scientist.net/papers/
[coding-style-guide]: https://clarkgrubb.com/makefile-style-guide
