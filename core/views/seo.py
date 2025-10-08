import datetime

from calendar import timegm
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import x_robots_tag
from django.contrib.sites.requests import RequestSite
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.utils.http import http_date

from core import models


def robots_txt_view(request):
    site_settings = models.SiteSettings.get()
    return HttpResponse(site_settings.robots, content_type="text/plain")


class TextPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return models.TextPage.objects.filter(slug__isnull=False, show_in_sitemap=True)


@x_robots_tag
def sitemap(
        request,
        sitemaps,
        section=None,
        template_name="sitemap.xml",
        content_type="application/xml",
):
    req_protocol = request.scheme
    req_site = RequestSite(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_urls(
                page=page, site=req_site, protocol=req_protocol))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    response = TemplateResponse(
        request, template_name, {"urlset": urls}, content_type=content_type
    )
    if hasattr(site, "latest_lastmod"):
        # if latest_lastmod is defined for site, set header so as
        # ConditionalGetMiddleware is able to send 304 NOT MODIFIED
        lastmod = site.latest_lastmod
        response["Last-Modified"] = http_date(
            timegm(
                lastmod.utctimetuple()
                if isinstance(lastmod, datetime.datetime)
                else lastmod.timetuple()
            )
        )
    return response
