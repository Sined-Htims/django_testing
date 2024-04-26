import pytest

from django.conf import settings
from django.urls import reverse


# Количество новостей на главной странице — не более 10. (1)
@pytest.mark.django_db  # Как это работает?
def test_news_count(ten_news, client):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


# Новости отсортированы от самой свежей к самой старой. (2)
@pytest.mark.django_db  # Как это работает?
def test_news_order(ten_news, client):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


# Комментарии на странице отдельной новости отсортированы от старых к новым (3)
def test_comments_order(client, two_comment, id_for_args):
    response = client.get(reverse('news:detail', args=id_for_args))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


# Анонимному пользователю не видна форма комментариев а авторизир. видна(4)
@pytest.mark.django_db  # Как это работает?
@pytest.mark.parametrize(
    'parametrize_client, expecting_answer',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )
)
def test_anonymous_client_has_no_form(
    id_for_args, parametrize_client, expecting_answer
):
    response = parametrize_client.get(reverse('news:detail', args=id_for_args))
    if expecting_answer is True:
        assert 'form' in response.context
    else:
        assert 'form' not in response.context
