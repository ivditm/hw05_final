from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.db.models import F, Q

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return ' '.join(self.text.split()[:settings.NUMBER_OF_WORDS])


class Comment(models.Model):
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Пост',
        help_text='Пост, к которому будет относиться комментарий'
    )

    class Meta:
        ordering = ['-created']
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self) -> str:
        return ' '.join(self.text.split()[:settings.NUMBER_OF_WORDS])


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name='подписчик',)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following",
                               verbose_name='автор')

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(user=F('author')),
                            name='could_not_follow_itself'),
            UniqueConstraint(fields=['user', 'author'], name='unique_follower')
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
