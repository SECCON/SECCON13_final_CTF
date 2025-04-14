# How to setup

1. Add [server.crt](./certs/server.crt) to your certificate store (required)
2. Add the following entries to your `hosts` file:
```
127.0.0.1 auth.seccon.internal
127.0.0.1 admin.seccon.internal
127.0.0.1 app.seccon.internal
127.0.0.1 seccon.internal
```
3. Run `docker compose up -d`

