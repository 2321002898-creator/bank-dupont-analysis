"""BankHealth Analyzer — dashboard phân tích sức khỏe tài chính ngân hàng.

Chạy ứng dụng: streamlit run app.py
"""

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
    "Bank": "Ngân hàng đang phân tích", "LNST": 1000.0, "NetInterestIncome": 5000.0,
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


def render_bank_analysis(bank_name, bank_data):
    """Render đầy đủ dashboard hiện hữu cho một ngân hàng độc lập."""
    metrics = calculate_metrics(bank_data)
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
        st.plotly_chart(pie, use_container_width=True, key=f"loan_groups_{bank_name}")
    with dupont_col:
        st.subheader("Mô hình Dupont")
        tree = go.Figure()
        tree.add_trace(go.Scatter(x=[.5, .2, .8], y=[1, .35, .35], mode="markers+text", text=[f"<b>ROE</b><br>{metrics['roe'] * 100:.2f}%", f"<b>ROA</b><br>{metrics['roa'] * 100:.2f}%", f"<b>EM</b><br>{metrics['em']:.2f}x"], textposition="bottom center", marker=dict(size=[42, 36, 36], color=["#173f67", "#2a9d8f", "#e9c46a"]), hovertemplate="%{text}<extra></extra>"))
        for x_end in (.2, .8):
            tree.add_shape(type="line", x0=.5, y0=.92, x1=x_end, y1=.43, line=dict(color="#9aabbc", width=2))
        tree.add_annotation(x=.5, y=.67, text="ROE = ROA × Đòn bẩy tài chính", showarrow=False, font=dict(size=15, color="#425466"))
        tree.update_layout(height=410, margin=dict(l=10, r=10, t=10, b=25), showlegend=False, xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(visible=False, range=[0, 1.2]))
        st.plotly_chart(tree, use_container_width=True, key=f"dupont_tree_{bank_name}")

    st.divider()
    summary_col, alert_col = st.columns([1.35, 1], gap="large")
    status, icon, message, level = npl_status(metrics["npl"])
    with alert_col:
        st.subheader("Cảnh báo NPL")
        getattr(st, level)(f"{icon} **Mức {status} — NPL: {metrics['npl']:.2f}%**\n\n{message}.")
    with summary_col:
        st.subheader("Bảng tổng hợp chỉ số")
        summary = pd.DataFrame({"Chỉ số": ["Tổng dư nợ", "Nợ quá hạn", "Tỷ lệ NPL", "Bao phủ nợ xấu", "Đòn bẩy tài chính (EM)"], "Giá trị": [f"{metrics['total_loan']:,.2f}", f"{metrics['overdue']:.2f}%", f"{metrics['npl']:.2f}%", f"{metrics['coverage']:.2f}%", f"{metrics['em']:.2f}x"]})
        st.dataframe(summary, use_container_width=True, hide_index=True, column_config={"Chỉ số": st.column_config.TextColumn(width="large")}, key=f"summary_table_{bank_name}")


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


def render_manual_form():
    """Form nhập liệu cũ, chỉ sử dụng khi chưa có dữ liệu upload."""
    with st.form("bank_input_form", border=False):
        st.markdown('<p class="form-title">📥 FORM NHẬP DỮ LIỆU</p>', unsafe_allow_html=True)
        st.markdown('<p class="form-note">Cập nhật số liệu đầu vào rồi nhấn <b>Phân tích</b> để làm mới dashboard.</p>', unsafe_allow_html=True)
        business_col, funding_col, credit_col = st.columns(3, gap="large")
        with business_col:
            st.markdown('<div class="input-group"><p class="input-group-title">💼 Kinh doanh</p>', unsafe_allow_html=True)
            business_left, business_right = st.columns(2)
            with business_left:
                lnst = st.number_input("LNST", value=MANUAL_DEFAULTS["LNST"], min_value=0.01, format="%.2f", help="Lợi nhuận sau thuế", step=NUMBER_INPUT_STEP)
                total_assets = st.number_input("Tổng tài sản", value=MANUAL_DEFAULTS["TotalAssets"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            with business_right:
                nii = st.number_input("NII", value=MANUAL_DEFAULTS["NetInterestIncome"], min_value=0.01, format="%.2f", help="Thu nhập lãi thuần", step=NUMBER_INPUT_STEP)
                equity = st.number_input("Vốn chủ sở hữu", value=MANUAL_DEFAULTS["Equity"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            st.markdown("</div>", unsafe_allow_html=True)
        with funding_col:
            st.markdown('<div class="input-group"><p class="input-group-title">🏦 Nguồn vốn</p>', unsafe_allow_html=True)
            casa = st.number_input("CASA", value=MANUAL_DEFAULTS["CASA"], min_value=0.01, format="%.2f", help="Tiền gửi không kỳ hạn", step=NUMBER_INPUT_STEP)
            total_deposit = st.number_input("Tổng tiền gửi", value=MANUAL_DEFAULTS["TotalDeposit"], min_value=0.01, format="%.2f", help="Tổng tiền gửi khách hàng", step=NUMBER_INPUT_STEP)
            st.markdown("</div>", unsafe_allow_html=True)
        with credit_col:
            st.markdown('<div class="input-group"><p class="input-group-title">💳 Tín dụng</p>', unsafe_allow_html=True)
            credit_left, credit_right = st.columns(2)
            with credit_left:
                group1 = st.number_input("Nhóm 1", value=MANUAL_DEFAULTS["Group1"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
                group2 = st.number_input("Nhóm 2", value=MANUAL_DEFAULTS["Group2"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
                group3 = st.number_input("Nhóm 3", value=MANUAL_DEFAULTS["Group3"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            with credit_right:
                group4 = st.number_input("Nhóm 4", value=MANUAL_DEFAULTS["Group4"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
                group5 = st.number_input("Nhóm 5", value=MANUAL_DEFAULTS["Group5"], min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
                provision = st.number_input("DPRR", value=MANUAL_DEFAULTS["Provision"], min_value=0.01, format="%.2f", help="Dự phòng rủi ro tín dụng", step=NUMBER_INPUT_STEP)
            st.markdown("</div>", unsafe_allow_html=True)
        _, action_col, _ = st.columns([2, 1, 2])
        with action_col:
            submitted = st.form_submit_button("PHÂN TÍCH", use_container_width=True, type="primary")

    manual_data = {"Bank": MANUAL_DEFAULTS["Bank"], "LNST": lnst, "NetInterestIncome": nii, "TotalAssets": total_assets, "Equity": equity, "CASA": casa, "TotalDeposit": total_deposit, "Group1": group1, "Group2": group2, "Group3": group3, "Group4": group4, "Group5": group5, "Provision": provision}
    if submitted:
        st.toast("Dashboard đã được cập nhật.", icon="✅")
    return manual_data


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


st.title("🏦 BankHealth Analyzer")
st.caption("Bảng điều khiển phân tích sức khỏe tài chính ngân hàng")

# Session state giữ dữ liệu sau các lần Streamlit tự chạy lại khi người dùng đổi lựa chọn.
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

uploaded_file = st.file_uploader("📤 Tải dữ liệu ngân hàng", type=["xlsx", "csv"], help="Cột bắt buộc: " + ", ".join(REQUIRED_COLUMNS))
if uploaded_file is not None:
    st.session_state.uploaded_data = load_uploaded_data(uploaded_file)
    st.success(f"Đã nhập thành công {len(st.session_state.uploaded_data)} ngân hàng.")

if st.session_state.uploaded_data is None:
    # Chế độ mặc định: chỉ phân tích một ngân hàng từ form nhập tay.
    manual_data = render_manual_form()
    render_bank_analysis(manual_data["Bank"], manual_data)
else:
    uploaded_data = st.session_state.uploaded_data
    bank_names = uploaded_data["Bank"].astype(str).tolist()
    st.markdown("### Chọn ngân hàng để phân tích")
    primary_bank = st.selectbox("Ngân hàng chính", bank_names, key="primary_bank")
    additional_banks = st.multiselect("Thêm ngân hàng để so sánh", [bank for bank in bank_names if bank != primary_bank], key="additional_banks", placeholder="Chọn thêm ngân hàng")
    selected_banks = [primary_bank, *additional_banks]
    bank_lookup = {str(row["Bank"]): row for _, row in uploaded_data.iterrows()}

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
