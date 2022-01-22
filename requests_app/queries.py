from databases.core import Connection


async def insert_request(connection: Connection, key: str, json: str):
    await connection.execute(
        """
        insert into
            requests.requests
            (id, body, duplicates)
        values
            (:key, :json, 1)
        on duplicate key update
            duplicates = duplicates + 1
        """,
        {'key': key, 'json': json}
    )


async def get_request(connection: Connection, key: str):
    return await connection.fetch_one(
        "select * from requests.requests where id = :key limit 1",
        {'key': key}
    )