FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

#default flask port
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]