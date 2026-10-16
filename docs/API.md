# Toyota City Driver — 保養相關 API（逆向摘要）

來源 APK：`com.hotai.toyota.citydriver.official`（v6.5.17 / VERSION_CODE 253）

## 認證

| Header | 值 |
|--------|-----|
| `securityToken` | OAuth 登入後的 access token（App 存在 SharedPreferences） |

Car API **不**使用 `Authorization: Bearer`，header 名稱就是 `securityToken`（見 `DefaultCarApiService.AUTHORIZATION_HEADER_NAME`）。

## 1. 保養紀錄列表

| 項目 | 值 |
|------|-----|
| Base URL | `https://htapp-api.hotaicloud.com/api/1.0/CRAPP/T/` |
| Route | `CRAPP030_Q01`（`CarApi.GetCarHistory`） |
| Method | POST |
| Content-Type | `application/json` |

**Request body**

```json
{
  "CUSTID": "<客戶編號>",
  "LICSNO": "<車牌>"
}
```

**Response**：`GetCarHistoryResponse`，`ResultData.WORKLIST[]` 欄位：

| 欄位 | 說明 |
|------|------|
| `RTPTDT` | 日期 |
| `RTPTML` | 時間 |
| `TOTAMT` | 金額 |
| `WORKNO` | 工單號 |
| `BRKDS` | 客戶需求描述 |
| `BRNHCD` | 服務廠代碼 |
| `DLRCD` | 經銷商代碼 |

App 流程：`GetCarWarrantyRecordUseCase` → `SecretaryRepository.getCarWarrantyRecord` → `CarApiService.getCarHistory`。

## 2. 保養明細（Web / PDF）

App 在 `CarWarrantyRecordViewModel.getWarrantyRecordDetailsUrl` 組 URL：

```
https://htapp-api.hotaicloud.com/repairitem?para=<AES 加密 Base64>
```

**明文 JSON**（`WarrantyRecordDetail`）：

```json
{
  "securityToken": "<token>",
  "brand": "T",
  "dlrCd": "<DLRCD>",
  "brnhCd": "<BRNHCD>",
  "workNo": "<WORKNO>"
}
```

**加密**：`AesCrypt.encryptPayment` — AES/CBC/PKCS7Padding，Key/IV 為 BuildConfig 的 Base64：

- `PAY_KEY` = `quUhjkd9nAIYNAsUeq56ZGZyOyfFCmi4jWEGwuGuE+k=`
- `PAY_IV` = `n/MRfztUlqJC8goWvxycwA==`

WebView 開啟此 URL 顯示保養明細（通常可另存 PDF）。

## 3. 其他 Car API routes（完整列表）

| Route | 用途（類名） |
|-------|----------------|
| CRAPP010_Q01 | GetCarInformation |
| CRAPP010_Q02 | QueryLevel |
| CRAPP010_Q12 | GetCarData |
| CRAPP020_D01 | CancelReserve |
| CRAPP020_I01 | ReserveRegularMaintenance |
| CRAPP020_I02 | ReserveRegularMaintenanceForLexus |
| CRAPP020_I03 | ReserveRegularMaintenanceI03 |
| CRAPP020_U01 | EditReserveRegularMaintenance |
| CRAPP020_Q02 | GetFactoryFreeTimes |
| CRAPP020_Q02T | GetFactoryFreeTimesForT |
| CRAPP020_Q03 | GetExtendedMaintainMemo |
| CRAPP020_Q04 | GetRecommendedMaintenanceContent |
| CRAPP020_Q05 | GetReserveDetail |
| CRAPP020_Q06 | Q06 |
| CRAPP020_Q07 | GetReserveList |
| CRAPP020_Q08 | GetReserveDetailByWorkNo |
| CRAPP030_Q01 | **GetCarHistory** |
| CRAPP030_Q03 | CheckEngineNoIsVerified |
| CRAPP023_Q01 | GetBPFactoryFreeTimes |
| CRAPP023_Q02 | GetBPReserveDetail |
| CRAPP023_I01 | ReserveBPEval |
| CRAPP060_Q01 | WhetherToAskEDMWillingness |
| CRAPP060_I01 | UpdateAskEDMCanAsk |
| UploadFile1 | UploadBpPhotos |

## 4. TPI Middle（備用明細 URL）

`GetWarrantyRecordServiceDetailsWebUrlUseCase` 可呼叫：

- `GetRepairItems/{brand}`（POST，body: `brnhcd`, `dlrcd`, `workno`）

本 CLI 目前採用 App 實際開 WebView 的 **repairitem + para** 路徑。
