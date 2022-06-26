db.createUser({
    user: "db_admin",
    pwd: "!Yh096yGs-886%",
    roles: [
        {
            role: 'readWrite',
            db: 'deer_block_message'
        }
    ]
})