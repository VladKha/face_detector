import numpy as np
import cv2
from sklearn.externals import joblib

from . import MODEL_PATH
from skimage.feature import hog
from .utils import sliding_window, pyramid, non_max_suppression, rgb2gray


class Detector:
    def __init__(self, downscale=1.5, window_size=(178, 218), window_step_size=20, threshold=0.4):
        self.clf = joblib.load(MODEL_PATH)
        self.downscale = downscale
        self.window_size = window_size
        self.window_step_size = window_step_size
        self.threshold = threshold

    def detect(self, image):
        clone = image.copy()

        image = rgb2gray(image)

        # list to store the detections
        detections = []

        # current scale of the image
        downscale_power = 0

        # downscale the image and iterate
        for im_scaled in pyramid(image, downscale=self.downscale, min_size=self.window_size):
            # if the width or height of the scaled image is less than
            # the width or height of the window, then end the iterations
            if im_scaled.shape[0] < self.window_size[1] or im_scaled.shape[1] < self.window_size[0]:
                break
            for (x, y, im_window) in sliding_window(im_scaled, self.window_step_size,
                                                    self.window_size):
                if im_window.shape[0] != self.window_size[1] or im_window.shape[1] != self.window_size[0]:
                    continue

                # calculate the HOG features
                feature_vector = hog(im_window)
                X = np.array([feature_vector])
                prediction = self.clf.predict(X)
                if prediction == 1:
                    x1 = int(x * (self.downscale ** downscale_power))
                    y1 = int(y * (self.downscale ** downscale_power))
                    detections.append((x1, y1,
                                       x1 + int(self.window_size[0] * (
                                               self.downscale ** downscale_power)),
                                       y1 + int(self.window_size[1] * (
                                               self.downscale ** downscale_power))))

            # Move the the next scale
            downscale_power += 1

        # Display the results before performing NMS
        clone_before_nms = clone.copy()
        for (x1, y1, x2, y2) in detections:
            # Draw the detections
            cv2.rectangle(clone_before_nms, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)

        # Perform Non Maxima Suppression
        detections = non_max_suppression(np.array(detections), self.threshold)

        clone_after_nms = clone
        # Display the results after performing NMS
        for (x1, y1, x2, y2) in detections:
            # Draw the detections
            cv2.rectangle(clone_after_nms, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)

        return clone_before_nms, clone_after_nms
