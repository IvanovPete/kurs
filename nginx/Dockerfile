FROM nginx:alpine

# Копируем файлы фронтенда
COPY ./kurs_frontend /usr/share/nginx/html
# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

