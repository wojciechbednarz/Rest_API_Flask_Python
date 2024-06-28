# CONTRIBUTING

## Dockerfile for flask run

#####FROM python:3.10
#####EXPOSE 5000 
#####WORKDIR /app
#####COPY requirements.txt .
#####RUN pip install --no-cache-dir --upgrade -r requirements.txt
#####COPY . .
#####CMD ["flask", "run", "--host", "0.0.0.0"]


## How to run Dockerfile locally

'''
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" IMAGE_NAME 
sh -c "flask run" --host 0.0.0.0"
'''
