# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY app /app

# Expose the port the app runs on
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=api.py

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
