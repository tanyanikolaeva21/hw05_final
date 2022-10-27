from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username='test_user',
                email='test@mail.ru',
                password='test_pass'),
            text='Тестовая запись для создания нового поста',
        )

        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Stesha')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home(self):
        """страница главная доступна всем"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group(self):
        """страница группы доступна всем"""
        response = self.guest_client.get(reverse('posts:group_posts', kwargs={
            'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_guest_on_login(self):
        """Страница /create/ перенаправит неавторизованного пользователя
        на страницу логина."""
        response = self.client.get(reverse('posts:post_create'), follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_posts', kwargs={
                'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': self.post.author}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /unexisting_page/."""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
