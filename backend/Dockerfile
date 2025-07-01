FROM python:3.10

WORKDIR /App

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 👇 Tell Python where to start looking for packages
ENV PYTHONPATH=/App/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
