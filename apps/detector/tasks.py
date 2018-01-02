import base64
import io

import numpy as np
from PIL import Image
from celery import shared_task, current_task

from detector.detector import Detector


@shared_task
def detect_faces(base64_encoded_image):
    print('enter detect_faces')

    current_task.update_state(meta={'process_percent': 20})

    image = Image.open(io.BytesIO(base64.b64decode(base64_encoded_image)))
    image = np.array(image)
    current_task.update_state(meta={'process_percent': 25})

    detector = Detector()
    image_before_nms, image_after_nms = detector.detect(image)
    current_task.update_state(meta={'process_percent': 90})

    # read and encode image file to be able to transfer it through json
    im = Image.fromarray(image_after_nms.astype("uint8"))
    raw_bytes = io.BytesIO()
    im.save(raw_bytes, "PNG")
    raw_bytes.seek(0)  # return to the start of the file
    detected_image_encoded = base64.b64encode(raw_bytes.read()).decode('utf-8')
    current_task.update_state(meta={'process_percent': 99})

    print('exit detect_faces\n')
    return base64_encoded_image, detected_image_encoded
