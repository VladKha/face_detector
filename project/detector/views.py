import os
import scipy.misc

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from hog import hog


def index(request):
    original_photo = request.FILES.get('upload_photo')
    if request.method == 'POST' and original_photo:

        image = scipy.misc.imread(original_photo)
        histogram_descriptor, hog_image = hog(image)  # , pixels_per_cell=(16, 16), cells_per_block=(4, 4))

        fs = FileSystemStorage()
        hog_file_name = 'hog.png'
        hog_file_path = os.path.join(settings.MEDIA_ROOT, hog_file_name)
        scipy.misc.imsave(hog_file_path, hog_image)
        hog_image_url = fs.url(hog_file_name)

        original_photo_name = 'original.png'
        fs.delete(original_photo_name)
        original_file_name = fs.save(original_photo_name, original_photo)
        original_photo_url = fs.url(original_file_name)
        return render(request, 'detector/index.html', {
            'original_photo_url': original_photo_url, 'hog_image_url': hog_image_url
        })
    return render(request, 'detector/index.html', {})
