Git Flow 小结
###################

:date: 2020-05-24 12:55
:category: Tools
:tags: Git, Workflow
:Slug: git-flow-summary
:author: Qian Gu
:summary: git-flow 翻译、总结、实践

git-flow 是 Vincent Driessen 在 2010 年写的文章 `A successful Git branching model`- 中提出的一种管理 git branch 的模型，当时 git 才刚刚被发明出来。经过 10 来年的发展，已经有很多公司都采用这种方式作为标准流程来管理自己的软件开发了。如果像 Web App 这类的持续交付 continuous delivery 的软件，可以采用更简单的 `GitHub Flow`-，但是对于传统的那种版本概念非常清晰的软件，git-flow 还是非常适用的。下面的内容是原文的简单汇总和翻译，完整内容请看原文。

.. note::

    这里还有一篇翻译：`Git分支管理策略`-

    Git 的工作流程有很多中，git-flow 是之前最流行的做法。就像作者自己所说，git-flow 非常适合传统的软件开发，但是对于 CI/CD 的项目，则显得太繁琐，推荐使用 Github FLow 和 GitLab FLow，这里有相关的翻译和介绍：`Git 工作流程`-

.. -A successful Git branching model: https://nvie.com/posts/a-successful-git-branching-model/
.. -GitHub Flow: https://guides.github.com/introduction/flow/
.. -Git分支管理策略: http://www.ruanyifeng.com/blog/2012/07/git.html
.. -Git 工作流程: http://www.ruanyifeng.com/blog/2015/12/git-workflow.html

---------

.. image:: https://nvie.com/img/git-model@2x.png
    :alt: GitFlow Diagram

Why Git
===========

网上有很多 Git 和 SVN 这种集中式的代码管理系统优缺点的对比。简而言之，Git 从根本上改变了程序员对 branch/merge 的思考方式，

+ SVN 方式：merge 要非常小心 conflict，一般很久才 merge 一次
+ Git 方式：每天都会进行，是日常工作的一部分

Git 让码农的生活更加容易。

Decentralized & Centralized
==============================

Git 实际上是一个分布式的管理系统，并不存在技术意义上真正的 central repo，但是因为需要一个大家都能访问的服务器节点（比如 GitHub）方便相互之间同步，所以在 Git 中一般把这个服务器节点叫做 ``origin``。项目中的所有成员都和 origin 打交道，完成 ``pull``, ``push`` 等操作。

有时候对于某个比较大的 feature，可能需要多个同学一起完成，这个时候相关的同学可以组成一个 subteam，他们相互之间进行 pull/push，如下图所示，Alice 和 Bob，Alice 和 David，David 和 Clair 组成了 3 个 subteam。要组建 subteam 也非常简单，Alice 只需要定义一个 ``git remote``，指向 Bob 的 repo 地址即可。

.. image:: https://nvie.com/img/centr-decentr@2x.png
    :alt: Decentralized & Centralized Diagram

Main Branch
===============

主分支一共有两条，即服务器上的 central repo 应该有两条生命期无限长的 branch，

+ ``master``
+ ``develop``

每个小组成员都应该对 ``origin/master`` 分支非常熟悉，它是发布产品的主分支，``HEAD`` 指向的永远是可以随时在产品中部署的代码。

而 ``origin/develop`` 分支是用来发布新 feature 的主分支，``HEAD`` 指向的代码永远指向最新交付的新功能。有些人把它叫做 集成分支，顾名思义它是用来做集成的，也就是所有开发者会把开发的新 feature 代码都集成到这个分支中，为 release 做准备。所有 nightly build 都应该用这个分支的代码。

当 develop 分支上的代码保持稳定，达到可以 release 的程度了，所有的修改都要通过某种方式 merge 回 master 分支，并且用版本号打个 tag（具体方法后面 release 分支一节描述）。所以每次 merge 回 master，都是发布了一个新的产品 release，所以可以利用 Git 提供的 hook 函数实现只要 master 有新的 commit，就自动编译和推送最新代码到产品服务器上。

Supporting Branch
=======================

除了 master 和 develop 两个主分支，还有一些支持性的分支以实现小组成员之间的并行开发，比如跟踪不同的新 feature，修改 bug 等。和主分支不同都是，这些支持性的分支的生命周期是有限的。这里一共定义了 3 种分支，

+ ``Feature branches``
+ ``Release branches``
+ ``Hotfix branch``

这 3 个分支每个都有非常明确的目的，使用也非常严格，从哪个分支中 branch 出来，最终 merge 到哪个 branch 都有严格要求。这些 branch 从技术上来说就是普通的 branch，并无特殊之处，但是因为我们特殊的用法所以将其归为一大类。

Feature Branches
-------------------

+ 来源：可能是 ``develop``
+ 终点：必须是 ``develop``
+ 命名规则：除了 master, develop, release-\*, hotfix-\* 之外，其他名字都可以

顾名思义，Feature 分支的目的就是为了开发新 feature，有时候开始开发新 feature 的时候并不知道最终 merge 回哪个 release 分支，只要开始开发这个 feature，那么该 feature 分支就会一直存在，直到最后 merge 回 develop 或者是丢弃掉（中途放弃开发）。

Feature 分支一般只存在于相关开发者的本地 repo 中，并不会存在 origin 上，除非是多和协作共同完成一个大 feature 的情况。

1.  创建 feature 分支

    .. code-block:: bash
        :linenos: table

        // creating a new feature branch
        git checkout -b feature-xxx develop

2.  结束 feature 分支

    .. code-block:: bash
        :linenos: table

        // merge back to develop branch
        git checkout develop
        git merge --no-ff feature-xxx
        git branch -d feature-xxx
        git push origin develop
    
    .. note::
    
        用 ``--no-ff`` 来保留 branch 信息。

Release Branch
------------------

+ 来源：可能是 ``develop``
+ 终点：必须是 ``develop`` & ``master``
+ 命名规则：release-\*

Release 分支的作用是为最终产品发布做准备，在这个 branch 上允许做最后一刻的修改，比如微小的 bug 修改，为发布准备 meta-data（版本号，build 日期等等），在 release 分支上做这些事情的好处是可以保持 develop 分支的干净整洁。

创建 release 分支的时间点非常关键，主要有两方面的约束，

1. 不能太早，相关功能的代码要全部 ready：当前要发布的 release 包含的新 feature 必须都已经合入 develop 之中
2. 不能太晚，代码要防污染：不能包含下一次 release 对应的 feature 代码

约束 1 要求 ``develop`` 分支（几乎）完成了新 release 的所有功能才可以创建 ``release`` 分支。约束 2 要求未来下一次 release 的 feature 代码则一定不能合并进来，这些新 feature 必须等到创建当前 release 之后才能合进 develop 分支。

在创建了 release 分支之后，develop 分支就可以为“下一次 release”做准备了。

1.  创建 release 分支

    .. code-block:: bash
        :linenos: table

        git checkout -b release-1.2 develop
        ./bump-version.sh 1.2
        git commit -a -m "Bumped version number to 1.2"

    创建好的 release 分支可能会存在一段时间，这段时间内如果有 bug 修改，应该在 release 分支上，而不是 develop 上。新 feature 禁止直接加到 release 分支上，而是应该加到 develop 上，等待下一次的 release。

2.  结束 release 分支

    .. code-block:: bash
        :linenos: table

        git checkout master
        git merge --no-ff release-1.2
        git tag -a 1.2
        git checkout develop
        git merge -no-ff release-1.2
        git branch -d release-1.2

    当 release 分支最终达到可以 release 状态的时候，需要做的事情有
    
    + 把 release 分支 merge 回 master（前面描述过，master 的每个结点都是一个 release 版本）
    + 给 master 分支打 tag，方便以后回溯版本
    + 把 release 分支 merge 回 develop 分支（保存 release 分支上的 bug 修改）

Hotfix Branches
-------------------

+ 来源：可能是 ``master``
+ 终点：必须是 ``develop`` & ``master``
+ 命名规则：hotfix-*

hotfix 分支的作用和 release 有点类似，也是为了新产品发布，但是它是计划之外的。hoftfix 是为了应对那种意外发现的，急待解决的产品 bug，如果发现产品上有一个马上就要解决的重大 bug，那么就可以从 master 的该节点上创建一个 hotfix 分支。

典型场景：

突然发现 master 分支上正在使用的产品版本（比如说是 release-1.2）有一个致命 bug，但是 develop 分支因为合入了新 feature，还没有稳定，不能直接在 develop 分支上进行修复，此时就需要创建一个 hotfix 分支。

由上面的例子可以看出，hotfix 分支存在的意义是让团队中的一部分人来进行快速的产品 fix，另外一部分人仍然按照计划进行开发，相互不影响。

1.  创建一个 hotfix 分支

    .. code-block:: bash
        :linenos: table

        git checkout -b hotfix-1.2.1 master
        ./bump-version.sh 1.2.1
        git commit -a -m "Bumped version number to 1.2.1"
    
    在修改完 bug 之后，把修改结果 commit
    
    .. code-block:: bash
        :linenos: table

        git commit -m "FIxed severe production problem"

2.  结束 hotfix 分支

    最后 bugfix 的内容除了要 merge 回 master，还要 merge 回 develop，以保证下一次 release 的时候这个 bug 已经被修复了。这个过程和结束 release  分支很类似。
    
    .. code-block:: bash
        :linenos: table

        git checkout master
        git merge --no-ff hotfix-1.2.1
        git tag -a 1.2.1
        git checkout -b develop
        git merge --no-ff hotfix-1.2.1
        git branch -d hotfix-1.2.1
    
    有个特殊情况：**如果存在一个 release 分支，那么应该将 hotfix 分支 merge 到 release 分支，而不是 develop 分支**。Merge 到 release 的 bugfix 代码最终会随着 release 代码一起合入到 develop 分支中，不需要担心丢失。（如果 develop 分支需要马上就合入这个 bugfix，等不到 release  分支结束，那么也可以将 bugfix 合入到 develop 中。）

Summary
=========

这个模型并没有提出什么惊人的新概念，但是在实际工作中非常有用，这个优雅的模型可以让整个 team 中的成员对 branch 分支有一个共同的认识。

Practice -- git-flow
========================

上面是原文的翻译和总结，在实践中，有个 git 扩展 ``git-flow`` 工具可以帮助我们遵守这套规则。这里有一篇 `git flow cheatsheet`- 方便查看。

.. -git flow cheatsheet: https://danielkummer.github.io/git-flow-cheatsheet/

Install
---------

.. code-block:: bash
    :linenos: table

    sudo apt-get install git-flow


Setup
------

.. code-block:: bash
    :linenos: table

    git flow init

回答一系列问题即可，推荐使用默认值

Features
-----------

1.  创建一个 feature 分支：

    + 基于 develop 创建了一个新 feature 分支，并切换过去

    .. code-block:: bash
        :linenos: table

        git flow feature start MYFEATURE

2.  结束一个 feature 分支：

    + 把 MYFEATURE 分支 merge 回 develop 分支
    + 删除该 feature 分支
    + 切换回 develop 分支

    .. code-block:: bash
        :linenos: table

        git flow feature finish MYFEATURE

3.  发布一个 feature

    .. code-block:: bash
        :linenos: table

        git flow feature publish MYFEATURE

    把 feature 分支发布到 remote 服务器，方便其他人使用

4.  获取一个其他人发布的 feature

    .. code-block:: bash
        :linenos: table

        git flow feature pull origin MYFEATURE

Release
---------

1.  创建一个 release 分支

    .. code-block:: bash
        :linenos: table

        git flow release start RELEASE [BASE]

    通过一个可选项 [BASE] 来制定 develop 上的某个特定节点

2.  把 release 分支的结果发布给其他开发者

    .. code-block:: bash
        :linenos: table

        git flow release publish RELEASE

3.  结束一个 release 分支

    + 把 release 分支 merge 回 master 分支
    + 用 release 分支的名字给 master 打 tag
    + 把 release 分支 merge 回 develop 分支
    + 删除 release 分支

    .. code-block:: bash
        :linenos: table

        git flow release finish RELEASE

    .. note::

        别忘了把你的 tag push 到远程 repo：git push origin --tags

Hotfix
----------

1.  创建一个 hotfix 分支

    .. code-block:: bash
        :linenos: table

        git flow hotfix start VERSION [BASENAME]

2.  结束一个 hotfix 分支

    + 把 hotfix 分支 merge 回 develop 和 master 分支
    + 用 hotfix 的 version 给 master 分支打 tag

    .. code-block:: bash
        :linenos: table

        git flow hotfix finish VERSION

Zsh Extension
----------------

zsh 里面有两个相关插件，

+ ``git flow completion``，自动补全
+ ``git-flow``，提供命令的各种 alias

给 zsh 安装 `git flow completion`- 插件的步骤，

1.  下载插件 
    
    .. code-block:: bash
        :linenos: table

        git clone https://github.com/bobthecow/git-flow-completion ~/.oh-my-zsh/custom/plugins/git-flow-completion

2.  更新 ``.zshrc`` 文件

    .. code-block:: bash
        :linenos: table

        plugins=(<some-plugin> <another-plugin> git-flow-completion)

3.  重新 source 之后就可以看到自动补全的效果了

.. -git flow completion: https://github.com/bobthecow/git-flow-completion

Ref
========

`A successful Git branching model`-

`git flow cheatsheet`-
