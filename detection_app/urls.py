from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home_view, name='home' ),
    path('register/', views.register_view, name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('profile/', views.profile_view, name='profile'),
    path('delete/', views.profile_delete_account, name='profile_delete_account'),
    
    
    #Detekcja obiektów
    path('detect/', views.object_detection_upload, name='object_detection_upload'),
    path('detect/<int:image_id>/', views.object_detection_process, name='object_detection_process'),
    path('detect/history/', views.object_detection_history, name='object_detection_history'),
    path('detect/<int:image_id>/', views.object_detection_detail, name='object_detection_detail'),
    
    # Reset hasła
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)