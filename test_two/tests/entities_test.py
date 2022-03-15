from api.entities import Entity, Property, EventStatus
from api.database import verify_table_exists, set_database
from api.model import Boolean, Integer, Varchar, EnumType
import pytest

TEST_TABLE_NAME = 'test_table' 

class TestModel:

    member1 = Property(Varchar(255))
    member2 = Property(Boolean())
    member3 = Property(Integer(2))
    member4 = Property(EnumType(EventStatus))

class TestModelEntity(Entity, TestModel):

    table_name = TEST_TABLE_NAME

class TestEntities:

    @pytest.fixture(autouse=True)
    def configure_database(self, mysql):
        set_database(mysql)

    def test_should_create_a_select_statment(self):
        test_model_entity = TestModelEntity()
        select_statment = test_model_entity.get_select_statment()
        assert select_statment == f'SELECT id, member1, member2, member3, member4 FROM {TEST_TABLE_NAME}'

    def test_should_create_table_with_success(self):
        test_model_entity = TestModelEntity()
        test_model_entity.create_table()
        assert verify_table_exists(test_model_entity.table_name) == True