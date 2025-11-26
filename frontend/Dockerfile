# ---- Base Stage ----
# Use a specific, stable Node.js version. 'alpine' is a lightweight version.
FROM node:20-alpine AS base

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# ---- Dependencies Stage ----
# Install all dependencies, including devDependencies, for development and building
FROM base AS dependencies
RUN npm install

# ---- Build Stage ----
# Build the React application
FROM dependencies AS build

# Copy the rest of your app's source code
COPY . .
RUN npm run build

# ---- Production Stage ----
# Use a lightweight Nginx server to serve the static files
FROM nginx:1.25-alpine AS production

# Expose the port Nginx will run on
EXPOSE 5173

# Copy the built assets from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy a custom Nginx configuration if needed (optional but good practice for routing)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# The default command for the nginx image is to start the server, so CMD is not needed.
