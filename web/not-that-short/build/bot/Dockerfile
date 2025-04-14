FROM node:23.7.0

RUN apt-get update && apt-get install -y chromium
RUN apt-get install -y ca-certificates libnss3-tools
RUN rm -rf /var/lib/apt/lists/*

COPY ./server.crt /usr/local/share/ca-certificates/

RUN update-ca-certificates

RUN groupadd -r pptruser \
    && useradd -r -g pptruser -G audio,video pptruser \
    && mkdir -p /home/pptruser/Downloads \
    && chown -R pptruser:pptruser /home/pptruser

WORKDIR /app
COPY package.json package-lock.json ./
ENV PUPPETEER_SKIP_DOWNLOAD=true
RUN npm install --omit=dev
COPY . .

USER pptruser


# Add the server certificate for local testing
RUN mkdir -p /home/pptruser/.pki/nssdb \
    && certutil -N --empty-password -d sql:/home/pptruser/.pki/nssdb \
    && certutil -d sql:/home/pptruser/.pki/nssdb -A -t "P,," -n server -i /usr/local/share/ca-certificates/server.crt

EXPOSE 1337

CMD ["node", "index.js"]
