import base64
import io

from PIL import Image
from celery.result import AsyncResult
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .forms import ImageUploadForm
from .tasks import detect_faces


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

            # read and encode image file to be able to transfer it through json
            original_image = Image.open(io.BytesIO(original_image.read()))
            raw_bytes = io.BytesIO()
            original_image.save(raw_bytes, "PNG")
            raw_bytes.seek(0)
            base64_encoded_image = base64.b64encode(raw_bytes.read()).decode('utf-8')

            task = detect_faces.delay(base64_encoded_image)
            return JsonResponse({'task_id': task.id})
        else:
            return HttpResponse(content='Upload a valid image. The file you uploaded was either '
                                        'not an image or a corrupted image.', status=415)
    context['form'] = form
    print('exit index')
    return render(request, 'detector/index.html', context)


def poll_face_detector_state(request):
    """ A view to report the progress to the user """
    print('enter poll_face_detector_state')
    poll_result = {}
    if request.is_ajax():
        task_id = request.GET.get('task_id')
        if task_id:
            task = AsyncResult(task_id)
            poll_result['result'] = task.result
            poll_result['state'] = task.state
        else:
            poll_result['result'] = 'No task_id in the request'
    else:
        poll_result['result'] = 'This is not an ajax request'

    print('exit poll_face_detector_state\n')
    return JsonResponse(poll_result)
