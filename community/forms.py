from django import forms
from django.utils.text import slugify
from .models import Discussion, Post, Category


class DiscussionForm(forms.ModelForm):
    """Form per creare/modificare una discussione."""

    class Meta:
        model = Discussion
        fields = ["title", "category", "dog", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Inserisci il titolo della discussione...",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "dog": forms.Select(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Descrivi la tua domanda o condividi la tua esperienza...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Filtra solo le categorie attive
        self.fields["category"].queryset = Category.objects.filter(is_active=True)

        # Filtra solo i cani dell'utente corrente
        if self.user and self.user.is_authenticated:
            self.fields["dog"].queryset = self.user.profiles.all().order_by("dog_name")
        else:
            self.fields["dog"].queryset = self.fields["dog"].queryset.none()

        self.fields["dog"].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and self.user.is_authenticated:
            instance.author = self.user
        if commit:
            instance.save()
        return instance


class PostForm(forms.ModelForm):
    """Form per creare/modificare un post/risposta."""

    class Meta:
        model = Post
        fields = ["content", "parent"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Scrivi la tua risposta...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["parent"].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and self.user.is_authenticated:
            instance.author = self.user
        if commit:
            instance.save()
        return instance


class DiscussionSearchForm(forms.Form):
    """Form per la ricerca e il filtro delle discussioni."""

    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Cerca nelle discussioni...",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="Tutte le categorie",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        choices=[("", "Tutti gli stati")] + Discussion.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    my_dogs = forms.BooleanField(
        required=False,
        label="Solo discussioni sui miei cani",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    my_posts = forms.BooleanField(
        required=False,
        label="Solo discussioni a cui ho partecipato",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class NotificationPreferencesForm(forms.Form):
    """Form per le preferenze di notifica."""

    email_on_reply = forms.BooleanField(
        required=False,
        label="Ricevi email per nuove risposte",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    email_on_mention = forms.BooleanField(
        required=False,
        label="Ricevi email per le menzioni",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    email_on_like = forms.BooleanField(
        required=False,
        label="Ricevi email per i mi piace",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    in_app_only = forms.BooleanField(
        required=False,
        label="Mostra notifiche solo nell'app",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
