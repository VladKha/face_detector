import os
import scipy.misc

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from .forms import ImageUploadForm
from hog import hog


def index(request):
    form = ImageUploadForm(request.POST, request.FILES)
    context = {}
    if request.method == 'POST':
        if form.is_valid():
            original_image = form.cleaned_data['image']
            image = scipy.misc.imread(original_image)
            histogram_descriptor, hog_image = hog(image)  # , pixels_per_cell=(16, 16), cells_per_block=(4, 4))

            fs = FileSystemStorage()
            hog_file_name = 'hog.png'
            hog_file_path = os.path.join(settings.MEDIA_ROOT, hog_file_name)
            scipy.misc.imsave(hog_file_path, hog_image)
            hog_image_url = fs.url(hog_file_name)

            original_image_name = 'original.png'
            fs.delete(original_image_name)
            original_file_name = fs.save(original_image_name, original_image)
            original_image_url = fs.url(original_file_name)

            context['original_image_url'] = original_image_url
            context['hog_image_url'] = hog_image_url
        else:
            context['error_message'] = 'Upload a valid image. ' \
                'The file you uploaded was either not an image or a corrupted image.'
    context['form'] = form
    return render(request, 'detector/index.html', context)
