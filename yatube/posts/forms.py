from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        def check(self):
            data = self.check['text']
            if data == '':
                raise forms.ValidationError('Зачем ничего не написал?')
            return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

        def check(self):
            data = self.check['text']
            if data == '':
                raise forms.ValidationError('Зачем ничего не написал?')
            return data
