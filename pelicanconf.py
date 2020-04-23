# -*- coding: utf-8 -*- #

from datetime import datetime

AUTHOR = 'Qian Gu'
SITEURL = 'http://guqian110.github.io'
SITENAME = "Qian's Blog"
SITETITLE = AUTHOR
SITESUBTITLE = 'Stay hungry. Stay foolish.'
SITEDESCRIPTION = "Qian's Thoughts and Writings"
SITELOGO = SITEURL + '/images/logo.png'
FAVICON = SITEURL + '/images/favicon.png'
BROWSER_COLOR = '#333333'

ROBOTS = 'index, follow'

JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANG = 'en'
OG_LOCALE = 'en'
LOCALE = 'en_US.utf-8'
DATE_FORMATS = {'en': '%Y-%m-%d %H:%M'}

PATH = 'content'
ARTICLE_URL = 'posts/{category}/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{category}/{slug}.html'
PAGE_URL = 'pages/{slug}.html'
PAGE_SAVE_AS = 'pages/{slug}.html'
DIRECT_TEMPLATES = {'index', 'categories', 'authors', 'archives', 'tags'}

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
HOME_HIDE_TAGS = False
PYGMENTS_STYLE = 'monokai'
USE_LESS = True
DEFAULT_PAGINATION = 10

MENUITEMS = (('Authors', '/authors.html'),
             ('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),
             )

SOCIAL = (
    ('envelope', 'mailto:guqian110@163.com'),
    ('github', 'https://github.com/guqian110'),
    ('rss', '/feeds/all.atom.xml'),
)

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = datetime.now().year

# DISQUS_SITENAME = "flex-pelican"
# ADD_THIS_ID = 'ra-55adbb025d4f7e55'

STATIC_PATHS = ['images', 'files']

CUSTOM_CSS = 'static/custom.css'


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

# THEME = '../pelican-themes/Flex'
THEME = '../Flex'
PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['i18n_subsites', 'post_stats', 'section_number', 'neighbors', 'related_posts', 'sitemap', 'pelican-toc']
GITHUB_CORNER_URL = 'https://github.com/guqian110/guqian110.github.io'
# i18n_subsites
I18N_TEMPLATES_LANG = 'zh'
# setion_number
SECTION_NUMBER_MAX = 5
#sitemap
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
# toc
TOC = {
    'TOC_HEADERS'       : '^h[1-6]', # What headers should be included in
                                     # the generated toc
                                     # Expected format is a regular expression

    'TOC_RUN'           : 'true',    # Default value for toc generation,
                                     # if it does not evaluate
                                     # to 'true' no toc will be generated

    'TOC_INCLUDE_TITLE': 'true',     # If 'true' include title in toc
}

