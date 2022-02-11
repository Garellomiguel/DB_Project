FROM alpine:latest

RUN apk update
RUN apk add py-pip
RUN apk add --no-cache python3-dev 
RUN pip install --upgrade pip

WORKDIR /app

COPY ./requirements.txt .
RUN pip --no-cache-dir install -r requirements.txt

COPY ./src .

EXPOSE 5000

CMD ["python3", "app.py"]