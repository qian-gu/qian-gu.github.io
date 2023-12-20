Title: 学习 Vim 使用 Vundle 管理插件
Date: 2014-04-16 17:06
Category: Tools
Tags: vim, vundle
Slug: learning-vim-vundle
Author: Qian Gu
Series: Learning Vim
Summary: 学习 Vim，使用 Vundle 管理插件 。

学习 Vim，使用 Vundle 管理插件 。

## Vim 插件

Vim 的强大之处在于它的可扩展性，你可以把它当作一个简单的文本编辑器，也可以安装各种功能强大的插件，把它武装成一个 IDE 。我们可以从 [Vim 官网][Vim-official] 或 [Vim Awesome][Awesome] 上找到 Vim 插件 。

[Vim-official]: http://www.vim.org/scripts/script-search-results.php
[Awesome]: https://vimawesome.com/

## 什么是 Vundle

Vim 的插件虽然强大，但是因为 Vim 根本就没有插件管理这个概念，所有插件的文件都散布在~/.vim下的几个文件夹中，配置 vim 的过程, 就是在网上不停的搜插件，拷贝到 `~/.vim` 下，发现更新，要重新下载重新拷贝，想要删除某个不需要插件，更是要小心翼翼的不要删错。配置出顺手的 Vim, 需要极大的耐心和运气，而且如果换一台电脑，就要重复一次这样的痛苦经历 。

自然地，因为管理插件的需求，最早出现了一些管理插件的脚本，但是写脚本需要一定的 shell 知识，直接 copy 别人的自己并不一定适用 。后来，出现了一些插件，比如 pathogen，muzuiget，vim-flavor，Vundle 等 。

目前比较流行的方式是采用 [Vundle][vundle-github] 来管理插件，Vundle 的介绍：

> Vundle is short for Vim bundle and is a Vim plugin manager.

Vundle 可以在交互的方式下做到：

+ 在 `.vimrc` 中管理和配置插件
+ 安装插件
+ 更新插件
+ 按名字搜索插件
+ 删除插件

[vundle-github]: https://github.com/gmarik/Vundle.vim

## 如何使用 Vundle 管理插件

### 安装 Vundle

从 GitHub 上 clone 下来就可以了

    #!Shell
    git clone https://github.com/gmarik/vundle.git ~/.vim/bundle/vundle

### 配置 Vundle

将下列内容加入到 `.vimrc` 文件中

    #!Shell
    set nocompatible              " be iMproved, required
    filetype off                  " required
    
    " set the runtime path to include Vundle and initialize
    set rtp+=~/.vim/bundle/Vundle.vim
    call vundle#begin()
    " alternatively, pass a path where Vundle should install plugins
    "call vundle#begin('~/some/path/here')
    
    " let Vundle manage Vundle, required
    Plugin 'VundleVim/Vundle.vim'
    
    " The following are examples of different formats supported.
    " Keep Plugin commands between vundle#begin/end.
    " plugin on GitHub repo
    Plugin 'tpope/vim-fugitive'
    " plugin from http://vim-scripts.org/vim/scripts.html
    " Plugin 'L9'
    " Git plugin not hosted on GitHub
    Plugin 'git://git.wincent.com/command-t.git'
    " git repos on your local machine (i.e. when working on your own plugin)
    Plugin 'file:///home/gmarik/path/to/plugin'
    " The sparkup vim script is in a subdirectory of this repo called vim.
    " Pass the path to set the runtimepath properly.
    Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
    " Install L9 and avoid a Naming conflict if you've already installed a
    " different version somewhere else.
    " Plugin 'ascenator/L9', {'name': 'newL9'}
    
    " All of your Plugins must be added before the following line
    call vundle#end()            " required
    filetype plugin indent on    " required
    " To ignore plugin indent changes, instead use:
    "filetype plugin on
    "
    " Brief help
    " :PluginList       - lists configured plugins
    " :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
    " :PluginSearch foo - searches for foo; append `!` to refresh local cache
    " :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
    "
    " see :h vundle for more details or wiki for FAQ
    " Put your non-Plugin stuff after this line
    
从上面的配置文件中可以看到，Vundle 把插件分为了 4 类：

1. plugin on GitHub repo

    GitHub 上的插件，需要按照 `usrname/repos` 的格式写出插件的名称

2. plugin from http://vim-scripts.org/vim/scripts.html 

    Vim scripts 上的插件，不用作者名，直接写插件名

3. git plugin not hosted on GitHub

    不是 GitHub 上的插件，需要写出插件的 git 链接

4. git repo on your local machine

    本地 git repo 的插件，需要写出插件的路径
    
### 运行 Vundle

修改好 `.vimrc` 文件后，打开 Vim，使用以下命令管理插件

+ 列表

        #!Shell
        :PluginList // 列出已安装的插件

+ 安装

        #!Shell
        :PluginInstall  //安装插件

+ 搜索

        #!Shell
        :PluginSearch foo  // 搜索插件

+ 更新

        #!Shell
        :PluginInstall!  // 或者
        :PluginUpdate

+ 删除

    在 `.vimrc` 文件中删除/注释掉相应的插件名，然后输入命令
    
        #!Shell
        :PluginClean

## 参考

[vim中的杀手级插件: vundle](http://zuyunfei.com/2013/04/12/killer-plugin-of-vim-vundle/)

[Vundle 管理 Vim 插件](http://www.zfanw.com/blog/vundle-vim-plugin-management.html)
