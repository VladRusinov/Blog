from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    """Форма создания публикации"""

    class Meta:
        model = Post
        exclude = ('author', )
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M:%S',
                attrs={'type': 'datetime-local'}
            )
        }


class EditProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    """Форма для комментария"""

    class Meta:
        model = Comment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['cols'] = 10
        self.fields['text'].widget.attrs['rows'] = 5
