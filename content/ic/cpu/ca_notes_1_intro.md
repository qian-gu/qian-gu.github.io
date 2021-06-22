Title: CA 笔记 —— 引言
Date: 2021-01-13 19:21
Category: IC
Tags: CA
Slug: ca_intro
Author: Qian Gu
Series: Computer Architecture 笔记
Status: draft
Summary: 引言

!!! note
   这个系列是 Computer Architecture 的主题阅读笔记，主要参考资料为：
   1. H&P
   2. P&H
   3. ICS 胡 （简化版的 CSAPP + P&H）
   4. CA 胡 （介于 P&H 和 H&P 之间）

## CA 研究的是什么

## 如何评价一个计算机

衡量指标： 借用芯片的评价维度 PPA。

### 性能 Performance

性能评价的多维度

benchmark

### 功耗 Power

### 面积 Area

也就是成本。

| 概念 | 含义 | 类比 |
| ---- | ---- | ---- |
| 无 ILP          | 指令之间原子性执行，不重叠      | 单车道，任意时刻只能有一辆车在上面跑 |
| `pipeline`      | 指令按照流水线式执行，重叠在一起 | 单车道，可以有多辆车同时在上面跑    |
| `single-issue`  | 指令发射速度 < 1 instr/cycle  | 只有一个收费口                   |
| `multi-issue`   | 指令发射速度 > 1 instr/cycle  | 多个收费口                      |
| `out-of-order`  | 指令乱序执行                  | 多车道，拖拉机不堵保时捷          |

## CA 的发展

## CA 的设计原则

## Ref

[Tomasolu wiki](https://en.wikipedia.org/wiki/Tomasolu_algorithm)

[Revervation Station wiki](https://en.wikipedia.org/wiki/Reservation_station)

[Computer Architecture - Chapter 3.4](https://book.douban.com/subject/6795919/)

[ECE252 duke]()