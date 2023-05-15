FROM python:3.11.1

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/"

RUN pip install --upgrade pip

COPY ./requirements.txt /app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

COPY ./app /app
