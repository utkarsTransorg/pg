FROM node:18-alpine3.17 AS build

# Set working directory
WORKDIR /app

# Copy only package.json and package-lock.json to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install --silent

# Copy the rest of the application files
COPY . .

# Build the application
RUN npm run build

# Use Ubuntu to host the app
FROM ubuntu:22.04

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Copy the build output to Nginx's HTML directory
COPY --from=build /app/dist /var/www/html/

# Copy a custom Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 5173

# Run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]