from django.shortcuts import render, redirect, get_object_or_404    
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm, CustomPasswordChangeForm, ImageUploadForm
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import CustomUser, UserProfile, DetectionImage
import os
import time as time_module
from .object_detector import ObjectDetector, COCO_CLASSES
from django.core.paginator import Paginator


def register_view(request):
    """
    Widok rejestracji użytkownika
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Automatyczne logowanie po rejestracji
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Rejestracja zakończona sukcesem! Witamy na naszej stronie.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Popraw błędy w formularzu.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def home_view(request):
    return render(request, 'home/index.html')
def custom_login_view(request):
    """
    Własny widok logowania
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Witaj z powrotem, {username}!')
            
            # Przekierowanie do next parametru lub dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
    
    return render(request, 'loginin/login.html')

def custom_logout_view(request):
    """
    Własny widok wylogowania
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Zostałeś pomyślnie wylogowany.')
    return redirect('login')

@login_required
def dashboard_view(request):
    """
    Panel użytkownika po zalogowaniu
    """
    user = request.user
    context = {
        'user': user,
        'profile': getattr(user, 'profile', None),
    }
    return render(request, 'dash/dashboard.html', context)

@login_required
def profile_view(request):
    """
    Główny widok profilu użytkownika - używa include dla partial templates
    """
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Domyślnie pokazujemy zakładkę z przeglądem
    active_tab = request.GET.get('tab', 'overview')
    
    # Inicjalizujemy formularze
    user_form = UserUpdateForm(instance=user)
    profile_form = UserProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(request.user)
    
    # Obsługa formularzy POST
    if request.method == 'POST':
        if 'user_data_submit' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Dane podstawowe zostały zaktualizowane.')
                return redirect(f'{request.path}?tab=basic')
            else:
                active_tab = 'basic'
                
        elif 'profile_data_submit' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profil społecznościowy został zaktualizowany.')
                return redirect(f'{request.path}?tab=social')
            else:
                active_tab = 'social'
                
        elif 'password_change_submit' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Twoje hasło zostało pomyślnie zmienione!')
                return redirect(f'{request.path}?tab=password')
            else:
                active_tab = 'password'
    
    context = {
        'user': user,
        'profile': profile,
        'active_tab': active_tab,
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    
    return render(request, 'profile/profile.html', context)

@login_required
def profile_delete_account(request):
    """
    Usuwanie konta użytkownika (z potwierdzeniem)
    """
    if request.method == 'POST':
        # Potwierdzenie usunięcia
        if 'confirm_delete' in request.POST:
            user = request.user
            logout(request)  # Wyloguj użytkownika
            user.delete()    # Usuń konto
            messages.success(request, 'Twoje konto zostało pomyślnie usunięte.')
            return redirect('home')
        else:
            messages.error(request, 'Musisz potwierdzić chęć usunięcia konta.')
    
    context = {
        'active_tab': 'delete',
    }
    return render(request, 'partials/profile_delete_account.html', context)




@login_required
def object_detection_upload(request):
    """
    Widok przesyłania obrazu do detekcji obiektów
    """
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Zapisz obraz bez commita
            detection_image = form.save(commit=False)
            detection_image.user = request.user
            detection_image.save()
            
            # Przekieruj do przetwarzania
            return redirect('object_detection_process', image_id=detection_image.id)
        else:
            messages.error(request, 'Popraw błędy w formularzu.')
    else:
        form = ImageUploadForm()
    
    # Pobierz historię przetwarzania użytkownika
    user_images = DetectionImage.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    
    context = {
        'form': form,
        'user_images': user_images,
        'active_tab': 'detection'
    }
    return render(request, 'detect/object_detection_upload.html', context)


@login_required
def object_detection_process(request, image_id):
    """
    Widok przetwarzania obrazu i wyświetlania wyników
    """
    detection_image = get_object_or_404(DetectionImage, id=image_id, user=request.user)
    
    # Sprawdź czy obraz był już przetwarzany
    if detection_image.processed_image and detection_image.detection_results:
        return render(request, 'detect/object_detection_results.html', {
            'detection_image': detection_image,
            'active_tab': 'detection'
        })
    
    # Przetwarzanie obrazu
    try:
        start_time = time_module.time()
        
        # Inicjalizacja detektora
        MODEL_URL = "https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2"
        detector = ObjectDetector(MODEL_URL)
        
        # Wczytanie i przygotowanie obrazu
        original_image, image_tensor = detector.load_and_preprocess_from_file(
            detection_image.original_image.file
        )
        
        # Wykonanie detekcji
        results = detector.detect_objects(image_tensor)
        
        # Przetworzenie wyników
        boxes, scores, classes = detector.process_detections(results, confidence_threshold=0.5)
        
        # Przygotowanie wyników do zapisu
        detection_results = []
        for i, (box, score, class_id) in enumerate(zip(boxes, scores, classes)):
            class_name = COCO_CLASSES.get(class_id, 'unknown')
            detection_results.append({
                'id': i + 1,
                'class_id': int(class_id),
                'class_name': class_name,
                'confidence': float(score),
                'bbox': [float(coord) for coord in box]
            })
        
        # Rysowanie detekcji na obrazie
        image_with_detections = detector.draw_detections(
            original_image, boxes, scores, classes, COCO_CLASSES
        )
        
        # Zapis przetworzonego obrazu
        filename = f"processed_{detection_image.id}_{os.path.basename(detection_image.original_image.name)}"
        processed_image_path = detector.save_processed_image(image_with_detections, filename)
        
        # Aktualizacja modelu
        processing_time = time_module.time() - start_time
        
        detection_image.processed_image = processed_image_path
        detection_image.detection_results = {
            'objects': detection_results,
            'total_objects': len(detection_results),
            'confidence_threshold': 0.5
        }
        detection_image.objects_detected = len(detection_results)
        detection_image.processing_time = processing_time
        detection_image.processed_at = timezone.now()
        detection_image.save()
        
        messages.success(request, f'Detekcja zakończona sukcesem! Znaleziono {len(detection_results)} obiektów.')
        
    except Exception as e:
        messages.error(request, f'Wystąpił błąd podczas przetwarzania obrazu: {str(e)}')
        return redirect('object_detection_upload')
    
    context = {
        'detection_image': detection_image,
        'active_tab': 'detection'
    }
    return render(request, 'detect/object_detection_results.html', context)


@login_required
def object_detection_history(request):
    
    user_images = DetectionImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Paginacja
    paginator = Paginator(user_images, 10)  # 10 elementów na stronę
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user_images': page_obj,
        'active_tab': 'history'
    }
    return render(request, 'detect/object_detection_history.html', context)


@login_required
def object_detection_detail(request, image_id):
    """
    Szczegóły pojedynczego przetworzenia
    """
    detection_image = get_object_or_404(DetectionImage, id=image_id, user=request.user)
    
    context = {
        'detection_image': detection_image,
        'active_tab': 'history'
    }
    return render(request, 'detect/object_detection_detail.html', context)