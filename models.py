from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)
    current_load = Column(Integer, default=0)

    assignments = relationship("OperatorAssignment", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

    contacts = relationship("Contact", back_populates="lead")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    assignments = relationship("OperatorAssignment", back_populates="source")
    contacts = relationship("Contact", back_populates="source")


class OperatorAssignment(Base):
    __tablename__ = "operator_assignments"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    weight = Column(Integer, default=1)

    operator = relationship("Operator", back_populates="assignments")
    source = relationship("Source", back_populates="assignments")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())

    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")