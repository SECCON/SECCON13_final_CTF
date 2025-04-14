FROM node:22-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget

RUN wget https://github.com/cloudflare/cloudflared/releases/download/2025.2.0/cloudflared-linux-amd64 -O cloudflared
RUN chmod +x cloudflared

COPY solve.js .
COPY key.key .
COPY cert.crt .

CMD ["node", "solve.js"]