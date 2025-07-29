FROM python:3.13-alpine
WORKDIR app/
COPY . .
RUN pip install -r requirements.txt
CMD python main.py && uvicorn web.app:app --host localhost --port 8005