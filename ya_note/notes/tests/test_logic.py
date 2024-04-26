from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNote(TestCase):
    DEFULT_TITLE = 'Заголовок'
    SLUG_NOTE = 'title'
    CHECK_TITLE = 'Проверка слага'
    NOTE_TEXT = 'Note text'
    NOTE_UPDATE_TEXT = 'Note update text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Creater')
        cls.reader = User.objects.create(username='Reader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.DEFULT_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.SLUG_NOTE,
            author=cls.author,
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_add = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.CHECK_TITLE,
            'text': cls.NOTE_TEXT,
        }
        cls.form_edit_data = {
            'title': cls.DEFULT_TITLE,
            'text': cls.NOTE_UPDATE_TEXT,
            'slug': cls.SLUG_NOTE
        }

# Проверка анонимный посетитель не может создать заметку (1)
    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url_add, data=self.form_data)
        note_count = Note.objects.count()
        # Ожидаем, что в БД будет одна заметка,
        # т.к. в setUp-е изначально создана одна заметка для другого теста.
        self.assertEqual(
            note_count, 1, msg='В БД проблемы с кол-вом записей'
        )

# Юзер может создать заметку + автотранслит названия замтеки в слаг (1, 3)
    def test_user_can_create_note_and_slug(self):
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(
            response,
            self.url_done,
            msg_prefix='Редирект, не произошел, дальнейший тест остановлен'
        )
        note_count = Note.objects.count()
        # Убеждаемся, что есть две заметки. Т.к. одна уже существует в БД
        # для другого теста
        self.assertEqual(note_count, 2, msg='В БД проблемы с кол-вом записей')
        note = Note.objects.last()
        self.assertEqual(note.title, self.CHECK_TITLE, msg='Проблема в тайтле')
        self.assertEqual(note.text, self.NOTE_TEXT, msg='Проблема в тексте')
        self.assertEqual(note.author, self.author, msg='Проблема в авторе')
        self.assertEqual(
            note.slug, slugify(self.CHECK_TITLE), msg='Проблема в слаге'
        )

# Проверка невозможности создания заметки с одинаковым slug-ом (2)
    def test_user_cant_use_busy_slug(self):
        self.form_data.update({'slug': self.SLUG_NOTE})
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG_NOTE + WARNING
        )
        note_count = Note.objects.count()
        # Ожидаем, что в БД будет одна заметка,
        # т.к. в setUp-е изначально создана одна заметка для другого теста.
        self.assertEqual(
            note_count, 1, msg='В БД проблемы с кол-вом записей'
        )

# Проверка удаления заметки автором (4)
    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(
            response,
            self.url_done,
            msg_prefix='Редирект, не произошел, дальнейший тест остановлен'
        )
        note_count = Note.objects.count()
        # Ожидаем ноль заметок в системе.
        self.assertEqual(
            note_count, 0, msg='В БД проблемы с кол-вом записей'
        )

# Проверка невозможности удаления чужой заметки (4)
    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что запись по-прежнему на месте.
        note_count = Note.objects.count()
        self.assertEqual(
            note_count, 1, msg='В БД проблемы с кол-вом записей'
        )

# Проверка изменения заметки автром (4)
    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.url_edit, data=self.form_edit_data
        )
        self.assertRedirects(
            response,
            self.url_done,
            msg_prefix='Редирект, не произошел, дальнейший тест остановлен'
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text,
            self.NOTE_UPDATE_TEXT,
            msg='Изменения в БД не произошли'
        )

# Проверка невозможности изменить пользователем чужую заметку (4)
    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(
            self.url_edit, data=self.form_edit_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text, self.NOTE_TEXT, msg='Изменения в БД произошли'
        )
