# Use an official Node.js image as the base image
FROM node:18-alpine as build

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install --no-optional

# Copy the rest of the application code
COPY . .

# Build the React application
RUN npm run build

# Use a lightweight server to serve the built files
FROM nginx:alpine

# Copy the build output to the NGINX web server directory
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom NGINX configuration
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# Expose the port on which the app runs
EXPOSE 80

# Start the NGINX server
CMD ["nginx", "-g", "daemon off;"]
