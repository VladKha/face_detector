#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for face_detector project with Celery configuration stored in config.celery.py
su -m myuser -c "celery -A config worker -l info"
