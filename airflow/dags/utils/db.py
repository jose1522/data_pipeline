import sqlalchemy


def get_avro_schema(engine, table_name):
    # Use SQLAlchemy to reflect the table metadata
    metadata = sqlalchemy.MetaData()
    table = sqlalchemy.Table(table_name, metadata, autoload_with=engine)

    # Convert the table metadata to an Avro schema
    fields = [
        {"name": column.name, "type": ["null", str(column.type)]}
        for column in table.columns
    ]
    schema = {
        "name": table_name,
        "type": "record",
        "fields": fields,
    }

    return schema
