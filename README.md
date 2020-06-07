# blog_generator

Personal blog generator powered by pelican.

## Dependencies

1. [guqian110/Flex theme](https://github.com/guqian110/Flex)
2. [pelican-plugins](https://github.com/getpelican/pelican-plugins)

## Installation

```bash
git clone https://github.com/getpelican/pelican-themes
git clone https://github.com/getpelican/pelican-plugins
git clone https://github.com/guqian110/blog_generator
cd blog_generator
# custom your pelicanconfig.py and Makefile
```

## Local Debug

```bash
make clean
make html
```

Open the generated html pages with a browse for debug.

## Publish

```bash
# modifiy publishconf.py
make clean
make publish
```