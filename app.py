"""BankHealth Analyzer — dashboard phân tích sức khỏe tài chính ngân hàng.

Chạy ứng dụng: streamlit run app.py
"""

import hashlib

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


NUMBER_INPUT_STEP = 1000.0
REQUIRED_COLUMNS = [
    "Bank", "LNST", "NetInterestIncome", "TotalAssets", "Equity", "CASA",
    "TotalDeposit", "Group1", "Group2", "Group3", "Group4", "Group5", "Provision",
]
MANUAL_DEFAULTS = {
    "Bank": "", "LNST": 1000.0, "NetInterestIncome": 5000.0,
    "TotalAssets": 200000.0, "Equity": 20000.0, "CASA": 30000.0,
    "TotalDeposit": 150000.0, "Group1": 120000.0, "Group2": 3000.0,
    "Group3": 1200.0, "Group4": 800.0, "Group5": 500.0, "Provision": 3000.0,
}

st.set_page_config(page_title="BankHealth Analyzer", page_icon="🏦", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
      [data-testid="InputInstructions"] {display: none;}
      .block-container {max-width: 1440px; padding: 1.5rem 2.25rem 3rem;}
      [data-testid="stAppViewContainer"] {background: #f7f9fc;}
      h1 {color: #123a63; letter-spacing: -.03em; margin-bottom: .1rem !important;}
      div[data-testid="stMetric"] {background:#fff; border:1px solid #e2e9f2; border-radius:14px; padding:1rem 1.15rem; box-shadow:0 3px 12px rgba(32,61,92,.05);}
      div[data-testid="stMetricLabel"] {color:#5d6b7e;}
      div[data-testid="stMetricValue"] {color:#123a63;}
      div[data-testid="stForm"] {border:1px solid #dce6f1; border-radius:16px; padding:1.2rem 1.4rem 1rem; background:linear-gradient(180deg,#fff 0%,#f5f9fd 100%); box-shadow:0 4px 16px rgba(32,61,92,.04);}
      .form-title {font-size:1.08rem; font-weight:750; color:#123a63; margin:0;}
      .form-note {color:#6b7a90; margin:.15rem 0 1rem; font-size:.9rem;}
      .input-group {height:100%; background:rgba(255,255,255,.78); border:1px solid #e6edf5; border-radius:12px; padding:.85rem .9rem .15rem; margin-bottom:.2rem;}
      .input-group-title {font-size:.94rem; font-weight:700; color:#244d76; margin:0 0 .45rem;}
      div[data-testid="stNumberInput"] label {font-size:.84rem; color:#506176;}
      div[data-testid="stNumberInput"] input {background:#fff; border-color:#d6e1ed;}
      div[data-testid="stFormSubmitButton"] {margin-top:.6rem;}
      .dashboard-title {color:#123a63; margin:0 0 .7rem; font-size:1.4rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def safe_divide(numerator, denominator):
    """Trả về 0 nếu mẫu số bằng 0."""
    return numerator / denominator if denominator else 0


def score_comment(value, good, average, messages):
    if value >= good:
        return f"✅ {messages[0]}"
    if value >= average:
        return f"🟡 {messages[1]}"
    return f"🔴 {messages[2]}"


def npl_status(npl):
    if npl > 3:
        return "Đỏ", "🔴", "Nguy cơ rủi ro tín dụng cao", "error"
    if npl >= 1.5:
        return "Vàng", "🟡", "Cần theo dõi chặt chẽ", "warning"
    return "Xanh", "🟢", "Chất lượng tín dụng đang được kiểm soát tốt", "success"


def calculate_metrics(bank_data):
    """Dùng lại nguyên công thức phân tích của ứng dụng cho một ngân hàng."""
    total_loan = bank_data["Group1"] + bank_data["Group2"] + bank_data["Group3"] + bank_data["Group4"] + bank_data["Group5"]
    bad_debt = bank_data["Group3"] + bank_data["Group4"] + bank_data["Group5"]
    roa = safe_divide(bank_data["LNST"], bank_data["TotalAssets"])
    roe = safe_divide(bank_data["LNST"], bank_data["Equity"])
    nim = safe_divide(bank_data["NetInterestIncome"], bank_data["TotalAssets"])
    casa_ratio = safe_divide(bank_data["CASA"], bank_data["TotalDeposit"]) * 100
    npl = safe_divide(bad_debt, total_loan) * 100
    overdue = safe_divide(bank_data["Group2"] + bad_debt, total_loan) * 100
    coverage = safe_divide(bank_data["Provision"], bad_debt) * 100
    em = safe_divide(bank_data["TotalAssets"], bank_data["Equity"])
    return {"total_loan": total_loan, "bad_debt": bad_debt, "roa": roa, "roe": roe, "nim": nim, "casa_ratio": casa_ratio, "npl": npl, "overdue": overdue, "coverage": coverage, "em": em}


def render_bank_analysis(bank_name, bank_data, instance_key=None):
    """Render đầy đủ dashboard hiện hữu cho một ngân hàng độc lập."""
    metrics = calculate_metrics(bank_data)
    chart_key = instance_key or bank_name
    st.markdown(f'<h2 class="dashboard-title">{bank_name}</h2>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("ROA", f"{metrics['roa'] * 100:.2f}%", score_comment(metrics["roa"], .02, .01, ("Hiệu quả tài sản tốt", "Mức trung bình", "Hiệu quả thấp")))
    kpi2.metric("ROE", f"{metrics['roe'] * 100:.2f}%", score_comment(metrics["roe"], .15, .10, ("Khả năng sinh lời cao", "Mức sinh lời khá", "Sinh lời thấp")))
    kpi3.metric("NIM", f"{metrics['nim'] * 100:.2f}%", score_comment(metrics["nim"], .03, .02, ("Biên lãi thuần tốt", "Mức trung bình", "Biên lãi thấp")))
    kpi4.metric("CASA", f"{metrics['casa_ratio']:.2f}%", score_comment(metrics["casa_ratio"], 30, 20, ("CASA rất tốt", "CASA khá", "CASA thấp")))

    st.divider()
    chart_col, dupont_col = st.columns(2, gap="large")
    with chart_col:
        st.subheader("Cơ cấu nhóm nợ")
        debt_df = pd.DataFrame({"Nhóm nợ": ["Nhóm 1", "Nhóm 2", "Nhóm 3", "Nhóm 4", "Nhóm 5"], "Dư nợ": [bank_data["Group1"], bank_data["Group2"], bank_data["Group3"], bank_data["Group4"], bank_data["Group5"]]})
        pie = px.pie(debt_df, names="Nhóm nợ", values="Dư nợ", hole=.52, color="Nhóm nợ", color_discrete_sequence=["#4c9f70", "#e9c46a", "#f4a261", "#e76f51", "#b23a48"])
        pie.update_traces(textposition="inside", textinfo="percent+label")
        pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="")
        # Key theo tên ngân hàng giúp nhiều tab có biểu đồ cùng cấu hình không trùng ID.
        st.plotly_chart(pie, use_container_width=True, key=f"loan_groups_{chart_key}")
    with dupont_col:
        st.subheader("Mô hình Dupont")
        tree = go.Figure()
        tree.add_trace(go.Scatter(x=[.5, .2, .8], y=[1, .35, .35], mode="markers+text", text=[f"<b>ROE</b><br>{metrics['roe'] * 100:.2f}%", f"<b>ROA</b><br>{metrics['roa'] * 100:.2f}%", f"<b>EM</b><br>{metrics['em']:.2f}x"], textposition="bottom center", marker=dict(size=[42, 36, 36], color=["#173f67", "#2a9d8f", "#e9c46a"]), hovertemplate="%{text}<extra></extra>"))
        for x_end in (.2, .8):
            tree.add_shape(type="line", x0=.5, y0=.92, x1=x_end, y1=.43, line=dict(color="#9aabbc", width=2))
        tree.add_annotation(x=.5, y=.67, text="ROE = ROA × Đòn bẩy tài chính", showarrow=False, font=dict(size=15, color="#425466"))
        tree.update_layout(height=410, margin=dict(l=10, r=10, t=10, b=25), showlegend=False, xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(visible=False, range=[0, 1.2]))
        st.plotly_chart(tree, use_container_width=True, key=f"dupont_tree_{chart_key}")

    st.divider()
    summary_col, alert_col = st.columns([1.35, 1], gap="large")
    status, icon, message, level = npl_status(metrics["npl"])
    with alert_col:
        st.subheader("Cảnh báo NPL")
        getattr(st, level)(f"{icon} **Mức {status} — NPL: {metrics['npl']:.2f}%**\n\n{message}.")
    with summary_col:
        st.subheader("Bảng tổng hợp chỉ số")
        summary = pd.DataFrame({"Chỉ số": ["Tổng dư nợ", "Nợ quá hạn", "Tỷ lệ NPL", "Bao phủ nợ xấu", "Đòn bẩy tài chính (EM)"], "Giá trị": [f"{metrics['total_loan']:,.2f}", f"{metrics['overdue']:.2f}%", f"{metrics['npl']:.2f}%", f"{metrics['coverage']:.2f}%", f"{metrics['em']:.2f}x"]})
        st.dataframe(summary, use_container_width=True, hide_index=True, column_config={"Chỉ số": st.column_config.TextColumn(width="large")}, key=f"summary_table_{chart_key}")


def render_comparison_overview(selected_banks, bank_lookup):
    """Hiển thị bảng benchmark và biểu đồ NPL/NIM cho các ngân hàng được chọn."""
    overview_rows = []
    for bank_name in selected_banks:
        metrics = calculate_metrics(bank_lookup[bank_name])
        overview_rows.append({"Ngân hàng": bank_name, "ROA": metrics["roa"] * 100, "ROE": metrics["roe"] * 100, "NIM": metrics["nim"] * 100, "CASA": metrics["casa_ratio"], "NPL": metrics["npl"]})

    overview = pd.DataFrame(overview_rows)
    st.subheader("Bảng so sánh chỉ số")
    st.dataframe(overview.style.format({"ROA": "{:.2f}%", "ROE": "{:.2f}%", "NIM": "{:.2f}%", "CASA": "{:.2f}%", "NPL": "{:.2f}%"}), use_container_width=True, hide_index=True)

    st.subheader("So sánh chất lượng tín dụng và biên lãi")
    chart_data = overview.melt(id_vars="Ngân hàng", value_vars=["NPL", "NIM"], var_name="Chỉ số", value_name="Tỷ lệ (%)")
    comparison_chart = px.bar(chart_data, x="Ngân hàng", y="Tỷ lệ (%)", color="Chỉ số", barmode="group", color_discrete_map={"NPL": "#e76f51", "NIM": "#2a9d8f"})
    comparison_chart.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="")
    st.plotly_chart(comparison_chart, use_container_width=True)


def open_bank_dialog(mode, existing_data=None):
    """Mở dialog tạo mới hoặc chỉnh sửa; các input không chiếm diện tích dashboard."""
    is_editing = mode == "edit"
    initial = existing_data.to_dict() if existing_data is not None else MANUAL_DEFAULTS
    original_name = str(initial["Bank"]).strip()
    dialog_title = f"Edit Bank: {original_name}" if is_editing else "Add New Bank"

    @st.dialog(dialog_title, width="large")
    def bank_editor():
        st.caption("Kiểm tra số liệu bằng Preview trước khi lưu vào dataset tích lũy.")
        bank_name = st.text_input("Tên ngân hàng", value=original_name, disabled=is_editing, key=f"dialog_bank_{mode}_{original_name}")
        business_col, funding_col, credit_col = st.columns(3, gap="large")
        with business_col:
            st.markdown('<div class="input-group"><p class="input-group-title">💼 Kinh doanh</p>', unsafe_allow_html=True)
            lnst = st.number_input("LNST", value=float(initial["LNST"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_lnst_{mode}_{original_name}")
            nii = st.number_input("NII", value=float(initial["NetInterestIncome"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_nii_{mode}_{original_name}")
            total_assets = st.number_input("Tổng tài sản", value=float(initial["TotalAssets"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_assets_{mode}_{original_name}")
            equity = st.number_input("Vốn chủ sở hữu", value=float(initial["Equity"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_equity_{mode}_{original_name}")
            st.markdown("</div>", unsafe_allow_html=True)
        with funding_col:
            st.markdown('<div class="input-group"><p class="input-group-title">🏦 Nguồn vốn</p>', unsafe_allow_html=True)
            casa = st.number_input("CASA", value=float(initial["CASA"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_casa_{mode}_{original_name}")
            total_deposit = st.number_input("Tổng tiền gửi", value=float(initial["TotalDeposit"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_deposit_{mode}_{original_name}")
            st.markdown("</div>", unsafe_allow_html=True)
        with credit_col:
            st.markdown('<div class="input-group"><p class="input-group-title">💳 Tín dụng</p>', unsafe_allow_html=True)
            group1 = st.number_input("Nhóm 1", value=float(initial["Group1"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_group1_{mode}_{original_name}")
            group2 = st.number_input("Nhóm 2", value=float(initial["Group2"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_group2_{mode}_{original_name}")
            group3 = st.number_input("Nhóm 3", value=float(initial["Group3"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_group3_{mode}_{original_name}")
            group4 = st.number_input("Nhóm 4", value=float(initial["Group4"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_group4_{mode}_{original_name}")
            group5 = st.number_input("Nhóm 5", value=float(initial["Group5"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_group5_{mode}_{original_name}")
            provision = st.number_input("DPRR", value=float(initial["Provision"]), min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP, key=f"dialog_provision_{mode}_{original_name}")
            st.markdown("</div>", unsafe_allow_html=True)

        bank_data = {"Bank": bank_name.strip(), "LNST": lnst, "NetInterestIncome": nii, "TotalAssets": total_assets, "Equity": equity, "CASA": casa, "TotalDeposit": total_deposit, "Group1": group1, "Group2": group2, "Group3": group3, "Group4": group4, "Group5": group5, "Provision": provision}
        preview_col, save_col = st.columns(2)
        with preview_col:
            preview_requested = st.button("📋 Preview Analysis", use_container_width=True, key=f"preview_{mode}_{original_name}")
        with save_col:
            save_requested = st.button("💾 Update" if is_editing else "💾 Save to Master Dataset", use_container_width=True, type="primary", key=f"save_{mode}_{original_name}")

        if preview_requested:
            preview_name = bank_data["Bank"] or "Ngân hàng đang nhập"
            st.divider()
            st.markdown("### Kết quả phân tích tạm thời")
            render_bank_analysis(preview_name, bank_data, instance_key=f"dialog_preview_{mode}_{original_name}")

        if save_requested:
            if not bank_data["Bank"]:
                st.error("Vui lòng nhập Tên ngân hàng trước khi lưu.")
                return
            if is_editing:
                st.session_state.master_data.loc[st.session_state.master_data["Bank"].astype(str) == original_name, REQUIRED_COLUMNS] = [bank_data[column] for column in REQUIRED_COLUMNS]
            elif bank_data["Bank"] in set(st.session_state.master_data["Bank"].astype(str).str.strip()):
                st.error(f"Ngân hàng '{bank_data['Bank']}' đã tồn tại.")
                return
            else:
                st.session_state.master_data = pd.concat([st.session_state.master_data, pd.DataFrame([bank_data])], ignore_index=True)[REQUIRED_COLUMNS]
            st.rerun()

    bank_editor()


def load_uploaded_data(uploaded_file):
    """Đọc và xác thực file upload trước khi lưu vào session state."""
    try:
        data = pd.read_excel(uploaded_file) if uploaded_file.name.lower().endswith(".xlsx") else pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Không thể đọc file: {error}")
        st.stop()

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        st.error(f"File thiếu cột bắt buộc: {', '.join(missing_columns)}")
        st.stop()
    if data["Bank"].isna().any() or (data["Bank"].astype(str).str.strip() == "").any():
        st.error("Cột Bank không được để trống.")
        st.stop()
    if data["Bank"].duplicated().any():
        duplicates = data.loc[data["Bank"].duplicated(keep=False), "Bank"].astype(str).unique()
        st.error(f"Tên ngân hàng bị trùng: {', '.join(duplicates)}")
        st.stop()

    # Ép kiểu số sớm để phát hiện file không đúng định dạng trước khi phân tích.
    numeric_columns = [column for column in REQUIRED_COLUMNS if column != "Bank"]
    try:
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError):
        st.error("Các cột tài chính phải chứa dữ liệu số hợp lệ.")
        st.stop()
    return data[REQUIRED_COLUMNS].copy()


def merge_uploaded_data(uploaded_data):
    """Hợp nhất file upload vào master_data; tên trùng sẽ được ghi đè bởi file mới."""
    incoming = uploaded_data.copy()
    incoming["Bank"] = incoming["Bank"].astype(str).str.strip()
    existing = st.session_state.master_data.copy()
    existing["Bank"] = existing["Bank"].astype(str).str.strip()
    overwritten = incoming["Bank"].isin(existing["Bank"]).sum()
    # Bỏ bản ghi cũ cùng tên trước khi nối để chỉ giữ bản ghi mới từ file upload.
    remaining = existing.loc[~existing["Bank"].isin(incoming["Bank"])]
    st.session_state.master_data = pd.concat([remaining, incoming], ignore_index=True)[REQUIRED_COLUMNS]
    return overwritten


# Dataset duy nhất cho cả file upload và dữ liệu nhập tay; không bị mất khi Streamlit rerun.
if "master_data" not in st.session_state:
    st.session_state.master_data = pd.DataFrame(columns=REQUIRED_COLUMNS)
if "uploaded_file_signature" not in st.session_state:
    st.session_state.uploaded_file_signature = None

with st.sidebar:
    st.header("Quản lý dữ liệu")
    uploaded_file = st.file_uploader("📤 Tải dữ liệu ngân hàng", type=["xlsx", "csv"], help="Cột bắt buộc: " + ", ".join(REQUIRED_COLUMNS))
    if uploaded_file is not None:
        # Chỉ merge khi người dùng thực sự chọn file mới, tránh ghi đè chỉnh sửa ở các rerun sau.
        file_signature = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        if file_signature != st.session_state.uploaded_file_signature:
            uploaded_data = load_uploaded_data(uploaded_file)
            overwritten_count = merge_uploaded_data(uploaded_data)
            st.session_state.uploaded_file_signature = file_signature
            st.success(f"Đã nhập {len(uploaded_data)} ngân hàng ({overwritten_count} bản ghi được cập nhật).")

    if st.button("➕ Add Manual Bank", use_container_width=True, type="primary"):
        open_bank_dialog("add")

    st.divider()
    st.subheader("Data Management")
    if st.session_state.master_data.empty:
        st.caption("Chưa có ngân hàng trong dataset.")
    else:
        st.dataframe(st.session_state.master_data[["Bank"]], use_container_width=True, hide_index=True)
        managed_bank = st.selectbox("Chọn ngân hàng", st.session_state.master_data["Bank"].astype(str).tolist(), key="managed_bank")
        edit_col, delete_col = st.columns(2)
        with edit_col:
            if st.button("✏️ Edit", use_container_width=True):
                bank_row = st.session_state.master_data.loc[st.session_state.master_data["Bank"].astype(str) == managed_bank].iloc[0]
                open_bank_dialog("edit", bank_row)
        with delete_col:
            if st.button("🗑️ Delete", use_container_width=True):
                st.session_state.master_data = st.session_state.master_data.loc[st.session_state.master_data["Bank"].astype(str) != managed_bank].reset_index(drop=True)
                # Xóa lựa chọn cũ để selectbox/multiselect không giữ tên ngân hàng vừa bị xóa.
                st.session_state.pop("primary_bank", None)
                st.session_state.pop("additional_banks", None)
                st.rerun()

st.title("🏦 BankHealth Analyzer")
st.caption("Bảng điều khiển phân tích sức khỏe tài chính ngân hàng")

master_data = st.session_state.master_data
if master_data.empty:
    st.info("Dataset hiện trống. Hãy tải file hoặc dùng nút “Add Manual Bank” ở thanh bên.")
else:
    # Cả dữ liệu upload và nhập tay đều được lấy từ cùng một danh sách ngân hàng.
    bank_names = master_data["Bank"].astype(str).unique().tolist()
    if st.session_state.get("primary_bank") not in bank_names:
        st.session_state.primary_bank = bank_names[0]
    st.markdown("### Chọn ngân hàng để phân tích")
    primary_bank = st.selectbox("Ngân hàng chính", bank_names, key="primary_bank")
    comparison_options = [bank for bank in bank_names if bank != primary_bank]
    # Lọc session state cũ để không giữ lựa chọn bị trùng với ngân hàng chính vừa đổi.
    if "additional_banks" in st.session_state:
        st.session_state.additional_banks = [bank for bank in st.session_state.additional_banks if bank in comparison_options]
    additional_banks = st.multiselect("Thêm ngân hàng để so sánh", comparison_options, key="additional_banks", placeholder="Chọn thêm ngân hàng")
    selected_banks = [primary_bank, *additional_banks]
    bank_lookup = {str(row["Bank"]): row for _, row in master_data.iterrows()}

    # Từ hai ngân hàng trở lên, tab overview luôn được đặt đầu tiên.
    if len(selected_banks) >= 2:
        tab_labels = ["📊 Overview & Comparison", *selected_banks]
        tabs = st.tabs(tab_labels)
        with tabs[0]:
            render_comparison_overview(selected_banks, bank_lookup)
        for tab, bank_name in zip(tabs[1:], selected_banks):
            with tab:
                render_bank_analysis(bank_name, bank_lookup[bank_name])
    else:
        render_bank_analysis(primary_bank, bank_lookup[primary_bank])
