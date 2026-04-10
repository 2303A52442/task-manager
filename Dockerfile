# Dockerfile - Instructions to build the Docker image for Task Manager

# Step 1: Use official lightweight Python image as the base
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file and install dependencies
# (Doing this before copying the rest of the app allows Docker to cache this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy all project files into the container
COPY . .

# Step 5: Expose port 5000 so it can be accessed from outside the container
EXPOSE 5000

# Step 6: Define the command to run the application
CMD ["python", "app.py"]
