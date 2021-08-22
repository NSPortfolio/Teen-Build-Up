from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from app.models import Area, Post

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=250)
    first_name = forms.CharField(max_length=250)
    last_name = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email','first_name','last_name','password1','password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise ValidationError("This email address already exists.")
        return email

class BasicUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','first_name','last_name')

class Area(forms.ModelForm):
    area = forms.CharField(required=True)
    class Meta:
        model = Area
        fields = ('area',)

class PostOrganization(forms.ModelForm):
    website = forms.CharField(required=True)
    area = forms.CharField(required=True)
    update = forms.CharField(widget=forms.Textarea, required=False)
    recentevent = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Post
        fields = ('name_of_organization', 'organization', 'interest', 'website', 'area', 'communication', 'description', 'looking', 'update', 'recentevent',)
