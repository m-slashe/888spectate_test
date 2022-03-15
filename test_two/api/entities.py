from __future__ import annotations
from enum import Enum
from api.logger import logger
from api.database import get_database, verify_table_exists
from api.model import Boolean, DateTime, EnumType, Float, ForeignKey, Integer, Property, Varchar
from typing import Any, Dict, List, cast
from datetime import datetime

class EventType(Enum):
    PrePlay = 'preplay'
    InPlay = 'inplay'

class EventStatus(Enum):
    Pending = 'pending'
    Started = 'started'
    Ended = 'ended'
    Cancelled = 'cancelled'

class Outcome(Enum):
    Unsettled = 'unsettled'
    Void = 'void'
    Lose = 'lose'
    Win = 'win'

class Entity:

    id = Property(Integer(8))
    table_name: str

    def drop_table(self):
        mydb = get_database()
        cursor = mydb.cursor()
        cursor.execute(f'DROP TABLE {self.table_name}')

    def create_table(self):
        if not verify_table_exists(self.table_name):
            mydb = get_database()
            create_table_cursor = mydb.cursor()
            properties = self.get_properties()

            def get_table_columns(properties):
                columns = []
                for prop in properties:
                    property_attr = cast(Property, getattr(self, prop))
                    column_name = prop
                    if hasattr(property_attr.type, 'column_name'):
                        column_name = property_attr.type.column_name
                    
                    columns.append(f"{column_name} {cast(Property, getattr(self, prop)).type.get_table_type()}")
                return columns

            table_columns = ", ".join(get_table_columns(properties))
            constraint_statements = []
            for prop in properties:
                if hasattr(cast(Property, getattr(self, prop)).type, 'get_table_constraint'):
                    constraint_statements.append(cast(Property, getattr(self, prop)).type.get_table_constraint())

            constraint_string = ''
            if len(constraint_statements) > 0:
                constraint_string = f", {', '.join(constraint_statements)}"

            create_table_statement = f'CREATE TABLE {self.table_name} (id INT NOT NULL AUTO_INCREMENT, {table_columns}, CONSTRAINT id_pk PRIMARY KEY (id){constraint_string})'
            logger.debug(f'Create Statement: {create_table_statement}')
            create_table_cursor.execute(create_table_statement)
        else:
            logger.info(f'{self.table_name} table already created')

    def get_properties(self, *, with_id = False):
        properties = []
        for prop in dir(self):
            if isinstance(getattr(self, prop), Property):
                properties.append(prop)
        if not with_id:
            properties.remove('id')
        return properties

    def get_columns(self, properties):
        columns = []
        for prop in properties:
            member_property = cast(Property, getattr(self, prop))
            column_name = prop
            if hasattr(member_property.type, 'column_name'):
                column_name = member_property.type.column_name
            
            columns.append(column_name)
        return columns

    def is_date(self, string: str):
        try:
            datetime.strptime(string, '%a, %d %b %Y %H:%M:%S GMT')
            return True
        except:
            return False

    def get_values(self, properties):
        values = []
        for prop in properties:
            member_property = cast(Property, getattr(self, prop))
            value = member_property.value

            if self.is_date(member_property.value):
                value = datetime.strptime(member_property.value, '%a, %d %b %Y %H:%M:%S GMT')

            values.append(value)
        return values

    def update_by_json(self, json: Dict[str, Any]):
        properties = self.get_properties(with_id=True)
        for prop in properties:
            if json.get(prop) is not None:
                cast(Property, getattr(self, prop)).set(json[prop])
        return self

    def get_select_statment(self):
        properties = self.get_properties(with_id=True)
        columns = self.get_columns(properties)
        return f"SELECT {', '.join(columns)} FROM {self.table_name}"

    def get_all(self):
        select_statment = self.get_select_statment()

        mydb = get_database()
        mycursor = mydb.cursor()
        mycursor.execute(select_statment)
        return self.__tranform_result__(mycursor)

    def append_custom_filters(self, filter_dict, where_filters, values_filters):
        pass

    def get_by_filter(self, filter_dict):
        property_filters = {}
        properties = self.get_properties()
        for prop in filter_dict:
            if prop.replace('regexp_', '') in properties:
                property_filters[prop] = filter_dict[prop]
                
        select_statment = self.get_select_statment()

        mydb = get_database()
        mycursor = mydb.cursor()

        def get_value_where(prop: str):
            if 'regexp_' in prop:
                return f"REGEXP_LIKE({prop.replace('regexp_', '')}, %s)"
            elif isinstance(cast(Property, getattr(self, prop)).type, Varchar):
                return f"LOWER({prop}) like LOWER(CONCAT('%%', %s, '%%'))"
            elif isinstance(cast(Property, getattr(self, prop)).type, ForeignKey):
                return f'{prop}_id = %s'
            else:
                return f'{prop} = %s'

        where_filters = list(map(get_value_where, property_filters))
        values_filters = [property_filters[prop] for prop in property_filters]

        self.append_custom_filters(filter_dict, where_filters, values_filters)

        where_statement = ' AND '.join(where_filters)

        val = tuple(values_filters)

        select_filter_statement = f'{select_statment} WHERE {where_statement}'

        mycursor.execute(select_filter_statement, val)
        return self.__tranform_result__(mycursor)

    def get_by_id(self, id: int) -> Entity:
        select_statment = self.get_select_statment()

        mydb = get_database()
        mycursor = mydb.cursor()
        val = (str(id))
        mycursor.execute(f'{select_statment} WHERE id = %s', val)
        results = self.__tranform_result__(mycursor)
        results_transformed = [self.__class__().update_by_json(result) for result in results]
        return results_transformed[0]

    def __tranform_result__(self, cursor):
        properties = self.get_properties(with_id=True)
        result = cursor.fetchall()

        pre_results = [{ prop: row[index] for index, prop in enumerate(properties) } for row in result]

        def transform_data_type(old_object):
            new_object = {}
            for prop in old_object:
                value = old_object[prop]

                if isinstance(getattr(self, prop).type, Boolean):
                    value = True if old_object[prop] == 1 else False

                new_object[prop] = value
            return new_object

        return list(map(transform_data_type, pre_results))

    def create(self):
        properties = self.get_properties()

        mydb = get_database()
        mycursor = mydb.cursor()
                
        sql = f"INSERT INTO {self.table_name} ({', '.join(self.get_columns(properties))}) VALUES ({', '.join(['%s' for x in range(len(properties))])})"

        val = tuple(self.get_values(properties))
        mycursor.execute(sql, val)

        mydb.commit()

        logger.info(f"{mycursor.rowcount} record inserted.")
        self.id.set(mycursor.lastrowid)
        return mycursor.lastrowid

    def update(self):
        properties = self.get_properties()
        columns = self.get_columns(properties)

        mydb = get_database()
        mycursor = mydb.cursor()

        set_statment = ', '.join(map(lambda prop: f'{prop} = %s', columns))
        sql = f'UPDATE {self.table_name} SET {set_statment} WHERE id = %s'
        parameters_list = self.get_values(properties)
        parameters_list.append(cast(Property, getattr(self, 'id')).value)
        val = tuple(parameters_list)
        mycursor.execute(sql, val)

        mydb.commit()
        logger.info(f"{mycursor.rowcount} record updated.")

    def to_json(self):
        properties = self.get_properties(with_id=True)
        return { prop: cast(Property, getattr(self, prop)).value for prop in properties }

class Sport:

    name = Property(Varchar(255))
    slug = Property(Varchar(255))
    active = Property(Boolean())

class SportEntity(Entity, Sport):

    table_name = 'sports'

    def append_custom_filters(self, filter_dict, where_filters: List[str], values_filters: List[Any]):
        if 'event_active_threshold' in filter_dict:
            value_filter = filter_dict['event_active_threshold']
            where_filters.append(f'EXISTS ( SELECT 1 total FROM events WHERE sport_id = {self.table_name}.id GROUP BY sport_id HAVING COUNT(1) >= %s)')
            values_filters.append(value_filter)
        return where_filters

class Event:
    
    name = Property(Varchar(255))
    slug = Property(Varchar(255))
    active = Property(Boolean())
    type = Property(EnumType(EventType)) 
    sport = Property(ForeignKey(SportEntity, 'sport_id'))
    status = Property(EnumType(EventStatus)) 
    scheduled_start = Property(DateTime())
    actual_start = Property(DateTime())

class EventEntity(Entity, Event):

    table_name = 'events'

    def append_custom_filters(self, filter_dict, where_filters: List[str], values_filters: List[Any]):
        if 'selection_active_threshold' in filter_dict:
            value_filter = filter_dict['selection_active_threshold']
            where_filters.append(f'EXISTS ( SELECT 1 total FROM selections WHERE event_id = {self.table_name}.id GROUP BY event_id HAVING COUNT(1) >= %s)')
            values_filters.append(value_filter)
        return where_filters

class Selection:

    name = Property(Varchar(255))
    event = Property(ForeignKey(EventEntity, 'event_id'))
    price = Property(Float(6, 2))
    active = Property(Boolean())
    outcome = Property(EnumType(Outcome)) 

class SelectionEntity(Entity, Selection):

    table_name = 'selections'