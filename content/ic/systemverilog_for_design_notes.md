Title: 《SystemVerilog for Design》笔记
Date: 2021-01-22 19:21
Category: IC
Tags: SystemVerilog
Slug: systemverilog_for_design_notes
Author: Qian Gu
Summary: 读书笔记

!!! note
    1. 本书假定读者已经掌握了 Verilog，主要内容是从对比角度介绍 SV 如何让设计者在更高层次对硬件进行建模，如何更高效地进行开发
    2. 笔记只记录了可综合的语法特性，略去了不可综合的部分

## Chapter 1 Introduction to SystemVerilog

Verilog 的标准：

+ Verilog-1995 (`IEEE Std 1364-1995`)
+ Verilog-2001 (`IEEE Std 1364-2001`)
+ Verilog-2005 (`IEEE Std 1364-2005`)

SV 的标准：

+ IEEE Std 1800-2005
+ IEEE Std 1800-2009（合并 IEEE 1364-2005 和 IEEE 1800-2005）
+ IEEE Std 1800-2012

## Chapter 2 SystemVerilog Declration Spaces

Verilog 中的 `wire`, `reg`, `task`, `function` 只能声明在 `module` 内部，这样做的缺点就是：同一个 taks、function 要在多个 module 中进行重复声明，不仅增加工作量，还可能导致多个相同功能的副本不对齐的错误。

### Package

`package` 可以解决上述问题，在其内部可以声明的有，

+ `parameter`, `localparam`
+ `const`
+ `typedef`
+ `taks`（必须是 `automatic`）
+ `function`（必须是 `automatic`）
+ `import`

要在其他 module 中引用 package 中的声明，可以有 4 种方式：

| 方式 | 限制 |
| ---- | ---- |
| 用 `::` 直接引用 | 多次使用时每次都要写完成路径，繁琐 |
| 通过 `import <name>` 明确导入 | 如果要导入多个，依然繁琐 |
| 通过 `import *` 通配符导入 | 实际上是把 package 加入到搜索路径中，优先级最低，端口上依然要通过作用域符号引用 |
| 导入到 `$unit` 中使用 | 可以去掉端口上的作用域符号，缺点见下文 |

task 和 function 必须带上 automatic，而且不能包含静态变量，这是因为例化的每个 task/function 必须都有自己独立完整的一套资源，相互之间不能共享。同理，package 中也不能定义变量（logic/wire/reg），它们是不可综合的。

### $unit

SV 定义了一个 compilaton unit scope 的概念（即在 module、package 之外的区域，类似于 C 语言中的全局变量），可以存放一些独立于 package、module，interface 的声明：

+ variable
+ net
+ constant
+ typedef, enum, class
+ task, function

!!! warning
    $unit 不是全局的，只对那些与其同时编译的源文件可见。每次编译的时候会产生一个专属于这次编译的特定的 compilation unit scope，如果几个文件分开编译，就可能产生某些信号不可见的情况，这是**非常危险**的！直接在 $unit 中做声明是非常不好的习惯，会产生混乱的代码，维护、复用、debug 都非常困难。

SV 标识符的搜索策略： 本地声明 > 通配符导入的声明 > $unit 中的声明 > hierarchy 中的声明，完全向后兼容 Verilog 的搜索策略。

!!! note
    所有的标识符和类型定义必须先声明后使用。

如果一个标识符没有定义就使用，那么 Verilog 会自动隐式地将其声明为 net 类型（一般来说就是 `wire`），而且编译不会报错，所以可能会导致很微妙的错误：

```
#!verilog
module m1();
    assign sig = ...; // a is a local net
endmoule

reg sig;

module m2():
    assign b = sig; // sig is previous $unit variable
endmoule
```
总之，把 package 导入到 $unit 中会遇到很多问题：

1. 对文件编译顺序有要求
2. 多个文件分多次编译和同时一次性编译的效果不同
3. 可以通过条件编译的方式解决，但仍然需要注意很多细节

### summary

!!! 本章小结
    + 不要在 $unit 中做任何声明，所有的声明都应该放在有名字的 package 中
    + 在必要时可以把 package 导入到 $unit 中（比如某些 module/interface 中包含了定义在 package 中的自定义类型）
    + **不推荐使用 $unit，应该用 package 来规避相应风险。**

## Chapter 3 SystemVerilog Literal Values and Built-in Data Types

### Literal assigments

Verilog 中赋值全 1 的方法是不可扩展的（line 8），只能通过一些小技巧来实现（line 9～10）：

```
#!verilog
parameter SIZE = 32;
reg [SIZE-1 : 0] data;

assign data = '0;
assign data = 'bz;
assign data = 'bx;

assign data = 32'hFFFF_FFFF;
assign data = ~0;
assign data = -1;
```

SV 新增语法可以实现可扩展的赋值：

```
#!verilog
assign data = '0;
assign data = '1;
assign data = 'z;
assign data = 'x;
```

### variable

SV 中对一个信号的定义包含两部分：

+ `type`：一共有两种，定义了信号是 net 还是 varibale
+ `data type`：一共有两种，定义了信号是 2-state 还是 4-state

| type | example |
| ----- | ---- |
| varible | `var`, `reg` |
| net | `wire`, `wor`, `wand` |

| data type | example |
| -------- | ----- |
| 2-state | `bit`, `byte`, `int` ... |
| 4-state | `logic` |

`logic` 实际上并不是 `type`，而是 `data type`，表示信号取值是 4-state。只使用 logic 会自动推断出一个 variable，所以它可以和 `var` 配合起来，显式地定义。从语法上来说，logic 和 reg 等价，但是它不会像 reg 一样模糊不清。而 net 类型必须是 4-state data type，所以它也可以和 logic 配合显式定义。

    #!verilog
    var  logic [31:0] addr; // 32-bit varible
    wire logic [31:0] data; // 32-bit net

`bit` 同 logic 一样，它并不是 `type`，而是 `data type`，表示信号取值是 2-state。只使用 bit 会自动推断出一个 variable，所以它也可以和 var 配合起来显式定义。

    #!verilog
    var bit [31:0] addr;

基本上 variable 可以替代所有的 reg 和 wire，它可以出现在 `always_comb`, `always_ff`, `assign` 这些地方。但是有一条限制：

**variable 不能被多个源驱动。**

这个限制可以帮助我们避免设计中的 bug，因为绝大部分设计中信号都应该只有一个驱动源。

### signed and unsigned

SV 中的 `byte`, `shortint`, `int`, `longint` 默认是 signed 类型，可以通过显式的方式声明为 unsigned 类型，需要注意的是声明时 singed/unsigned 关键字只能放在 type 关键字的后面。

```
#!verilog
int s_int;  // signed 32-bit varibale
int unsigned u_int;  // unsigned 32-bit variable
```

### static and automatic variable

Verilog-1995 中所有的 varibale 都是 static 类型的，因为它们都是用来对硬件建模的，所以天然就是 static 类型。到了 Verilog-2001，task 和 function 中的 variable 可以声明成 automatic 类型，意味着这个 variable 的存储空间是由工具自动动态分配的，不再使用时会自动释放空间。automatic 类型主要是用来做验证或者是总线的功能模型。它有个作用是在多次调用的 task 中，以使得在前一个 task 没有结束时可以进行下一次调用。

### type casting

Verilog 只能在 assign 时进行类型转化，或者是调用系统函数 signed/unsigned。SV 新增的类型转化可以直接在表达式中进行，不需要 assign 语句。SV 的类型转化分为两种：

+ static(compile time) cast 静态转换是可综合的，发生在编译阶段，而且不会检查转化后取值是否正确，所以一定要小心处理！

        #!verilog
        // type casting： <type>'(<expression>)
        7 + int'(2.0 * 3.0)  // cas result of (2.0 * 3.0) to int, then add 7

        // size casting： <size>'(<expression>)
        logic [15:0] a, b, y;
        y = a + b**16'(2)      // cast literal value 2 to be 16-bits wide

        // sign casting： <sign>'(<expression>)
        shortint a, b;
        int y;
        y = y - signed'({a,b});  // cast concat result to a signed value

+ dynamic(run time) cast 动态转化（系统函数 $cast），是不可综合的

!!! 本章小结
    + 声明只包含 data type（`logic`, `bit`），没有 type 时，默认推断出 varibale
    + 关键字 `var` 是可选的，并不会影响综合和仿真行为，只是增加代码可读性
    + 只有 `var` 没有 data type 时，默认是 logic 类型
    + net 类型（`wire`）取值只能是 `logic` 类型（声明时 logic 可以选）
    + `bit`, `byte`, `int` 等虽然是 data type，但是只能和 var 搭配，所以也可以看成是 type
    + 可综合的设计，只使用 `logic`
    + automatic 主要是仿真用，设计时的 automatic 只有定义在 package 中的 task/function 使用
    + 小心使用 static cast

## Chapter 4 SystemVerilog User-Defined and Enumerated Types

SV 支持用户自定义数据类型，可以在保持准确性和可综合的前提下，让用户可以写出数量更少、可读性更好的语句在更高层次上对硬件进行建模。

### user-defined types

typedef 可以根据需要定义在 module、package、$unit 中，一般来说，为了提高代码可读性，自定义类型的名称以 `_t` 结尾。

```
#!verilog
typedef int unsigned unit;
uint a, b;

typedef logic [3:0] nibble;
nibble [7:0] data;  // a 32-bit vector made from 8 nibble types
```

### enumerated types

verilog 中没有枚举类型，设计 FSM 时只能通过 parameter 或者是 define 的形式实现。SV 新增的枚举类型可以实现相同功能，代码可读性更好。

```
#!systemverilog
enum {red, green, blue} RGB;  // variable can have the values of red, green, blue
enum {WAIT, LOAD, STORE} State, NextState;
```

如果 label 很多，而且都很有规律，一个一个写出来非常繁琐，SV 还提供了两种定义 label 序列的方法：

    #!systemverilog
    enum {RESET, S[5], W[6:9]} state;  // state = RESET, S0, S1, ...S5, W6, ... W9

显然，在同一个作用域内 label 必须是独一无二的，否则会发生冲突。

    #!systemverilog
    // Error
    module FSM (...);
        enum {GO, STOP} fsm1_state;
        enum {WAIT, GO, DONE} fsm2_state;

    // Ok
    module FSM (...);
        always @(posedge clk) begin: fsm1
            enum {STOP, Go} fsm1_state;
            end

    always @(posedge clk) begin: fsm2
        enum {WAIT, GO, DONE} fsm2_state;
    end

enumerate 数据类型默认是 int 类型（32-bit 的 2-state 类型），list 中的第一个 label 的值为 0, 第二个为 1, 依次类推，每个 label 会根据前面的取值自动 +1，所以没必要把每个 label 的取值都显式地写出来。但是不同 label 的取值必须不同。

    #!systemverilog
    enum {A=1, B, C, X=24, Y, Z} list1;  // B=2, C=3, Y=25, Z=26
    enum {A=1, B, C, D=1} list2;  // Error

enumerate 的类型也可以用户自定义，如果给 label 赋值则必须位宽匹配，否则会报错；如果 label 的数量超过了类型可以取值的数量也会报错；给 4-state 类型的 label 赋值了 x/z，那么下一个 label 必须显式赋值。

    #!systemverilog
    enum bit {TRUE, FALSE} Boolean;  // 1-bit wide, 2-state
    enum logic [1:0] {WAITE, LOAD, READY} state;  // 2-bit wide, 4-state

    enum logic [2:0] {WAITE = 3'b001, LOAD = 3'b010, READY = 3'b100} state;

    enum {WAITE = 3'b001, LOAD=3'b010, READY=3'b100} state;  // Error!

    enum logic {A=1'b0, B, C} list;  // Error: too many labels for 1-bit size

    enum logic [1:0] {WAIT, ERR=2'bxx, LOAD, READY} state;  // Error!

enum 和 typedef 配合使用时，叫做 typed enumerated type，用 import 时只会导入 type name，并不会导入 label，所有 label 必须显式导入，或者通过通配符导入。

    #!systemverilog
    package chip_types;
        typedef enum {WAIT, LOAD, STORE} states_t;
    endpackage
        
    // Error
    module chip(...);
        import chip_types::states_t;  // import the typedef name only
    
        states_t state, next_state;
        always_ff @(posedge clk or negedge rst_n)
            if (!rst_n)
                state <= WAIT;  // ERROR: WAIT has not been imported!
            else
                state <= next_state;

    // Ok
    import chip_types::WAIT;  // method 1
    import chip_types::*;  // method 2

大部分的 Verilog/SV 的 var 都是宽松类型，基本上任何类型的任何值都可以赋值给一个 var，在赋值时会根据规则自动转换成 var 对定的类型。enum 类型则是个 semi-strong type，只能用对应的 label、同类型的另外一个 enum、通过 cast 转换成对应 enum 类型的变量赋值。

    #!systemverilog
    typedef enum {WAIT, LOAD, READY} states_t;
    states_t state, next_state;
    int foo;

    state = next_state;  // legal
    foo = state + 1;     // legal, booth is `int` type
    state = foo + 1;     // Error: illegal
    state = state + 1;   // Error: illegal
    state++;             // Error: illegal
    next_state += state; // Error: illegal

### summary

!!! 本章小结
    + typedef 可以提高代码可读性，命名使用 `_t` 结尾
    + enum 是 semi-strong type，可以提高设计的安全，import 时注意 label 的导入

## Chapter 5 Systemverilog Arrays, Structures and Unions

### struct

Verilog 中没有机制表示一组相关信号，只能通过信号前缀的方式来表示，SV 新增了类似 C 中的 structure，structure 内可以是任何类型的 variable，包括用户自定义的类型。

```
#!systemverilog
struct {
    int           a, b;      // 32-bit variable
    opcode_t      opcode;    // user-defined type
    logic [31:0]  address;   // 24-bit variable
    bit           error;     // 1-bit 2-state var
} instruction_word;

instruction_word.address = 24'hF000001E;
```
strcut 可以是一组 var 也可以是一组 net，前面可以加上可选的 `var` 或 `wire`, `bit` 等，因为 net 本身要求是 4-state 类型，所以声明 net struct 时内部的所有成员也都必须是 4-state 的类型。虽然 struct 作为整体是可以声明为 net，但是 net 类型本身并不能作为 struct 内部的成员。可以用 `interface` 来实现同样的效果。

    #!systemverilog
    var struct {
        logic [31:0]  a, b;
        logic [ 7:0]  opcode;
        logic [23:0]  address;
    }  instruction_word_var;

    wire struct {
        logic [31:0]  a, b;
        logic [ 7:0]  opcode;
        logic [23:0]  address;
    }  instruction_word_net;

struct 可以和 typedef 配合使用，没有 typedef 的 struct 叫做匿名 struct。struct 可以声明在 module 或 interface 内部使用，也可以定义在 package 中或 $unit 中供多个 module 使用。一般来说 struct 都是和 typedef 一起定义在 package 中，因为大多数情况下我们定一个 struct 的目的是为了在多个地方复用，比如在模块端口之间传递等。

    #!systemverilog
    typedef struct {            // structure definition
        logic [31:0]  a, b;
        logic [ 7:0]  opcode;
        logic [23:0]  address;
    }  instruction_word_t;

    instruction_word_t IW;  // structure allocation

struct 和 array 很类似，它们的不同之处和 C 语言中的类似：

+ array 是一组同类型、同宽度的信号，strcut 内的信号可以是不同类型、不同宽度
+ array 中的信号通过下标来引用，strcut 中的信号通过名字来引用

struct 可以用 `.` 给每个成员单独赋值，也可以给整个 struct 赋值，但是两种方式不能混用。

    #!systemverilog
    typedef struct {
        logic [31:0]  a, b;
        logic [ 7:0]  opcode;
        logic [23:0]  address;
    }  instruction_word_t;

    instruction_word_t IW;

    assign IW = '{100, 5, 8'hFF, 0};                      // legal
    assign IW = '{address:0, opcode:8'hFF, a:100, b:5};   // legal
    assign IW = '{address:0, 8'hFF, 100, 5};              // illegal

struct 默认是 unpacked 模式，即内部的成员是相互独立的，标准并不规定工具如何处理这些成员的存储关系；也可以声明成 packed 模式，packed strcut 内部的成员按照声明顺序存储，规则为：第一个元素在 MSB，依次类推。packed strcut 内部的成员可以通过名字来引用，也可以直接通过下标来引用。

    #!systemverilog
    struct packed {
        logic         valid;
        logic [ 7:0]  tag;
        logic [31:0]  data;
    } data_word;

    data_word.tag = 8'hF0;
    data_word[39:32] = 8'hF0;

上面定义的 data_word 的存储格式如下：

```
#!text
+--------------+--------------+
| valid | tag  | data         |
+--------------+--------------+
   40    39  32 31           0
```

packed struct 存储时是按照 vector 处理的，所以对它的操作也和 vector 相同，可以对其进行数学运算、逻辑操作等。

    #!systemverilog
    typedef struct packed {
        logic         valid;
        logic [ 7:0]  tag;
        logic [31:0]  data;
    } data_word_t;

    data_word_t packet_in, packet_out;
    always @(posedge clk)
        packet_out <= packet_in << 2;

packed struct 还可以声明成 signed/unsigned 类型，主要会影响到其作为一个整体以 vector 类型参与数学运算和比较运算时的行为，但不会影响到内部成员的 signed/unsigned 的类型，每个成员仍然基于成员本身的声明类型。从 packed struct 中截取出的一部分永远是 unsigned 类型，这和 verilog 是一致的。

    #!systemverilog
    typedef struct packed signed {
        logic                valid;
        logic        [ 7:0]  tag;
        logic signed [31:0]  data;
    } data_word_t;

    data_word_t A, B;
    always @(posedge clk)
        if (A < B)          // signed comparison
            ...

module、interface、task/function 的端口也可以声明为 struct 类型：首先必须用 typedef 将其声明为用户自定义类型。

    #!systemverilog
    package definitions;

        typedef enum {ADD, SUB, MULT, DIV} opcode_t;

        typedef struct {
            logic  [31:0]  a, b;
            opcode_t       opcode;
            logic  [23:0]  address;
            logic          error;
        } instruction_word_t;

    endpackage

    module alu (
        input definitions::instruction_word_t  IW,
        input wire                             clk);

            ...

    endmodule

!!! warning
    unpacked struct 作为模块端口进行连接时，这两个模块的 strcut 类型必须是同一类型。即使两个模块各自定义了一套完全相同的匿名 struct，它们仍然是不同类型。所以必须用 typedef 将其声明为用户自定义类型才可以。

### union

SV 中也新增了类似 C 语言的 union，其声明方法和赋值方法和 struct 类似。

```
#!systemverilog
union {
    int i;
    int unsigned u;
} data;

data.i = -5;
data.u = -5;
```
union 也可以和 struct 一样用 typedef 声明成用户自定义类型，如果没有 typedef 则是匿名 union。

+ **unpacked union 是不可综合的**

+ packed union 要求所有成员的 bit 位宽必须一致，所以 **packed union 是可综合的**。packed union 只能存储整数类型的数据，它可以按照一种类型写入，用另外一种类型读出，硬件模型不需要做任何特殊处理来保存数据是如何存储的，因为所有成员的位宽都相同

    下面这个例子说明了 packed union 的两种表现方式：要么是一个 packed struct 方式的数据包，要么是一个数组

        #!systemverilog
        typedef struct packed {
            logic [15:0] source_addr;
            logic [15:0] dst_addr;
            logic [31:0] data;
            logic [7:0] opcode;
        } data_packet_t;

        union packed {
            data_packet_t     packet;  // packed structure
            logic [7:0][7:0]  bytes;   // packed array
        } dreg;

    这两种方式的存储格式如下所示。

        #!text
        +-------------+----------+------+--------+
        | source_addr | dst_addr | data | opcode |
        +-------------+----------+------+--------+
         63            47         31     7      0

        +----------+----------+----------+----------+----------+----------+----------+----------+
        | bytes[7] | bytes[6] | bytes[5] | bytes[4] | bytes[3] | bytes[2] | bytes[1] | bytes[0] |
        +----------+----------+----------+----------+----------+----------+----------+----------+
         63         55         47         39         31         23         15         7        0

一个 struct 和 union 的应用实例：

    #!systemverilog
    package definitions;

        typedef enum {ADD, SUB, MULT, DIV, SL, SR} opcode_t;

        typedef enum {UNSIGNED, SIGNED} operand_types_t;

        typedef union packed {
            logic        [31:0] u_data;
            logic singed [31:0] s_data;
        } data_t;

        typedef struct packed {
            opcode_t         opc;
            operand_types_t  op_type;
            data_t           op_a;
            data_t           op_b;
        } instr_t;

    endpackage

    import definitions::*;

    module alu (
        input instr_t IW,
        output data_t alu_out);

        always @(IW)
            if (IW.op_type == SIGNED)
                case (IW.opc)
                    ADD: alu.s_data = IW.op_a.s_data + IW.op_b.s_data;
                    // ...
                endcase
            else
                case (IW.opc)
                    ADD: alu.u_data = IW.op_a.u_data + IW.op_b.u_data;
                    // ...
                endcase
    endmodule

### array

**unpacked array**：

Verilog 中的 array 一次只能访问一个元素，或者是一个元素的一个切片，操作多个元素会报错。

    #!verilog
    integer i [7:0][3:0][7:0];

    integer j;

    j = i[3][0][1];  // legal: select 1 element
    j = i[3][0];     // illegal: selects 8 elements

这种 array 在 sv 中叫做 unpacked array，array 中的元素是分开存储的，标准并不会规定工具如何存储。相对于 Verilog，SV 的增强之处在于可以声明任何类型的 array，包括用户自定义的类型，而且可以引用 array 整体或者是一个 slice，从而实现复制 array，需要注意的是，复制时等号两端的 array 维度和类型必须一致。

    #!systemverilog
    typedef enum {Mo, Tu, We, Th, Fr, Sa, Su} Week;
    Week Year [1:52];

    int a1 [7:0][1023:0];
    int a2 [8:1][1:1024];

    a2 = a1;        // legal, copy an entire array
    a2[3] = a1[0];  // legal, copye a slice of an array

SV 还支持简化版的 array 定义，就像 C 语言一样，只需要定义 array 的大小即可，但是这种写法不能用在 vector(packed arry) 中。

    #!systemverilog
    logic  [31:0] data [1024];    // legal, equal to next line
    logic  [31:0] data [0:1023];

    logic [32] d;   // illegal vector declaration

**packed array**：

Verilog 中把位宽范围放在标识符前面的声明叫做 vector，把位宽范围放在标识符后面的声明叫做 array。SV 的叫法稍微不同，而且扩展了 packed array 使其可以声明成多维数组。

+ vector = packed array
+ array = unpacked array

```
#!systemverilog
wire [3:0] select;      // 4-bit packed array
reg [63:0] data;        // 64-bit packed array
logic [3:0][7:0] data;  // 2-D packed array: 4 8-bit sub-arrays
```

SV 定义了 packed array 的存储方式：像 vector 一样整个 array 必须连续存储，packed array 内部的每个维度都是 vector 的一个字段。上面例子中二维数组存储方式如下所示，这是协议规定的，和仿真器、编译器、操作系统、平台无关。

```
#!text
+--------------+--------------+--------------+--------------+
| data[3][7:0] | data[2][7:0] | data[1][7:0] | data[0][7:0] |
+--------------+--------------+--------------+--------------+
 31          24 23          16 15           8 7            0
```

packed array 只能用下面元素组成，

+ bit-wise 类型：logic、bit、reg
+ packed array, packed struct, packed union
+ 任何 net 类型：wire

```
#!systemverilog
typedef struct packed {
    logic [ 7:0] crc;
    logic [63:0] data;
} data_word;

data_word [7:0] darray; // 1-D packed array of packed structures
```

packed array 可以按照一个元素、一部分 bit、一个 slice 的粒度访问：

```
#!systemverilog
logic [3:0] [7:0] data;  // 2-D packed array

wire [31:] out = data;              // whole array

wire sign = data[3][7];             // bit-select

wire [3:0] nib = data[0][3:0];      // part-select

byte high_byte;
assign high_byte = data[3];         // 8-bit slice

logic [15:0] word;
assign word = data[1:0];            // 2 slices
```

因为 packed array 是按照 vector 存储的，所以所有 Verilog 中对 vector 的操作对 packed array 也是合法的，包括：

+ bit 选择
+ 部分选择
+ 数据拼接
+ 数学操作
+ 关系操作
+ bit-wise 操作
+ 逻辑操作

如果位宽不匹配，packed array 会被自动截断/扩展成符号左边的位宽，这个规则和 Verilog 是一致的。

packed 和 unpacked 都很灵活，那么什么时候应该用什么类型的 array 呢？

| 类型 | 用途 |
| ---- | ---- |
| unpacked array | <ul><li>元素是 unpacked 类型的 struct，union，以及其他非 bit-wise 的类型</li><li>一次访问一整个元素的 array，比如 RAM/ROM</li></ul> |
| packed array | <ul><li>多个 1-bit 类型的信号组成的 vector（verilog 的用法）</li><li>可能访问 sub-field 的 vector</li></ul> |

关于赋值，

+ packed array 赋值可以像 verilog 里面的 vector 赋值一样

        #!systemverilog
        logic [1:0][1:0][7:0] a;  // 3-D packed arraay

        a[1][1][0] = 1'b0;    // assign to one bit
        a = 32'hF1A3C5E7;     // assign to full array
        a[1][0][3:0] = 4'hF;  // assign to a part select
        a[0] = 16'hFACE;      // assign to a slice
        a = {16'bz, 16'b0};   // assign concatenation

+ unpacked array 可以用 SV 的新语法赋值

    其中 `'{}` 表明内部是一个 list，通过前面的单引号和 Vrilog 的拼接操作符区分，而且 `'{}`、`'{n{}}` 和 verilog 中的 `{}`、`{n{}}` 不同，后者内部需要明确每个元素的位宽，前者位宽声明是可选的。

        #!systemverilog
        byte a [0:3][0:3];
        a[1][0] = 8'h5;                // assign to one element
        a = '{4'{7, 3, 0, 5}};         // assign a list to the full array
        a[3] = '{'hF, 'hA, 'hC, 'hE};  // assign a list to slice of array

当 packed 和 unpacked 多维数组嵌套在一起时，数组的下标寻址规则如下：

+ 首先寻址 unpacked array，从左到右的顺序
+ 其次寻址 packed array，也是从左到右的顺序

![indexing](/images/systemverilog_for_design_notes/indexing.png)

用户自定义类型也可以用来组成 array，形成复合数据类型。

```
#!systemverilog
typedef int unsigned uint;
unit u_array [0:127];       // array of user types

typedef logic [3:0] nibble;
nibble [31:0] big_word;     // packed array, is equalitent to
logic [31:0] [3:0] big_word;

typedef nibble nib_array [0:3];
nib_array compound_array [0:7];         // is equalitent to
logic [3:0] compound_array [0:7][0:3];
```

Verilog 只允许 1-D 的 packed array 作为模块端口、task/function 参数，而 SV 允许任何类型的任何 array 作为端口。

```
#!systemverilog
module CPU (...);
    ...
    logic [7:0] lookup_table [0:255];

    lookup i1 (.LUT(lookup_table));
    ...
endmodule

module lookup (output logic [7:0] LUT [0:255]);
    ...
endmodule
```

struct 和 union 也可以作为 array 的元素，需要注意的是 packed array 的元素也必须是 packed 类型。同理 array 也可以作为 struct/union 的元素，packed struct/union 的元素也必须是 packed 类型。

```
#!systemverilog
typedef struct paced {
    logic [31:0] a;
    logic [ 7:0] b;
} packet_t;

packet_t [23:0] packet_array;  // packed array of 24 structures

typedef struct {
    int a;
    real b;
} data_t;

data_t data_array [23:0];  // unpacked array of 24 structures

struct packed {              // packed structure
    logic parity;
    logic [3:0][7:0] data;   // packed array
} data_word;

struct {                     // unpacked structure
    logic data_ready;
    logic [7:0] data [0:3];  // unpacked array
} packet_t;
```

### foreach

有时候需要迭代处理 array 中的每个元素，一般都是通过 for 循环来处理，但是如果有很多个 for 循环或者是 array 的维度较多，则需要声明很多个 index，为了避免这一繁琐的声明，SV 新增了一种语法 `foreach` 来自动迭代，设计者不需要再手动声明每个 index 变量了。

```
#!systemverilog
int sum [1:8][1:3];

foreach (sum[i, j])
    sum[i][j] = i +j;

function [15:0] gen_crc (logic [15:0][7:0] d);
    foreach (gen_crc[i]) gen_crc[i] = ^d[i];
endfunction
```

上面这个例子中：

+ i, j 不需要声明，直接使用
+ i, j 用逗号隔开，和维度的映射规则和前面说的嵌套 array 寻址相同，所以上例中 i 指向外层循环、j 指向内层循环
+ 如果想跳过某一维度，可以用两个逗号跳过，如果是在尾部，直接不写出来即可
+ 这些循环变量是自动生成的、只读、只对循环内部可见

### array system function

大部分系统函数都是不可综合的，但是下面这些和 array 相关的系统函数是例外，它们是可综合的：

| 函数 | 功能 |
| ----- | ---- |
| $dimensions(array_name) | 返回 array 的维度 |
| $left(array_name, dimension) | 返回 array 特定维度的 msb |
| $right(array_name, dimension) | 返回 array 特定维度的 lsb |
| $low(array_name, dimension) | 返回 array 特定维度的最低位索引 |
| $high(array_name, dimension) | 返回 array 特定维度的最高位索引 |
| $size(array_name, dimension) | 返回 array 特定维度元素总数 $high - $low + 1 |
| $increasement(array_name, dimension) | 如果 $left >= $right 返回 1，否则返回 0 |
| $bits(expression) | 返回 expression 的总 bit 数（expression 的位宽是静态不变的，所以可综合）|

### dynamic arrays, associative arrays, sparse arrays, strings

这些都是不可综合的。

### summary

!!! 本章小结
    + unpacked/packed struct 都是可综合的
    + struct 可以作为端口在 module、interface、task/function 之间连接
    + 只有 packed union 是可综合的，unpacked union 是不可综合的
    + array 及其赋值是可综合的，包括
        + array 声明：packed/unpacked 都是可综合的，维度可以是任意数
        + array 赋值：给单个元素、部分 bit 位、单个元素的 part-select、array slice、整个 array 赋值，default 关键字也是可综合的
        + array 复制：packed-to-packed、相同 layout 的 unpacked-to-unpacked 都是可综合的
        + struct/union 中的 array 也是可综合的，其中 union 必须是 packed，所以其内部的 array 也必须是 packed
        + struct/union 组成的 array 也是可综合的
        + array 作为模块端口是可综合的


## Chapter 6 Systemverilog Procedural Blocks, Tasks and Functions

Verilog 中的 `always` 块的用法很多，既可以对硬件建模写可综合的代码，可以在仿真中建模写不可综合的代码，所以有很多各种各样的规则，这对设计者、工具都提出了很高的要求，SV 通过新增语法解决了这些问题:

+ always_comb
+ always_ff
+ always_latch

### awalys_comb

顾名思义，组合逻辑专用。和普通的 always 相比其好处是：

+ 不需要再写出敏感列表，不会有漏掉信号的 bug
+ 要求赋值语句的左侧信号不能在其他地方赋值，防止不符合组合逻辑的行为
+ 工具不需要再推测设计意图
+ `always_comb` 比 `always @*` 更好，因为 `always @*` 在有函数调用时推断出来的敏感列表可能不完整

```
#!systemverilog
always @* begin             // infers @(data)
    a1 = data << 1;
    b1 = decode();
end

always_comb begin           // infers @(data, sel, c, d, e)
    a2 = data << 1;
    b2 = decode();
end

function decode;        // function with no inputs
    begin
        case (sel)
            2'b01:   decode = d | e;
            2'b10:   decode = d & e;
            default: decode = c;
        endcase
    end
endfunction
```

### always_latch

和 always_comb 一样也不需要写出敏感列表，只是工具会自动推断出 latch，所以检查规则也略有变化。

```
#!systemverilog
always_latch
    if (en) q <= d;
```

### always_ff

同理，always_ff 用来对触发器进行建模，设计者必须提供敏感列表，而且每个信号前面必须有前缀 posedge 或者是 negedge。

```
#!systemverilog
always_ff @(posedge clk, negedge rst_n)
    if (!rst_n)
        q <= 0;
    else
        q <= d;
```

### task/function

SV 对 task/function 也做了一些增强，主要包括下面几点：

+ 不再强制要求 `begin ... end`，会自动推断出来

        #!systemverilog
        function states_t NextState (states_t State);
            NextState = State;
            case (State)
                WAITE: if (start) NextState = LOAD;
                LOAD:  if (done)  NextState = STORE;
                STORE:            NextState = WAITE;
            endcase
        endfunction

+ Verilog 中的 function 名字本身就是一个变量，返回值就是对同名变量赋值，最后一次给函数名所赋的值就是返回值。SV 新增了 return 语句，而且 return 语句的优先级高于同名变量，即如果有 return 语句，可以把同名变量当成一个临时变量来用

        #!systemverilog
        function int add_and_inc (input int a, b);
            return a + b + 1;
        endfunction

        function int add_and_inc (input int a, b);
            add_and_inc = a + b;
            return ++add_and_inc;
        endfunction

+ 新增的 void function 可以不必有返回值，可以像普通语句一样调用，就像 task 一样

        #!systemverilog
        typedef struct {
            logic        valid;
            logic [ 7:0] check;
            logic [63:0] data;
        } packet_t;

        function void fill_packet (
            input  logic [63:0] data_in,
            output packet_t     data_out );

            data_out.data = data_in;
            for (int i=0; i<=7; i++)
                data_out.check[i] = ^data_in[8*i +: 8];
            data_out.valid = 1;
        endfunction

+ Verilog 只运行按位置传参，错误的传参顺序可能导致错误；SV 新增了按名传参，可以减少犯错的机会

        #!systemverilog
        always @(posedge clk)
            restult <= divide(.denominator(b), .numerator(a));

+ Verilog 中的 function 只能有 input 参数，唯一的 output 参数就是函数名；SV 为 function 新增了 output 参数。为了保证可综合性，带 output 的 function 不能出现在连续赋值语句中

+ Verilog 要求 function 至少有一个参数，即使内部不会用到这个参数；SV 允许 function 不带参数，前面 always_comb 有个实例

+ Verilog 要求每个参数都必须有 input/output 表明方向；SV 简化了语法，参数默认的方向是 input，除非明确声明了方向，后续的参数都是这个方向。同时 SV 默认参数是 logic 类型

        #!systemverilog
        function int compare (int a, b);
            ...
        endfunction

        task mytask (a, b, output y1, y2);
            ...
        endtask

+ SV 还允许 funciton 参数有默认值，这样调用时如果不涉及，可以不传递这个参数

        #!systemverilog
        function int incrementer(int cout=0, step=1);
            incrementer = count + step;
        endfunction

        always @(posedge clk)
            result <= incrementer(data_bus);

+ struct、union、array 都可以作为 function 的参数

### summary

!!! 本章小结
    + `always_comb`, `always_latch`, `always_ff` 都是可综合的，用它们取代 `always` 增强设计
    + 用 void function 代替 tasks，提高设计的安全性

## Chapter 7 Systemverilog Procedural Statements

SV 新增了一些新语法和新的操作符，可以让设计者写出更加精简的可综合 RTL 代码。

### new operators

**自增/自减操作符： `++`, `--`**

类似 C 语言，赋值和自增/自减有先后之分。因为 SV 中有阻塞/非阻塞两种赋值方式，`++` 和 `--` 的行为和阻塞赋值是一样的。

!!! warning
    不要在非阻塞赋值中使用自增/自减操作符。也就是说它们只能用来对组合逻辑进行建模，不能用在时序逻辑中。（例外情况：类似 for 循环下标这种用法，不是真正的信号）

```
#!systemverilog
for(i=0; i<=32; i++) begin
    ...
end

// post-increment
while (i++ < LIMIT) begin: loop1
    ...     // last value of i will be LIMIT
end

// pre-increment
while (++j < LIMIT) begin: loop2
    ...     // last value of j will be LIMIT-1
end

// act as blocking assignment, following two statements are equivalent
i++;
i = i + 1;
```

**赋值操作符**

以 `+=` 为例，

```
#!systemverilog
out += in;       // is equalitent to
out = out + in;
```

除了加法，`=` 还可以和其他操作符结合，所有新增赋值操作汇总如下。

`+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`, `<<<=`, `>>>=`。

所有的赋值操作符的行为也和阻塞赋值一样，所以和自增/自减一样，只能用在组合逻辑建模中。

**带 don't care 的等价操作符**

Verilog 中有两种等价操作符 `==` 和 `===`，SV 新增的操作符 `==?` ，它们的区别在于对 x/z 的判断。

+ `==`：只要任何一个操作数带 x/z，返回结果是 1'bx
+ `===`：bit-wise 比较，要求 1, 0, x, z 精确匹配，完全一样才返回 1‘b1，否则返回 1'b0 |
+ `==?`：右操作数中的 x/z 当成是通配符，和左操作数对应 bit 的任何值都匹配
+ `!=?`：对 `==?` 取反

!!! note
    1. 如果左右位宽不匹配，会在比较前做位宽扩展，扩展规则和逻辑比较 `==` 的规则相同
    2. `==?` 和 `!=?` 可综合的前提是右操作数是常数，即不能是可变化的信号值。

**判断是否存在 inside**

类似于 Python 中的 `in` 效果。`inside` 是可综合的，但是很多综合工具可能并不支持。

```
#!systemverilog
logic [2:0] a;
if (a inside {3'b001, 3'b010, 3'b100})

// equalitent
if ( (a == 3'b001) || (a == 3'b010) || (3 == 3'b100))

// the set of values can be an array
int d_array [0:1023];
if (13 inside {d_array})    // test if value 13 occurs anywhere in array d_array
```

### for loops

Verilog 中 for 循环的 index 变量必须声明在循环外部，如果一个模块中有多个 for 循环，而且要保证名字相互之间不同，或者把声明放到 always 块中，这时候可以重名。

SV 做了一下增强：

+ 可以在 for 循环中定义局部变量，不同 for 循环的局部变量可以重名

        #!systemverilog
        always_ff @(posedge clk)
            for (bit [4:0] i = 0; i <= 15; i++)

        always_ff @(posedge clk)
            for (int i = 0; i <= 1024; i++)

    需要注意的是，这种变量是 automatic 类型，而 automatic 类型的变量有以下限制：

    + automatic 变量不能在外部访问
    + automatic 变量无法 dump 到 VCD 文件中

    所以 for 循环外部是无法访问这写变量的，如果一定要访问，那么就要挪到 for 外部定义。

+ 一次可以声明多个变量，和 C 语言类似

        #!systemverilog
        for (int i=1, j=0; i*j < 128; i++, j+=3)

        for (int i=1, byte j=0; i*j < 128; i++, j+=3)

### do...while loop

`do...while` 和 `while` 一样，在某些限制条件（这些条件是要能让综合器可以静态地判断循环次数，和 for 类似）下是可综合的，一般来说 RTL 中机会不会使用这两种语法，略。

### foreach

见 Chapter 5 中关于 array 部分。

### jump statements

SV 新增的 `break`, `continue`, `return` 都是可综合的，规则和 `disable` 一样。（一般很少用）

```
#!systemverilog
// continue example
logic [15:0] array [0:255];
always_comb begin
    for (int i = 0; i <= 255; i++) begin: loop
        if (array[i] == 0)
            continue;   // skip empty elements
        transform_function(array[i]);
    end
end

// break example
always_comb begin
    first_bit = 0;
    for (int i=0; i<=63; i=i+1) begin
        if (i < start_range) continue;
        if (i > end_range)   break;
        if (data[i]) begin
            first_bit = i;
            break;
        end
    end
end

// return example
task add_up_to_max (input  [ 5:0] max,
                    output [63:0] result);
    result = 1;
    if (max == 0) return;
    for (int i=1; i<=63; i=i+1) begin
        result = result + result;
        if (i == max) return;
    end
endtask
```

### block names

当有多层 begin...end 嵌套时，即使有缩进，有时候也很那找到 end 对应的 begin，SV 支持给 end 后面也加上 name，这个特性对综合没有任何影响，只是为了提高代码可读性。

!!! warning
    end 后面的名字必须和匹配的 begin 名字相同，否则会报错。

```
#!systemverilog
begin: <block name>
    ...
end
```

### statement label

SV 还支持给单个语句加上 label，就和 begin...end 块一样，不过语法是类似 C 语言的风格。给语句加上 label 的好处很多，

+ 提高代码可读性
+ 方便文档/其他地方引用具体语句
+ 帮助 debug 工具和 coverage 工具分析

begin...end 块也是一个 statement，所以也可以给它加上 label。

!!! warning
    begin...end 块不能同时使用 label 和 block name。

```
#!systemverilog
// <label> : <statement>

always_comb begin
    decoder: case (opcode)
        ...
    endcase
end

// named block
begin: block1
    ...
end: block1

// labeled block
block2: begin
            ...
        end
```

### case statement

Verilog 标准特意规定了 case 语句的选择必须是按照顺序来评估，所以暗含着优先级。会得到类似 if-else-if 的效果。如果设计本身没有优先级时，综合工具要做特别的处理，把优先级逻辑优化掉。

SV 为此特意定义了两个描述符来限定 case 语句：

+ `unique case` 表示无优先级的 case，它要求表达式和 case item 之间必须是一一映射的关系，表达式必须能且只能匹配一个 item，否则会报错。unique case 和 always_comb 配合使用，这两个特性带来的额外检查可以提高 RTL 的综合结果符合设计意图。

        #!systemverilog
        unique case (<case_expression>)
            ... // case items
        endcase

+ `priority case` 表示有优先级的 case，它要求表达式至少要匹配一项 item，如果有多项匹配时，选择对一个匹配项。使用这个限定符表示设计者是有意这么做的，有多个匹配项也符合设计意图。有时候即使使用了 priority，如果 case item 本身是不可能同时匹配，那么综合工具也会自动把优先逻辑优化掉。

        #!systemverilog
        priority case (<case_expression>)
            ... // case items
        endcase

Verilog 中定义了两个 program 来帮助综合工具，

+ `parallel_case`：告诉综合工具去掉优先级逻辑，所有分支是并行同级关系
+ `full_case`：未使用到的 expression value 是无关紧要的，可优化掉这部分逻辑

所以 unique case 实际上就相当于同时使能了 full_case 和 parallel_case，而 priority case 相当于只使能了 full_case。但是使用这两个新语法比 program 更健壮，可以减少风险。

### if...else

unique 和 priority 也可以用来限定 if-else 语句。仿真工具会按照我们书写顺序来评估每个条件，综合工具也会产生优先级逻辑来保持和仿真的一致性，但是通常，我们书写顺序并不是真正想要的效果。

+ `unique if...else` 表明设计者并不关心优先级，综合工具可以把优先级逻辑优化掉。

        #!systemverilog
        logic [2:0]  sel;
        always_comb begin
            unique if (sel == 3'b001) mux_out = a;
              else if (sel == 3'b010) mux_out = b;
              else if (sel == 3'b100) mux_out = c;
        end

+ `priority if...else` 表明设计者关心优先级，所以工具要保留优先级逻辑。

### summary

!!! summary
    + `++` 和 `--` 都是可综合的，但是工具支持并不好，为了健壮性，避免使用这两个操作符
    + 新增的赋值操作符是可综合的，有些综合工具对部分操作符有限制，为了健壮性，避免使用这些赋值操作符
    + `==?` 和 `!=?` 可综合的前提是右操作数是常数
    + 增强性 for 循环也是可综合的，和 Verilog 中的 for 规则相同
    + `do...while` 在某些条件下是可综合的，避免使用
    + `break`, `continue`, `return` 都是可综合的，避免使用
    + `unique`  和 `priority` 都是可综合的，可以提高设计的健壮性

## Chapter 8 Modeling Finite State Machine with Systemverilog

使用前面 7 章介绍的新特性，使用 FSM 对一个交通灯控制系统建模的例子。和传统 Verilog 相比，有以下特点：

+ 统一使用 `logic` 代替 `reg`/`wire`
+ 使用 `always_comb` 和 `always_ff` 代替通用 `always`
+ begin...end 加了 name
+ 使用 enum 类型描述所有状态
    + 明确类型为 `logic`（默认是 `int`，32-bit 2-state）
    + 明确给出 label 的取值（方便控制编码类型，比如 one-hot, one-cold, binary 等）
    + enum 变量只能用 label 赋值，不要用数字给 enum 变量赋值，也不要给部分 bit 赋值
+ 使用 `unique case` 代替普通 case
    + 如果是 one-hot 编码，可以调换 case expression 和 case selection items 的位置，某些综合工具下面积更优

```
#!systemverilog
module traffic_light (output logic green_light,
                                   yellow_light,
                                   red_light,
                      input        sensor,
                      input [15:0] green_downcnt,
                                   yellow_downcnt,
                      input        clock, resetN);

    enum {R_BIT = 0,
          G_BIT = 1,
          Y_BIT = 2} state_bit;

    enum logic [2:0] {RED    = 3'b001 << R_BIT,   // explicit enum definition
                      GREEN  = 3'b001 << G_BIT,
                      YELLOW = 3'b001 << Y_BIT} State, Next;

    always_ff @(posedge clk, negedge resetN)
        if (!resetN) State <= RED;
        else         State <= Next;

    always_comb begin: set_next_state
        Next = State;   // the default for each branch below
        unique case (1'b1)  // reversed case statement
            State[R_BIT]: if (sensor)              Next = GREEN;
            State[G_BIT]: if (green_downcnt  == 0) Next = YELLOW;
            State[Y_BIT]: if (yellow_downcnt == 0) Next = RED;
        endcase
    end: set_next_state

    always_comb begin: set_outputs
        {red_light, green_light, yellow_light} = 3'b000;
        unique case (1'b1)  // reversed case statement
            State[R_BIT]: red_light    = 1'b1;
            State[G_BIT]: green_light  = 1'b1;
            Staet[Y_BIT]: yellow_light = 1'b1;
        endcase
    end: set_outputs

endmodule
```

## Chapter 9 Systemverilog Design Hierarchy

### module prototypes

大型设计可能会分散定义在几十个文件中，在模块中例化另外一个文件中的模块时，综合工具要做大量工作，包括检查这个文件的模块的定义，包括端口数量、端口位宽、甚至是端口顺序。SV 提供了 `external module` 语法在例化该模块的文件中声明模块原型，可以简化综合步骤。

声明方式有两种：

```
#!systemverilog
// Verilog-1995 style
extern module counter (cnt, d, clock, resetN);

// Verilog-2001 style
extern module counter #(parameter N = 15)
                       (output logic [N:0] cnt,
                        input  wire  [N:0] d,
                        input  wire        clock,
                                           load,
                                           resetN);
```

声明模块原型可以写在任何地方：在 module/interface 之外的声明实际上定义在 $unit 中，这时模块原型声明对于和这个文件一起综合的其他文件来说都是可见的。

原型和模块的实际定义必须严格一致：包括端口顺序、端口位宽都必须相同，如果不同会报错。

如果模块参数、端口非常多，重复写两遍非常麻烦，SV 提供了新语法 `.*` 解决这个问题。

```
#!systemverilog
// prototype
extern module counter #(parameter N = 15)
                       (output logic [N:0] cnt,
                        input  wire  [N:0] d,
                        input  wire        clock,
                                           load,
                                           resetN);

// difinition
module counter ( .* );
    always_ff @(posedge clk, negedge resetN)
        if (!resetN)   cnt <= 0;
        else if (load) cnt <= d;
        else           cnt <= cnt + 1;
endmodule
```

### named ending statements

前面介绍了 SV 允许给 begin...end 后面加上名字，以提高代码可读性，实际上很多代码块都可以加上名字：

+ begin...end
+ package...endpackage
+ interface...endinterface
+ task...endtask
+ function...endfunction
+ module...endmodule

### nested module declarations

Verilog 中的模块默认是全局的可见的，所以在设计中的任何地方都可以访问这些模块的定义。这个机制简单强大，但是有两个问题：

+ 模块访问是无限制的，但是有时候我们希望隐藏某些模块，防止外部访问
+ 大型设计中可能产生命名冲突

Verilog 虽然可以通过配置文件的方式解决问题，但是不够优雅。SV 为解决这个问题提供了一种方法：嵌套的模块定义。和 C 语言类似，嵌套的模块定义只能被父模块或者是同一层级结构的模块访问。

为了可维护性一般都是一个文件放一个模块，且文件名和模块名相同，嵌套模块的方式显然违背了这个原则，所以嵌套模块应该和 \`include 配合使用。

```
#!systemverilog
module ip_core (input logic clock);
    `include sub1.v;    // sub1 is a nested module
    `include sub2.v;    // sub2 is a nested module
endmodule

// stored in file sub1.v
module sub1(...)
    ...
endmoudle

// stored in file sub2.v
module sub2(...)
    ...
endmoudle
```
### simplified netlists of module instances

Verilog 提供了两种端口连接方式：

+ 按端口顺序连接：缺点太多，大部分情况都被禁止使用
+ 按端口名连接：优点是不容易出错，缺点是模块和端口数量较多时非常繁琐

SV 提供了三种新的连接方式：

+  `.name` 方式：在许多端口连接上，信号名和端口名是一致的，这个时候就可以用这种方式，结合了端口顺序和端口名两种方式的优点。
    

        #!systemverilog
        prom prom (
            .dout (program_data),
            .clk,
            .address (program_address)
            );

    !!! note
        1. 必须声明和端口同名的，用于连接的 var / net 信号
        2. 连线的位宽必须和模块端口保持一致
        3. 两个端口的也必须兼容
        4. 无法使用 .name 方式连接的端口必须用端口名连接

+ `.*` 方式：比 .name 更进一步，例化模块时连信号名都不需要写，直接用通配符来匹配（条件同 .name）

        #!systemverilog
        prom prom (
            .*,
            .dout (program_data),
            .address (program_address)
            );

+ interface 方式：见下一章

### net aliasing

SV 新增了信号别名的语法，给信号起别名的 assign 语句有点像，但是并不完全相同。因为 assign 是单方向的，等号右边的信号的值可以传递给左边，但是左边的值无法传递给右边，而 `alias` 是双向的，因为本质上多个名字指向的是同一个资源。

```
#!systemverilog
wire reset, rst, resetN, rstN;

alias rst = reset;
alias reset = resetN;
alias resetN = rstN;

alias rst = reset = resetN = rstN;
```

使用别名有几个约束：

+ 只能给 net 类型起别名
+ 只能在相同类型的 net 直接使用别名
+ 别名必须位宽相同

别名也不需要预先显式地声明好才能用，它遵守 Verilg 中模块端口的隐式推断规则可以由工具自动推断出来：

+ alias 两端任何一个未声明的名字都会自动推断出一个 net 类型信号
+ 默认是 wire 类型
+ 如果 net 是模块端口信号，则其位宽和端口一致
+ 如果 net 不是端口信号，则默认是 1-bit

虽然 `.*` 可以减少工作量，但是有个前提条件是：模块端口名必须一样，否则还是得用传统的端口连接方式。而这个问题可以通过 alias 解决：**只需要先用 alias 把不同端口名设置为别名即可，这些模块例化时端口列表只写 `.*` 即可**。

### pass values through module ports

Verilog 对什么信号可以做作为模块端口有严格的约束，而 SV 基本上把这些限制都去掉了，基本上任何类型都可以作为模块端口，包括任何类型的 packed/unpacked 数组、structure、union、用户自定义类型等。

但是 SV 还是有两个约束，这两个约束都非常直白，都是为了建模的准确性而设立的：

+ 第一条是：var 类型只能有一个源驱动。因为 SV 中的 var 只是简单地保存赋值，所以有多个赋值时会保存最后一个赋值，而硬件在多驱动时的硬件行为并不是这样。所以 SV 要求只有 net 类型信号可以有多驱动。
+ 所有 unpacked 类型的信号（struct、union、array）作为端口连接时，必须一模一样，包括维度的数量、每个维度的大小、每个元素的位宽都必须一样。（隐含条件，struct、union 必须用 typedef 才能作为端口连接）。这个条件对 packed 类型并不其作用，因为 packed 类型是按照 vector 来处理的，SV/Verilog 有相应的规则处理位宽不匹配的情况

### reference ports

不可综合，略。

### enhanced port declarations

Verilog-1995 风格的端口声明已经没有人用了，但是 Verilog-2001 还是有点繁琐，

+ 所有端口都必须显式声明方向
+ 多个端口一起声明时，如果要改数据类型则必须连带方向一起声明（下例中的 a, b 和 ci）
+ 多个端口一起声明时，如果要改变端口位宽必须连带方向一起声明（下例中的 result 和 co）

```
#!systemverilog
// verilog-2001
module accum (inout  wire [31:0]  data,
              output reg  [31:0]  result,
              output reg          co,
              input       [31:0]  a, b,
              input  tril         ci     );
    ...
endmodule

// SV
module accm (wire  [31:0]  data,
             output reg [31:0] result, reg co,
             input [31:0] a, b, tril ci);
    ...
endmodule
```

!!! note
    一般为了代码健壮性、减少错误，大部分 coding style 都规定还要一行一个端口地声明，不会用到这个特性。

### parameterized types

Verilog 中的 parameter 只能参数化端口位宽，SV 新增了一个可综合的新语法 `parameter type`，可以对端口类型进行参数化，进一步提高了模块的多态性。实际上 Verilog 模块端口类型一般只有 wire/reg，而且是固定的，所以也不需要对类型参数化，而 SV 中有很多类型，甚至用户可以自定义类型，所以类型参数化就有必要了。

```
#!systemverilog
module adder #(parameter type ADDERTYPE = shortint)
              (input  ADDERTYPE  a, b,  // redefinable type
               output ADDERTYPE  sum,   // redefinable type
               output logic      carry);
    ADDERTYPE tmp;
    ...
endmodule

module big_chip (...);
    shortint        a, b, r1;
    int             c, d, r2;
    int unsigned    e, f, r3;
    wire            carry1, carry2, carry3;

    // 16-bit unsigned adder
    adder  i1 (a, b, r1, carry1);

    // 32-bit signed adder
    adder  #(.ADDERTYPE(int))  i2 (c, d, r2, carry2);

    // 32-bit unsigned adder
    adder  #(.ADDERTYPE(int unsigned))  i3 (e, f, r3, carry3);
endmoudle
```

### summary

!!! 本章小结
    + 必要时给 begin...end 后面加上 name，增强可读性
    + nested module 和 \`include 配合使用
    + 顶层集成用 `.*` 配合 alias 减少工作量
    + 为了减少错误，避免使用增强型的端口声明语法

## Chapter 10 Systemverilog Interfacees

### concepts

Verilog 中是通过模块端口进行连接，这种方式在端口数量非常多的时候很繁琐，比如说多个模块连接到总线上时，

+ 每个模块定义处都要声明总线的所有信号
+ 顶层集成时也要把每个模块的所有端口都写出来
+ 信号很多时连线可能出错
+ 如果总线变了，多个地方都要同步修改

SV 新增了一个叫 `interface` 的语法，可以把一组端口定义成一个端口，这样使用/修改起来就非常方便了。interface 并不是简单的把信号组合打包在一起，它里面还可以定义其他功能代码，比如其他离散的信号、接口的协议、检查协议的验证代码等：

+ type declration
+ task/function
+ procedural block
+ program block
+ assertion

```
#!systemverilog
interface main_bus;
    wire    [15:0] data;
    wire    [15:0] address;
    logic   [ 7:0] slave_instruction;
    logic          slave_request;
    logic          bus_grant;
    logic          bus_request;
    logic          slave_ready;
    logic          data_ready;
    logic          mem_read;
    logic          mem_write;
endinterface

module processor (
    main_bus    bus,
    output logic [15:0] jump_address
    //...);

endmodule
```

### interface declration

### using interface

### instantiating and connecting interface

### referencing signals within an interface

### interface modports

### using task/function in interface

### using procedural blocks in interface

### reconfigurable interface

### summary

!!! 本章小结
    + 