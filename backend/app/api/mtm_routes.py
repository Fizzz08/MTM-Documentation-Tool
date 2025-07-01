from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.models.mtm_model import MTMRecord
from app.services import mtm_service
from app.core.database import get_db

router = APIRouter(prefix="/mtm", tags=["MTM"])

# ✅ Create new record
@router.post("/")
def create_record(record: MTMRecord, db: Session = Depends(get_db)):
    return mtm_service.create_record(db, record)

# ✅ Get all records
@router.get("/")
def read_all_records(db: Session = Depends(get_db)):
    return mtm_service.get_all_records(db)


# ✅ Download all records as XML
@router.get("/xml/all")
def get_all_xml(db: Session = Depends(get_db)):
    try:
        xml = mtm_service.get_all_records_as_ncpdp_xml(db)
        if not xml:
            return Response(content="<Error>No XML returned</Error>", media_type="application/xml", status_code=404)
        return Response(content=xml, media_type="application/xml")
    except Exception as e:
        return Response(content=f"<Error>{str(e)}</Error>", media_type="application/xml", status_code=500)


# ✅ Get record by transaction ID
@router.get("/{transaction_id}")
def read_record(transaction_id: str, db: Session = Depends(get_db)):
    record = mtm_service.get_record_by_id(db, transaction_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

# ✅ Delete record by transaction ID
@router.delete("/{transaction_id}")
def delete_record(transaction_id: str, db: Session = Depends(get_db)):
    deleted = mtm_service.delete_record_by_id(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted successfully"}

# ✅ Download record as XML by transaction ID
@router.get("/xml/{transaction_id}")
def get_xml_by_id(transaction_id: str, db: Session = Depends(get_db)):
    xml = mtm_service.get_record_as_ncpdp_xml_by_id(db, transaction_id)
    if xml.startswith("<Error>"):
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(content=xml, media_type="application/xml")

