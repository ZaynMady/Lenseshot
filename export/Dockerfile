# ---- Base Stage ----
# Use a specific Node.js version for consistency.
FROM node:18-alpine AS base

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
# This is done first to leverage Docker's layer caching.
# The npm install step will only re-run if these files change.
COPY package*.json ./

# ---- Dependencies Stage ----
# Install only production dependencies.
FROM base AS dependencies
RUN npm install --production

# ---- Build/Development Stage ----
# This stage can be used for development with all dependencies.
FROM base AS dev-dependencies
RUN npm install

# ---- Production Stage ----
# Create the final, lean production image.
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
# Copy the rest of the application code
COPY . .

# Expose the port the app runs on.
EXPOSE 4000

# The command to start the app.
CMD ["npm", "start"]
