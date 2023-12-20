Title: 学习 Vim 初步配置 Vim
Date: 2014-04-16 12:44
Category: Tools
Tags: vim
Slug: learning-vim-vimrc-preliminary
Author: Qian Gu
Series: Learning Vim
Summary: 总结初步配置 Vim，让 Vim 更顺手 。

总结初步配置 Vim，让 Vim 更顺手 。

## 在哪里配置 Vim

[学习 Vi 和 Vim 编辑器][learning-vi-and-vim-editor]：

> Vim 依照特定顺序寻找初始化的信号，它执行找到的第一组指令（可以是 环境变量 or 配置文件），然后开始编辑工作 。所以，Vim 在下列清单中遇到的第一个项目，就是清单中被执行的唯一项目 。书寻如下：

> 1. `VIMINIT` 。它是环境变量，如果不为空，Vim 把它的内容当作 ex 命令执行

> 2. 用户 `vimrc` 文件 。

> 3. `exrc` 选项 。如果设置了 Vim 的 exrc 选项，它会寻找三个额外的配置文件 。

`vimrc`（vim runtime configure）文件一般有 3 个：

1. /etc/vim/vimrc

    本配置文件影响所有的用户，一般不应该更改这个配置文件，因为谁也不能保证别人的喜好和自己一样 。

2. /usr/share/vim/vimrc

    输入命令

        #!Shell
         ll /usr/share/vim/vimrc

    就可以看到，本文件是 `/etc/vim/vimrc` 的软链接 。

3. ~/.vimrc

    一般来说，配置 vim 就是在这个文件中配置，如果不存在的话 `touch` 一个新文件并命名 `。vimrc` 。我们在下面说的配置都是在本文件中配置 。

[learning-vi-and-vim-editor]: http://book.douban.com/subject/6126937/

## 映射 `esc` 键

因为历史原因，Joy 设计 vi 时采用的键盘和我们现在用的标准键盘布局并不一样，当时他的键盘的 `esc` 键在现在我们的 `Caps Lock` 键的位置，所以才设计使用 `esc` 作为模式转换键 。为了更加方便顺手地使用 vim，当然要把这两个键相互调换一下 。

在 vim 的官网上就有介绍如何实现两个按键的调换

[Map caps lock to escape in XWindows][Map caps lock to escape in XWindows]

具体方法，在 `～/` 目录下新建一个文件，加入一下内容

    #!Shell
    ! Swap caps lock and escape
    remove Lock = Caps-Lock
    keysym Escape = Caps-Lock
    keysym Caps-Lock = Escape
    add Lock = Caps-Lock

保存为 .speedswrapper

然后输入命令

    #!Shell
    xmodmap ~/.speedswrapper

这时，对于整个系统范围，这两个键已经调换了位置 。

[Map caps lock to escape in XWindows]: http://vim.wikia.com/wiki/Map-caps-lock-to-escape-in-XWindows

## 设置颜色主题 colorscheme

Vim 自带一些颜色主题，一般存放在 `/usr/share/vim/vim7x` 目录下（我的 Vim 版本为 7.3，所以路径为 `/usr/share/vim/vim73`）.

如果对系统自带的主题不满意，网上有很多不错的主题，个人最喜欢 [molikai][molikai] 主题，把下载下来的配色文件拷贝到 `usr/share/vim/vim73` 路径下，打开 vim 后 输入

    #!Shell
    :colorscheme molikai

就 ok 了～ 不过这个方法在关闭 vim 后就恢复了，要想省去每次都输命令的烦恼，只需要在下一步 .vimrc 文件中加入以下内容就可以了

    #!Shell
    colorscheme molikai

[molikai]: https://github.com/tomasr/molokai

## 编写 .Vimrc

vimrc 文件是配置 Vim 编辑特性比较好的地方，差不多任何 Vim 选项都能在次文件中被设置为打开或者关闭，而且它特别适合设置全局变量与定义函数、缩写、按键映射 。

+ 注释以双引号 `“` 开始，可位于一行的任何2位置，所有位于双引号后面的文本，包括双引号都会被视为注释而忽略

+ 可以用冒号 `:` 表示 ex 命令

### 配置 Vim 特性

vimrc 配置很简单，网上有很多人都分享了自己的配置方案 。我找到一份注释良好的[配置范例][config-file]，这篇博客的作者总结了自己 8 年的使用经验，给出了 [Basic][Basic] 和 [Awesome][Awesome] 两份配置文件。一开始只需要看基础版就足够了，后续可以在高级版上定制自己的配置。

[config-file]: https://github.com/amix/vimrc
[Basic]: https://github.com/amix/vimrc/blob/master/vimrcs/basic.vim
[Awesome]: https://github.com/amix/vimrc

## 参考

[学习vi 和 Vim 编辑器][learning-vi-and-vim-editor]

[The Ultimate vimrc][config-file]
