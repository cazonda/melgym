FROM python:3.10-alpine3.17

#set work directory
WORKDIR /usr/src/app

#environment variables needed during build time
ARG DJANGO_ALLOWED_HOSTS
ARG SECRET_KEY
ARG DATABASE_URL


RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add py3-pip py3-pillow py3-cffi py3-brotli python3-dev pango libffi-dev 

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

#RUN python manage.py collectstatic
#RUN python manage.py makemigrations
#hello delete me
RUN python manage.py migrate
#RUN python manage.py createsuperuser --noinput || True
