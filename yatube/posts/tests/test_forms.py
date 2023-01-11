from http import HTTPStatus
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
UPLOADED_2 = SimpleUploadedFile(
    name='MINE.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
PATH_TO_PICTURE = 'posts/small.gif'
PATH_TO_PICTURE_2 = 'posts/MINE.gif'


URL_POST_CREATE = 'posts:post_create'
ADRESS_CREATE = reverse('posts:post_create')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='WTF',
            id=1)

        cls.group = Group.objects.create(
            title='TEST',
            slug='TEST',
            description='СТАЛО ПОНЯТНЕЕ, СПАСИБО'
        )
        cls.group1 = Group.objects.create(
            title='TEST1',
            slug='TEST1',
            description='Я ВОТ ТОЖЕ КОНСТАНТА'
        )
        cls.post = Post.objects.create(
            text='Я - КОНСТАНТА?',
            group=cls.group,
            author=cls.user,
        )
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      args=[cls.user.username])
        cls.EDIT_REVERSE = reverse('posts:post_edit', args=[cls.post.pk])
        cls.DETAIL_REVERSE = reverse('posts:post_detail', args=[cls.post.pk])
        cls.COMMENT_REVERSE = reverse('posts:add_comment', args=[cls.post.pk])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """Валидная форма создает запись в Post."""

        post_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'ВСЕ РАВНО ЖЕСТЬ',
            'image': UPLOADED
        }
        response = self.authorized_client.post(
            reverse(URL_POST_CREATE),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            self.PROFILE_REVERSE
        )
        new_post = Post.objects.latest('id')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.group.pk, form_data['group'])
        self.assertEqual(new_post.image, PATH_TO_PICTURE)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""

        posts_count = Post.objects.count()
        form_data = {
            'text': 'PIPEC',
            'group': self.group1.pk,
            'image': UPLOADED_2
        }
        response = self.authorized_client.post(
            self.EDIT_REVERSE,
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.get(pk=1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            self.DETAIL_REVERSE)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.author, self.user)
        self.assertEqual(edit_post.group.pk, form_data['group'])
        self.assertEqual(edit_post.image, PATH_TO_PICTURE_2)

    def test_comment_create(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Happy new year',
            'post': self.post,
            'author': self.user
        }
        response = self.authorized_client.post(
            self.COMMENT_REVERSE,
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            self.DETAIL_REVERSE
        )
        new_comment = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(new_comment.text, form_data['text'])
        self.assertEqual(new_comment.author, self.user)
        self.assertEqual(new_comment.post.pk, form_data['post'].pk)

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
