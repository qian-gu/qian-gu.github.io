# blog_generator

Personal blog generator powered by pelican.

# dependencies

1. [pelican-themes](https://github.com/getpelican/pelican-themes)
2. [pelican-plugins](https://github.com/getpelican/pelican-plugins)

# installation

```bash
git clone https://github.com/getpelican/pelican-themes
git clone https://github.com/getpelican/pelican-plugins
git clone https://github.com/guqian110/blog_generator
cd blog_generator
# custom your pelicanconfig.py and Makefile
```

# Local Debug

```bash
make clean
make html
```

Open the generated html pages with a browse for debug.

# publish

```bash
# modifiy publishconf.py
make clean
make publish
```