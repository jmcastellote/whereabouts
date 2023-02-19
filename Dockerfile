FROM python:slim-bullseye as builder

WORKDIR /whereabouts

RUN pip install poetry --upgrade
RUN poetry self add poetry-plugin-bundle

COPY ./pyproject.toml .

RUN poetry bundle venv /install --only main
RUN rm /install/bin/python*


# Final container
FROM python:slim-bullseye

WORKDIR /whereabouts

#RUN  useradd -ms /bin/bash whereabouts

COPY --from=builder /install /usr/local
RUN mkdir -p /install/bin && ln -s /usr/local/bin/python /install/bin/python
COPY . .

ENV PYTHONPATH /whereabouts

#USER whereabouts

CMD uvicorn --host 0.0.0.0 --port 8787 awsgi:app --reload
