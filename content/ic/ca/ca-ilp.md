Title: CPU 关键技术 —— ILP
Date: 2021-01-13 19:21
Category: IC
Tags: CPU, Tomasolu
Slug: cpu-ilp
Author: Qian Gu
Series: CPU 关键技术
Status: draft
Summary: 总结 Tomasolu 细节

!!! note
   这个系列是 Computer Architecture 的主题阅读笔记，主要参考资料为：
   1. H&P
   2. P&H
   3. ICS 胡 （简化版的 CSAPP + P&H）
   4. CA 胡 （介于 P&H 和 H&P 之间）

## Why ILP

## What is ILP

ILP = pipeline + superscalar
         时间        空间

superscalar == multi-issue

计算机体系结构基础 P22
## How to ILP

| 概念 | 含义 | 类比 |
| ---- | ---- | ---- |
| 无 ILP          | 指令之间原子性执行，不重叠      | 单车道，任意时刻只能有一辆车在上面跑 |
| `pipeline`      | 指令按照流水线式执行，重叠在一起 | 单车道，可以有多辆车同时在上面跑    |
| `single-issue`  | 指令发射速度 < 1 instr/cycle  | 只有一个收费口                   |
| `multi-issue`   | 指令发射速度 > 1 instr/cycle  | 多个收费口                      |
| `out-of-order`  | 指令乱序执行                  | 多车道，拖拉机不堵保时捷          |

## Ref

[Tomasolu wiki](https://en.wikipedia.org/wiki/Tomasolu-algorithm)

[Revervation Station wiki](https://en.wikipedia.org/wiki/Reservation-station)

[Computer Architecture - Chapter 3.4](https://book.douban.com/subject/6795919/)

[ECE252 duke]()