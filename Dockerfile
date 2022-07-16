# Pull base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create local_data_storage 
RUN mkdir -p /app/local_data_store && \
    LC_ALL=C </dev/urandom tr -dc 'A-Za-z0-9!"#$%&()*+,-./:;<=>?@[\]^_`{|}~' | head -c 50 > /app/local_data_store/secret.txt && \
    echo DJANGO_SECRET_KEY='"'`cat /app/local_data_store/secret.txt`'"' > /app/local_data_store/secret_key.txt && \
    rm /app/local_data_store/secret.txt
    # TODO: chown  

# Set work directory
WORKDIR /app

# Install dependencies
COPY goya_core/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --quiet -r requirements.txt

# Copy project
COPY . /app/
