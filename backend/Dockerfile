# --- BACKEND Dockerfile ---
FROM python:3.13

# Set workdir
WORKDIR /app

# Install deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask server (assumes run.py exists and calls app.run())
CMD ["python", "run.py"]
