from django import forms
from .models import Post, Comment
from markdownx.fields import MarkdownxFormField


class PostForm(forms.ModelForm):
    content = MarkdownxFormField()

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Separate tags with commas'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            })
        }
        labels = {
            'body': ''
        }