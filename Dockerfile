FROM python:3.9-slim

WORKDIR /app
COPY . /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1111
EXPOSE 2222
EXPOSE 8080

CMD ["./run.sh"]
# CMD ["python", "-u", "HTTPServer.py", ";", "python", "-u", "Whisper.py", ";", "python",  "-u", "Client.py"]
# CMD ["python", "Whisper.py"]
# CMD ["python", "Client.py"]

