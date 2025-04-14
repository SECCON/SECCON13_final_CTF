import puppeteer from 'puppeteer';

const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? console.log('No admin username') ?? process.exit(1);
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? console.log('No admin password') ?? process.exit(1);
const AUTH_URL = 'https://' + (process.env.AUTH_HOSTNAME ?? console.log('No auth hostname') ?? process.exit(1));
export const APP_URL = 'https://' + (process.env.APP_HOSTNAME ?? console.log('No app hostname') ?? process.exit(1));

const sleep = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const visit = async (url) => {
  console.log(`start: ${url}`);

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/usr/bin/chromium',
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--js-flags="--noexpose_wasm"',
    ],
  });

  const context = await browser.createBrowserContext();

  try {
    const page = await context.newPage();
    
    // Login
    await page.goto(AUTH_URL + '/login', { timeout: 3_000 });
    await page.type('input[name="username"]', ADMIN_USERNAME);
    await page.type('input[name="password"]', ADMIN_PASSWORD);
    await page.click('button[type="submit"]');

    await page.waitForSelector('#go-app');
    await page.click('#go-app');

    // Visit reported URL
    await page.goto(url, { timeout: 3_000 });
    await sleep(5_000);
    await page.close();
  } catch (e) {
    console.error(e);
  }

  await context.close();
  await browser.close();

  console.log(`end: ${url}`);
};
