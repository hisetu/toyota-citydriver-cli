from __future__ import annotations

import os
from dataclasses import dataclass

# From com.hotai.toyota.citydriver.official.BuildConfig (prd release)
CAR_API_BASE = "https://htapp-api.hotaicloud.com/api/1.0/CRAPP/T/"
REPAIR_ITEM_BASE = "https://htapp-api.hotaicloud.com/"
TPI_MIDDLE_BASE = "https://htapp-api.hotaicloud.com/api/1.0/"

PAY_KEY_B64 = "quUhjkd9nAIYNAsUeq56ZGZyOyfFCmi4jWEGwuGuE+k="
PAY_IV_B64 = "n/MRfztUlqJC8goWvxycwA=="

BRAND = "T"
APP_ID = "TAPP"


@dataclass(frozen=True)
class Session:
    security_token: str

    @classmethod
    def from_env(cls) -> "Session":
        token = os.environ.get("TCD_SECURITY_TOKEN", "").strip()
        if not token:
            msg = (
                "缺少 TCD_SECURITY_TOKEN。"
                "請從已登入的 My Toyota App 取得 securityToken（例如 mitmproxy 攔截 "
                "CRAPP API 請求 header `securityToken`）。"
            )
            raise SystemExit(msg)
        return cls(security_token=token)
