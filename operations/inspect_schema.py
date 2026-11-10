##	Inspect database structure

from database.schema import get_database_schema
from config import DB_CONFIG


def execute(connection):
    print("\nInspecting database schema...")

    schema = get_database_schema(
        connection,
        DB_CONFIG["database"]
    )

    print(f"\nFound {len(schema)} tables.\n")

    for table_name, columns in schema.items():
        print(f"TABLE: {table_name}")

        for column in columns:
            print(
                f"  {column['name']} "
                f"| {column['type']} "
                f"| Nullable: {column['nullable']} "
                f"| Key: {column['key']}"
            )

        print()

    print("Schema inspection completed.")

    return schema