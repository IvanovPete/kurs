FROM nginx:alpine

# Копируем файлы фронта
COPY . /usr/share/nginx/html

# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
