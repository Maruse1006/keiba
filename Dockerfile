FROM python:3.10.14
RUN apt-get update && \
    apt-get -y install mariadb-client
RUN mkdir /code
WORKDIR /code
COPY . /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]