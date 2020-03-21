FROM python:alpine3.7
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080 
ENTRYPOINT [ "python" ] 
CMD [ "run_app.py" ]