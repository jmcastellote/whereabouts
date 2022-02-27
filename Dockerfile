FROM python:slim-bullseye as builder

COPY ./requirements.txt .

RUN apt update && \
    apt install -y python3-pip gcc python3-dev libpq-dev && \
    mkdir /install && \
    pip install --prefix=/install --upgrade -r requirements.txt


FROM python:slim-bullseye

WORKDIR /whereabouts

#RUN  useradd -ms /bin/bash whereabouts

COPY --from=builder /install /usr/local
COPY . .

#USER whereabouts

CMD uvicorn --host 0.0.0.0 --port 8787 awsgi:app --reload
