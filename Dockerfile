FROM python:3.11-slim
WORKDIR /app
# Installiere grundlegende Abhängigkeiten (RunPod SDK ist zwingend)
RUN pip install --no-cache-dir runpod requests
COPY handler.py .
# Starte den RunPod Serverless Handler
CMD [ "python", "-u", "handler.py" ]
