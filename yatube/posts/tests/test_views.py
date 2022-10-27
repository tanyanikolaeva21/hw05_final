from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, Follow
from django.core.cache import cache

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stesha')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='test_slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = self.post.id
        slug = self.group.slug
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': slug}),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user}),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html,
         чтобы отредактировать пост."""
        post_id = self.post.id
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_index_page_show_correct_context(self):
        """Шаблон posts/index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон posts/group_list.html сформирован с правильным контекстом."""
        slug = self.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': slug})
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)

    def test_cache_index(self):
        """Тест кэша страницы index.html"""
        first_state = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)


class FollowTests(TestCase):
    def setUp(self):
        self.client_authorized_follower = Client()
        self.client_authorized_following = Client()
        self.user_follower = User.objects.create_user(username='follower',
                                                      email='test@mail.ru',
                                                      password='pass')
        self.user_following = User.objects.create_user(username='following',
                                                       email='test1@mail.ru',
                                                       password='pass')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Текст поста'
        )
        self.client_authorized_follower.force_login(self.user_follower)
        self.client_authorized_following.force_login(self.user_following)

    def test_follow(self):
        self.client_authorized_follower.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Пост не появился в ленте у неподписанного пользователя"""
        self.client_authorized_follower.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.user_following.username}))
        self.client_authorized_follower.get(
            reverse('posts:profile_unfollow', kwargs={
                'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """пост появляется в ленте подписчика"""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.client_authorized_follower.get(
            reverse('posts:follow_index'))
        post_text_0 = response.context['page_obj'][0].text
        self.assertEqual(post_text_0, 'Текст поста')
        response = self.client_authorized_following.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response, 'Текст поста')
