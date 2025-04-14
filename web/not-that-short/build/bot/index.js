import express from 'express';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import { visit, APP_URL } from './bot.js';

const PORT = '1337';

const app = express();

app.use(
  helmet({
      contentSecurityPolicy: {
          directives: {
              'default-src': ["'none'"],
              'form-action': ["'none'"],
              'style-src': ["https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css"],
              'script-src': ["'sha256-u9HjrxQqdaDhbkbY6Pt8RHrifu2uP0Wpqty6Zew+y/E='"],
              'connect-src': ["'self'"],
              'font-src': null,
              'img-src': null,
              'base-uri': null,
              'object-src': null,
              'script-src-attr': null,
              'upgrade-insecure-requests': null,
          },
      },
      strictTransportSecurity: false,
  }),
);

app.use(express.json());

app.use(express.static('public'));


app.get('/app-url', async (req, res) => {
  return res.send(APP_URL);
});

app.use(
  '/api',
  rateLimit({
    // Limit each IP to 4 requests per 1 minute
    windowMs: 60 * 1000,
    max: 4,
  })
);

app.post('/api/report', async (req, res) => {
  const { url } = req.body;
  if (typeof url !== 'string' || !url.startsWith(APP_URL + '/')) {
    return res.status(400).send('Invalid url');
  }

  try {
    await visit(url);
    return res.sendStatus(200);
  } catch (e) {
    console.error(e);
    return res.status(500).send('Something wrong');
  }
});

app.listen(PORT, '0.0.0.0');
