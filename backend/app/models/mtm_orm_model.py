from sqlalchemy import Column, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MTMRecordORM(Base):
    __tablename__ = 'newDataset'
    __table_args__ = {'schema': 'MTM_ANALYTICS', 'quote': False}

    RECORD_TYPE = Column(String)
    TRANSACTION_ID = Column(String, primary_key=True, unique=True, index=True)
    DATE = Column(String)
    PHARMACY_NCPDP_ID = Column(String)
    PHARMACIST_NPI = Column(String)
    PATIENT_ID = Column(String)
    FIRST_NAME = Column(String)
    LAST_NAME = Column(String)
    DOB = Column(String)
    GENDER = Column(String)
    PAYER_ID = Column(String)
    PLAN_NAME = Column(String)
    INTERVENTION_TYPE = Column(String)
    MTM_SERVICE_CODE = Column(String)
    START_DATE = Column(String)
    END_DATE = Column(String)
    OUTCOME = Column(String)
    RECOMMENDATIONS = Column(String)
    PRESCRIBER_CONTACTED = Column(String)
    PRESCRIBER_NPI = Column(String)
    PRESCRIBER_RESPONSE = Column(String)
    FOLLOW_UP_DATE = Column(String)
    NOTES = Column(String)
