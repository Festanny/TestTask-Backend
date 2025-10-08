from django.db import models
from django.urls import reverse
from .base import BaseMenuItemModel, BaseSEOModel
from bs4 import BeautifulSoup


class TextPage(BaseMenuItemModel, BaseSEOModel):
    """Тектовая страница"""

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    is_generic_page = models.BooleanField(
        verbose_name="Является стандартной страницей",
        help_text="Снять галочку, если страница обрабатывается кастомной view",
        blank=True,
        default=False
    )

    def get_absolute_url(self):
        return reverse('text_page', kwargs={'page_slug': self.slug})


class ArticleManager(models.Manager):

    def get_published(self):
        return super().get_queryset().filter(is_published=True)


class Article(BaseSEOModel):
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    image = models.FileField(verbose_name="Изображение", upload_to="articles/", blank=True)
    publish_at = models.DateTimeField(verbose_name="Дата публикации", help_text="Используется для отложенного постинга",
                                      null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ArticleManager()

    def __str__(self):
        return self.name

    def publish(self):
        """Функция для публикации статьи"""
        self.is_published = True
        self.save()

    @property
    def next_article(self):
        return self.get_next_by_created_at()

    @property
    def previous_article(self):
        return self.get_previous_by_created_at()

    @property
    def heading_structure(self) -> list:
        """
        Метод для получения оглавления статьи на основе тегов h

        :rtype: list
        :return: Список заголовков и якорных ссылок
        """
        soup = BeautifulSoup(self.content, "html.parser")
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        return [{'header': header.get_text(), 'slug': header['id']} for header in headers]

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
