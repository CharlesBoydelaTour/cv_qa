cd /home/site/wwwroot/cv_qa_website
python manage.py migrate
gunicorn --workers 2 --threads 4 --timeout 60 --access-logfile \
    '-' --error-logfile '-' --bind=0.0.0.0:8000 \
    cv_qa_website.wsgi