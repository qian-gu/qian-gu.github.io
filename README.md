# qian-gu.github.io

Personal blog generator powered by pelican.

## Dependency

+ [pelican-plugins](https://github.com/getpelican/pelican-plugins)
+ using [Flex Theme](https://github.com/qian-gu/Flex)
+ pelican search depends on [stork](https://stork-search.net/docs/install)

## Build

```bash
# install stork
cargo install stork-search --locked
# create env
conda create -n blog python=3.8
# clone repos
git clone https://github.com/getpelican/pelican-plugins --recursive
git clone https://github.com/qian-gu/qian-gu.github.io  --recursive
cd qian-gu.github.io
# install packages
pip install -r requirements.txt
```

## Local Debug

```bash
# switch environment
conda activate blog
# rebuild
make clean
make html
```

Open the generated html pages within a browse.

## Publish

```bash
# switch environment
conda activate blog
# clean dummy and tmp file first
make clean
# publish to github
make github
```

## Save content

```bash
# switch environment
conda activate blog
# clean output
rm output -rf
# commit and push
git add .
git cmmint -m "add new post"
git push
```
