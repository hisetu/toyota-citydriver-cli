from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from .config import BRAND, CAR_API_BASE, REPAIR_ITEM_BASE, Session
from .crypto import encrypt_payment_payload


def _unwrap_json_string(raw: str) -> Any:
    text = raw.strip()
    if text.startswith('"') and text.endswith('"'):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            pass
    if isinstance(text, str) and text.startswith('"{"'):
        text = text.replace('"{', "{", 1).replace('}"', "}", 1).replace("\\", "")
    return json.loads(text)


@dataclass
class MaintenanceRecord:
    date: str
    time: str
    total: str
    work_no: str
    customer_request: str
    factory_code: str
    dealer_code: str

    @classmethod
    def from_work_list(cls, item: dict[str, Any]) -> "MaintenanceRecord":
        return cls(
            date=item.get("RTPTDT", ""),
            time=item.get("RTPTML", ""),
            total=item.get("TOTAMT", ""),
            work_no=item.get("WORKNO", ""),
            customer_request=item.get("BRKDS", ""),
            factory_code=item.get("BRNHCD", ""),
            dealer_code=item.get("DLRCD", ""),
        )


def fetch_maintenance_records(
    session: Session,
    *,
    cust_id: str,
    license_plate: str,
    timeout: float = 60.0,
) -> list[MaintenanceRecord]:
    url = f"{CAR_API_BASE}CRAPP030_Q01"
    body = {"CUSTID": cust_id, "LICSNO": license_plate}
    headers = {
        "Content-Type": "application/json",
        "securityToken": session.security_token,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=body, headers=headers)
        resp.raise_for_status()
        data = _unwrap_json_string(resp.text)

    result_data = data.get("ResultData") or {}
    work_list = result_data.get("WORKLIST") or []
    return [MaintenanceRecord.from_work_list(w) for w in work_list]


def build_repair_detail_url(session: Session, record: MaintenanceRecord) -> str:
    payload = {
        "securityToken": session.security_token,
        "brand": BRAND,
        "dlrCd": record.dealer_code,
        "brnhCd": record.factory_code,
        "workNo": record.work_no,
    }
    para = encrypt_payment_payload(payload)
    return f"{REPAIR_ITEM_BASE}repairitem?para={quote(para, safe='')}"


_PDF_URL_RE = re.compile(r"""https?://[^\s"'<>]+\.pdf""", re.IGNORECASE)


def download_maintenance_pdf(
    session: Session,
    record: MaintenanceRecord,
    dest_path: str,
    *,
    timeout: float = 120.0,
) -> str:
    detail_url = build_repair_detail_url(session, record)
    headers = {"User-Agent": "ToyotaCityDriverCLI/0.1"}
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(detail_url, headers=headers)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "").lower()

        if "pdf" in content_type or resp.content.startswith(b"%PDF"):
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            return dest_path

        html = resp.text
        matches = _PDF_URL_RE.findall(html)
        if not matches:
            raise RuntimeError(
                "repairitem 回傳 HTML 但未找到 PDF 連結；"
                f"請用瀏覽器開啟 URL 確認：{detail_url}"
            )
        pdf_url = matches[0]
        pdf_resp = client.get(pdf_url, headers=headers)
        pdf_resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(pdf_resp.content)
        return dest_path
