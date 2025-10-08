import logging

from django.utils.functional import SimpleLazyObject

from . import models

logger = logging.getLogger(__name__)


def site_settings(request):

    def get_settings_or_empty():
        try:
            return models.SiteSettings.get()
        except (models.SiteSettings.DoesNotExist, models.SiteSettings.MultipleObjectsReturned) as e:
            logger.warning("Got error when loading SiteSettings, use an empty settings instead")
            return models.SiteSettings()

    return {
        "site_settings": SimpleLazyObject(get_settings_or_empty),
    }


def company_contacts(request):
    return {
        "contacts": models.CompanyContacts.objects.first()
    }


def extra_fields(request):
    return {
        "extra_fields": {
            f.key: f for f in models.ExtraFields.objects.all()
        }
    }


def text_pages(request):
    pages = models.TextPage.objects.order_by("menu_position", "pk")
    return {
        "text_pages": {
            p.slug: p for p in pages
        }
    }
