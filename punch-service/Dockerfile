FROM python:3.11.1

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/"

RUN pip install --upgrade pip

COPY ./requirements.txt /app/
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
# RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

COPY ./app /app
COPY .prod.env /app/.env

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
