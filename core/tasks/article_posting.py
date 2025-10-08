import pdb

from django.utils import timezone

from _project_.celery import app
from core.models import Article


@app.task(name="core.tasks.publish_scheduled_articles")
def publish_scheduled_articles():
    now = timezone.now()
    articles_to_publish = Article.objects.filter(is_published=False, publish_at__lte=now)

    for article in articles_to_publish:
        article.publish()
