from django.test import TestCase
from django.conf import settings

from ..models import Comment, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='TEST',
            slug='TEST',
            description='TEST',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='TEST',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='TEST'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        group = self.group
        comment = self.comment
        test_dict = {
            post: ' '.join(
                post.text.split()[:settings.NUMBER_OF_WORDS]),
            group: group.title,
            comment: ' '.join(
                comment.text.split()[:settings.NUMBER_OF_WORDS]),
        }
        for field, expected_value in test_dict.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value, 'oops!')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses_post = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        field_verboses_comment = {
            'text': 'Текст комментария',
            'created': 'Дата публикации',
            'author': 'Автор',
            'post': 'Пост',
        }
        DICT = {
            Post: field_verboses_post,
            Comment: field_verboses_comment,
        }
        for model, dict in DICT.items():
            for field, expected_value in dict.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts_post = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку'
        }
        field_help_texts_comment = {
            'text': 'Введите текст комментария',
            'post': 'Пост, к которому будет относиться комментарий'
        }
        DICT = {
            Post: field_help_texts_post,
            Comment: field_help_texts_comment
        }
        for model, field_help_texts in DICT.items():
            for field, expected_value in field_help_texts.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        expected_value)
