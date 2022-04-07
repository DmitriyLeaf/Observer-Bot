FROM python:3.9

COPY /source /source
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /source

# Run an app
CMD ["python", "main.py"]