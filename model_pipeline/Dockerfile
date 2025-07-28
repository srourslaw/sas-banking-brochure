# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file FIRST, to leverage Docker's caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code (including the src directory)
COPY . .

# Tell Docker that the container listens on port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# The command to run when the container starts.
# This runs the Uvicorn server, pointing to the 'app' object inside the 'src/app.py' file.
CMD ["python", "src/app.py"]