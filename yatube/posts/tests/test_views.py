import shutil
import tempfile

from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.utils import check_post_exist
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
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

    def setUp(self):
        cache.clear()

    def test_check_views_context(self):
        """Проверим контекст страницы group_list"""
        response_index = self.authorized_client.get(ADRESS_INDEX)
        response_groop = self.authorized_client.get(self.GROUP_REVERSE)
        response_prof = self.authorized_client.get(self.PROFILE_REVERSE)
        response_detail = self.authorized_client.get(self.DETAIL_REVERSE)
        MU_DICT = {
            tuple(response_index.context['page_obj']):
            tuple(Post.objects.all()[:settings.NUMBER_OF_POSTS]),
            response_groop.context[
                'page_obj'][0].group.slug: self.group.slug,
            response_prof.context[
                'page_obj'][0].author.username: self.user.username,
            response_detail.context['post']: self.post,
            response_detail.context['comments'][0]: self.comment
        }
        for context, expected in MU_DICT.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

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
        """до сих пор без понятия что должно произойти"""
        self.following.delete()
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

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_first_page_contains_correct_num_records(self):
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

    def test_second_page_contains_correct_num_records(self):
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

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
