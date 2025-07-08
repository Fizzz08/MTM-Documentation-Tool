from fastapi import APIRouter, Response, HTTPException
from typing import List
from models.mtm_messaging_model import PatientRecord
from services.mtm_messaging import convert_to_ncpdp_message
from fastapi.responses import StreamingResponse
from fastapi import Depends
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.mtm_orm_model import MTMRecordORM

router = APIRouter(prefix="/mtm", tags=["MTM"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/ncpdp/messaging/download/{patient_id}", response_class=Response)
def download_patient_message(patient_id: str):
    with SessionLocal() as db:
        record = db.query(MTMRecordORM).filter(MTMRecordORM.PATIENT_ID == patient_id).first()
        if record:
            patient = PatientRecord.from_orm_model(record)
            content = convert_to_ncpdp_message(patient)
            return Response(content=content, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename={patient_id}.txt"})
        raise HTTPException(status_code=404, detail="Patient not found")
    
# GET: All patient records for NCPDP messaging
@router.get("/ncpdp/messaging", response_model=List[PatientRecord])
def get_all_messaging_patients():
    with SessionLocal() as db:
        records = db.query(MTMRecordORM).all()
        return [PatientRecord.from_orm_model(r) for r in records]

# GET: Patient record by ID
@router.get("/ncpdp/messaging/{patient_id}", response_model=PatientRecord)
def get_messaging_patient_by_id(patient_id: str):
    with SessionLocal() as db:
        record = db.query(MTMRecordORM).filter(MTMRecordORM.PATIENT_ID == patient_id).first()
        if record:
            return PatientRecord.from_orm_model(record)
        raise HTTPException(status_code=404, detail="Patient not found")

@router.get("/ncpdp/messaging/{patient_id}/{key}", response_model=dict)
def get_value_by_messaging_key(patient_id: str, key: str):
    with SessionLocal() as db:
        record = db.query(MTMRecordORM).filter(MTMRecordORM.PATIENT_ID == patient_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Patient not found")

        patient = PatientRecord.from_orm_model(record)
        value = getattr(patient, key.upper(), None)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found or value is empty for this patient.")

        return {key.upper(): value}


@router.get("/messaging/all", response_class=Response)
def get_all_records_messaging(db: Session = Depends(get_db)):
    records = db.query(MTMRecordORM).all()
    messages = [convert_to_ncpdp_message(PatientRecord.from_orm_model(r)) for r in records]
    full_text = "\n\n".join(messages)
    return Response(
        content=full_text,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=all_patients.txt"}
    )