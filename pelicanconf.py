# -*- coding: utf-8 -*- #

from datetime import datetime

AUTHOR = 'Qian Gu'
SITEURL = 'http://guqian110.github.io'
SITENAME = AUTHOR
SITETITLE = "Qian's Blog"
SITESUBTITLE = 'Stay hungry. Stay foolish.'
SITEDESCRIPTION = "Qian's Thoughts and Writings"
SITELOGO = 'images/logo.png'
FAVICON = 'images/favicon.png'
BROWSER_COLOR = '#333333'
PYGMENTS_STYLE = 'monokai'

ROBOTS = 'index, follow'

PATH = 'content'
THEME = '../pelican-themes/Flex'
TIMEZONE = 'Asia/Shanghai'

ARTICLE_URL = 'posts/{category}/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{category}/{slug}.html'
PAGE_URL = 'pages/{slug}.html'
PAGE_SAVE_AS = 'pages/{slug}.html'
DIRECT_TEMPLATES = {'index', 'categories', 'authors', 'archives', 'tags'}

I18N_TEMPLATES_LANG = 'zh'
DEFAULT_LANG = 'zh'
OG_LOCALE = 'zh_CN'
LOCALE = 'zh_CN'

DATE_FORMATS = {'zh': '%Y-%m-%d %H:%M'}

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
HOME_HIDE_TAGS = False

SOCIAL = (
    ('envelope-o', 'mailto:guqian110@163.com'),
    ('github', 'https://github.com/guqian110'),
    ('rss', '/feeds/all.atom.xml'),
)

MENUITEMS = (('Authors', '/authors.html'),
             ('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),
             )

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = datetime.now().year
DEFAULT_PAGINATION = 10

# DISQUS_SITENAME = "flex-pelican"
# ADD_THIS_ID = 'ra-55adbb025d4f7e55'

STATIC_PATHS = ['images', 'files']

CUSTOM_CSS = 'static/custom.css'

USE_LESS = True

LINKS_IN_NEW_TAB = 'external'

# GOOGLE_ADSENSE = {
#     'ca_id': 'ca-pub-6625957038449899',
#     'page_level_ads': True,
#     'ads': {
#         'aside': '8752710348',
#         'main_menu': '',
#         'index_top': '',
#         'index_bottom': '1124188687',
#         'article_top': '',
#         'article_bottom': '4843941849',
#     }
# }

JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['i18n_subsites', 'neighbors', 'related_posts', 'series', 'sitemap']
GITHUB_CORNER_URL = 'https://github.com/guqian110/guqian110.github.io'
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.6,
        'indexes': 0.6,
        'pages': 0.5,
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly',
    }
}
