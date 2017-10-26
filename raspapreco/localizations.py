import gettext
import locale

try:
    LOCALE, _E = locale.getdefaultlocale()
    language = gettext.translation('bcontext', 'locale/', [LOCALE])
    language.install()
except FileNotFoundError:
    gettext.install('bcontext')
