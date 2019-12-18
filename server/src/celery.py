from celery import Celery
from brat_server import app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
    )
    # task_routes = {
    #     'brat_server.server.src.tasks.internal.*': {'queue': 'internal'},
    #     'brat_server.server.src.tasks.communication.*': {'queue': 'communication'},
    # }

    celery.conf.update(app.config)
    # celery.conf.update(task_routes=task_routes)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
