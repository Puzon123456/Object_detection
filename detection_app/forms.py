from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser, UserProfile
import re
from .models import DetectionImage

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'twój@email.com'
        }),
        label="Adres email"
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+48 123 456 789'
        }),
        label="Numer telefonu",
        max_length=15
    )
    
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Data urodzenia"
    )
    
    newsletter = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Chcę otrzymywać newsletter"
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': 'required'
        }),
        label="Akceptuję regulamin serwisu"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2', 
            'first_name', 'last_name', 'phone', 'birth_date',
            'city', 'address', 'newsletter', 'terms_accepted'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'nazwa użytkownika'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'imię'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'nazwisko'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'miasto'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'adres zamieszkania',
                'rows': 3
            }),
        }
        labels = {
            'username': 'Nazwa użytkownika',
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'city': 'Miasto',
            'address': 'Adres',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Użytkownik z tym adresem email już istnieje.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Prosta walidacja numeru telefonu
            phone_pattern = r'^[\+]?[0-9\s\-\(\)]{9,15}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError("Podaj poprawny numer telefonu.")
        return phone

    def clean_terms_accepted(self):
        terms_accepted = self.cleaned_data.get('terms_accepted')
        if not terms_accepted:
            raise ValidationError("Musisz zaakceptować regulamin.")
        return terms_accepted

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Tworzenie profilu użytkownika
            UserProfile.objects.create(user=user)
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website', 'facebook', 'twitter', 'linkedin']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Napisz coś o sobie...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twojastrona.pl'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/twojprofil'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/twojprofil'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/twojprofil'
            }),
        }
        labels = {
            'avatar': 'Awatar',
            'bio': 'O sobie',
            'website': 'Strona internetowa',
            'facebook': 'Facebook',
            'twitter': 'Twitter',
            'linkedin': 'LinkedIn',
        }
        


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website', 'facebook', 'twitter', 'linkedin']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Napisz coś o sobie...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twojastrona.pl'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/twojprofil'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/twojprofil'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/twojprofil'
            }),
        }
        labels = {
            'avatar': 'Awatar',
            'bio': 'O sobie',
            'website': 'Strona internetowa',
            'facebook': 'Facebook',
            'twitter': 'Twitter',
            'linkedin': 'LinkedIn',
        }

class UserUpdateForm(forms.ModelForm):
    """Formularz aktualizacji danych użytkownika"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'twój@email.com'
        }),
        label="Adres email"
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+48 123 456 789'
        }),
        label="Numer telefonu",
        max_length=15
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'birth_date', 'city', 'address', 'newsletter']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'nazwa użytkownika'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'imię'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'nazwisko'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'miasto'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'adres zamieszkania',
                'rows': 3
            }),
            'newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'username': 'Nazwa użytkownika',
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'birth_date': 'Data urodzenia',
            'city': 'Miasto',
            'address': 'Adres',
            'newsletter': 'Chcę otrzymywać newsletter',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Sprawdź czy email nie jest już używany przez innego użytkownika
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Użytkownik z tym adresem email już istnieje.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Prosta walidacja numeru telefonu
            phone_pattern = r'^[\+]?[0-9\s\-\(\)]{9,15}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError("Podaj poprawny numer telefonu.")
        return phone

class CustomPasswordChangeForm(PasswordChangeForm):
    """Dostosowany formularz zmiany hasła"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dodaj klasy Bootstrap do pól
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        
        # Spolszcz etykiety
        self.fields['old_password'].label = 'Aktualne hasło'
        self.fields['new_password1'].label = 'Nowe hasło'
        self.fields['new_password2'].label = 'Potwierdź nowe hasło'
        
        # Spolszcz placeholder
        self.fields['old_password'].widget.attrs['placeholder'] = 'Wprowadź aktualne hasło'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Wprowadź nowe hasło'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Powtórz nowe hasło'
        





class ImageUploadForm(forms.ModelForm):
    """Formularz przesyłania obrazu do detekcji"""
    
    class Meta:
        model = DetectionImage
        fields = ['original_image']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'original_image': 'Wybierz obraz do analizy'
        }
    
    def clean_original_image(self):
        image = self.cleaned_data.get('original_image')
        if image:
            # Sprawdź rozmiar pliku (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Obraz nie może być większy niż 10MB")
            
            # Sprawdź typ pliku
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Nieobsługiwany format obrazu. Użyj JPG, PNG, BMP lub TIFF.")
        
        return image