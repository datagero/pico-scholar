# Use an official Node.js image as the base image
FROM node:18-alpine as build

# Set the working directory inside the container
WORKDIR /app


# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install application dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install --unsafe-perm=true --allow-root

# add app
COPY . ./
RUN npm run build

## Method 1: Below use nginx to serve the app through gitpod
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


## Method 2: The below works for OpenShift deployments without nginx
# # RUN chown -R 1000:1000 ./
# RUN mkdir -p /app/node_modules/.cache 
# RUN chown -R 1000:0 /app && chmod -R ug+rwx /app
# RUN chown -R 1000:0 /app/node_modules/.cache
# RUN chmod -R 777 /app/node_modules/.cache
# USER 1000

# EXPOSE 3000

# # Disable host check to fix Invalid Host header
# ENV WDS_SOCKET_PORT 0

# # start app
# CMD ["npm", "start"]
