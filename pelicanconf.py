#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Qian Gu'
SITENAME = u"Qian's Blog"
SITEURL = 'https://guqian110.github.io'


TIMEZONE = 'Asia/Shanghai'
DATE_FORMATS = {'zh':'%Y-%m-%d %H:%M'}

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'))
         

# Social widget
SOCIAL = (('Email', 'mailto:guqian110@163.com', 'envelope'),
          ('Github', 'http://github.com/guqian110'))

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# path
PATH = 'content'
STATIC_PATHS = ['images', 'files']
ARTICLE_URL = 'posts/{category}/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{category}/{slug}.html'
PAGE_URL = 'pages/{slug}.html'
PAGE_SAVE_AS = 'pages/{slug}.html'
DIRECT_TEMPLATES = {'index', 'categories', 'authors', 'archives', 'search'}

# article info
SHOW_ARTICLE_AUTHOR = True
SHOW_ARTICLE_CATEORY = True
SHOW_DATE_MODIFIED = True
DISPLAY_ARTICLE_INFO_ON_INDEX = True
DISPLAY_PAGES_ON_MENU = True

# pygemnts
PYGEMNTS_STYLE = 'monokai'

# site brand
SITELOGO = 'images/logo.png'
SITELOGO_SIZE = 32

# breadcrumbs
BOOTSTRAP_NAVBAR_INVERSE = True
DISPLAY_BREADCRUMBS = True
DISPLAY_CATEGORY_IN_BREADCRUMBS = True
DISPLAY_ARCHIVES_IN_BREADCRUMBS = True

# favicon
FAVICON = 'images/favicon.png'

# about me
ABOUT_ME = 'Icer + BYR'
AVATAR = 'images/logo.png'

# content license
CC_LICENSE = 'CC-BY-NC'

# github
GITHUB_USER = 'guqian110'

# GITHUB_URL = 'https://github.com/guqian110'
DISPLAY_TAGS_INLINE = True

# sidebar image
# SIDEBAR_IMAGES = ['images/logo.png']

# theme bootstrap3 cfg
THEME = '../pelican-themes/pelican-bootstrap3'
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

# ############################# plugins ##############################
PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['i18n_subsites', 'tag_cloud', 'related_posts', 'series', 'tipue_search', 'liquid_tags', 'sitemap', ]
# series
SHOW_SERIES = True
# tag cloud
TAG_CLOUD_MAX_ITEMs = 20
# disqus
DISQUS_ID_PREFIX_SLUG = True
DISQUS_SITENAME = 'guqian110'
# site map
SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.7,
        "indexes": 0.5,
        "pages": 0.3,
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly",
    }
}
