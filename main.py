from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random
from typing import List

import models
import schemas
from database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Distribution CRM")


@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    db_operator = models.Operator(**operator.dict())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator


@app.get("/operators/", response_model=List[schemas.Operator])
def read_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operators = db.query(models.Operator).offset(skip).limit(limit).all()
    return operators


@app.put("/operators/{operator_id}", response_model=schemas.Operator)
def update_operator(operator_id: int, operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    db_operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if not db_operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    for field, value in operator.dict().items():
        setattr(db_operator, field, value)

    db.commit()
    db.refresh(db_operator)
    return db_operator


@app.post("/sources/", response_model=schemas.Source)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    db_source = models.Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@app.get("/sources/", response_model=List[schemas.Source])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = db.query(models.Source).offset(skip).limit(limit).all()
    return sources


@app.post("/assignments/", response_model=schemas.Assignment)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    db_assignment = models.OperatorAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@app.get("/assignments/", response_model=List[schemas.Assignment])
def read_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assignments = db.query(models.OperatorAssignment).offset(skip).limit(limit).all()
    return assignments


def distribute_lead(source_id: int, db: Session):
    assignments = db.query(models.OperatorAssignment).filter(
        models.OperatorAssignment.source_id == source_id
    ).all()

    if not assignments:
        return None

    available_operators = []
    weights = []

    for assignment in assignments:
        operator = assignment.operator
        if operator.is_active and operator.current_load < operator.max_load:
            available_operators.append(operator)
            weights.append(assignment.weight)

    if not available_operators:
        return None

    chosen_operator = random.choices(available_operators, weights=weights, k=1)[0]
    return chosen_operator


@app.post("/contacts/", response_model=schemas.ContactResponse)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(
        models.Lead.external_id == contact.lead_external_id
    ).first()

    if not lead:
        lead = models.Lead(external_id=contact.lead_external_id)
        db.add(lead)
        db.commit()
        db.refresh(lead)

    operator = distribute_lead(contact.source_id, db)
    operator_id = operator.id if operator else None

    if operator:
        operator.current_load += 1
        db.commit()

    db_contact = models.Contact(
        lead_id=lead.id,
        source_id=contact.source_id,
        operator_id=operator_id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return schemas.ContactResponse(
        id=db_contact.id,
        lead_id=db_contact.lead_id,
        source_id=db_contact.source_id,
        operator_id=db_contact.operator_id,
        created_at=db_contact.created_at,
        lead_external_id=lead.external_id
    )


@app.get("/leads/", response_model=List[schemas.Lead])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = db.query(models.Lead).offset(skip).limit(limit).all()
    return leads


@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).offset(skip).limit(limit).all()
    result = []
    for contact in contacts:
        result.append(schemas.ContactResponse(
            id=contact.id,
            lead_id=contact.lead_id,
            source_id=contact.source_id,
            operator_id=contact.operator_id,
            created_at=contact.created_at,
            lead_external_id=contact.lead.external_id
        ))
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
