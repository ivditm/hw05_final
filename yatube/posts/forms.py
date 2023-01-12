from django import forms

from .models import Comment, Post


class BaseFormClass(forms.ModelForm):
    def check(self):
        data = self.check['text']
        if data == '':
            raise forms.ValidationError('Зачем ничего не написал?')
        return data


class PostForm(BaseFormClass):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Ваш текст',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку'
        }


class CommentForm(BaseFormClass):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'поделитесь своими мыслями'}
