# toyota-citydriver-cli

從 Toyota **My Toyota / City Driver** 官方 App（`com.hotai.toyota.citydriver.official`）逆向擷取的保養 API，提供 CLI 列出保養紀錄並下載明細 PDF。

## 功能

- 查詢保養工單列表（`CRAPP030_Q01`）
- 產生與 App 相同的 `repairitem` 明細 URL
- 下載單筆或批次保養明細 PDF

## 需求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)（建議）

## 安裝

```bash
git clone https://github.com/hisetu/toyota-citydriver-cli.git
cd toyota-citydriver-cli
uv sync
uv run tcd --help
```

## 認證

需要 App 登入後的 **securityToken**（header 名稱為 `securityToken`，不是 Bearer）：

```bash
export TCD_SECURITY_TOKEN='...'
```

取得方式（擇一）：

1. 以 mitmproxy 攔截 App「保養紀錄」請求，從 `CRAPP030_Q01` 的 header 複製 `securityToken`
2. 從裝置備份／已登入環境讀取 token（依平台而定）

另需 **CUSTID**（客戶編號）與 **車牌**（`LICSNO`），可在 App 車輛資料或上述 API 請求 body 中看到。

## 用法

```bash
# 列出保養紀錄
uv run tcd list --plate ABC-1234 --cust-id YOUR_CUST_ID

# 產生單筆明細 URL
uv run tcd url --work-no WORKNO --dealer DLRCD --factory BRNHCD

# 下載單筆 PDF
uv run tcd download --work-no WORKNO --dealer DLRCD --factory BRNHCD -o record.pdf

# 批次下載
uv run tcd download-all --plate ABC-1234 --cust-id YOUR_CUST_ID -d ./pdfs
```

## API 說明

逆向摘要見 [docs/API.md](docs/API.md)。

## 免責

僅供存取**本人**車輛資料。請遵守和泰／Toyota 服務條款，勿分享 token 或大量自動化請求。
