Title: Patterson and Hennessy 学习笔记 #5 —— Chapter 5 Large and Fast:Exploiting Memory Hierarchy
Date: 2020-12-20 22:28
Category: IC
Tags: Patterson and Hennessy
Slug: learning_patterson_and_hennessy_notes_5_chapter_5
Author: Qian Gu
Series: Patterson & Hennessy Notes
Summary: Patterson and Hennessy 读书笔记，第五章
Status: draft

> Ideally one would desire an indefinitely large memory capacity such that any
particular ... word would be immediately available. ... We are ... forced to recognize the possibility of constructing a hierarchy of memories, each of which has greater capacity than the preceding but which is less quickly accessible.
> 
>   -- A. W. Burks, H. H. Goldstine, and J. von Neumann
> 
>      _Preliminary Discussion of the Logical Design of an Electronic Computing Instrument_, 1946

## Introduction


## A Simple Implementation Scheme



## An Overview of Pipeling


## A Pipelined Scheme


## Parallelism via Instructions



## Fallacies and Pitfalls

+ `Fallacies` 谬论：错误概念
+ `Pitfalls` 陷阱：特定条件下成立的规律的错误推广

**谬论：pipeline 非常简单**

呵呵。

**谬论：pipeline 的概念和实现工艺无关**

显然，工艺的实现难度和代价会反过来影响设计的取舍。

**陷阱：没有考虑到 ISA 的设计会反过来影响到 pipeline 的设计**

很多复杂的 ISA 会导致实现的困难，这也是 RISC-V 的设计目标之一：用简单的 ISA 简化硬件设计，以达到更高的主频和性能。

## Summary

!!! important
    + pipeline 可以提高 throughput 但是不能减少 latency
    + 