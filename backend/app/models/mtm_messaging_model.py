from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date

class PatientRecord(BaseModel):
    # Required NCPDP Messaging Fields with messaging format keys
    AM20: str  # TRANSACTION_ID
    AM25: str  # PATIENT_ID
    AM29: str  # FIRST_NAME + LAST_NAME
    CBS: str   # LAST_NAME
    PRV: str   # PHARMACIST_NPI
    RX: str    # MTM_SERVICE_CODE
    DT: str    # DATE (MMDDYYYY)
    DOS: str   # START_DATE (MMDDYYYY)
    PR: str    # PRESCRIBER_NPI

    # Optional Fields
    F01: Optional[int] = None
    QTY: Optional[int] = None
    DAY: Optional[int] = None
    NDC: Optional[str] = None
    DAW: Optional[int] = None
    DUR: Optional[str] = None
    DX: Optional[str] = None
    UC: Optional[str] = None
    PAY: Optional[str] = None
    PAT: Optional[str] = None

    @field_validator("DT", "DOS", mode="before")
    @classmethod
    def format_date(cls, v):
        if isinstance(v, (datetime, date)):
            return v.strftime("%m%d%Y")
        return v

    @classmethod
    def from_orm_model(cls, record):
        data = {
            "AM20": record.TRANSACTION_ID,
            "AM25": record.PATIENT_ID,
            "AM29": f"{record.FIRST_NAME}{record.LAST_NAME}",
            "CBS": record.LAST_NAME,
            "PRV": record.PHARMACIST_NPI,
            "RX": record.MTM_SERVICE_CODE,
            "DT": record.DATE,
            "DOS": record.START_DATE,
            "PR": record.PRESCRIBER_NPI,
        }

        # Optional fields
        optional_fields = {
            "F01": getattr(record, 'FILL_NUMBER', None),
            "QTY": getattr(record, 'QUANTITY_DISPENSED', None),
            "DAY": getattr(record, 'DAYS_SUPPLY', None),
            "NDC": getattr(record, 'NDC', None),
            "DAW": getattr(record, 'DAW', None),
            "DUR": getattr(record, 'DUR', None),
            "DX": getattr(record, 'DIAGNOSIS_CODE', None),
            "UC": getattr(record, 'USUAL_CUSTOMARY_CHARGE', None),
            "PAY": getattr(record, 'PAYMENT_AMOUNT', None),
            "PAT": record.RECOMMENDATIONS or record.NOTES
        }

        for key, value in optional_fields.items():
            if value not in [None, "", 0, 0.0]:
                data[key] = value

        return cls(**data)