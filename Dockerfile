FROM python:3.12.7-slim AS base

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

USER app

ENTRYPOINT ["python", "-m", "app"]
CMD ["serve"]
