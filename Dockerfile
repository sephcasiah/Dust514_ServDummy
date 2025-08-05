FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir
EXPOSE 59224 59233 8080
CMD ["python", "dust514_servdummy_fly.py"]
