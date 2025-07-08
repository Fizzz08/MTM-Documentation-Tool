from models.mtm_messaging_model import PatientRecord

def convert_to_ncpdp_message(record: PatientRecord):
    lines = [
        f"AM20 {record.AM20}",
        f"AM25 {record.AM25}A",
        f"AM29 CA {record.AM29}",
        f"CBS {record.CBS}",
        f"PRV {record.PRV}",
        f"RX {record.RX}",
        f"DT {record.DT}",
        f"DOS {record.DOS}",
        f"PR {record.PR}",  
        f"PAT {record.PAT}"
    ]

    if getattr(record, "FILL_NUMBER", None) is not None:
        lines.append(f"F01 {record.FILL_NUMBER}")
    if getattr(record, "QUANTITY_DISPENSED", None) is not None:
        lines.append(f"QTY {record.QUANTITY_DISPENSED}")
    if getattr(record, "DAYS_SUPPLY", None) is not None:
        lines.append(f"DAY {record.DAYS_SUPPLY}")
    if getattr(record, "NDC", None):
        lines.append(f"NDC {record.NDC}")
    if getattr(record, "DAW", None) is not None:
        lines.append(f"DAW {record.DAW}")
    if getattr(record, "PRESCRIBER_NPI", None):
        lines.append(f"PR {record.PRESCRIBER_NPI}")
    if getattr(record, "DUR", None):
        lines.append(f"DUR {record.DUR}")
    if getattr(record, "DIAGNOSIS_CODE", None):
        lines.append(f"DX {record.DIAGNOSIS_CODE}")
    if getattr(record, "USUAL_CUSTOMARY_CHARGE", None):
        lines.append(f"UC {record.USUAL_CUSTOMARY_CHARGE}")
    if getattr(record, "PAYMENT_AMOUNT", None):
        lines.append(f"PAY {record.PAYMENT_AMOUNT}")
    if getattr(record, "NOTES", None) or getattr(record, "RECOMMENDATIONS", None):
        lines.append(f"PAT {record.NOTES or record.RECOMMENDATIONS}")

    return "\n".join(lines)
