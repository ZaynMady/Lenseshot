# Use a specific, lightweight Python version for a smaller image size.
FROM python:3.13

# Set the working directory in the container.
WORKDIR /app

# --- Install Shared Library ---
# Copy the shared library from the parent directory and install it.
# This is done first to leverage caching.
COPY ./my-util-lib /app/my-util-lib
RUN pip install --no-cache-dir /app/my-util-lib

# --- Install Service-Specific Dependencies ---
# Copy only the requirements.txt to leverage Docker's layer caching.
# The pip install command will only be re-run if requirements.txt changes.
COPY ./scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
# Copy the rest of the application code from the 'scripts' directory.
COPY ./scripts .

# Expose the port the app runs on.
EXPOSE 8000

# The command to run the application will be provided by docker-compose.yml
RUN flask run --host=0.0.0.0 --port=7000