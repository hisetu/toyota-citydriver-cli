from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .api import MaintenanceRecord, build_repair_detail_url, download_maintenance_pdf, fetch_maintenance_records
from .config import Session

app = typer.Typer(
    name="tcd",
    help="Toyota City Driver 保養紀錄 / PDF CLI（逆向自官方 App API）",
    no_args_is_help=True,
)


def _print_records(records: list[MaintenanceRecord]) -> None:
    if not records:
        typer.echo("（無保養紀錄）")
        return
    for i, r in enumerate(records, start=1):
        typer.echo(
            f"{i:>3}. {r.date} {r.time}  工單={r.work_no}  "
            f"店={r.dealer_code}/{r.factory_code}  金額={r.total}\n"
            f"      {r.customer_request}"
        )


@app.command("list")
def list_records(
    plate: str = typer.Option(..., "--plate", "-p", help="車牌（LICSNO）"),
    cust_id: str = typer.Option(..., "--cust-id", "-c", help="客戶編號（CUSTID）"),
) -> None:
    """列出保養紀錄（CRAPP030_Q01 / GetCarHistory）。"""
    session = Session.from_env()
    records = fetch_maintenance_records(session, cust_id=cust_id, license_plate=plate)
    _print_records(records)


@app.command("url")
def show_url(
    work_no: str = typer.Option(..., "--work-no", help="工單號 WORKNO"),
    dealer: str = typer.Option(..., "--dealer", help="經銷商 DLRCD"),
    factory: str = typer.Option(..., "--factory", help="服務廠 BRNHCD"),
) -> None:
    """輸出 App 使用的 repairitem Web URL（含加密 para）。"""
    session = Session.from_env()
    record = MaintenanceRecord(
        date="",
        time="",
        total="",
        work_no=work_no,
        customer_request="",
        factory_code=factory,
        dealer_code=dealer,
    )
    typer.echo(build_repair_detail_url(session, record))


@app.command("download")
def download_one(
    work_no: str = typer.Option(..., "--work-no", help="工單號"),
    dealer: str = typer.Option(..., "--dealer", help="DLRCD"),
    factory: str = typer.Option(..., "--factory", help="BRNHCD"),
    output: Path = typer.Option(..., "--output", "-o", help="輸出 PDF 路徑"),
) -> None:
    """下載單筆保養明細 PDF。"""
    session = Session.from_env()
    record = MaintenanceRecord(
        date="",
        time="",
        total="",
        work_no=work_no,
        customer_request="",
        factory_code=factory,
        dealer_code=dealer,
    )
    path = download_maintenance_pdf(session, record, str(output))
    typer.echo(f"已寫入 {path}")


@app.command("download-all")
def download_all(
    plate: str = typer.Option(..., "--plate", "-p"),
    cust_id: str = typer.Option(..., "--cust-id", "-c"),
    out_dir: Path = typer.Option(Path("maintenance-pdfs"), "--out-dir", "-d"),
    limit: Optional[int] = typer.Option(None, "--limit", help="最多下載幾筆（由新到舊）"),
) -> None:
    """列出並下載所有保養 PDF。"""
    session = Session.from_env()
    records = fetch_maintenance_records(session, cust_id=cust_id, license_plate=plate)
    if limit is not None:
        records = records[:limit]
    out_dir.mkdir(parents=True, exist_ok=True)
    _print_records(records)
    typer.echo("")
    for r in records:
        filename = f"{r.date}_{r.work_no}.pdf".replace("/", "-")
        dest = out_dir / filename
        try:
            download_maintenance_pdf(session, r, str(dest))
            typer.echo(f"OK  {dest.name}")
        except Exception as exc:  # noqa: BLE001 — CLI 逐筆回報
            typer.echo(f"FAIL {r.work_no}: {exc}", err=True)


if __name__ == "__main__":
    app()
