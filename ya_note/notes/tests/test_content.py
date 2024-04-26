from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Creater')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            slug='test',
            author=cls.author,
        )
        cls.notes_list_url = reverse('notes:list')

# Отдельная заметка передаётся на страницу со списком заметок в списке
# object_list, в словаре context;
# В список заметок одного пользователя не попадают заметки другого пользователя
    def test_notes_list_for_different_users(self):
        clients = ((self.author_client, True), (self.reader_client, False))
        for parametrize_client, note_in_list in clients:
            with self.subTest(
                parametrize_client=parametrize_client,
                note_in_list=note_in_list
            ):
                response = parametrize_client.get(self.notes_list_url)
                object_list = response.context['object_list']
                if note_in_list is True:
                    self.assertIn(self.notes, object_list)
                else:
                    self.assertNotIn(self.notes, object_list)

# На страницы создания и редактирования заметки передаются формы.
    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,))
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
