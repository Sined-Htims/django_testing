from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


# Проверка доступности страницы для анона через client(1,2,6)
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    # arrange
    url = reverse(name, args=args)
    # act
    response = client.get(url)
    # assert
    assert response.status_code == HTTPStatus.OK


# Проверка доступа автору и другому авторизир. пользователю по ссылкам (3,5)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, args, expected_status
):
    # arrange
    url = reverse(name, args=args)
    # act
    response = parametrized_client.get(url)
    # assert
    assert response.status_code == expected_status


# Проверка редиректа (4)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_redirects(client, name, args):
    # arrange
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    # act
    response = client.get(url)
    # assert
    assertRedirects(response, expected_url)
