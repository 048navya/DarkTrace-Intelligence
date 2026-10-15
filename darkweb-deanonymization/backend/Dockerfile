FROM python:3.12-slim
WORKDIR /project
COPY darkweb-deanonymization/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY darkweb-deanonymization /project/darkweb-deanonymization
WORKDIR /project/darkweb-deanonymization/backend
RUN useradd --create-home analyst
USER analyst
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
