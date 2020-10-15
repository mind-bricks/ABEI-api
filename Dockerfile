FROM python:3.6

EXPOSE 80

# COPY ./misc /services/misc

COPY ./scripts /services/scripts

WORKDIR /services

RUN bash scripts/build-prod

COPY . /services

CMD bash scripts/run-prod
