# Base django project

## Deploy

`sudo apt-get install redis-server build-essential libssl-dev libffi-dev python3-dev`

Устанавливаем pipenv глобально

`pip install pipenv --user`

`ln -s /home/<user>/.local/bin/pipenv /usr/bin/pipenv` (see )

Создаём файл с переменными окружения:
`cp example.env .env`

Открываем и заполняем доступы:
`nano .env`

Устанавливаем зависимости
`pipenv sync`

Создаём sites
`python manage.py create_sites domain=your_domain`


## Работа с зависимостями
См. https://pipenv.pypa.io/en/latest/pipfile
### Активация virtualenv 
`pipenv shell`

`python manage.py runserver`

### Выйти из шелла
`exit`

### Добавить новую зависимость
`pipenv install django-whatever`

После этого необходимо закоммитить `pipfile` и `pipfile.lock`

### Установить зависимости (на новую машину)
`pipenv sync`


## Доступный функционал "из коробки"

- Редактируемые через админку robots.txt, favicon, возможность вставки html в конец head и body
- Текстовые страницы (подробнее см. ниже)
- UTM метки сохраняются в session, доступны по ключу `core.constants.SessionKeys.UTM`
- Unhandled exceptions автоматически уходят в телеграм
- Пример отправки уведомлений в telegram (utils.telegram.messages)
- В контексте шаблонов доступен объект `site_settings` 
- Абстрактные модели `core.models.BaseSEOModel` и `core.models.BaseMenuItemModel`
- Подключена кастомная модель юзера (accounts.models.User)
- Контакты компании: модель `core.models.misc.CompanyContacts`, единственная запись сразу доступна в контексте по ключу `contacts`
- Extra fields, задаваемые через админку, сразу доступные в контексте в формате`extra_fields.field_key`

## Работа с текстовыми страницами (`core.models.TextPage`)

### Предполагается 2 сценария:
Страница имеет статичный контент, т.е. не требует дополнительного контекста, чтобы отрендерить шаблон.
В этом случае достаточно добавить её через админку, указать `slug=<my_slug>`, заполнить поле content (разрешен html). 
Страница сразу будет доступна по url `/page/<my_slug>/`

Страница имеет динамический контент, коорый нужно достать из базы и положить в контекст.
В этом случае можно сделать свою view, включив в наследники `core.mixins.TextPageMixin`, и задать аттрибут `page_slug`.
В кастомной вьюхе можно переопределить `get_context_data()` или всё что ещё захочется. 
Так же свою view нужно вручную прописать в urls. В данном случае, мы лишаемся возможности редактировать slug через админку (точнее он не влияет на реальный урл)

Пример 1
Кастомная вьюха с доп. контекстом
```
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
```

Пример 2
Кастомная вьюха, slug и seo данные хранятся в самой модели (а не в TextPage)
```
    models.py
        class News(BaseSEOModel):
            ...

    views.py:
        class NewsDetailView(TextPageMixin, DetailView):
            template = "news_detail.html"
            queryset = News.objects.all()
            page_slug = "does-not-matter"


    urls.py:
        urlpatterns = [
            path('page/news/<str:slug>/', views.NewsDetailView.as_view()),  # <--- Выше GenericPageView
            path('page/<str:slug>/', views.GenericPageView.as_view()),
        ]
```