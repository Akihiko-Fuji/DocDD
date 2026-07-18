#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################################
# Name    : streamlit_app.py
# Author  : Akihiko Fujita
# Update  : 2026-05-20
############################################################################

"""results_record_db 可視化・投入 UI の Streamlit アプリ本体。

主な責務:
- 取り込みファイルのアップロードと ingest 実行フローを提供
- 工程別の実績データを集計し、表・グラフで可視化
- DB クエリ結果を画面操作に合わせて取得・表示する

"""
from __future__ import annotations

import hashlib
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator, List, Sequence

import altair as alt
import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db import get_session
from ingest import apply_ingest_plan, load_order_product_master, prepare_ingest_file

PROCESS_FLOW: List[str] = ["内装組立", "外装組立", "出荷検査"]
STAGNATION_PAIRS = [("内装組立", "外装組立"), ("外装組立", "出荷検査")]
WORK_LOG_COLUMNS = [
    "order_no",
    "product_name",
    "process_name",
    "worker_name",
    "start_ts",
    "end_ts",
    "elapsed_sec",
    "work_sec",
    "result_cd",
]
REQUIRED_COLUMNS = set(WORK_LOG_COLUMNS)
INGEST_STATE_KEYS = [
    "ingest_plan",
    "ingest_uploaded_bytes",
    "ingest_plan_name",
    "ingest_batch_id",
    "ingest_source_fingerprint",
    "ingest_apply_in_progress",
]
SAMPLE_FILE_RENAME_MAP = {
    "internal_assembly_log.csv": "INTASM_YamadaTaro_202601.csv",
    "internal_assembly_log_invalid.csv": "INTASM_YamadaTaro_202602.csv",
    "external_assembly_log.csv": "EXTASM_SatoKen_202601.csv",
    "external_assembly_log_invalid.csv": "EXTASM_SatoKen_202602.csv",
    "shipping_inspection_log.csv": "SHIPCHK_202601.csv",
    "shipping_inspection_log_invalid.csv": "SHIPCHK_202601_invalid.csv",
}


def _is_streamlit_runtime() -> bool:
    """Streamlit 実行コンテキスト上で起動しているかを返す。"""
    return get_script_run_ctx() is not None


def _safe_message(prefix: str, exc: Exception) -> str:
    """例外情報をユーザー向け表示文字列に整形する。"""
    return f"{prefix}: {type(exc).__name__}: {exc}"


def _uploaded_fingerprint(uploaded) -> tuple[str, str] | None:
    """アップロードファイルの同一性判定用フィンガープリントを返す。"""
    if uploaded is None:
        return None
    content = uploaded.getvalue()
    return uploaded.name, hashlib.sha256(content).hexdigest()


def _clear_ingest_state() -> None:
    """取込関連のセッション状態を初期化する。"""
    for key in INGEST_STATE_KEYS:
        st.session_state.pop(key, None)


def _normalize_upload_name(file_name: str) -> str:
    """教材の旧サンプル名を現行命名へ読み替え、ファイル名部分を返す。"""
    original_name = Path(file_name).name
    mapped_name = SAMPLE_FILE_RENAME_MAP.get(original_name.lower(), original_name)
    return Path(mapped_name).name or "upload.csv"


@contextmanager
def _temporary_upload(file_name: str, content: bytes) -> Iterator[Path]:
    """共通取込処理へ渡す内容を一時ファイルとして提供する。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / _normalize_upload_name(file_name)
        path.write_bytes(content)
        yield path


def _load_order_product_master() -> dict[str, str]:
    """サンプルの受注-製品マスタを読み込む。"""
    path = (
        Path(__file__).resolve().parents[1] / "sample_data" / "order_product_master.csv"
    )
    if not path.exists():
        return {}
    return load_order_product_master(str(path))


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    """DataFrame を UTF-8(BOM付き) CSV バイト列へ変換する。"""
    return df.to_csv(index=False).encode("utf-8-sig")


def _empty_work_log_df() -> pd.DataFrame:
    """work_log 相当の空 DataFrame を返す。"""
    return pd.DataFrame(columns=[*WORK_LOG_COLUMNS, "work_date", "hour_bucket"])


def _filter_work_logs(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    selected_process: Sequence[str],
    selected_workers: Sequence[str],
) -> pd.DataFrame:
    """KPI1/KPI3共通の期間・工程・作業者フィルタを適用する。"""
    if df.empty or not selected_process or not selected_workers:
        return df.iloc[0:0].copy()
    return df[
        (df["work_date"] >= start_date)
        & (df["work_date"] <= end_date)
        & (df["process_name"].isin(selected_process))
        & (df["worker_name"].isin(selected_workers))
    ].copy()


def build_kpi1(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    selected_process: list[str],
    selected_workers: list[str],
) -> pd.DataFrame:
    """KPI1（工程別・時間帯別作業件数）を作成する。"""
    filtered = _filter_work_logs(
        df, start_date, end_date, selected_process, selected_workers
    )
    if filtered.empty:
        return pd.DataFrame(
            columns=["hour_slot", "hour_order", "process_name", "work_count"]
        )

    filtered["hour_order"] = filtered["end_ts"].dt.hour
    filtered = filtered[(filtered["hour_order"] >= 8) & (filtered["hour_order"] <= 17)]

    hour_orders = list(range(8, 18))
    slot_grid = pd.MultiIndex.from_product(
        [hour_orders, selected_process], names=["hour_order", "process_name"]
    ).to_frame(index=False)
    slot_grid["hour_slot"] = slot_grid["hour_order"].map(lambda h: f"{h:02d}:00")

    if filtered.empty:
        kpi1 = slot_grid.copy()
        kpi1["work_count"] = 0
    else:
        filtered["hour_slot"] = filtered["hour_order"].map(lambda h: f"{h:02d}:00")
        grouped = (
            filtered.groupby(["hour_order", "process_name"], as_index=False)
            .size()
            .rename(columns={"size": "work_count"})
        )
        kpi1 = slot_grid.merge(grouped, on=["hour_order", "process_name"], how="left")
        kpi1["work_count"] = kpi1["work_count"].fillna(0).astype(int)

    kpi1["process_name"] = pd.Categorical(
        kpi1["process_name"], categories=PROCESS_FLOW, ordered=True
    )
    return kpi1.sort_values(["hour_order", "process_name"]).reset_index(drop=True)


def build_kpi2(
    df: pd.DataFrame, start_date: date, end_date: date
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """KPI2（工程間滞留）推移と明細を作成する。"""
    if df.empty:
        empty = pd.DataFrame(columns=["pair", "timestamp", "stagnation_count"])
        return empty, pd.DataFrame(
            columns=["order_no", "pair", "from_end", "to_start", "is_invalid_sequence"]
        )

    trend_rows = []
    detail_rows = []
    period_start_ts = pd.Timestamp(start_date)
    period_end_ts = pd.Timestamp(f"{end_date.isoformat()} 23:45:00")
    scoped_from_df = df[df["end_ts"] <= period_end_ts].copy()
    all_buckets = pd.date_range(start=period_start_ts, end=period_end_ts, freq="15min")
    buckets = [ts for ts in all_buckets if 8 <= ts.hour < 17]

    for frm, to in STAGNATION_PAIRS:
        from_df = scoped_from_df[scoped_from_df["process_name"] == frm][
            ["order_no", "end_ts"]
        ].rename(columns={"end_ts": "from_end"})
        if from_df.empty:
            continue
        to_df = df[df["process_name"] == to][["order_no", "start_ts"]].rename(
            columns={"start_ts": "to_start"}
        )
        tmp = from_df.merge(to_df, on="order_no", how="left")
        tmp["is_invalid_sequence"] = tmp["to_start"].notna() & (
            tmp["to_start"] < tmp["from_end"]
        )
        tmp["pair"] = f"{frm} → {to}"

        tmp = tmp[
            (tmp["from_end"] <= period_end_ts)
            & ((tmp["to_start"].isna()) | (tmp["to_start"] >= period_start_ts))
        ].copy()
        if tmp.empty:
            continue
        detail_rows.append(
            tmp[["order_no", "pair", "from_end", "to_start", "is_invalid_sequence"]]
        )

        valid_tmp = tmp[~tmp["is_invalid_sequence"]].copy()
        for ts in buckets:
            count = (
                (valid_tmp["from_end"] <= ts)
                & ((valid_tmp["to_start"].isna()) | (valid_tmp["to_start"] > ts))
            ).sum()
            trend_rows.append(
                {
                    "pair": f"{frm} → {to}",
                    "timestamp": ts,
                    "stagnation_count": int(count),
                }
            )

    trend = (
        pd.DataFrame(trend_rows)
        if trend_rows
        else pd.DataFrame(columns=["pair", "timestamp", "stagnation_count"])
    )
    detail = (
        pd.concat(detail_rows, ignore_index=True)
        if detail_rows
        else pd.DataFrame(
            columns=["order_no", "pair", "from_end", "to_start", "is_invalid_sequence"]
        )
    )
    return trend, detail


def build_kpi3(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    selected_process: list[str],
    selected_workers: list[str],
) -> pd.DataFrame:
    """KPI3（作業者別・日別実績）を作成する。"""
    filtered = _filter_work_logs(
        df, start_date, end_date, selected_process, selected_workers
    )
    if filtered.empty:
        return pd.DataFrame(
            columns=["work_date", "process_name", "worker_name", "work_count"]
        )
    kpi3 = (
        filtered.groupby(["work_date", "process_name", "worker_name"], as_index=False)
        .size()
        .rename(columns={"size": "work_count"})
    )
    kpi3["process_name"] = pd.Categorical(
        kpi3["process_name"], categories=PROCESS_FLOW, ordered=True
    )
    return kpi3.sort_values(["work_date", "process_name", "worker_name"])


def _load_work_log_df() -> pd.DataFrame:
    """DB の work_log を画面表示用 DataFrame として読み込む。"""
    try:
        with get_session() as session:
            df = pd.read_sql(
                text(f"SELECT {', '.join(WORK_LOG_COLUMNS)} FROM work_log"),
                session.get_bind(),
            )
    except (SQLAlchemyError, ValueError) as exc:
        st.error(_safe_message("work_log SQL 実行失敗", exc))
        return _empty_work_log_df()
    if not REQUIRED_COLUMNS.issubset(df.columns):
        st.error(
            f"work_log の必須列が不足しています: {sorted(REQUIRED_COLUMNS - set(df.columns))}"
        )
        return _empty_work_log_df()
    df["start_ts"] = pd.to_datetime(df["start_ts"], errors="coerce")
    df["end_ts"] = pd.to_datetime(df["end_ts"], errors="coerce")
    df = df.dropna(subset=["end_ts", "worker_name", "process_name"])
    df["work_date"] = df["end_ts"].dt.date
    df["hour_bucket"] = df["end_ts"].dt.floor("h")
    return df[df["process_name"].isin(PROCESS_FLOW)].copy()


def _run_import_tab() -> None:
    """Import タブのUIと取込処理を実行する。"""
    st.subheader("Import")
    uploaded = st.file_uploader("取込ファイル", type=["csv", "xlsx", "xlsm"])
    current_fp = _uploaded_fingerprint(uploaded)
    if st.session_state.get("ingest_source_fingerprint") != current_fp:
        _clear_ingest_state()

    if uploaded and st.button("検証・プレビュー", type="primary"):
        try:
            uploaded_bytes = uploaded.getvalue()
            upload_name = _normalize_upload_name(uploaded.name)
            with _temporary_upload(upload_name, uploaded_bytes) as upload_path:
                with get_session() as session:
                    plan = prepare_ingest_file(
                        session,
                        str(upload_path),
                        order_product_map=_load_order_product_master(),
                    )
            st.session_state["ingest_uploaded_bytes"] = uploaded_bytes
            st.session_state["ingest_plan_name"] = upload_name
            st.session_state["ingest_plan"] = plan
            st.session_state["ingest_batch_id"] = plan.ingest_batch_id
            st.session_state["ingest_source_fingerprint"] = current_fp
            st.success("検証が完了しました")
        except (SQLAlchemyError, ValueError, OSError, ImportError) as exc:
            _clear_ingest_state()
            st.error(_safe_message("取込ファイルの検証に失敗しました", exc))
    plan = st.session_state.get("ingest_plan")
    if plan:
        st.write(
            f"登録候補: {len(plan.candidates)}件 / reject候補: {len(plan.rejects)}件"
        )
        st.dataframe(pd.DataFrame([c.__dict__ for c in plan.candidates]))
        st.dataframe(pd.DataFrame([r.__dict__ for r in plan.rejects]))
        if st.button(
            "DBへ登録", disabled=bool(st.session_state.get("ingest_apply_in_progress"))
        ):
            uploaded_bytes = st.session_state.get("ingest_uploaded_bytes")
            safe_name = st.session_state.get("ingest_plan_name", "upload.csv")
            if uploaded_bytes is None:
                st.error(
                    "アップロード元ファイルが見つかりません。再度検証してください。"
                )
                return
            try:
                st.session_state["ingest_apply_in_progress"] = True
                with get_session() as session:
                    # prepare/apply を同一トランザクションで再実行して重複判定の一貫性を確保する。
                    with _temporary_upload(safe_name, uploaded_bytes) as upload_path:
                        fresh_plan = prepare_ingest_file(
                            session,
                            str(upload_path),
                            order_product_map=_load_order_product_master(),
                            ingest_batch_id=st.session_state.get("ingest_batch_id"),
                        )
                    result = apply_ingest_plan(session, fresh_plan)
                st.success(
                    f"登録完了 inserted={result.inserted}, rejected={result.rejected}"
                )
                _clear_ingest_state()
                st.rerun()
            except (SQLAlchemyError, ValueError, OSError, ImportError) as exc:
                st.error(_safe_message("DB登録に失敗しました", exc))
            finally:
                st.session_state.pop("ingest_apply_in_progress", None)


def _run_kpi1_tab(
    base_df: pd.DataFrame,
    start_date: date,
    end_date: date,
    selected_process: list[str],
    selected_workers: list[str],
) -> None:
    """KPI1 タブを描画する。"""
    st.subheader("KPI1 工程別時間別")
    kpi1 = build_kpi1(base_df, start_date, end_date, selected_process, selected_workers)
    if not kpi1.empty:
        chart = (
            alt.Chart(kpi1)
            .mark_bar()
            .encode(
                x=alt.X(
                    "hour_slot:N",
                    title="時刻（1時間単位）",
                    sort=alt.SortField(field="hour_order", order="ascending"),
                    axis=alt.Axis(labelAngle=-45),
                ),
                xOffset=alt.XOffset("process_name:N", sort=PROCESS_FLOW),
                y=alt.Y("work_count:Q", title="作業件数（件）"),
                color=alt.Color("process_name:N", title="工程", sort=PROCESS_FLOW),
                tooltip=["hour_slot:N", "process_name:N", "work_count:Q"],
            )
            .properties(height=460, title="工程別・時間帯別の作業件数")
        )
        st.altair_chart(chart, use_container_width=True)
    st.download_button(
        "KPI1 CSV ダウンロード",
        data=_to_csv_bytes(kpi1),
        file_name="kpi1_process_hourly.csv",
        mime="text/csv",
        key="download_kpi1_csv",
    )
    st.dataframe(kpi1, width="stretch", height=420)


def _run_kpi2_tab(base_df: pd.DataFrame, start_date: date, end_date: date) -> None:
    """KPI2 タブを描画する。"""
    st.subheader("KPI2 工程間滞留（15分足の仕掛り推移）")
    st.info(
        "工程間滞留は、前工程完了〜次工程開始までの未着手件数を15分足で可視化します（8:00〜17:00）。"
    )
    trend, detail = build_kpi2(base_df, start_date, end_date)
    if not trend.empty:
        chart = (
            alt.Chart(trend)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "timestamp:T",
                    title="時刻（15分足の時点）",
                    axis=alt.Axis(format="%m/%d %H:%M", labelAngle=-45),
                ),
                y=alt.Y("stagnation_count:Q", title="仕掛り件数（件）"),
                color=alt.Color("pair:N", title="工程間"),
                tooltip=["timestamp:T", "pair:N", "stagnation_count:Q"],
            )
            .properties(height=460, title="工程間仕掛り推移（8:00〜17:00）")
        )
        st.altair_chart(chart, use_container_width=True)
    st.download_button(
        "KPI2 推移CSV ダウンロード",
        data=_to_csv_bytes(trend),
        file_name="kpi2_stagnation_trend.csv",
        mime="text/csv",
        key="download_kpi2_trend_csv",
    )
    st.download_button(
        "KPI2 明細CSV ダウンロード",
        data=_to_csv_bytes(detail),
        file_name="kpi2_stagnation_detail.csv",
        mime="text/csv",
        key="download_kpi2_detail_csv",
    )
    st.dataframe(trend, width="stretch", height=320)
    st.dataframe(detail, width="stretch", height=320)


def _run_kpi3_tab(
    base_df: pd.DataFrame,
    start_date: date,
    end_date: date,
    selected_process: list[str],
    selected_workers: list[str],
) -> None:
    """KPI3 タブを描画する。"""
    st.subheader("KPI3 作業者別日別実績")
    kpi3 = build_kpi3(base_df, start_date, end_date, selected_process, selected_workers)
    if not kpi3.empty:
        process_options = [
            p
            for p in PROCESS_FLOW
            if p in kpi3["process_name"].astype(str).unique().tolist()
        ]
        selected_kpi3_process = st.selectbox(
            "工程を選択", options=process_options, key="kpi3_process"
        )
        view_df = kpi3[kpi3["process_name"].astype(str) == selected_kpi3_process]
        chart = (
            alt.Chart(view_df)
            .mark_bar()
            .encode(
                x=alt.X("worker_name:N", title="作業者"),
                y=alt.Y("work_count:Q", title="作業件数（件）"),
                color=alt.Color("work_date:T", title="日付", timeUnit="yearmonthdate"),
                tooltip=[
                    "work_date:T",
                    "process_name:N",
                    "worker_name:N",
                    "work_count:Q",
                ],
            )
            .properties(height=460, title=f"{selected_kpi3_process} 作業者別日別実績")
        )
        st.altair_chart(chart, use_container_width=True)
    st.download_button(
        "KPI3 CSV ダウンロード",
        data=_to_csv_bytes(kpi3),
        file_name="kpi3_worker_daily.csv",
        mime="text/csv",
        key="download_kpi3_csv",
    )
    st.dataframe(kpi3, width="stretch", height=420)


def _resolve_date_range(
    selected_range: object, default_start: date, default_end: date
) -> tuple[date, date]:
    """Streamlitの日付入力値を必ず開始日・終了日の組へ揃える。"""
    if isinstance(selected_range, tuple):
        if len(selected_range) == 2:
            return selected_range[0], selected_range[1]
        if len(selected_range) == 1:
            return selected_range[0], selected_range[0]
    if isinstance(selected_range, date):
        return selected_range, selected_range
    return default_start, default_end


def main() -> None:
    """ダッシュボード画面全体を初期化して描画する。"""
    if not _is_streamlit_runtime():
        print("This app must be launched with: streamlit run streamlit_app.py")
        return
    st.set_page_config(page_title="KPI ダッシュボード", layout="wide")
    st.title("実績 KPI ダッシュボード")
    base_df = _load_work_log_df()
    if base_df.empty:
        st.warning("表示対象データがありません")
    min_date = min(base_df["work_date"]) if not base_df.empty else date(2026, 1, 1)
    max_date = max(base_df["work_date"]) if not base_df.empty else date(2026, 1, 31)
    date_range = st.date_input(
        "期間", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    start_date, end_date = _resolve_date_range(date_range, min_date, max_date)
    selected_process = st.multiselect(
        "工程", options=PROCESS_FLOW, default=PROCESS_FLOW
    )
    worker_options = (
        sorted(base_df["worker_name"].dropna().astype(str).unique().tolist())
        if not base_df.empty
        else []
    )
    selected_workers = st.multiselect(
        "作業者", options=worker_options, default=worker_options
    )
    tabs = st.tabs(
        ["Import", "KPI1 工程別時間別", "KPI2 工程間滞留", "KPI3 作業者別日別"]
    )
    with tabs[0]:
        _run_import_tab()
    with tabs[1]:
        _run_kpi1_tab(base_df, start_date, end_date, selected_process, selected_workers)
    with tabs[2]:
        _run_kpi2_tab(base_df, start_date, end_date)
    with tabs[3]:
        _run_kpi3_tab(base_df, start_date, end_date, selected_process, selected_workers)


if __name__ == "__main__":
    main()
