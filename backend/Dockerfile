# Stage 1: Install dependencies
FROM python:3.9 AS dependencies

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt first, to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Install Model dependencies
# CMD ["python", "pipelines/prepare_model.py"]

# Stage 3: Copy application code and use cached dependencies
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy dependencies from the previous stage
COPY --from=dependencies /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy the application code into the container
COPY . /app

# RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')"

# Make port 8000 available to the world outside this container
EXPOSE 8000 8080 5000

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run the application
CMD ["fastapi", "dev", "serverfastapi/main.py", "--host", "0.0.0.0"]
