from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Rozszerzony model użytkownika
    """
    email = models.EmailField(unique=True, verbose_name="adres email")
    phone = models.CharField(max_length=15, blank=True, verbose_name="telefon")
    birth_date = models.DateField(null=True, blank=True, verbose_name="data urodzenia")
    city = models.CharField(max_length=100, blank=True, verbose_name="miasto")
    address = models.TextField(blank=True, verbose_name="adres")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="data rejestracji")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="data aktualizacji")
    is_verified = models.BooleanField(default=False, verbose_name="zweryfikowany")
    newsletter = models.BooleanField(default=False, verbose_name="newsletter")
    terms_accepted = models.BooleanField(default=False, verbose_name="akceptacja regulaminu")
    
    class Meta:
        app_label = 'detection_app'  # DODAJ TĘ LINIĘ
        verbose_name = "użytkownik"
        verbose_name_plural = "użytkownicy"
    
    
    
    def __str__(self):
        return f"{self.username} ({self.email})"

class UserProfile(models.Model):
    """
    Dodatkowy profil użytkownika
    """
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name="awatar"
    )
    
    bio = models.TextField(blank=True, verbose_name="o sobie")
    website = models.URLField(blank=True, verbose_name="strona internetowa")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    twitter = models.URLField(blank=True, verbose_name="Twitter")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'detection_app'  # DODAJ TĘ LINIĘ
        verbose_name = "profil użytkownika"
        verbose_name_plural = "profile użytkowników"
    
    

    def __str__(self):
        return f"Profil: {self.user.username}"
    
class DetectionImage(models.Model):
    """ Model do przechowywania przesyłanych obrazów i wyników detekcji"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='detection_images')
    original_image = models.ImageField(upload_to='detection_images/original/')
    processed_image = models.ImageField(upload_to='detection_images/processed/', blank=True, null=True)
    
    # Wyniki detekcji
    detection_results = models.JSONField(default=dict, blank=True)  
    
    # Metadane
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Statystyki
    objects_detected = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0)  
    
    class Meta:
        verbose_name = "obraz do detekcji"
        verbose_name_plural = "obrazy do detekcji"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Obraz {self.id} - {self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    
