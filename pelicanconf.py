# -*- coding: utf-8 -*- #

from datetime import datetime

AUTHOR = 'Qian Gu'
SITEURL = ''
SITENAME = "Qian's Blog"
SITETITLE = AUTHOR
SITESUBTITLE = u"Read >> Think >> Write"
SITEDESCRIPTION = "Qian's Thoughts and Writings"
SITELOGO = SITEURL + '/images/logo.png'
FAVICON = SITEURL + '/images/favicon_64x64.ico'
BROWSER_COLOR = '#333333'
RELATIVE_URLS = True

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
DIRECT_TEMPLATES = {'index', 'categories', 'authors', 'archives', 'tags', 'search'}

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
HOME_HIDE_TAGS = False
PYGMENTS_STYLE = 'monokai'
# USE_LESS = True
DEFAULT_PAGINATION = 10

MENUITEMS = (('Authors', '/authors.html'),
             ('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),
             )

SOCIAL = (
    ('envelope', 'mailto:guqian110@163.com'),
    ('github', 'https://github.com/qian-gu'),
    ('twitter', 'https://twitter.com/qian_gu'),
    ('rss', '/feeds/all.atom.xml'),
)

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = datetime.now().year

DISQUS_SITENAME = "ChienGu"
# ADD_THIS_ID = 'ra-55adbb025d4f7e55'

STATIC_PATHS = ['images', 'files']

# CUSTOM_CSS = 'static/custom.css'


LINKS_IN_NEW_TAB = True

GOOGLE_ADSENSE = {
    'ca_id': 'ca-pub-1821536199377100',
    'page_level_ads': True,
    'ads': {
        'aside': '',
        'main_menu': '',
        'index_top': '',
        'index_bottom': '1124188687',
        'article_top': '',
        'article_bottom': '4843941849',
    }
}
GOOGLE_ANALYTICS = "UA-48826831-1"

# THEME = '../pelican-themes/Flex'
THEME = 'Flex'
PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['i18n_subsites', 'cjk-auto-spacing', 'neighbors', 'related_posts', 
           'sitemap', 'representative_image', 'tipue_search', 'render_math', 'series'
          ]
GITHUB_CORNER_URL = 'https://github.com/qian-gu/qian-gu.github.io'
# i18n_subsites
I18N_TEMPLATES_LANG = 'en'
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

### dark mode
THEME_COLOR = 'ligtht'
THEME_COLOR_AUTO_DETECT_BROWSER_PREFERENCE = True
THEME_COLOR_ENABLE_USER_OVERRIDE = True

PYGMENTS_STYLE = 'monokai'
PYGMENTS_STYLE_DARK = 'monokai'

## render_math
MATH_JAX = {'color': 'blue'}
## cjk-auto-spacing
CJK_AUTO_SPAING_TITLE = True

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite' : {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.admonition' :{},
        'markdown.extensions.toc': {},
    },
    'output_format': 'html5'
}
