# Use the official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the server files into the container
COPY src/ .

# Install any required dependencies
RUN pip install requests

# Expose the port that the server listens on
EXPOSE 8000

# Set the entry point command to run the server
CMD ["python", "server.py"]
