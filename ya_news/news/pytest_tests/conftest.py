from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news_instance = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news_instance


@pytest.fixture
def ten_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    ten_news = News.objects.bulk_create(all_news)
    return ten_news


@pytest.fixture
def comment(author, news):
    comment_instance = Comment.objects.create(
        news=news,
        text='Tекст',
        author=author,
    )
    return comment_instance


@pytest.fixture
def two_comment(author, news):
    now = timezone.now()
    for index in range(2):
        two_comment = Comment.objects.create(
            news=news,
            text=f'Tекст {index}',
            author=author,
        )
        two_comment.created = now + timedelta(days=index)
        two_comment.save()
    return two_comment


@pytest.fixture
def id_for_args(news):
    return news.id,


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def form_data():
    form_data = {
        'text': 'Comment'
    }
    return form_data
