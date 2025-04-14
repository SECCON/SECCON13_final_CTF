FROM node:23.7.0-slim

WORKDIR /app

COPY package*.json ./
RUN npm i

COPY . .

RUN mkdir -p /app/data

EXPOSE 3000

CMD ["node", "server.js"]
