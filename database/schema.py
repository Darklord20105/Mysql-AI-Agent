def get_database_schema(connection, database_name):
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, ORDINAL_POSITION
            """,
            (database_name,)
        )

        columns = cursor.fetchall()

        schema = {}

        for column in columns:
            table_name = column["TABLE_NAME"]

            if table_name not in schema:
                schema[table_name] = []

            schema[table_name].append({
                "name": column["COLUMN_NAME"],
                "type": column["COLUMN_TYPE"],
                "nullable": column["IS_NULLABLE"],
                "key": column["COLUMN_KEY"]
            })

        return schema

    finally:
        cursor.close()