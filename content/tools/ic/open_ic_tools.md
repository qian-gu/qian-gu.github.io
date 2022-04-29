Title: 开源 IC 工具/库汇总
Date: 2021-07-03 17:16
Category: Tools
Tags: IC_tools
Slug: open_ic_tools_libraries_summary
Author: Qian Gu
Status: draft
Series: Open IC Tools & Library
Summary: 汇总 IC 设计中常用的开源小工具和开源库

## Tools

| 工具                  | 用途 |
| -------------------- | ------------- |
| [Wavedrom][wavedrom] | 画波形图        |
| [bitfield][bitfield] | 画 bit 示意图   |
| [logidrom][logidrom] | 画数字逻辑电路图 |
| [svlint][svlint]     | linter        |
| [fusesoc][fusesoc]   | `pip` for HDL |
| [iverilog][iverilog] | simulator     |
| [verilator][verilator] | simulator     |
| [verible][verible]   | SV 开发工具，包含了 parser，sytle-linter 和 formatter |

[wavedrom]: https://github.com/wavedrom/wavedrom
[bitfield]: https://github.com/wavedrom/bitfield
[logidrom]: https://github.com/wavedrom/logidrom
[svlint]: https://github.com/dalance/svlint
[fusesoc]: https://github.com/olofk/fusesoc
[iverilog]: http://iverilog.icarus.com/
[verilator]: https://www.veripool.org/verilator/
[verible]: https://github.com/chipsalliance/verible

## Library

| 工具                            | 用途                      |
| ------------------------------ | ------------------------- |
| [fusesoc-cores][fusesoc-cores] | fusesoc 官方库             |
| [common-cells][common-cells]   | PULP 的常用库，兼容 fusesoc |

[fusesoc-cores]: https://github.com/fusesoc/fusesoc-cores
[common-cells]: https://github.com/pulp-platform/common_cells

## Others

https://github.com/ben-marshall/awesome-open-hardware-verification
