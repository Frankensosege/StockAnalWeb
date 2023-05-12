from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'user_name', 'passwd']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),
            'passwd': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': '이메일',
            'user_name': '표시명',
            'passwd': '비밀번호',
        }
