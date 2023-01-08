from django.test import TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User

URL_INDEX = '/'
URL_CREATE = '/create/'
REVERSE_INDEX = reverse('posts:index')
REVERSE_CREATE = reverse('posts:post_create')
ADRESS_GROUP = '/group/TOSKA/'
ADRESS_PROFILE = '/profile/ALADIN/'
ADRESS_POST = '/posts/1/'
ADRESS_EDIT = '/posts/1/edit/'
URL_FOLLOW = '/follow/'
REVERSE_FOLLOW = reverse('posts:follow_index')
ADRESS_COMMENT = '/posts/1/comment/'
ADRESS_PROF_FOLLOW = '/profile/ALADIN/follow/'
ADRESS_PROF_UNFOLLOW = '/profile/ALADIN/unfollow/'


class RoutesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='ALADIN')

        cls.group = Group.objects.create(
            title='TEST',
            slug='TOSKA',
            description='HZ'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            text='С РОЖДЕСТВОМ',
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
            REVERSE_INDEX: URL_INDEX,
            cls.GROUP_REVERSE: ADRESS_GROUP,
            cls.PROFILE_REVERSE: ADRESS_PROFILE,
            cls.DETAIL_REVERSE: ADRESS_POST,
            REVERSE_CREATE: URL_CREATE,
            cls.EDIT_REVERSE: ADRESS_EDIT,
            REVERSE_FOLLOW: URL_FOLLOW,
            cls.REVERSE_PROF_FOLLOW: ADRESS_PROF_FOLLOW,
            cls.REVERSE_PROF_UNFOLLOW: ADRESS_PROF_UNFOLLOW,
            cls.COMMENT_REVERSE: ADRESS_COMMENT
        }

    def test_using_correct_template(self):
        for reverse_name, adress in self.TEST_DICT.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse_name, adress)
