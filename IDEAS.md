# 🏦 BankHealth Analyzer - Mini App Phân Tích Rủi Rô & Sức Khỏe Tài Chính Ngân Hàng

## 📌 1. Giới Thiệu Ý Tưởng
**BankHealth Analyzer** là một Mini App thông minh giúp đơn giản hóa việc đánh giá và phân tích "sức khỏe" tài chính của một ngân hàng thương mại. Ứng dụng chuyển đổi các số liệu thô từ Báo cáo tài chính thành các chỉ số trực quan, tập trung vào hai khía cạnh sống còn trong quản trị ngân hàng: **Hiệu quả sinh lời (Mô hình Dupont, NIM, CASA)** và **Quản trị rủi ro tín dụng (Tỷ lệ nợ xấu, Bao phủ nợ xấu)**.

---

## ⚙️ 2. Công Nghệ Triển Khai (Python Stack)
Ứng dụng được xây dựng hoàn toàn trên nền tảng **Python**, tối ưu hóa tốc độ xử lý dữ liệu và khả năng trực quan hóa giao diện:
*   **Giao diện người dùng (UI/UX):** `Streamlit` (Hỗ trợ kéo thả, tạo giao diện Web/Mini App responsive cực nhanh bằng Python mà không cần viết HTML/CSS).
*   **Xử lý số liệu & Logic:** `Pandas` và `NumPy`.
*   **Trực quan hóa đồ thị:** `Plotly` hoặc `Matplotlib` (Vẽ biểu đồ động, sơ đồ cây Dupont tương tác).

---

## 💼 3. Các Nghiệp Vụ Chính Của Ứng Dụng

Ứng dụng được chia làm 4 khối nghiệp vụ luồng dữ liệu khép kín:

### 📥 Nghiệp vụ 1: Thu Thập & Nhập Liệu (Data Input)
Thiết kế giao diện Form nhập liệu chia làm 3 nhóm chỉ số cốt lõi:
1.  **Số liệu kinh doanh:** Lợi nhuận sau thuế (LNST), Thu nhập lãi thuần, Tổng tài sản, Vốn chủ sở hữu (Vốn CSH).
2.  **Cơ cấu nguồn vốn:** Tiền gửi không kỳ hạn (CASA), Tổng tiền gửi khách hàng.
3.  **Chất lượng tín dụng:** Dư nợ phân cấp từ **Nhóm 1 đến Nhóm 5** và Quỹ dự phòng rủi ro tín dụng.

### 🧮 Nghiệp vụ 2: Xử Lý Logic & Tính Toán Chỉ Số
Hệ thống tự động tính toán các chỉ số tài chính theo công thức chuẩn của Ngân hàng Nhà nước:
*   **Nhóm sinh lời:** 
    *   $ROA = \frac{LNST}{Tổng\ Tài\ sản}$
    *   $ROE = \frac{LNST}{Vốn\ Chủ\ sở\ hữu}$
    *   $NIM = \frac{Thu\ nhập\ lãi\ thuần}{Tổng\ Tài\ sản}$
*   **Nhóm quản trị rủi ro (Nợ xấu):**
    *   $Tổng\ dư\ nợ = Nhóm\ 1 + Nhóm\ 2 + Nhóm\ 3 + Nhóm\ 4 + Nhóm\ 5$
    *   $Tỷ\ lệ\ nợ\ xấu\ (NPL) = \frac{Nhóm\ 3 + Nhóm\ 4 + Nhóm\ 5}{Tổng\ dư\ nợ} \times 100\%$
    *   $Tỷ\ lệ\ bao\ phủ\ nợ\ xấu = \frac{Quỹ\ dự\ phòng\ rủi\ ro}{Nhóm\ 3 + Nhóm\ 4 + Nhóm\ 5} \times 100\%$
*   **Nhóm tối ưu chi phí vốn:**
    *   $Tỷ\ lệ\ CASA = \frac{Tiền\ gửi\ không\ kỳ\ hạn}{Tổng\ tiền\ gửi} \times 100\%$

### 🌳 Nghiệp vụ 3: Phân Rã Mô Hình Dupont (Dupont Visualizer)
Trực quan hóa chỉ số ROE thành sơ đồ cây phân cấp tương tác (Tree-chart):
*   **Bậc 1:** Tách $ROE = ROA \times Đòn\ bẩy\ tài\ chính\ (Tổng\ Tài\ sản\ /\ Vốn\ CSH)$.
*   **Bậc 2:** Tách $ROA = Biên\ lợi\ nhuận\ thuần\ \times\ Vòng\ quay\ Tài\ sản$.
*   *Tính năng Python:* Người dùng có thể hover (di chuột) vào từng nhánh cây để xem tỷ trọng đóng góp của từng yếu tố vào biến động của ROE.

### 🚨 Nghiệp vụ 4: Cảnh Báo Ngưỡng Rủi Rô & Nhận Xét Tự Động
*   **Hệ thống đèn tín hiệu (Traffic Light Alert):** Tự động đổi màu chỉ số dựa trên mức độ an toàn. (Ví dụ: Tỷ lệ nợ xấu < 1.5% hiện **Xanh**, từ 1.5% - 3% hiện **Vàng**, > 3% lập tức báo động **Đỏ**).
*   **Trợ lý AI phân tích tự động:** Thuật toán tự động ghép chuỗi văn bản (Text-generation logic) để đưa ra kết luận nhanh về tình hình tài chính của ngân hàng vừa nhập liệu.

---

## 🚀 4. Kế Hoạch Phát Triển Tính Năng Mở Rộng (Cộng Điểm)
*   **Lưu trữ lịch sử:** Dùng file `SQLite` hoặc `JSON` cục bộ để lưu lại lịch sử phân tích của các ngân hàng qua các năm.
*   **So sánh đối chiếu:** Vẽ biểu đồ đường (Line chart) so sánh trực quan xu hướng nợ xấu hoặc biên NIM giữa Ngân hàng A và Ngân hàng B để tìm ra đơn vị quản trị tốt hơn.