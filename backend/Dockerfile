# Stage 2: Copy application code and use cached dependencies
# The current stage `pico-env-builder` already contains dependencies.
FROM datagero/pico-env-builder:latest AS pico-backend

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

RUN pip install fastapi-cors>="^0.0.6"
RUN mkdir -p /app/nltk_data && \
    python -m nltk.downloader -d /app/nltk_data punkt wordnet stopwords

# Make ports available to the world outside this container
EXPOSE 8000 8080 5000 3000 8501

# Define environment variable
ENV NLTK_DATA=/app/nltk_data
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run the application
CMD ["uvicorn", "serverfastapi.main:app", "--host", "0.0.0.0", "--loop", "asyncio"]
