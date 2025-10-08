import pdb

from django.http import Http404

from . import models


class TextPageMixin:
    """
    Достаёт TextPage на каждый GET запрос, кладёт его в контекст
    Возвращает 404 если TextPage не найдена
    В дочерней view необходимо задать page_slug, либо переопределить _get_page_slug()

    Пример использования:

    views.py:
        class FAQView(TextPageMixin, TemplateView):
            template = "faq.html"
            page_slug = "faq"

            # Не получается использовать GenericTextPageView, нужен доп. контекст
            def get_context_data(self, context):
                ctx = super().get_context_data(context)
                ctx["questions"] = Question.objets.all()
                return ctx

    urls.py:
        urlpatterns = [
            path('page/faq/', views.FAQView.as_view()),  # <--- Выше GenericPageView
            path('page/<str:slug>/', views.GenericPageView.as_view()),
        ]

    """

    page_slug = None

    def _get_page_slug(self):
        if self.page_slug is not None:
            # slug был явно перопределен в дочернем классе
            # Значит это "статичная" вьюха
            return self.page_slug
        else:
            # Пытаемся достать slug из url
            # Кейс для generic страницы
            return self.kwargs["page_slug"]

    def get_page_object(self):
        return models.TextPage.objects.get(slug=self.page_slug)

    def get(self, request, *args, **kwargs):
        self.page_slug = self._get_page_slug()
        try:
            self.text_page_obj = self.get_page_object()
        except models.TextPage.DoesNotExist:
            raise Http404()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["seo_object"] = self.text_page_obj
        return ctx


class CanonicalMixin:
    """
    Проверяет наличие  GET query,  добавляет в контекст пометку is_canonical
    При наличии параметров is_canonical принимает значение False, при отсутствии True
    """

    is_canonical: bool = False
    canonical_url: str

    def get(self, request, *args, **kwargs):
        self.is_canonical = len(request.GET.dict()) == 0
        self.canonical_url = request.build_absolute_uri()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "is_canonical": self.is_canonical,
            "canonical_url": self.canonical_url,
        })
        return context
