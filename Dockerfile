
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["bash", "start.sh"]
