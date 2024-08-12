from django import forms
from .models import Comment, Post


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش مشکل', 'گزارش مشکل'),
    )
    message = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(min_length=11, max_length=11, required=True)
    email = forms.EmailField()
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن باید عددی باشد!')
        else:
            return phone


class CommentForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('نام کوتاه میباشد!')
        else:
            return phone

    class Meta:
        model = Comment
        fields = ('name', 'body')


class SearchForm(forms.Form):
    query = forms.CharField()


class PostForm(forms.ModelForm):
    image1 = forms.ImageField(label="تصویر اول")
    image2 = forms.ImageField(label="تصویر دوم")

    class Meta:
        model = Post
        fields = ('title', 'description', 'reading_time')
