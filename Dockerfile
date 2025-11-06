FROM python:3.9-alpine
WORKDIR /app
RUN apk add --no-cache curl
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1"]
