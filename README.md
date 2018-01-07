# Face detector
[Website](https://face-detector-app.herokuapp.com/) for face detection from image.

Built using mine [object_detector](https://github.com/VladKha/object_detector) project (see more on it's [Github page](https://github.com/VladKha/object_detector)),
trained on faces datasets.
Tools for detection are inside _object_detector_ package located in project root.

_**Note 1:** site may need some spin up time if nobody has accessed it for a certain period._

_**Note 2:** detection can take some time (few seconds) depending on image size
 because of the slow algorithm (HOG + SVM framework)._

## Getting Started
These instructions will get you a copy of the project up and running
on your local machine for development purposes.
There are 2 ways of running the project for development of deployment:
_usual_ (not dockerized) and _dockerized_.

 _Usual_|_Dockerized_
 |:---|:---|
 1\. Install RabbitMQ | 1\. Install Docker and Docker-Compose
 2\. Copy environment file env.example and rename it to .env | 2\. Copy environment file env.example and rename it to .env
 3\. In .env file set DJANGO_SECRET_KEY and CELERY_BROKER_URL | 3\. In .env file set DJANGO_SECRET_KEY
 4\. Execute in command line `pip install -r requirements.txt` | 4\. Start docker engine
 5\. Start RabbitMQ | 5\. Execute in command line `sh up.sh` which will start-up all the containers (first time can take some time to boot up because of the Docker images downloading and building)
 6\. Start Celery worker `celery -A config worker -l` | 6\. Access website on http://0.0.0.0:8000/
 7\. Start Django server `python manage.py runserver 0.0.0.0:8000` | _**To shutdown dockerized application**_ - execute in command line `sh down.sh`
 8\. Access website on http://0.0.0.0:8000/ |



## Deployment into Heroku
```bash
    heroku login

    heroku create <app_name>

    # config environment vars
    heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production
    heroku config:set DJANGO_SECRET_KEY=<YOURS_DJANGO_SECRET_KEY>
    heroku config:set CELERY_BROKER_URL=<YOURS_CELERY_BROKER_URL>

    git push heroku master

    heroku ps:scale web=1 worker=1

    heroku open
```

## Built With
- Python 3.6
- [Django 2](https://www.djangoproject.com/) - back-end web framework
- [Bootstrap 4](https://getbootstrap.com/) - front-end framework for site design
- a little of jQuery and Ajax
- [Celery](http://www.celeryproject.org/) - asynchronous task queue/job queue based on distributed message passing
- [RabbitMQ 3.7](https://www.rabbitmq.com/) - message broker
- [Docker](https://www.docker.com/) - containerization
- [docker-compose](https://docs.docker.com/compose/) - tool for defining and running multi-container Docker applications

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details