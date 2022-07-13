!!! organize and save into Evernote, refer to Personal Project TP20xx serie(organize several
articels into series)

## What is PA

- definiation

## Why need PA

- ensure quality(Performance)
- save time

## How to PA

### Laws and Principles

- amdahl's low
- locality
- common case fast

### Methods

- roofline model
- BW equation: `BW = Outstanding * TransSize * BurstLen / Latency`

### How to optimize Performance

- Parallel
- Pipeline
- Cache

## Examples

- optimize convolution(common case fast)
- systolic array(Parallel + Amdahl)
- using TCM/cache save temporary data for reuse(locality)
- divide SRAM into banks to provide more bandwidth(parallel)
- flexable lanes for different performance demonds(parallel)
- roofline model for CNN-DSP interface
