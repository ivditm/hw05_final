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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_auhtor = Client()
        self.authorized_client_not_auhtor.force_login(self.user1)

    def test_free_pages_exist_at_desired_location(self):
        """Проверяем общедоступные страницы"""
        res_home = self.guest_client.get(URL_INDEX)
        res_groups = self.guest_client.get(
            self.GROUP_REVERSE
        )
        res_prof = self.guest_client.get(
            self.PROFILE_REVERSE
        )
        res_post = self.guest_client.get(
            self.DETAIL_REVERSE
        )
        res_unexist = self.guest_client.get(URL_UNEXISTING)
        test_dict = {
            res_home: HTTPStatus.OK,
            res_groups: HTTPStatus.OK,
            res_prof: HTTPStatus.OK,
            res_post: HTTPStatus.OK,
            res_unexist: HTTPStatus.NOT_FOUND
        }
        for response, expected_value in test_dict.items():
            with self.subTest(response=response):
                self.assertEqual(
                    response.status_code, expected_value, 'oops!')

    def test_url_exists_at_desired_location_authorized(self):
        """Проверим, что создать пост может только
           авторизованный пользователь"""
        res_create = self.authorized_client.get(URL_CREATE)
        self.assertEqual(
            res_create.status_code, HTTPStatus.OK, 'что-то не так с create'
        )

    def test_url_exists_at_desired_location_for_author(self):
        """Проверим, что автор может редактировать пост"""
        res_edit = self.authorized_client.get(
            self.EDIT_REVERSE
        )
        self.assertEqual(res_edit.status_code, HTTPStatus.OK,
                         'что-то не так с редактированием')

    def test_redirect_create(self):
        """Проверяем, что неавторизованный пользователь
           перенапрявдяется на страницу логина"""
        resp = self.guest_client.get(URL_CREATE, follow=True)
        self.assertRedirects(resp, URL_LOGIN + URL_CREATE)

    def test_redirect_edit(self):
        """Проверим, что не автор переадресуется на страницу поста"""
        resp = self.authorized_client_not_auhtor.get(
            self.EDIT_REVERSE,
            follow=True
        )
        self.assertRedirects(resp, self.DETAIL_REVERSE)

    def test_comment(self):
        """Проверим, что неавторизованный пользователь,
        не сможет оставить комментарий"""
        resp_fail = self.guest_client.get(self.COMMENT_REVERSE)
        self.assertRedirects(resp_fail,
                             URL_LOGIN + self.COMMENT_REVERSE)

    def test_follow_prof(self):
        """Проверим, что подписываться/отписываться
        могут только авторизированные пользователи"""
        resp_follow = self.guest_client.get(
            self.REVERSE_PROF_FOLLOW
        )
        resp_unfollow = self.guest_client.get(
            self.REVERSE_PROF_UNFOLLOW
        )
        TEST_DICT = {
            resp_follow: self.REVERSE_PROF_FOLLOW,
            resp_unfollow: self.REVERSE_PROF_UNFOLLOW
        }
        for resp, rev in TEST_DICT.items():
            with self.subTest(resp=resp):
                self.assertRedirects(resp, URL_LOGIN + rev)

    def test_check_follow(self):
        resp = self.authorized_client.get(REVERSE_FOLLOW)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_template(self):
        """Проверим использование шаблонов"""
        for adress, template in self.TEST_DICT.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
