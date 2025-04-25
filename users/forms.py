from django import forms
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('name', 'login', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = self.cleaned_data['password']  # Сохраняем пароль в явном виде
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=False,
        label="Новый пароль"
    )

    class Meta:
        model = User
        fields = ['name', 'login']

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user