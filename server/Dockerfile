FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --disable-pip-version-check -r ./requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV PATH="/venv/bin:$PATH"
CMD ["sh", "-c", "python scripts/load_user_data.py && exec uvicorn application:app --host 0.0.0.0 --port 8000"]
