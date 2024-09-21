from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string


@csrf_exempt
def custom_upload_file(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        file_name = get_random_string(20) + '.' + upload.name.split('.')[-1]
        file_path = default_storage.save(f'uploads/{file_name}', ContentFile(upload.read()))
        file_url = default_storage.url(file_path)
        return JsonResponse({'url': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)