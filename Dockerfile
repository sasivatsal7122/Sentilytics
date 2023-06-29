# Use the official Python image as the base image
FROM python:3.9.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY download_resources.py .
# Copy the entire project directory into the container
COPY . .

# Exclude unnecessary files and folders
COPY .dockerignore .dockerignore

# Expose the port your FastAPI application listens on (replace 8000 with your desired port)
EXPOSE 8000

RUN python download_resources.py
# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
