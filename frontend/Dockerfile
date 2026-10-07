# Etapa 1: compilar la app de React con Node
FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# La URL de la API se mete en el JavaScript al compilar: es la que usará el NAVEGADOR
ARG VITE_API_URL=http://127.0.0.1:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Etapa 2: servir solo los archivos compilados con nginx (sin Node ni node_modules)
FROM nginx:1.29-alpine
COPY --from=build /app/dist /usr/share/nginx/html
