from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.forms import WARNING
from news.models import Comment


# Анонимный пользователь не может отправить комментарий. (1)
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, id_for_args, form_data
):
    url = reverse('news:detail', args=id_for_args)
    client.post(url, data=form_data)
    comment_count = Comment.objects.count()
    assert comment_count == 0


# Авторизованный пользователь может отправить комментарий. (2)
def test_user_can_create_comment(
        author_client, author, form_data, id_for_args
):
    url = reverse('news:detail', args=id_for_args)
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


# Если комментарий содержит запрещённые слова, он не будет опубликован... (3)
def test_user_cant_use_bad_words(admin_client, form_data, id_for_args):
    url = reverse('news:detail', args=id_for_args)
    form_data['text'] = 'негодяй'
    response = admin_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


# Авторизованный пользователь может edit или delete свои комментарии. (4)
def test_author_can_edit_comment(
        author_client, form_data, comment_id_for_args, comment
):
    url = reverse('news:edit', args=comment_id_for_args)
    author_client.post(url, form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_note(author_client, comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    author_client.post(url)
    assert Comment.objects.count() == 0


# Авторизованный пользователь не может edit или delete чужие комментарии. (5)
def test_other_user_cant_edit_comment(
        admin_client, form_data, comment, comment_id_for_args
):
    url = reverse('news:edit', args=comment_id_for_args)
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_other_user_cant_delete_comment(admin_client, comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
