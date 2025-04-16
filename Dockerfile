# Use an official Python runtime as a parent image
# Using 'slim' reduces the image size
# FROM python:3.11-slim
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and ensure setuptools and wheel are installed/updated
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the requirements file into the container at /app
# Copying it separately allows Docker to cache the dependency installation
#                                                                        layer
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size, --system uses system Python (good
#                                                       practice in containers)
# RUN pip install --no-cache-dir -r requirements.txt --system
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Define the command to run your job's task when the container starts.
# Replace 'main.py' with the actual name of your main script.
# This command will be executed, and when it finishes, the container (and the
#                                                          job task) will stop.
# CMD ["python", "main.py"]

# Alternatively, if your script needs arguments, you might use ENTRYPOINT:
ENTRYPOINT ["python", "main.py"]
# Then you could potentially pass arguments during job execution if needed,
# although often the job's logic is self-contained or configured via
#                                                       environment variables.