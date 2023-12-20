Title: 学习 Vim 之 BufExplorer、NERDTree、WinManager、Airline 插件
Date: 2015-03-04 22:40
Category: Tools
Tags: vim, BufExplorer, NERDTree, WinManager, Airline
Slug: learning-vim-bufexplorer-nerdtree-winmanager-airline
Author: Qian Gu
Series: Learning Vim
Summary: 学习 BufExplorer、NERDTree、WinManager、Airline 插件。

## BufExplorer

我们可以使用 `:ls` 命令可以查看打开的 buffer，然后在不同的 buffer 之间切换：

    #!vim
    :bn

其中 `n` 是 buffer 的标号。

这种内置的方法效率比较低，尤其是当我们打开很多个 Buffer 之后，问题更加明显。所以就有了各种 buf 类的插件，最有名的就是 [BufExplorer][bufexplorer] 和 [MiniBufferExplorer][mini]。不同的人使用习惯不同，在 stackoverflow 上有专门讨论两者的优劣的问题：

[ViM: minibufexpl versus bufexplorer plugins][question1]

### Install

使用 Vundle 安装：

1. 在 .vimrc 中添加

        #!vim
        Plugin 'bufexplorer.zip'

2. 安装

        #!sh
        vim +PluginInstall

### Config

查看 help 文档，简单配置如下：


    #!vim
    let g:bufExplorerDetailedHelp     = 0      " Don't show detailed help.
    let g:bufExplorerShowRelativePath = 1      " Show relative paths.
    let g:bufExplorerSortBy           = 'mru'  " Sort by most recently used.
    let g:bufExplorerShowUnlisted     = 1      " Show unlisted buffers.

[bufexplorer]: http://www.vim.org/scripts/script.php?script_id=42
[mini]: http://www.vim.org/scripts/script.php?script_id=159
[question1]: http://stackoverflow.com/questions/1649187/vim-minibufexpl-versus-bufexplorer-plugins

## NERDTree

NERDTree 是一款可以提供树形目录的 vim 插件，使用它我们可以在 vim 内以树形结构浏览文件目录。

### Install

使用 Vundle 安装：

1. 在 .vimrc 中添加

        #!vim
        Plugin 'The-NERD-tree'

2. 安装

        #!sh
        vim +PluginInstall

### Usage

+ 输入 `:NERDTree` 打开 NERDTree 窗口

常用快捷键：

+ o 打开/关闭光标所在目录

+ t 在新 tab 中打开文件，并跳转到该 tab

+ T 在新 tab 中打开文件，并不跳转到该 tab

+ p 跳转到父节点

+ P 跳转到根节点

+ q 关闭 NERDTree 窗口

## Airline

状态栏也是一个非常重要的窗口，可以为我们提供一些文档的基本信息，我们可以自己 DIY，在 .vimrc 文件中添加相关的设置

    #!vim
    set statusline=%F%m%r%h%w\ [FORMAT=%{&ff}]\ [TYPE=%Y]\ [POS=%l,%v][%p%%]\ %{strftime(\"%d/%m/%y\ -\ %H:%M\")}

也可以使用 [Airline][airline] 插件，一款可以提供非常漂亮的状态栏的插件。它会覆盖掉 .vimrc 中对状态的配置，删除插件后配置信息可以重新起作用。

### Install

使用 Vundle 安装：

1. 在 .vimrc 中添加

        #!vim
        Pulgin 'vim-airline/vim-airline'

2. 安装

        #!sh
        vim +PluginInstall

### Config

为了保证状态栏始终显示，在 .vimrc 中添加

    #!vim
    let g:airline_powerline_fonts             = 1
    let g:airline#extensions#tabline#enabled  = 1
    let g:airline#extensions#tabline#fnamemod = ':t'
    let g:airline#extensions#tabline#buffer_idx_mode = 1
    nmap <leader>1 <Plug>AirlineSelectTab1
    nmap <leader>2 <Plug>AirlineSelectTab2
    nmap <leader>3 <Plug>AirlineSelectTab3
    nmap <leader>4 <Plug>AirlineSelectTab4
    nmap <leader>5 <Plug>AirlineSelectTab5
    nmap <leader>6 <Plug>AirlineSelectTab6
    nmap <leader>7 <Plug>AirlineSelectTab7
    nmap <leader>8 <Plug>AirlineSelectTab8
    nmap <leader>9 <Plug>AirlineSelectTab9
    nmap <leader>0 <Plug>AirlineSelectTab0
    nmap <leader>- <Plug>AirlineSelectPrevTab
    nmap <leader>+ <Plug>AirlineSelectNextTab

[airline]: https://github.com/vim-ariline/vim-airline

## WinManager

我们已经安装很多插件，比如 Taglist，BufExlporer、NERDTree 等，这时候我们就需要一个窗口管理插件来将它们组合起来 —— [WinManager][winmanager]

### Install

使用 Vundle 安装：

1. 在 .vimrc 中添加

        #!vim
        Plugin 'winmanager'

2. 安装

        #!sh
        vim +PluginInstall

### bugfix

修改 `~/.vim/bundle/winmanager/plugin/winmanager.vim` 中的 `ToggleWindowsManager` 函数，给 else 分支新增一行(下段代码第 7 行)：

```vim
" toggle showing the explorer plugins.
function! <SID>ToggleWindowsManager()
	if IsWinManagerVisible()
		call s:CloseWindowsManager()
	else
		call s:StartWindowsManager()
		exe 'q'
	end
endfunction
```

### Config

查看 help 文档，我们可以进行简单的设置：

    #!vim
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""
    " Config Winmanager
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""
    let g:winManagerWindowLayout="NERDTree|TagList"
    let g:NERDTree-title="[NERDTree]"

    nmap <C-m> :WMToggle<CR>

    function! NERDTree-Start()
        exec 'NERDTree'
    endfunction

    function! NERDTree-IsValid()
        return 1
    endfunction

这时候我们按下组合键 Ctrl-m 即可切换是否显示 winmanager 窗口布局。

[winmanager]: http://www.vim.org/scripts/script.php?script-id=95

## Ref

[vi/vim使用进阶: 文件浏览和缓冲区浏览](http://easwy.com/blog/archives/advanced-vim-skills-netrw-bufexplorer-winmanager-plugin/)

[ 将Vim改造为强大的IDE—Vim集成Ctags/Taglist/Cscope/Winmanager/NERDTree/OmniCppComplete（有图有真相）](http://blog.csdn.net/bokee/article/details/6633193)

[谁说Vim不是IDE？（三）](http://www.cnblogs.com/chijianqiang/archive/2012/11/06/vim-3.html)
