const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');

const app = express();
const port = 3000;

for (const env of ['ADMIN_HOSTNAME', 'APP_HOSTNAME', 'AUTH_HOSTNAME', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']) {
    if (!process.env[env]) {
        throw new Error(`${env} is not set`);
    }
}

const ADMIN_URL = `https://${process.env.ADMIN_HOSTNAME}`;
const APP_URL = `https://${process.env.APP_HOSTNAME}`;
const AUTH_URL = `https://${process.env.AUTH_HOSTNAME}`;
const LOGIN_TARGETS = new Map([
    ['ADMIN', ADMIN_URL + '/auth/callback'],
    ['APP', APP_URL + '/auth/callback']
]);

const db = new sqlite3.Database('/app/data/users.db');
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_admin BOOLEAN
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS auth_codes (
        code TEXT PRIMARY KEY,
        login_target TEXT,
        user_id INTEGER,
        username TEXT,
        is_admin BOOLEAN,
        expires_at INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )`);

    db.get('SELECT id, username, is_admin FROM users WHERE id = 1', [], (err, row) => {
        if (err) {
            console.error('Error checking admin user:', err);
            process.exit(1);
        }
        if (row && (row.username !== process.env.ADMIN_USERNAME || !row.is_admin)) {
            console.error('User ID 1 already exists with incorrect data: ', row);
            process.exit(1);
        }
        if (!row) {
            bcrypt.hash(process.env.ADMIN_PASSWORD, 10, (err, hashedPassword) => {
                if (err) {
                    console.error('Error hashing admin password:', err);
                    process.exit(1);
                }
                db.run('INSERT INTO users (id, username, password, is_admin) VALUES (1, ?, ?, ?)',
                    [process.env.ADMIN_USERNAME, hashedPassword, true],
                    (err) => {
                        if (err) {
                            console.error('Error creating admin user:', err);
                            process.exit(1);
                        }
                        console.log('Admin user created successfully');
                    }
                );
            });
        }
    });
});

app.set('trust proxy', '172.137.0.2');
app.use(
    '/registration',
    rateLimit({
        windowMs: 60 * 1000,
        max: 2,
    })
);
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: generateSecureToken(32),
    resave: false,
    saveUninitialized: false,
    cookie: { httpOnly: true }
}));
app.use(
    helmet({
        contentSecurityPolicy: {
            directives: {
                'default-src': ["'none'"],
                'style-src': [
                    // Top
                    "'sha256-Vil6PVLiEOcfz2w+jU4r3mjPzL53u3QBC71mQeZyhmw='",
                    // Login/Registration
                    "'sha256-hLpxLweknPKWglh0VLk/hsn/C1aQ2lQjv84TG408EC4='",
                ],
                'form-action': [APP_URL, ADMIN_URL, "'self'"],
                'font-src': null,
                'img-src': null,
                'script-src': null,
                'base-uri': null,
                'object-src': null,
                'script-src-attr': null,
            },
        },
    }),
);

app.set('view engine', 'ejs');

function generateSecureToken(bytes = 32) {
    return crypto.randomBytes(bytes).toString('hex');
}


app.get('/', (req, res) => {
    res.render('home', { user: req.session.user });
});

app.get('/register', (_, res) => {
    res.render('register');
});

app.post('/registration', async (req, res) => {
    const { username, password } = req.body;

    if (typeof username !== 'string' || typeof password !== 'string') {
        return res.status(400).json({ error: 'Invalid request' });
    }

    if (username === process.env.ADMIN_USERNAME) {
        return res.status(400).json({ error: 'Invalid username' });
    }

    if (password.length < 8 || password.length > 100) {
        return res.status(400).json({ error: 'Password must be between 8 and 100 characters long' });
    }

    if (username.length < 5 || username.length > 100) {
        return res.status(400).json({ error: 'Username must be between 5 and 100 characters long' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    db.run('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
        [username, hashedPassword, false],
        (err) => {
            if (err) {
                return res.render('register', { error: 'Username already exists' });
            } else {
                return res.redirect('/login');
            }
        }
    );
});

app.get('/login', (_, res) => {
    res.render('login');
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;

    if (typeof username !== 'string' || typeof password !== 'string') {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.get('SELECT * FROM users WHERE username = ?', [username], async (err, user) => {
        if (user && await bcrypt.compare(password, user.password)) {
            req.session.user = { id: user.id, username: user.username, is_admin: !!user.is_admin };
            const { login_target, state } = req.query;
            if (typeof login_target === 'string' && typeof state === 'string') {
                const url = new URL(`/auth/login`, AUTH_URL);
                url.searchParams.set('login_target', login_target);
                url.searchParams.set('state', state);
                return res.redirect(url.toString());
            } else {
                return res.redirect('/');
            }
        } else {
            return res.render('login', { error: 'Invalid credentials' });
        }
    });
});

app.get('/auth/login', (req, res) => {
    const { login_target, state } = req.query;

    if (typeof login_target !== 'string' || typeof state !== 'string') {
        return res.status(400).json({ error: 'Invalid request' });
    }

    if (!LOGIN_TARGETS.has(login_target)) {
        return res.status(400).send('Invalid login target');
    }

    if (!req.session.user) {
        const url = new URL(`/login`, AUTH_URL);
        url.searchParams.set('login_target', login_target);
        url.searchParams.set('state', state);
        return res.redirect(url.toString());
    }

    const code = generateSecureToken(32);
    const expiresAt = Date.now() + 10 * 60 * 1000;

    db.run('INSERT INTO auth_codes (code, login_target, user_id, username, is_admin, expires_at) VALUES (?, ?, ?, ?, ?, ?)',
        [code, login_target, req.session.user.id, req.session.user.username, req.session.user.is_admin, expiresAt],
        (err) => {
            if (err) {
                return res.status(500).send('Error generating authorization code');
            }

            const redirectUrl = new URL(LOGIN_TARGETS.get(login_target));
            redirectUrl.searchParams.set('code', code);
            redirectUrl.searchParams.set('state', state);
            res.redirect(redirectUrl.toString());
        }
    );
});

app.get('/auth/id', (req, res) => {
    const { code, login_target } = req.query;

    if (typeof code !== 'string' || typeof login_target !== 'string') {
        return res.status(400).json({ error: 'Invalid request' });
    }

    db.get(
        'SELECT * FROM auth_codes WHERE code = ? AND expires_at > ? AND login_target = ?',
        [code, Date.now(), login_target],
        (err, authCode) => {
            if (err || !authCode) {
                return res.status(400).json({ error: 'invalid_code' });
            }

            db.run('DELETE FROM auth_codes WHERE code = ?', [code]);

            res.json({
                user_id: authCode.user_id,
                username: authCode.username,
                is_admin: authCode.is_admin
            });
        }
    );
});

app.listen(port, () => {
    console.log(`Auth server running at http://localhost:${port}`);
});
