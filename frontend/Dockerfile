FROM node:22-alpine AS build

WORKDIR /app/frontend

ARG VITE_API_BASE_URL=/api/v1
ARG VITE_API_PROXY_TARGET=http://api:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_API_PROXY_TARGET=${VITE_API_PROXY_TARGET}

RUN npm install -g npm@11.12.0

COPY frontend/package.json frontend/package-lock.json ./
COPY frontend/tsconfig.json frontend/vite.config.ts frontend/eslint.config.js frontend/tailwind.config.ts ./
COPY frontend/postcss.config.cjs frontend/index.html ./
COPY frontend/src ./src

RUN npm ci
RUN npm run build

FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html

EXPOSE 80

