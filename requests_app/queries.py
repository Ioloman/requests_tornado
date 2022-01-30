from databases.core import Connection


async def insert_request(connection: Connection, key: str, json: str) -> None:
    await connection.execute(
        """
        insert into
            requests.requests
            (id, body, duplicates)
        values
            (:key, :json, 0)
        on duplicate key update
            duplicates = duplicates + 1
        """,
        {'key': key, 'json': json}
    )


async def get_request(connection: Connection, key: str):
    """[
    returns mapping from database
    """
    return await connection.fetch_one(
        "select * from requests.requests where id = :key limit 1",
        {'key': key}
    )


async def delete_request(connection: Connection, key: str) -> int:
    """
    returns amount of entries deleted
    """
    return await connection.execute(
        "delete from requests.requests where id = :key",
        {'key': key}
    )


async def update_request(connection: Connection, old_key: str, new_key: str, json: str) -> int:
    """
    returns amount of entries updated
    """
    return await connection.execute(
        """
        update 
            requests.requests
        set 
            id = :new_key, 
            body = :json, 
            duplicates = 0 
        where 
            id = :old_key
        """,
        {'new_key': new_key, 'json': json, 'old_key': old_key}
    )