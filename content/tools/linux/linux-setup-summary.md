Title: Linux 安装步骤备忘
Date: 2022-09-18 21:41
Category: Tools
Tags: linux
Slug: linux-setup-summary
Author: Qian Gu
Summary: 总结 linux 环境安装步骤

## 原因

最近折腾虚拟机时重复安装了很多次 ubuntu，总结一下过程，方便以后查阅。

## 安装步骤

!!! note
    必须注意安装顺序，否则可能会因为库文件版本冲突无法解决导致某个包安装失败。

### 虚拟机

如果是在虚拟机环境中安装，优先选择 VMWare Workstation + 最新版的 LTS ubuntu。安装完系统后安装 vmware-tool。

!!! note
    一般来说应该选择最新的 LTS，但是如果选择 Ubuntu 系统，且某软件对系统版本/动态库版本有特殊需求，可以选择较旧的、已经成功运行过的版本。较旧版本的一个问题是：某些最新软件无法 apt 安装，只能下载 deb 包手动安装，比如 `fd` 和 `rg`。

### 替换 apt 源

```bash
sudo vi /etc/apt/source.list
# copy and edit
sudo apt update
```

### 安装 build-essential

```bash
sudo apt install build-essential
```

### 安装 guake

```bash
sudo apt install guake
```

### 安装配置 git

```bash
sudo apt install git
git config --global user.name 'qian.gu'
git config --global user.email "guqian110@163.com"
git config --global core.editor "vim"
# generate ssh key
ssh-keygen -t ed25519 -C "guqian110@163.com"
# add to github/gitee etc
```

### 安装配置 vim

```bash
sudo apt install vim
git clone git@github.com:VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
git clone git@github.com:qian-gu/dotfiles.git
cp dotfiles/.vimrc ~/
# open vim and run :VundleInstall
```

### 安装 gnome

```bash
sudo apt install gnome
sudo apt install gnome-teaks gnome-shll-extensions
# install theme
git clone git@github.com:EliverLara/Ant
sudo mv Ant /usr/share/themes/Ant
# install file icon
git clone git@github.com:vinceliuice/Tela-icon-theme
cd Tela-icon-theme
./install -a
# tweak in tweak-tools, logout and re-login
```

### 安装 nerd font

https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powverlevel10k

set font in guake, terminal, vscode

### 安装 fd, ag, rg

```bash
sudo apt install silversearcher-ag
sudo apt install ripgrep
sudo apt install fd-find
```

### 安装 zsh

```bash
sudo apt install zsh
csh -s $(which zsh)
# logout and re-login
```

### 安装 zplug 及插件（含 fzf ）

```bash
cp dotfiles/.zshrc ~/.zshrc
source .zshrc
```

### 安装 anaconda

https://docs.anaconda.com/anaconda/install/linux/

```bash
# copy tsinghua anaconda source to ~/.condarc
conda clean -i
conda create - myenv numpy # test conda
```

### 安装 nvm/nmp/commitizen

```bash
# install nvm
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
# install nmp
nvm install node
# install commitizen for each repo
```
