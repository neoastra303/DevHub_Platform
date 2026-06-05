from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post, Profile, Project, TransactionLog


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    skills_text = forms.CharField(
        required=False,
        help_text="Comma-separated skills",
        widget=forms.TextInput(attrs={"placeholder": "Python, Django, PostgreSQL"}),
    )

    class Meta:
        model = Profile
        fields = ("headline", "bio", "avatar_seed")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["skills_text"].initial = ", ".join(self.instance.skill_names)

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            profile.set_skill_names(self.cleaned_data.get("skills_text", "").split(","))
        return profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {"content": forms.Textarea(attrs={"rows": 5})}


class ProjectForm(forms.ModelForm):
    tech_stack_text = forms.CharField(
        required=False,
        help_text="Comma-separated technologies",
        widget=forms.TextInput(attrs={"placeholder": "Django, PostgreSQL, Docker"}),
    )

    class Meta:
        model = Project
        fields = ("title", "summary", "description", "demo_url", "source_url", "is_featured")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tech_stack_text"].initial = ", ".join(self.instance.technology_names)

    def save(self, commit=True):
        project = super().save(commit=False)
        if commit:
            project.save()
            project.set_technology_names(self.cleaned_data.get("tech_stack_text", "").split(","))
        return project


class TransactionLogForm(forms.ModelForm):
    class Meta:
        model = TransactionLog
        fields = ("transaction_id", "amount", "status")
