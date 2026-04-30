FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
# Если нужен билд фронтенда, раскомментируйте следующую строку
# RUN npm run build
EXPOSE 3000 3001
CMD ["npx", "concurrently", "\"npm run start:site\"", "\"npm run start:admin\""]
RUN npm install --omit=dev

