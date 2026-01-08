from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.conf import settings


user = get_user_model()


class CustomUserCreationForm(UserCreationForm): 
    username = forms.CharField(
        label="ユーザー名",
        min_length=6,
        help_text="(半角英数6文字以上)"
    )
    nickname = forms.CharField(
        label="ニックネーム",
        required=False,
        help_text="(ニックネームを入力してください)",
    )
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
        min_length=6,
        help_text="(半角英数6文字以上)"
    )
    password2 = forms.CharField(
        label="パスワード（確認用)",
        widget=forms.PasswordInput,
        min_length=6
    )
    # UserCreationFormはModelFormを継承しているので、form.is_valid()のあと、form.save()すると
    # Userインスタンスが生成されusernameと,ハッシュ化されたpassword1
    # がpasswordとしてUserインスタンスに保持される
    class Meta:                                 
        model = user                           
        fields = ("username", "nickname", "password1", "password2")