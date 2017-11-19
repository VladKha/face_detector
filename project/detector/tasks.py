import os

import scipy.misc
from celery import shared_task, current_task
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from face_detector.detector import Detector


@shared_task
def detect_faces(original_file_name):
    print('enter detect_faces')

    current_task.update_state(meta={'process_percent': 15})

    fs = FileSystemStorage()
    original_image = fs.open(original_file_name)
    current_task.update_state(meta={'process_percent': 20})

    image = scipy.misc.imread(original_image)
    print(f'Image size {image.shape}')

    detector = Detector()
    image_before_nms, image_after_nms = detector.detect(image)
    current_task.update_state(meta={'process_percent': 90})

    detected_file_name = 'detected_' + original_file_name
    detected_file_path = os.path.join(settings.MEDIA_ROOT, detected_file_name)
    scipy.misc.imsave(detected_file_path, image_after_nms)
    current_task.update_state(meta={'process_percent': 95})

    detected_image_url = fs.url(detected_file_name)
    original_photo_url = fs.url(original_file_name)
    current_task.update_state(meta={'process_percent': 100})

    print('exit detect_faces\n')
    return original_photo_url, detected_image_url
