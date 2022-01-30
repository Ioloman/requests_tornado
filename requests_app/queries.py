from databases.core import Connection


async def insert_request(connection: Connection, key: str, json: str) -> None:
    """
    0 duplicates -> 1 unique request
    1 duplicates ->  2 same requests
    etc.
    """
    request = await connection.fetch_one(
        "select id from requests.requests where id = :key",
        {'key': key}
    )

    if request:
        await connection.execute(
            """
            insert into
                requests.requests
                (id, body, duplicates)
            values
                (:key, :json, 0)
            """,
            {'key': key, 'json': json}
        )
    else:
        await connection.execute(
            """
            update 
                requests.requests
            set 
                duplicates = duplicates + 1
            where 
                id = :key
            """,
            {'key': key}
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


async def get_statistics(connection: Connection):
    """
    because duplicates == 0 means 1 unique entry
    it is a bit complicated to count all requests and all duplicates
    duplicates == 1 means there's 2 same requests 
    so count(*) or +1 to everything needs to be added
    """
    return await connection.fetch_one(
        """
        select
            count(*) + sum(duplicates) as sum_all,
            sum(if(duplicates <= 0, 0, duplicates + 1)) as sum_duplicates
        from requests.requests
        """
    )