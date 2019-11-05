FROM python:3.7.3
ADD . /redis-task
WORKDIR /redis-task
RUN pip install -r requirements.txt
COPY . ./redis-task
CMD ["python", "app.py"]