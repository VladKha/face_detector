import json

from celery.result import AsyncResult
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .forms import ImageUploadForm
from .tasks import create_hog


def index(request):
    print('enter index')
    form = ImageUploadForm(request.POST, request.FILES)
    context = {}
    if request.method == 'POST':
        print('index post')
        print(form.errors)
        if form.is_valid():
            print('index post valid')
            original_image = form.cleaned_data['image']

            fs = FileSystemStorage()
            original_photo_name = original_image.name
            fs.delete(original_photo_name)
            original_file_name = fs.save(original_photo_name, original_image)
            # original_photo_url = fs.url(original_file_name)

            task = create_hog.delay(original_file_name)
            return JsonResponse({'task_id': task.id})
        else:
            return HttpResponse(content='Upload a valid image. The file you uploaded was either '
                                        'not an image or a corrupted image.', status=415)
    context['form'] = form
    print('exit index')
    return render(request, 'detector/index.html', context)


def poll_hog_state(request):
    """ A view to report the progress to the user """
    print('enter poll_hog_state')
    if request.is_ajax():
        task_id = request.GET.get('task_id')
        if task_id:
            task = AsyncResult(task_id)
            print('result len:', len(task.result))
            print('state:', task.state)
            is_ready = task.ready()
            if is_ready:
                data = task.result
            else:
                data = task.state
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)
    print('exit poll_hog_state')
    return HttpResponse(json_data, content_type='application/json')
