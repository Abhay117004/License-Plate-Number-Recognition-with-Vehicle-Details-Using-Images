# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
# Note: Many hosting providers will override this with their own port.
EXPOSE 5000

# Define environment variable for the port (good practice for hosting platforms)
ENV PORT 5000

# Run main.py when the container launches using the Flask development server.
CMD ["python", "main.py"]
