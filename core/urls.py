from django.urls import path
from django.views.generic import TemplateView

from . import views

sitemaps = {
    'index': views.IndexSitemap,
    'textpage': views.TextPageSitemap,
    'staticviews': views.StaticViewsSitemap,
}
app_name = 'core'

urlpatterns = [
    path('', TemplateView.as_view(**{"template_name": "base.html"}), name="index"),
    path('page/<slug:page_slug>/', views.GenericTextPageView.as_view(), name="text_page"),

    path('sitemap.xml', views.sitemap, {'sitemaps': sitemaps}),
    path('robots.txt', views.robots_txt_view),
]
