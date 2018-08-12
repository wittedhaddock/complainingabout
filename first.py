from __future__ import absolute_import

from flask import Flask
import requests
import json
import pprint
from celery import Celery

app = Flask(__name__)
pp = pprint.PrettyPrinter(indent=4)

userA = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
first_request = requests.get('https://www.reddit.com/r/all/new/.json?limit=1000', headers=userA)

def new_request_url():
	last_downloaded = first_request.json()['data']['after']
	return 'https://www.reddit.com/r/all/new/.json?limit=1000&id=' + last_downloaded


@app.route('/')
def hello_world():
	loopRedditFromRequest(new_request_url())
	return "loading..."


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery



flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(flask_app)


@celery.task()
def loopRedditFromRequest(fromRequest):
	r = requests.get(new_request_url(), headers=userA)
	first_request = r
	post_json = r.json()
	pp.pprint(post_json)