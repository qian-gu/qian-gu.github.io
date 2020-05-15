Title: PEP 学习系列之 4 —— PEP234
Date: 2020-05-10 23:51
Category: Python
Tags: PEP, python
Slug: learning_peps_series_4_pep234
Author: Qian Gu
Series: Learning PEPs
Summary: Iterator 学习笔记
Status: draft

[PEP 234 -- Iterators 原文链接][PEP234]。

[PEP274]: https://www.python.org/dev/peps/pep-00234/

| item | detail |
| ---- | ------ |
| PEP  |  234   |
| Title | Iterators |
| Author | |
| Status | Final |
| Type | Standards Track |
| Created | 30-Jan-2001 |
| Python-Version | 2.1 |
| Post-History | 31-Apr-2001 |


```
#!python
>>> {(k, v): k+v for k in range(4) for v in range(4)}
... {(3, 3): 6, (3, 2): 5, (3, 1): 4, (0, 1): 1, (2, 1): 3,
   (0, 2): 2, (3, 0): 3, (0, 3): 3, (1, 1): 2, (1, 0): 1,
   (0, 0): 0, (1, 2): 3, (2, 0): 2, (1, 3): 4, (2, 2): 4, (
   2, 3): 5}
```