from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        help_texts = {
            'text': 'Напишите новый текст сообщения',
            'group': 'Выберете группу',
            'image': 'Загрузить изображение',
        }
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        help_texts = {
            'text': 'Напишите текст комментария',
        }
        fields = ['text']
