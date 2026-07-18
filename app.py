"""BankHealth Analyzer — dashboard phân tích sức khỏe tài chính ngân hàng.

Chạy ứng dụng: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

NUMBER_INPUT_STEP = 1000.0

st.set_page_config(
    page_title="BankHealth Analyzer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>

/* Ẩn dòng "Press Enter to submit form" */
[data-testid="InputInstructions"] {
    display: none;
}

/* Phiên bản Streamlit cũ */
.st-emotion-cache-16idsys p {
    display: none;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
      .block-container {max-width: 1440px; padding: 1.5rem 2.25rem 3rem;}
      [data-testid="stAppViewContainer"] {background: #f7f9fc;}
      h1 {color: #123a63; letter-spacing: -.03em; margin-bottom: .1rem !important;}
      div[data-testid="stMetric"] {
        background: #fff; border: 1px solid #e2e9f2; border-radius: 14px;
        padding: 1rem 1.15rem; box-shadow: 0 3px 12px rgba(32,61,92,.05);
      }
      div[data-testid="stMetricLabel"] {color: #5d6b7e;}
      div[data-testid="stMetricValue"] {color: #123a63;}
      div[data-testid="stForm"] {
        border: 1px solid #dce6f1; border-radius: 16px; padding: 1.2rem 1.4rem 1rem;
        background: linear-gradient(180deg, #ffffff 0%, #f5f9fd 100%);
        box-shadow: 0 4px 16px rgba(32,61,92,.04);
      }
      .form-title {font-size: 1.08rem; font-weight: 750; color: #123a63; margin: 0;}
      .form-note {color: #6b7a90; margin: .15rem 0 1rem; font-size: .9rem;}
      .input-group {
        height: 100%; background: rgba(255,255,255,.78); border: 1px solid #e6edf5;
        border-radius: 12px; padding: .85rem .9rem .15rem; margin-bottom: .2rem;
      }
      .input-group-title {font-size: .94rem; font-weight: 700; color: #244d76; margin: 0 0 .45rem;}
      div[data-testid="stNumberInput"] label {font-size: .84rem; color: #506176;}
      div[data-testid="stNumberInput"] input {background: #fff; border-color: #d6e1ed;}
      div[data-testid="stFormSubmitButton"] {margin-top: .6rem;}
      .dashboard-title {color: #123a63; margin: 0 0 .7rem; font-size: 1.4rem;}
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


st.title("🏦 BankHealth Analyzer")
st.caption("Bảng điều khiển phân tích sức khỏe tài chính ngân hàng")

# Form nằm ngang, chia thành ba khối nghiệp vụ để toàn bộ dữ liệu quan trọng
# luôn hiển thị trong một vùng thao tác ngắn gọn.
with st.form("bank_input_form", border=False):
    st.markdown('<p class="form-title">📥 FORM NHẬP DỮ LIỆU</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="form-note">Cập nhật số liệu đầu vào rồi nhấn <b>Phân tích</b> để làm mới dashboard.</p>',
        unsafe_allow_html=True,
    )
    business_col, funding_col, credit_col = st.columns(3, gap="large")

    with business_col:
        st.markdown('<div class="input-group"><p class="input-group-title">💼 Kinh doanh</p>', unsafe_allow_html=True)
        business_left, business_right = st.columns(2)
        with business_left:
            lnst = st.number_input("LNST", value=1000.0, min_value=0.01, format="%.2f", help="Lợi nhuận sau thuế", step=NUMBER_INPUT_STEP)
            total_assets = st.number_input("Tổng tài sản", value=200000.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
        with business_right:
            net_interest_income = st.number_input("NII", value=5000.0, min_value=0.01, format="%.2f", help="Thu nhập lãi thuần", step=NUMBER_INPUT_STEP)
            equity = st.number_input("Vốn chủ sở hữu", value=20000.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
        st.markdown("</div>", unsafe_allow_html=True)

    with funding_col:
        st.markdown('<div class="input-group"><p class="input-group-title">🏦 Nguồn vốn</p>', unsafe_allow_html=True)
        casa = st.number_input("CASA", value=30000.0, min_value=0.01, format="%.2f", help="Tiền gửi không kỳ hạn", step=NUMBER_INPUT_STEP)
        total_deposit = st.number_input("Tổng tiền gửi", value=150000.0, min_value=0.01, format="%.2f", help="Tổng tiền gửi khách hàng", step=NUMBER_INPUT_STEP)
        st.markdown("</div>", unsafe_allow_html=True)

    with credit_col:
        st.markdown('<div class="input-group"><p class="input-group-title">💳 Tín dụng</p>', unsafe_allow_html=True)
        credit_left, credit_right = st.columns(2)
        with credit_left:
            group1 = st.number_input("Nhóm 1", value=120000.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            group2 = st.number_input("Nhóm 2", value=3000.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            group3 = st.number_input("Nhóm 3", value=1200.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
        with credit_right:
            group4 = st.number_input("Nhóm 4", value=800.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            group5 = st.number_input("Nhóm 5", value=500.0, min_value=0.01, format="%.2f", step=NUMBER_INPUT_STEP)
            provision = st.number_input("DPRR", value=3000.0, min_value=0.01, format="%.2f", help="Dự phòng rủi ro tín dụng", step=NUMBER_INPUT_STEP)
        st.markdown("</div>", unsafe_allow_html=True)

    _, action_col, _ = st.columns([2, 1, 2])
    with action_col:
        submitted = st.form_submit_button("PHÂN TÍCH", use_container_width=True, type="primary")

if submitted:
    st.toast("Dashboard đã được cập nhật.", icon="✅")

total_loan = group1 + group2 + group3 + group4 + group5
bad_debt = group3 + group4 + group5
roa = safe_divide(lnst, total_assets)
roe = safe_divide(lnst, equity)
nim = safe_divide(net_interest_income, total_assets)
casa_ratio = safe_divide(casa, total_deposit) * 100
npl = safe_divide(bad_debt, total_loan) * 100
overdue = safe_divide(group2 + bad_debt, total_loan) * 100
coverage = safe_divide(provision, bad_debt) * 100
em = safe_divide(total_assets, equity)

st.divider()
st.markdown('<h2 class="dashboard-title">Tổng quan hiệu quả</h2>', unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("ROA", f"{roa * 100:.2f}%", score_comment(roa, .02, .01, ("Hiệu quả tài sản tốt", "Mức trung bình", "Hiệu quả thấp")))
kpi2.metric("ROE", f"{roe * 100:.2f}%", score_comment(roe, .15, .10, ("Khả năng sinh lời cao", "Mức sinh lời khá", "Sinh lời thấp")))
kpi3.metric("NIM", f"{nim * 100:.2f}%", score_comment(nim, .03, .02, ("Biên lãi thuần tốt", "Mức trung bình", "Biên lãi thấp")))
kpi4.metric("CASA", f"{casa_ratio:.2f}%", score_comment(casa_ratio, 30, 20, ("CASA rất tốt", "CASA khá", "CASA thấp")))

st.divider()
chart_col, dupont_col = st.columns(2, gap="large")
with chart_col:
    st.subheader("Cơ cấu nhóm nợ")
    debt_df = pd.DataFrame({"Nhóm nợ": ["Nhóm 1", "Nhóm 2", "Nhóm 3", "Nhóm 4", "Nhóm 5"], "Dư nợ": [group1, group2, group3, group4, group5]})
    pie = px.pie(debt_df, names="Nhóm nợ", values="Dư nợ", hole=.52, color="Nhóm nợ", color_discrete_sequence=["#4c9f70", "#e9c46a", "#f4a261", "#e76f51", "#b23a48"])
    pie.update_traces(textposition="inside", textinfo="percent+label")
    pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="")
    st.plotly_chart(pie, use_container_width=True)
with dupont_col:
    st.subheader("Mô hình Dupont")
    tree = go.Figure()
    tree.add_trace(go.Scatter(x=[.5, .2, .8], y=[1, .35, .35], mode="markers+text", text=[f"<b>ROE</b><br>{roe * 100:.2f}%", f"<b>ROA</b><br>{roa * 100:.2f}%", f"<b>EM</b><br>{em:.2f}x"], textposition="bottom center", marker=dict(size=[42, 36, 36], color=["#173f67", "#2a9d8f", "#e9c46a"]), hovertemplate="%{text}<extra></extra>"))
    for x_end in (.2, .8):
        tree.add_shape(type="line", x0=.5, y0=.92, x1=x_end, y1=.43, line=dict(color="#9aabbc", width=2))
    tree.add_annotation(x=.5, y=.67, text="ROE = ROA × Đòn bẩy tài chính", showarrow=False, font=dict(size=15, color="#425466"))
    tree.update_layout(height=410, margin=dict(l=10, r=10, t=10, b=25), showlegend=False, xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(visible=False, range=[0, 1.2]))
    st.plotly_chart(tree, use_container_width=True)

st.divider()
summary_col, alert_col = st.columns([1.35, 1], gap="large")
status, icon, message, level = npl_status(npl)
with alert_col:
    st.subheader("Cảnh báo NPL")
    getattr(st, level)(f"{icon} **Mức {status} — NPL: {npl:.2f}%**\n\n{message}.")
with summary_col:
    st.subheader("Bảng tổng hợp chỉ số")
    summary = pd.DataFrame({"Chỉ số": ["Tổng dư nợ", "Nợ quá hạn", "Tỷ lệ NPL", "Bao phủ nợ xấu", "Đòn bẩy tài chính (EM)"], "Giá trị": [f"{total_loan:,.2f}", f"{overdue:.2f}%", f"{npl:.2f}%", f"{coverage:.2f}%", f"{em:.2f}x"]})
    st.dataframe(summary, use_container_width=True, hide_index=True, column_config={"Chỉ số": st.column_config.TextColumn(width="large")})
