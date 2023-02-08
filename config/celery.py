import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("python_django_team18",broker='redis://127.0.0.1:6379/0') # Вот так подключается к редису
# app = Celery("python_django_team18") # вот так почему то к кролику

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()