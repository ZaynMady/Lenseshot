# Use lightweight Python base
FROM python:3.13

# Set working directory inside container
WORKDIR /app

# Copy only requirements first for caching
COPY ./projects/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main project code
COPY ./projects /app

# Copy utilities if you want to use them in your Flask app
COPY ./utilities /app/utilities

# Expose Flask port
EXPOSE 7000

# Environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development  

# Run Flask
CMD ["flask", "run", "--port=7000"]
