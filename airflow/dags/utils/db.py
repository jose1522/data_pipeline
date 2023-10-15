import sqlalchemy


from sqlalchemy import Integer, String, Boolean, Float, Numeric, Date, DateTime, Time
import decimal


def _map_sqlalchemy_to_avro(sqlalchemy_type):
    # Integer Types
    if isinstance(sqlalchemy_type, Integer):
        return "int"

    # String Types
    elif isinstance(sqlalchemy_type, String):
        return "string"

    # Boolean Types
    elif isinstance(sqlalchemy_type, Boolean):
        return "boolean"

    # Floating Point Types
    elif isinstance(sqlalchemy_type, (Float, Numeric)):
        return "float" if isinstance(sqlalchemy_type, Float) else "double"

    # Decimal Type
    elif isinstance(sqlalchemy_type, decimal.Decimal):
        return {
            "type": "bytes",
            "logicalType": "decimal",
            "precision": sqlalchemy_type.precision,
            "scale": sqlalchemy_type.scale,
        }

    # Date and Time Types
    elif isinstance(sqlalchemy_type, Date):
        return {"type": "int", "logicalType": "date"}
    elif isinstance(sqlalchemy_type, DateTime):
        return {"type": "long", "logicalType": "timestamp-millis"}
    elif isinstance(sqlalchemy_type, Time):
        return {"type": "long", "logicalType": "time-millis"}

    else:
        return str(sqlalchemy_type)


def get_avro_schema(engine, table_name):
    # Use SQLAlchemy to reflect the table metadata
    metadata = sqlalchemy.MetaData()
    table = sqlalchemy.Table(table_name, metadata, autoload_with=engine)

    # Convert the table metadata to an Avro schema
    fields = [
        {"name": column.name, "type": ["null", _map_sqlalchemy_to_avro(column.type)]}
        for column in table.columns
    ]
    schema = {
        "name": table_name,
        "type": "record",
        "fields": fields,
    }

    return schema
