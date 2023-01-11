from django import forms

from .models import Comment, Post


class SuperClass(forms.ModelForm):
    def check(self):
        data = self.check['text']
        if data == '':
            raise forms.ValidationError('Зачем ничего не написал?')
        return data


class PostForm(SuperClass):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Ваш текст',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку'
        }


class CommentForm(SuperClass):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'поделитесь своими мыслями'}
