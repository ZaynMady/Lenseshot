# --- FRONTEND Dockerfile ---
FROM node:24.0.2

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json ./
RUN npm install

# Copy all frontend files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run in dev mode
CMD ["npm", "run", "dev", "--", "--host"]
