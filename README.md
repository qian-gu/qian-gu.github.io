# blog_generator

Personal blog generator powered by pelican.

# dependencies

1. [pelican-themes](https://github.com/getpelican/pelican-themes)
2. [pelican-plugins](https://github.com/getpelican/pelican-plugins)

# installation

```bash
mkdir blog
cd blog
git clone https://github.com/getpelican/pelican-themes
git clone https://github.com/getpelican/pelican-plugins
git clone https://github.com/guqian110/blog_generator
cd blog_generator
# custom your pelicanconfig.py and Makefile
```

# write content

Write blog source markdown file in `content` folder.

# generate blog

```bash
make clean
make html
```

# publish

The generated html blog is in the output folder, just copy it to your new repo to publish it, or you can custom the Makefile to pulish automatically.
