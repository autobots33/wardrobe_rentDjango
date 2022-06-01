from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from django import forms

class RegisterUserForm(UserCreationForm):
    email= forms.EmailField()
    first_name=forms.CharField(max_length=50)
    last_name=forms.CharField(max_length=50)
    Citizenship_Front=forms.ImageField()
    Citizenship_Back=forms.ImageField()
    address=forms.CharField(max_length=50)
    class Meta:
        model = User
        fields = ('email','first_name','last_name','Citizenship_Front','Citizenship_Back','address','password1','password2')
