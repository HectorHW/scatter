FROM node:18-alpine AS front_builder

WORKDIR /opt/scatter

COPY front .

RUN npm install && npm run build

FROM python:3.10.8-alpine3.16

WORKDIR /opt/scatter/front

COPY --from=0 /opt/scatter/build ./build

WORKDIR /opt/scatter

COPY requirements.txt /opt/scatter/

RUN pip install -r requirements.txt

COPY app.py freq.py /opt/scatter/

ENTRYPOINT [ "/opt/scatter/app.py" ]