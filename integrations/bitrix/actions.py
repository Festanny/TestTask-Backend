import pdb

from django.template import Template, Context

from . import tasks, api_urls, models


def create_lead(name, phone, email=None, **extra_fields):
    site_settings = models.Settings.objects.first()
    if site_settings.bitrix_webhook_url:
        urls = api_urls.BitrixApiUrls(site_settings.bitrix_webhook_url)

        title_template = Template(site_settings.bitrix_lead_title_template)
        title = title_template.render(Context({
            "phone": phone,
            **extra_fields
        }))

        tasks.create_lead.delay(
            urls.create_lead_url,
            site_settings.bitrix_custom_fields_map,
            title,
            name,
            phone,
            email=email,
            **extra_fields
        )
        print(1)
