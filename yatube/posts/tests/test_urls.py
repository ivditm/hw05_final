from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User


URL_INDEX = '/'
URL_CREATE = '/create/'
URL_UNEXISTING = '/unexisting_page/'
URL_LOGIN = '/auth/login/?next='
REVERSE_FOLLOW = reverse('posts:follow_index')


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TESTIK')
        cls.user1 = User.objects.create_user(username='TESTIKOVICH')

        cls.group = Group.objects.create(
            title='TEST',
            slug='TOSKA',
            description='TEST'
        )

        cls.post = Post.objects.create(
            text='TEST',
            group=cls.group,
            author=cls.user
        )

        cls.commement = Comment.objects.create(
            text='TEST',
            author=cls.user,
            post=cls.post
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
            URL_INDEX: 'posts/index.html',
            cls.GROUP_REVERSE: 'posts/group_list.html',
            cls.PROFILE_REVERSE: 'posts/profile.html',
            cls.DETAIL_REVERSE: 'posts/post_detail.html',
            URL_CREATE: 'posts/post_create.html',
            cls.EDIT_REVERSE: 'posts/post_create.html',
            REVERSE_FOLLOW: 'posts/follow.html',
        }
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_not_auhtor = Client()
        cls.authorized_client_not_auhtor.force_login(cls.user1)

    def test_free_pages_exist_at_desired_location(self):
        """Проверяем страницы"""
        DICT = {
            self.guest_client: {
                URL_INDEX: HTTPStatus.OK,
                URL_UNEXISTING: HTTPStatus.NOT_FOUND,
                URL_LOGIN: HTTPStatus.OK,
                self.PROFILE_REVERSE: HTTPStatus.OK,
                self.DETAIL_REVERSE: HTTPStatus.OK,
                self.GROUP_REVERSE: HTTPStatus.OK
            },
            self.authorized_client: {
                URL_CREATE: HTTPStatus.OK,
                REVERSE_FOLLOW: HTTPStatus.OK,
                self.EDIT_REVERSE: HTTPStatus.OK
            }
        }
        for client, second_dict in DICT.items():
            for url, status in second_dict.items():
                with self.subTest(url=url):
                    self.assertEqual(
                        client.get(url).status_code, status, 'oops!')

    def test_redirect(self):
        """Проверим редиректы"""
        resp_follow = self.guest_client.get(
            self.REVERSE_PROF_FOLLOW
        )
        resp_unfollow = self.guest_client.get(
            self.REVERSE_PROF_UNFOLLOW
        )
        resp_edit = self.authorized_client_not_auhtor.get(
            self.EDIT_REVERSE,
            follow=True
        )
        resp_comment = self.guest_client.get(self.COMMENT_REVERSE)
        resp_create = self.guest_client.get(URL_CREATE, follow=True)

        TEST_DICT = {
            resp_follow: URL_LOGIN + self.REVERSE_PROF_FOLLOW,
            resp_unfollow: URL_LOGIN + self.REVERSE_PROF_UNFOLLOW,
            resp_edit: self.DETAIL_REVERSE,
            resp_comment: URL_LOGIN + self.COMMENT_REVERSE,
            resp_create: URL_LOGIN + URL_CREATE

        }
        for resp, rev in TEST_DICT.items():
            with self.subTest(resp=resp):
                self.assertRedirects(resp, rev)

    def test_template(self):
        """Проверим использование шаблонов"""
        for adress, template in self.TEST_DICT.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
