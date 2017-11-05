. venv/bin/activate
cd raspapreco
celery -A restless.celery worker --loglevel=info
