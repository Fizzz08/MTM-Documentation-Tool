from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from models.mtm_model import MTMRecord
from services import mtm_service
from core.database import SessionLocal
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/mtm", tags=["MTM"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_mtm(record: MTMRecord, db: Session = Depends(get_db)):
    return mtm_service.create_record(db, record)

@router.get("/{patient_id}")
def read_mtm(patient_id: str, db: Session = Depends(get_db)):
    record = mtm_service.get_record_by_id(db, patient_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.get("/")
def get_all_mtm(db: Session = Depends(get_db)):
    return mtm_service.get_all_records(db)


# XML Endpoints
@router.get("/{patient_id}/xml")
def get_xml_by_id(patient_id: str, db: Session = Depends(get_db)):
    xml_data = mtm_service.get_record_as_ncpdp_xml_by_id(db, patient_id)
    return Response(content=xml_data, media_type="application/xml")

@router.get("/xml/all")
def get_all_records_xml(db: Session = Depends(get_db)):
    xml_data = mtm_service.get_all_records_as_ncpdp_xml(db)
    return Response(content=xml_data, media_type="application/xml")
