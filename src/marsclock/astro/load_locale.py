from marsclock import config

__CACHED_LOCALES = {}


def __load_locale_names(locale):
    """
    Load the month/day names for a locale and store in the caches.
    """
    print(f"Loading cache for {locale} from: {config.RESOURCE_PATH}")
    __CACHED_LOCALES[locale] = dict()
    for period in ['months', 'days']:
        __CACHED_LOCALES[locale][period] = dict()
        with open(f'{config.RESOURCE_PATH}/locale/datetime/{locale}.{period}.tsv') as fh:
            names = [l.strip().split('\t') for l in fh]
        __CACHED_LOCALES[locale][period]['abrv'] = [n[0] for n in names]
        __CACHED_LOCALES[locale][period]['full'] = [n[1] for n in names]


def get_locale(locale):
    """
    Return the month/day names for a locale. If it's not yet cached, load it.
    """
    if locale not in __CACHED_LOCALES:
        __load_locale_names(locale)
    return __CACHED_LOCALES[locale]
