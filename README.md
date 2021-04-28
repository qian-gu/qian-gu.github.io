# blog_generator

Personal blog generator powered by pelican.

## Dependency

+ [pelican-plugins](https://github.com/getpelican/pelican-plugins)

## Installation

```bash
git clone https://github.com/getpelican/pelican-plugins --recursive
git clone https://github.com/guqian110/blog_generator  --recursive
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

Push your new post to Github.
