from datetime import timedelta

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "myuser"
BROKER_PASSWORD = "mypassword"
BROKER_VHOST = "myvhost"

CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ( "daemon", "tasks", "mysite.tasks", )

CELERY_ROUTES = {
		"mysite.tasks.task_addFeed": {"queue": "staging"},
		"daemon.grabStories": {"queue": "stories"}
		}

CELERYBEAT_SCHEDULE = {
    "runs-every-30-seconds": {
        "task": "tasks.hello",
        "schedule": timedelta(seconds=30),
    },
}

CELERY_QUEUES = {
	'celery': {'binding_key': 'celery', 'exchange_type': 'direct', 'routing_key': 'celery', 'exchange': 'celery'}, 
	'feeds': {'binding_key': 'stories', 'exchange_type': 'direct', 'routing_key': 'stories', 'exchange': 'feeds'},
	'stories': {'binding_key': 'stories', 'exchange_type': 'direct', 'routing_key': 'stories', 'exchange': 'stories'} 
}
