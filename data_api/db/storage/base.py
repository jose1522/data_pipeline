from typing import Optional, List, Type, Union

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from db.models.base import BaseModel
from util.exceptions import RecordNotFound, RecordNotActive, DatabaseError
from util.storage import get_session


class BaseStorage:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
        self.model: Optional[Type[BaseModel]] = None

    def read(self, id: int, is_active_only: bool = True) -> Union[BaseModel, None]:
        """Read a record from the table.
        Args:
            id (int): ID of the record to read.
            is_active_only (bool, optional): Whether to only return active records. Defaults to True.
        Returns:
            Union[ModelType, None]: The record if it exists, else None.
        """
        db_obj = self.session.get(self.model, id)
        if not db_obj:
            raise RecordNotFound(id)
        if is_active_only and not db_obj.is_active:
            raise RecordNotActive(id)
        return db_obj

    def create(self, model: BaseModel) -> BaseModel:
        """Create a record in the table.
        Args:
            model (BaseModel): The model to create.
        Returns:
            BaseModel: The created model.
        """
        try:
            self.session.add(model)
        except SQLAlchemyError as e:
            raise DatabaseError(str(e))
        return model

    def update(self, id: int, data: dict) -> BaseModel:
        """Update a record in the table.
        Args:
            id (int): ID of the record to update.
            data (dict): Dictionary of the data to update.
        """
        db_object = self.read(id)
        db_object.update(data)
        try:
            self.session.add(db_object)
        except Exception as e:
            raise DatabaseError(str(e))
        return db_object

    def upsert(self, data: dict) -> BaseModel:
        db_object = self.session.query(self.model).filter_by(**data).first()
        if db_object:
            db_object.is_active = True
            self.session.add(db_object)
        else:
            db_object = self.create(self.model(**data))
        return db_object

    def delete(self, id: int, soft_delete: bool = True) -> None:
        """Delete a record from the table.
        Args:
            id (int): ID of the record to delete.
            soft_delete (bool, optional): Whether to soft delete the record. Defaults to True.
        """
        db_object = self.read(id)
        if soft_delete:
            db_object.soft_delete()
        else:
            self.session.delete(db_object)

    def filter(self, **kwargs) -> List[BaseModel]:
        """Filter records from the table.
        Args:
            **kwargs: Filter parameters.
        Returns:
            List[ModelType]: List of records that match the filter parameters.
        """
        is_active = kwargs.pop("is_active", True)
        return (
            self.session.query(self.model)
            .filter_by(is_active=is_active, **kwargs)
            .all()
        )

    def all(self, skip: int = 0, limit: int = 100) -> List[BaseModel]:
        """Get all records from the table.
        Args:
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.
        Returns:
            List[ModelType]: List of records.
        """
        return (
            self.session.query(self.model)
            .filter_by(is_active=True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, **kwargs) -> int:
        """Count records from the table.
        Args:
            **kwargs: Filter parameters.
        Returns:
            int: Number of records that match the filter parameters.
        """
        is_active = kwargs.pop("is_active", True)
        return (
            self.session.query(self.model)
            .filter_by(is_active=is_active, **kwargs)
            .count()
        )

    def exists(self, id: int, **kwargs) -> bool:
        """Check if a record exists in the table.
        Args:
            id (int): ID of the record to check.
            **kwargs: Filter parameters.
        Returns:
            bool: True if the record exists, else False.
        """
        is_active = kwargs.pop("is_active", True)
        return (
            self.session.query(self.model)
            .filter_by(id=id, is_active=is_active, **kwargs)
            .scalar()
            is not None
        )

    def bulk_upsert(self, data: list):
        """Bulk upsert records into the table.
        Args:
            data (list): List of dictionaries of data to upsert.
        """
        try:
            self.session.bulk_insert_mappings(self.model, data)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}") from e
