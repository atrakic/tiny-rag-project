FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt  ./
COPY city_demo.py  ./

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --disable-pip-version-check -r ./requirements.txt

# ENTRYPOINT [ "python", "city_demo.py" ]
