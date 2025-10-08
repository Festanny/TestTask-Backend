import requests

from _project_.celery import app


@app.task()
def create_lead(create_lead_url, fields_mapping, title, name, phone, email=None, **custom_fields):
    params = {
        "FIELDS[TITLE]": title,
        "FIELDS[NAME]": name,
        "FIELDS[PHONE][0][VALUE]": phone,
        "FIELDS[PHONE][0][VALUE_TYPE]": "WORK",
    }
    if email:
        params["FIELDS[EMAIL][0][VALUE]"] = email
        params["FIELDS[EMAIL][0][VALUE_TYPE]"] = "WORK"

    for field_k, field_v in custom_fields.items():
        bitrix_field_name = fields_mapping.get(field_k)
        params[f"FIELDS[{bitrix_field_name}]"] = field_v

    res = requests.get(create_lead_url, params, verify=False)
    res.raise_for_status()
