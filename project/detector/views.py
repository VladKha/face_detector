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
        print('form errors:', form.errors)
        if form.is_valid():
            print('index post valid')
            original_image = form.cleaned_data['image']

            fs = FileSystemStorage()
            original_photo_name = original_image.name
            fs.delete(original_photo_name)
            original_file_name = fs.save(original_photo_name, original_image)

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
    poll_result = {}
    if request.is_ajax():
        task_id = request.GET.get('task_id')
        if task_id:
            task = AsyncResult(task_id)
            poll_result['hog_result'] = task.result
            poll_result['state'] = task.state
        else:
            poll_result['hog_result'] = 'No task_id in the request'
    else:
        poll_result['hog_result'] = 'This is not an ajax request'

    print('exit poll_hog_state\n')
    return JsonResponse(poll_result)
