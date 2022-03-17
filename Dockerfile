FROM python:3.8

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 imagemagick  -y

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./download_models.sh /code/download_models.sh
RUN chmod -R 755 /code
RUN /code/download_models.sh

COPY . /code

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
