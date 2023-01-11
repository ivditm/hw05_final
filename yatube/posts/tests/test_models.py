from django.test import TestCase
from django.conf import settings
from django.db.utils import IntegrityError

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='abi')
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
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user1
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_dict = {
            self.post: ' '.join(
                self.post.text.split()[:settings.NUMBER_OF_WORDS]),
            self.group: self.group.title,
            self.comment: ' '.join(
                self.comment.text.split()[:settings.NUMBER_OF_WORDS]),
            self.follow: f'{self.user} подписан на {self.user1}'
        }
        for field, expected_value in test_dict.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value, 'oops!')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        DICT = {
            Post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа',
                'image': 'Картинка',
            },
            Comment: {
                'text': 'Текст комментария',
                'created': 'Дата публикации',
                'author': 'Автор',
                'post': 'Пост',
            },
            Follow: {
                'user': 'подписчик',
                'author': 'автор'
            }
        }
        for model, dict in DICT.items():
            for field, expected_value in dict.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        DICT = {
            Post: {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
                'image': 'Загрузите картинку'
            },
            Comment: {
                'text': 'Введите текст комментария',
                'post': 'Пост, к которому будет относиться комментарий'
            }
        }
        for model, field_help_texts in DICT.items():
            for field, expected_value in field_help_texts.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        expected_value)

    def test_do_not_accept_user_to_block_itself(self):
        with self.assertRaises(IntegrityError):
            Follow.objects.create(user=self.user, author=self.user)

    def test_actor_and_blocked_persons_should_unique_together(self):
        with self.assertRaises(IntegrityError):
            Follow.objects.create(user=self.user, author=self.user1)

    def test_both_user_could_block_each_other(self):
        Follow.objects.create(user=self.user1, author=self.user)
