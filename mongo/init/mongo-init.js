db = db.getSiblingDB('graylog');

// Create a user for the 'graylog' database
db.createUser({
    user: 'admin',
    pwd: 'adminpassword',
    roles: [{ role: 'readWrite', db: 'graylog' }]
});

// Create a collection and insert documents as before
db.createCollection('dummy');