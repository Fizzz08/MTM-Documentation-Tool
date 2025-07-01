from sqlalchemy.orm import Session
from models.mtm_orm_model import MTMRecordORM as MTMRecord  # ORM model
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

def get_record_by_id(db: Session, transaction_id: str):
    return db.query(MTMRecord).filter(MTMRecord.TRANSACTION_ID == transaction_id).first()

def get_all_records(db: Session):
    return db.query(MTMRecord).all()

def create_record(db: Session, record):
    # 'record' here should be a Pydantic model or similar with .dict()
    orm_record = MTMRecord(**record.dict())
    db.add(orm_record)
    db.commit()
    db.refresh(orm_record)
    return orm_record

def delete_record_by_id(db: Session, transaction_id: str):
    record = db.query(MTMRecord).filter(MTMRecord.TRANSACTION_ID == transaction_id).first()
    if record:
        db.delete(record)
        db.commit()
    return record


def convert_record_to_dict(record):
    def date_to_str(d):
        if d is None:
            return ""
        if isinstance(d, str):
            return d.replace("-", "")
        return d.strftime("%Y%m%d")

    return {
        "MessageID": record.TRANSACTION_ID,
        "MessageDate": date_to_str(record.DATE),
        "Pharmacy": {
            "NCPDPID": record.PHARMACY_NCPDP_ID,
            "PharmacistNPI": record.PHARMACIST_NPI
        },
        "Patient": {
            "Name": {
                "Last": record.LAST_NAME,
                "First": record.FIRST_NAME
            },
            "Gender": record.GENDER,
            "DOB": date_to_str(record.DOB)
        },
        "Payer": {
            "PayerID": record.PAYER_ID,
            "PlanName": record.PLAN_NAME
        },
        "MTMService": {
            "ServiceCode": record.MTM_SERVICE_CODE,
            "InterventionType": record.INTERVENTION_TYPE,
            "StartDate": date_to_str(record.START_DATE),
            "EndDate": date_to_str(record.END_DATE),
            "Outcome": record.OUTCOME,
            "Recommendation": record.RECOMMENDATIONS
        },
        "Prescriber": {
            "Contacted": record.PRESCRIBER_CONTACTED,
            "NPI": record.PRESCRIBER_NPI,
            "Response": record.PRESCRIBER_RESPONSE
        },
        "FollowUpDate": date_to_str(record.FOLLOW_UP_DATE),
        "Notes": record.NOTES
    }

def get_all_records_as_ncpdp_xml(db: Session) -> str:
    records = db.query(MTMRecord).all()
    print(f"✅ Found {len(records)} records in DB")

    if not records:
        print("⚠️ No records found")
        return "<Error>No records in database</Error>"

    all_records_dicts = [convert_record_to_dict(rec) for rec in records]
    root_dict = {"Record": all_records_dicts}
    xml_bytes = dicttoxml(root_dict, custom_root="MTMRequest", attr_type=False)
    dom = parseString(xml_bytes)
    pretty_xml_as_str = dom.toprettyxml(indent="  ")
    return pretty_xml_as_str


def get_record_as_ncpdp_xml_by_id(db: Session, transaction_id: str) -> str:
    record = db.query(MTMRecord).filter(MTMRecord.TRANSACTION_ID == transaction_id).first()

    if not record:
        return "<Error>Record not found</Error>"

    record_dict = convert_record_to_dict(record)
    wrapped = {"Record": record_dict}

    xml_bytes = dicttoxml(wrapped, custom_root="MTMRequest", attr_type=False)
    pretty_xml = parseString(xml_bytes).toprettyxml(indent="  ")

    return pretty_xml