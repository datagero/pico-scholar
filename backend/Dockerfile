# Stage 2: Copy application code and use cached dependencies
# The current stage `pico-env-builder` already contains dependencies.
FROM datagero/pico-env-builder:latest AS pico-env-builder

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000 8080 5000

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run the application
CMD ["uvicorn", "serverfastapi.main:app", "--host", "0.0.0.0"]
