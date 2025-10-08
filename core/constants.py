import enum


class SessionKeys(str, enum.Enum):
    UTM = "utm"


class AdminFields:
    SEO_FIELD = (
        'SEO информация',
        {
            "classes": ("collapse",),
            "fields": ('slug', 'show_in_sitemap', 'seo_h1', 'seo_title', 'seo_description', 'content')
        }
    )


__all__ = ["SessionKeys", "AdminFields"]
