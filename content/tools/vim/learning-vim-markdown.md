Title: 在 Vim 中写 Markdown 文件
Date: 2015-02-01 13:46
Category: Tools
Tags: vim, markdown
Slug: learning-vim-markdown
Author: Qian Gu
Series: Learning Vim
Summary: 在 Vim 中使用 Markdown 语法写文本。

记录一下最近在 Vim 中摸索使用 Markdown 的经历。

## Syntax Hightlight

Vim 可以通过插件来提供对 Markdown 语法的支持，网上找到很多这类插件，我找到的是下面这个 [preservim/vim-markdown][pv]。

### Install

使用 Vundle 管理插件，只需要在 `.vimrc` 文件中添加：

    #!vim
    Plugin 'godlygeek/tabular'
    Plugin 'preservim/vim-markdown'

然后输入命令即可。

    #!sh
    vim +PluginInstall

### File extension

Markdown 文件的后缀名可以是 `.markdown`，`mkd`，`mkdn`，`md` 等，但是插件只识别 `mkd` 和 `markdown` 两种：

[Enabling markdown highlighting in Vim][so1]

因为我们已经按照 .md 格式写了很多文本了，这时候更好选择当然是修改设置，让 vim 可以识别这种类型的文件，而不是修改文件后缀名。所以我们需要在 vimrc 中设置一下：

    #!vim
    au BufRead,BufNewFile *.md set filetype=markdown

这样 .md 文件就可以被识别了。

经过上面两步，此时再打开 markdown 文件就可以看到语法高亮了。

[markdown]: http://www.vim.org/scripts/script.php?script-id=2882
[pv]: https://github.com/preservim/vim-markdown
[so1]: http://stackoverflow.com/questions/10964681/enabling-markdown-highlighting-in-vim

## Preview

一些专门的 Markdown 软件、网页编辑器都是提供实时预览，Vim 虽然不提供预览窗口，但是配合浏览器，我们也可以实现实时预览的功能，当然还是依靠万能的插件。我使用的是 [iamcco/vim-preview.nvim][iamcco]。

### Install

1. 使用 Vundle 管理插件

    在 .vimrc 中添加

        #!vim
        Plugin 'iamcco/vim-markdown-preview'

    打开 vim，输入命令

        #!sh
        :PluginInstall
        :call mkdp#util#install()

### Use

```sh
# start preview
:MarkdownPreview
# stop preview
:MarkdownPreviewStop
```

[iamcco]: https://github.com/iamcco/vim-markdown-preview.nvim

## Ref

[preservim/vim-markdown][pv]

[Enabling markdown highlighting in Vim][so1]

[iamcco/markdown-preview.nvim][iamcco]
