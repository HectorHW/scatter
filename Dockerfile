FROM python:3.10.8-alpine3.16

WORKDIR /opt/scatter

COPY app.py freq.py questions.txt requirements.txt ./
COPY front/build ./front/build
RUN pip install -r requirements.txt

ENTRYPOINT [ "/opt/scatter/app.py" ]