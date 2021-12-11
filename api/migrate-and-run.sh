#!/usr/bin/dash

echo "running the script"
# sleep 3600
echo "1\n''\n1\n''\n2\n" | python manage.py makemigrations && \
python manage.py migrate && \
python manage.py runserver 0.0.0.0:8000