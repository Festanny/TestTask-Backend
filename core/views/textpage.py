from django.views import generic

from core import mixins, models


class GenericTextPageView(mixins.TextPageMixin, generic.TemplateView):

    def _get_page_slug(self):
        return self.kwargs["page_slug"]

    def get_template_names(self):
        return [f"pages/generic_text_page.html"]

    def get_page_object(self):
        return models.TextPage.objects.get(
            is_generic_page=True,
            slug=self.page_slug
        )
