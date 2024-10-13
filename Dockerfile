# Use the official Python image as a base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Change the working directory to the main application directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Change the working directory to the "src" directory
WORKDIR /app

# Expose the port that your FastAPI application will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
