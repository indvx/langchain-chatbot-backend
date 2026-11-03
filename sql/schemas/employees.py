from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from sql.models.employees import Employee as EmployeeModel



# Marshmallow schemas for serializing SQLAlchemy Employee ORM models to plain dictionaries.

class EmployeeSchema(SQLAlchemyAutoSchema):
    """Full employee serialization including timestamps and nested address relations."""
    class Meta:
        model = EmployeeModel
        load_instance = True
        include_relationships = True
        include_fk = True
        fields = (
            "id",
            "name",
            "email",
            "password",
            "employee_type",
            "created_at",
            "updated_at",
            "addresses",
        )


class CreateEmployeeSchema(SQLAlchemyAutoSchema):
    """Restricted schema for extracting signup fields (name, email, password)."""
    class Meta:
        model = EmployeeModel
        load_instance = True
        include_relationships = True
        include_fk = True
        fields = (
            "name",
            "email",
            "password",
        )


class ReadAllEmployeeSchema(SQLAlchemyAutoSchema):
    """Schema for serializing employee lists with addresses for administrative views."""
    class Meta:
        model = EmployeeModel
        load_instance = True
        include_relationships = True
        include_fk = True
        fields = (
            "id",
            "name",
            "email",
            "password",
            "employee_type",
            "created_at",
            "updated_at",
            "addresses",
        )


