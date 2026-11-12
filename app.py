import hashlib
import json
import requests
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Sát Hạch & Cắm Trại 24/11 - Đội",
    page_icon="⛺",
    layout="wide",
)

# Bin ID của npoint.io
BIN_ID = "89fea106b426901294dd"

# Giao diện CSS tùy chỉnh Dark Mode hiện đại
st.markdown(
    """
    <style>
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid #374151;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
        border-color: #10b981;
    }
    .auth-box {
        background: linear-gradient(145deg, #161e2e, #1f2937);
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #374151;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    .item-card {
        background: #161e2e;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 16px;
        border: 1px solid #2d3748;
    }
    .header-banner {
        background: linear-gradient(90deg, #065f46 0%, #1e3a8a 100%);
        padding: 25px;
        border-radius: 14px;
        margin-bottom: 20px;
        border: 1px solid #3b82f6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Hàm mã hóa mật khẩu
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# Hàm tải toàn bộ dữ liệu từ Cloud (bao gồm users, locations, requirements)
def load_data():
    try:
        url = f"https://api.npoint.io/{BIN_ID}"
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, dict):
                return {
                    "users": res_data.get("users", {}),
                    "locations": res_data.get("locations", []),
                    "requirements": res_data.get("requirements", []),
                }
    except Exception as e:
        st.error(f"Lỗi kết nối Cloud: {e}")
    return {"users": {}, "locations": [], "requirements": []}


# Hàm lưu toàn bộ dữ liệu lên Cloud
def save_data(data):
    try:
        url = f"https://api.npoint.io/{BIN_ID}"
        response = requests.put(url, json=data, timeout=6)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Không thể lưu lên Cloud: {e}")
        return False


# Khởi tạo trạng thái phiên đăng nhập
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# Tải dữ liệu từ Cloud
data = load_data()

# ==========================================
# MÀN HÌNH 1: ĐĂNG KÝ / ĐĂNG NHẬP BẮT BUỘC
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1.4, 1])

    with col_center:
        st.markdown(
            """
            <div class="auth-box">
                <h2 style="text-align: center; color: #10b981; margin-bottom: 5px;">⛺ CỔNG THÔNG TIN ĐỘI</h2>
                <p style="text-align: center; color: #9ca3af; font-size: 14px;">
                    Vui lòng đăng ký hoặc đăng nhập để tham gia kế hoạch Dã Ngoại & Sát Hạch 24/11
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Tài Khoản Mới"])

        # --- TAB ĐĂNG NHẬP ---
        with tab_login:
            with st.form("login_form"):
                login_name = st.text_input(
                    "Tên thành viên", placeholder="Nhập tên bạn đã đăng ký..."
                ).strip()
                login_pass = st.text_input(
                    "Mật khẩu", type="password", placeholder="Nhập mật khẩu..."
                )
                btn_login = st.form_submit_button("🚀 Vào Hệ Thống")

                if btn_login:
                    if not login_name or not login_pass:
                        st.warning("Vui lòng nhập đầy đủ tên và mật khẩu!")
                    elif login_name not in data["users"]:
                        st.error("Tên này chưa được đăng ký! Vui lòng chuyển sang tab 'Đăng Ký Tài Khoản Mới'.")
                    else:
                        if data["users"][login_name] == hash_password(login_pass):
                            st.session_state.logged_in = True
                            st.session_state.current_user = login_name
                            st.success(f"Chào mừng {login_name} quay trở lại!")
                            st.rerun()
                        else:
                            st.error("Mật khẩu không chính xác!")

        # --- TAB ĐĂNG KÝ ---
        with tab_register:
            with st.form("register_form"):
                reg_name = st.text_input(
                    "Tên của bạn (Dùng để hiển thị khi vote & nhận việc)",
                    placeholder="Ví dụ: Nguyễn Văn A...",
                ).strip()
                reg_pass = st.text_input(
                    "Tạo mật khẩu", type="password", placeholder="Nhập mật khẩu..."
                )
                reg_pass_confirm = st.text_input(
                    "Nhập lại mật khẩu",
                    type="password",
                    placeholder="Xác nhận lại mật khẩu...",
                )
                btn_reg = st.form_submit_button("✅ Đăng Ký & Lưu Lên Cloud")

                if btn_reg:
                    if not reg_name or not reg_pass:
                        st.warning("Vui lòng nhập tên và mật khẩu!")
                    elif reg_pass != reg_pass_confirm:
                        st.error("Mật khẩu xác nhận không khớp!")
                    elif reg_name in data["users"]:
                        st.error("Tên này đã có người đăng ký! Vui lòng chọn tên khác (ví dụ thêm tên đệm) hoặc đăng nhập.")
                    else:
                        # Lưu tài khoản mới lên npoint.io
                        data["users"][reg_name] = hash_password(reg_pass)
                        if save_data(data):
                            st.session_state.logged_in = True
                            st.session_state.current_user = reg_name
                            st.success("Đăng ký thành công và đã lưu lên Cloud!")
                            st.rerun()
                        else:
                            st.error("Lỗi khi lưu tài khoản lên Cloud. Vui lòng thử lại!")

# ==========================================
# MÀN HÌNH 2: GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP
# ==========================================
else:
    user = st.session_state.current_user

    # Thanh trên cùng hiển thị thông tin người dùng & nút đăng xuất
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.markdown(f"🟢 **Xin chào, {user}!** | Dữ liệu đang đồng bộ trực tuyến.")
    with top_col2:
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()

    # Banner tiêu đề
    st.markdown(
        """
        <div class="header-banner">
            <h1 style="margin:0; color: #ffffff;">⛺ KẾ HOẠCH DÃ NGOẠI & SÁT HẠCH TOÀN ĐỘI (24/11)</h1>
            <p style="margin-top:10px; color: #e5e7eb; font-size: 16px;">
                <b>Thông báo chính thức:</b> Ngày <b>24/11</b> tới đây anh em sẽ được nghỉ trọn vẹn nguyên ngày! 
                Chúng ta sẽ tổ chức chuyến cắm trại dã ngoại kết hợp làm Vòng 2 sát hạch nhân sự mới.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Chia tab giao diện
    tab1, tab2, tab3 = st.tabs(
        ["🗳️ Bình Chọn Địa Điểm", "📋 Danh Sách Đồ Cần Chuẩn Bị", "👥 Thành Viên & Hướng Dẫn"]
    )

    # --- TAB 1: BÌNH CHỌN ĐỊA ĐIỂM ---
    with tab1:
        st.subheader("📍 Đề Xuất & Bình Chọn Địa Điểm Cắm Trại")

        with st.form("form_add_location_unique", clear_on_submit=True):
            col_f1, col_f2 = st.columns([2, 3])
            with col_f1:
                new_loc_name = st.text_input(
                    "Tên địa điểm mới", placeholder="Ví dụ: Núi Chứa Chan..."
                )
            with col_f2:
                new_loc_desc = st.text_input(
                    "Mô tả / Khoảng cách", placeholder="Đường đi thuận lợi, cảnh đẹp..."
                )
            submitted_loc = st.form_submit_button("➕ Thêm Địa Điểm Mới")

            if submitted_loc:
                if new_loc_name:
                    new_id = str(len(data["locations"]) + 1)
                    data["locations"].append(
                        {
                            "id": new_id,
                            "name": new_loc_name,
                            "desc": new_loc_desc or "Chưa có mô tả",
                            "votes": 0,
                            "voters": [],
                            "created_by": user,
                        }
                    )
                    if save_data(data):
                        st.success(f"Đã thêm địa điểm '{new_loc_name}' lên hệ thống!")
                        st.rerun()
                    else:
                        st.error("Lưu thất bại!")
                else:
                    st.warning("Vui lòng nhập tên địa điểm!")

        st.markdown("### Danh sách các địa điểm hiện tại:")
        if not data["locations"]:
            st.info("Chưa có địa điểm nào được thêm. Hãy thêm địa điểm đầu tiên ở trên!")

        for idx, loc in enumerate(data["locations"]):
            loc_id = loc.get("id", str(idx))
            voters_list = loc.get("voters", [])
            has_voted = user in voters_list

            st.markdown('<div class="item-card">', unsafe_allow_html=True)
