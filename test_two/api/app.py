from api.database import verify_table_exists, connect_database, set_database
from api.entities import SelectionEntity, SportEntity, EventEntity
from flask import Flask
from api.api import api_blueprint

def create_app(*, db = None):
    app = Flask(__name__)
    app.register_blueprint(api_blueprint)

    if db is None:
        db = connect_database()

    set_database(db)

    entities = [SportEntity, EventEntity, SelectionEntity]
    for entity in entities:
        if not verify_table_exists(entity.table_name):
            entity().create_table()

    return app

