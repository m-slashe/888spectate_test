from typing import Any
from enum import Enum

class Type:

    def get_table_type(self):
        pass

class Varchar(Type):

    size: int

    def __init__(self, size):
        self.size = size

    def get_table_type(self):
        return f'VARCHAR({self.size})'

class Boolean(Type):
    
    def get_table_type(self):
        return 'BOOLEAN'

class Integer(Type):

    # https://dev.mysql.com/doc/refman/8.0/en/integer-types.html

    size: int
    
    def __init__(self, size):
        self.size = size

    def get_table_type(self):
        if self.size == 1:
            return 'TINYINT'
        elif self.size == 2:
            return 'SMALLINT'
        elif self.size == 3:
            return 'MEDIUMINT'
        elif self.size == 4:
            return 'INT'
        elif self.size == 8:
            return 'BIGINT'
        else:
            raise Exception(f'Size {self.size} for integer is not available')

class EnumType(Type):

    enum: Enum

    def __init__(self, enum: Enum):
        self.enum = enum

    def get_table_type(self):
        values = "', '".join([e.value for e in self.enum])
        return f"ENUM('{values}')"

class ForeignKey(Type):

    foreign_table: Any
    table_name: str
    column_name: str

    def __init__(self, foreign_table: Any, column_name: str):
        self.foreign_table = foreign_table
        self.table_name = self.foreign_table.table_name
        self.column_name = column_name

    def get_table_type(self):
        return f'INT NOT NULL'

    def get_table_constraint(self):
        return f'FOREIGN KEY ({self.column_name}) REFERENCES {self.table_name}(id)'

class DateTime(Type):

    def get_table_type(self):
        return 'DATETIME'

class Float(Type):

    size: int
    decimal: int
    
    def __init__(self, size: int, decimal: int):
        self.size = size
        self.decimal = decimal

    def get_table_type(self):
        return f'FLOAT({self.size}, {self.decimal})'

class Property:

    value: Any
    type: Type
    pristine = True

    def __init__(self, type):
        self.type = type

    def set(self, value: Any):
        self.pristine = False
        self.value = value