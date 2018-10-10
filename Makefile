DEFAULT_PORT=5000

run:
	gunicorn --bind 0.0.0.0:$(DEFAULT_PORT) wsgi