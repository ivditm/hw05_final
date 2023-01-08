import shutil
import tempfile

from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.common import check_post_exist
from posts.models import Comment, Follow, Group, Post, User


ADRESS_INDEX = reverse('posts:index')
ADRESS_CREATE = reverse('posts:post_create')
EMPTY = 0
REVERSE_FOLLOW = reverse('posts:follow_index')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

MY_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='my.gif',
    content=MY_GIF,
    content_type='image/gif'
)
PATH_TO_PICTURE = 'posts/my.gif'


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='ALADIN')
        cls.user1 = User.objects.create_user(username='OBI')
        cls.user2 = User.objects.create_user(username='Жасмин')

        cls.group = Group.objects.create(
            title='TEST',
            slug='TOSKA',
            description='HZ'
        )
        cls.group1 = Group.objects.create(
            title='TEST1',
            slug='OOOPS',
            description='TEST1'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )
        cls.post1 = Post.objects.create(
            text='Тестовый текст2',
            group=cls.group,
            author=cls.user1,
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст1',
            group=cls.group1,
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            text='hello',
            author=cls.user,
            post=cls.post
        )
        cls.following = Follow.objects.create(
            user=cls.user,
            author=cls.user1
        )
        cls.following1 = Follow.objects.create(
            user=cls.user2,
            author=cls.user
        )
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.user.username])
        cls.EDIT_REVERSE = reverse('posts:post_edit', args=[cls.post.pk])
        cls.DETAIL_REVERSE = reverse('posts:post_detail', args=[cls.post.pk])
        cls.GROUP_REVERSE = reverse('posts:group_list', args=[cls.group.slug])
        cls.COMMENT_REVERSE = reverse('posts:add_comment', args=[cls.post.pk])
        cls.REVERSE_PROF_FOLLOW = reverse('posts:profile_follow', args=[
            cls.user.username
        ])
        cls.REVERSE_PROF_UNFOLLOW = reverse('posts:profile_unfollow', args=[
            cls.user.username
        ])

        cls.TEST_DICT = {
            ADRESS_INDEX: 'posts/index.html',
            cls.GROUP_REVERSE: 'posts/group_list.html',
            cls.PROFILE_REVERSE: 'posts/profile.html',
            cls.DETAIL_REVERSE: 'posts/post_detail.html',
            ADRESS_CREATE: 'posts/post_create.html',
            cls.EDIT_REVERSE: 'posts/post_create.html',
            REVERSE_FOLLOW: 'posts/follow.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_using_correct_template(self):
        '''Проверим корректность template'''
        for reverse_name, template in self.TEST_DICT.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_check_index_context(self):
        """Проверим контекст страницы index"""
        response = self.authorized_client.get(ADRESS_INDEX)
        self.assertEqual(list(response.context['page_obj']),
                         list(Post.objects.all())[:settings.NUMBER_OF_POSTS])

    def test_check_group_list_context(self):
        """Проверим контекст страницы group_list"""
        response = self.authorized_client.get(self.GROUP_REVERSE)
        for post in list(response.context['page_obj']):
            with self.subTest(post=post):
                self.assertEqual(post.group.slug, self.group.slug)

    def test_check_profile_context(self):
        """проверим контекст страницы профайл"""
        response = self.authorized_client.get(self.PROFILE_REVERSE)
        for post in response.context['page_obj']:
            post_author = post.author.username
        self.assertEqual(post_author, self.user.username)

    def test_check_post_detail_contex(self):
        """Проверим контекст страницы post_detail"""
        response = self.authorized_client.get(self.DETAIL_REVERSE)
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['comments'][0], self.comment)

    def test_cache(self):
        """Проверим работу кэша"""
        my_post = Post.objects.create(
            text='это переделать заставят',
            author=self.user
        )
        response_1 = self.authorized_client.get(ADRESS_INDEX)
        my_post.delete()
        response_2 = self.authorized_client.get(ADRESS_INDEX)
        self.assertEqual(response_1.content, response_2.content)

    def test_check_forms_posts_context(self):
        resp_post_create = self.authorized_client.get(ADRESS_CREATE)
        resp_post_edit = self.authorized_client.get(self.EDIT_REVERSE)
        test_list = [resp_post_create, resp_post_edit]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for response in test_list:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_check_form_comment(self):
        resp = self.authorized_client.get(self.DETAIL_REVERSE)
        form_field = resp.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_suplement_check(self):
        """Проверим что пост не попадет в другую группу"""
        res_list_group = self.authorized_client.get(self.GROUP_REVERSE)
        response_list = [self.authorized_client.get(ADRESS_INDEX),
                         res_list_group,
                         self.authorized_client.get(self.PROFILE_REVERSE)]
        for response in response_list:
            self.assertTrue(check_post_exist(self.post, response))
        for post in res_list_group.context['page_obj']:
            post_group = post.group.slug
            self.assertNotEqual(post_group, self.group1.slug)

    def test_check_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей"""
        response = self.authorized_client.get(REVERSE_FOLLOW)
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user1)

    def test_more_check_follow(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан."""
        new_post = Post.objects.create(
            text='не переделывай меня',
            author=self.user1
        )
        response = self.authorized_client.get(REVERSE_FOLLOW)
        response_fail = self.authorized_client2.get(REVERSE_FOLLOW)
        self.assertTrue(new_post in response.context['page_obj'])
        self.assertFalse(new_post in response_fail.context['page_obj'])

    def test_unfollow(self):
        """без понятия что должно произойти"""
        self.following.delete()
        # А В ЧЕМ ПРОВЕРКА-ТО?
        response = self.authorized_client.get(REVERSE_FOLLOW)
        self.assertEqual(len(list(response.context['page_obj'])), EMPTY)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test')

        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='trash',
            description='создана для тестирования'
        )
        cls.NUM_OF_POSTS = 12
        cls.POSTS_SECONDE_PAGE = 2
        posts = [Post(text=f'text{i}', group=cls.group, author=cls.user)
                 for i in range(cls.NUM_OF_POSTS)]
        cls.posts = Post.objects.bulk_create(posts)
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.user.username])
        cls.GROUP_REVERSE = reverse('posts:group_list', args=[cls.group.slug])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Проверим паджинатор на первой странице"""
        res_index = self.authorized_client.get(ADRESS_INDEX)
        res_list_group = self.authorized_client.get(self.GROUP_REVERSE)
        res_prof = self.authorized_client.get(self.PROFILE_REVERSE)
        TEST_DICT = {
            res_index: settings.NUMBER_OF_POSTS,
            res_list_group: settings.NUMBER_OF_POSTS,
            res_prof: settings.NUMBER_OF_POSTS
        }
        for response, expected in TEST_DICT.items():
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        """Проверим паджинатор на второй странице"""
        res_index = self.authorized_client.get(ADRESS_INDEX + '?page=2')
        res_list_group = self.authorized_client.get(
            self.GROUP_REVERSE + '?page=2'
        )
        res_prof = self.authorized_client.get(
            self.PROFILE_REVERSE + '?page=2'
        )
        TEST_DICT = {
            res_index: self.POSTS_SECONDE_PAGE,
            res_list_group: self.POSTS_SECONDE_PAGE,
            res_prof: self.POSTS_SECONDE_PAGE
        }
        for response, expected in TEST_DICT.items():
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj']), expected)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageCheck (TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='WTF',
            id=1)

        cls.group = Group.objects.create(
            title='TEST',
            slug='TEST',
            description='С ПРОЩЕДЩИМИ ПРАЗДНИКАМИ!'
        )
        cls.post = Post.objects.create(
            text='Я - КОНСТАНТА?',
            group=cls.group,
            author=cls.user,
            image=UPLOADED
        )
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.user.username])
        cls.DETAIL_REVERSE = reverse('posts:post_detail', args=[cls.post.pk])
        cls.GROUP_REVERSE = reverse('posts:group_list', args=[cls.group.slug])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_image(self):
        """Проверим, что картинка передается
        на страницы: index, profile, group_list"""
        my_list = [ADRESS_INDEX, self.PROFILE_REVERSE,
                   self.GROUP_REVERSE]
        for my_reverse in my_list:
            with self.subTest(my_reverse=my_reverse):
                response = self.authorized_client.get(my_reverse)
                obj = response.context["page_obj"][0]
                self.assertEqual(obj.image, self.post.image)

    def test_check_image_post_detail(self):
        response = self.authorized_client.get(self.DETAIL_REVERSE)
        obj = response.context["post"]
        self.assertEqual(obj.image, self.post.image)
