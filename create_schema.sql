CREATE TABLE account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT,
    port INTEGER,
    type TEXT,
    username TEXT,
    password TEXT
);

CREATE TABLE rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER REFERENCES account(id),
    priority INTEGER NOT NULL DEFAULT 10,
    field TEXT,
    searchstring TEXT,
    destination TEXT
);

CREATE TABLE log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logtime INTEGER NOT NULL,
    account_id INTEGER REFERENCES account(id),
    rule_id INTEGER REFERENCES rule(id),
    logtext TEXT
);

