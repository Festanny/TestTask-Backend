from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core import models


class TextPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return models.TextPage.objects.filter(is_generic_page=True, show_in_sitemap=True)


class IndexSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['core:index']

    def location(self, item):
        return reverse(item)


class StaticViewsSitemap(Sitemap):
    """Reverse 'static' views for XML sitemap."""
    changefreq = "daily"
    priority = 0.5

    def items(self):
        # Return list of url names for views to include in sitemap
        return ["contacts"]

    def location(self, item):
        return reverse(item)
