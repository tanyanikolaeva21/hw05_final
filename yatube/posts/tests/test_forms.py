from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='stesha')
        cls.group = Group.objects.create(
            title='название',
            slug='slug',
            description='описание'
        )

    def setUp(self):
        self.user = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_by_login_user(self):
        """Проверка создания поста"""
        count = Post.objects.count()
        form_data = {
            'text': 'тестирование',
            'group': self.group.id,
        }
        url = reverse('posts:post_create')
        response = self.author_client.post(url, data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.author.username}))
        self.assertEqual(Post.objects.count(), count + 1)

    def test_post_edit(self):
        post = Post.objects.create(
            text='тестирование',
            author=self.author,
            group=self.group,
            id=1,
        )
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'тестирование',
            'group': self.group.id,
            'image': uploaded,
        }
        url = reverse('posts:post_detail', kwargs={'post_id': post.id})
        response = self.author_client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])

