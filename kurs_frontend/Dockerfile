# Simple Nginx image that directly serves the static files present in this folder.
FROM nginx:alpine

# Copy everything (HTML/CSS/JS) into the default nginx html directory.
COPY . /usr/share/nginx/html

# Optional custom nginx config (if the file exists in the project root)
COPY nginx.conf /etc/nginx/conf.d/default.conf

