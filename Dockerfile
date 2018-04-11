From python:3.6-alpine3.7
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8
RUN apk add --update \
    python-dev
#To satisfy unit tests running
ENV TOKEN='TOKEN' \
    USERNAME='USERNAME' \
    PASSWORD='PASSWORD' \
    ENVIRONMENT='Development'
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN ./build.sh


From python:3.6-alpine3.7
WORKDIR /usr/src/app
COPY --from=0 /usr/src/app/dist/*.whl .
RUN pip install hacker_one_importer-*.whl
CMD h1 imports
