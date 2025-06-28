#initializing Python version 
FROM python:3.13-slim
# Setting the working directory
WORKDIR /lenseshot

# Copying the requirements file into the container
COPY requirements.txt ./

# Installing the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copying the rest of the application code into the container
COPY . .

# Exposing the port on which the application will run
EXPOSE 5000

# Command to run the application
CMD ["python", "run.py"]