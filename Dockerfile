FROM python:3.12

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# no_NO.UTF-8 UTF-8/no_NO.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    pip install --no-cache-dir -r requirements.txt

ENV LANG=no_NO.UTF-8
ENV LC_ALL=no_NO.UTF-8

CMD ["python", "main.py"]