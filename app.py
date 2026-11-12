import hashlib
import requests
import streamlit as st

st.set_page_config(
    page_title="Sát Hạch & Cắm Trại 24/11 - Đội",
    page_icon="⛺",
    layout="wide",
)

BIN_ID = "827d1b013f00d93657e9"

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


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_data():
    try:
        url = f"https://npoint.io{BIN_ID}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, dict):
                return {
                    "users": res_data.get("users", {}),
                    "locations": res_data.get("locations", []),
                    "requirements": res_data.get("requirements", []),
                }
        else:
            st.warning(f"Cảnh báo tải dữ liệu (Mã {response.status_code}): {response.text}")
    except Exception as e:
        st.error(f"Lỗi kết nối Cloud: {e}")
    return {"users": {}, "locations": [], "requirements": []}


def save_data(data):
    url = f"https://npoint.io{BIN_ID}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return True

        response_put = requests.put(url, json=data, headers=headers, timeout=10)
        if response_put.status_code == 200:
            return True

        st.error(f"Server từ chối lưu (Mã {response.status_code}): {response.text}")
        return False
    except Exception as e:
        st.error(f"Lỗi mạng khi lưu lên Cloud: {e}")
        return False


def render_auth_page(data):
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.4, 1])

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

        with tab_login:
            with st.form("login_form"):
                login_name = st.text_input("Tên thành viên", placeholder="Nhập tên bạn đã đăng ký...").strip()
                login_pass = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
                btn_login = st.form_submit_button("🚀 Vào Hệ Thống")

                if btn_login:
                    if not login_name or not login_pass:
                        st.warning("Vui lòng nhập đầy đủ tên và mật khẩu!")
                    elif login_name not in data["users"]:
                        st.error("Tên này chưa được đăng ký! Vui lòng chuyển sang tab 'Đăng Ký Tài Khoản Mới'.")
                    elif data["users"][login_name] == hash_password(login_pass):
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_name
                        st.success(f"Chào mừng {login_name} quay trở lại!")
                        st.rerun()
                    else:
                        st.error("Mật khẩu không chính xác!")

        with tab_register:
            with st.form("register_form"):
                reg_name = st.text_input("Tên của bạn (Dùng để hiển thị khi vote & nhận việc)", placeholder="Ví dụ: Nguyễn Văn A...").strip()
                reg_pass = st.text_input("Tạo mật khẩu", type="password", placeholder="Nhập mật khẩu...")
                reg_pass_confirm = st.text_input("Nhập lại mật khẩu", type="password", placeholder="Xác nhận lại mật khẩu...")
                btn_reg = st.form_submit_button("✅ Đăng Ký & Lưu Lên Cloud")

                if btn_reg:
                    if not reg_name or not reg_pass:
                        st.warning("Vui lòng nhập tên và mật khẩu!")
                    elif reg_pass != reg_pass_confirm:
                        st.error("Mật khẩu xác nhận không khớp!")
                    elif reg_name in data["users"]:
                        st.error("Tên này đã có người đăng ký! Vui lòng chọn tên khác hoặc đăng nhập.")
                    else:
                        data["users"][reg_name] = hash_password(reg_pass)
                        if save_data(data):
                            st.session_state.logged_in = True
                            st.session_state.current_user = reg_name
                            st.success("Đăng ký thành công và đã lưu lên Cloud!")
                            st.rerun()


def render_locations_tab(data, user):
    st.subheader("📍 Đề Xuất & Bình Chọn Địa Điểm Cắm Trại")

    with st.form("form_add_location_unique", clear_on_submit=True):
        col_f1, col_f2 = st.columns([2, 3])
        with col_f1:
            new_loc_name = st.text_input("Tên địa điểm mới", placeholder="Ví dụ: Núi Chứa Chan...")
        with col_f2:
            new_loc_desc = st.text_input("Mô tả / Khoảng cách", placeholder="Đường đi thuận lợi, cảnh đẹp...")
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
                st.warning("Vui lòng nhập tên địa điểm!")

    st.markdown("### Danh sách các địa điểm hiện tại:")
    if not data["locations"]:
        st.info("Chưa có địa điểm nào được thêm. Hãy thêm địa điểm đầu tiên ở trên!")
        return

    for idx, loc in enumerate(data["locations"]):
        loc_id = loc.get("id", str(idx))
        voters_list = loc.get("voters", [])
        has_voted = user in voters_list

        st.markdown('<div class="item-card">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([3, 3.5, 1.5, 2])

        with col1:
            st.markdown(f"#### 🔥 {loc['name']}")
            if "created_by" in loc:
                st.caption(f"Đề xuất bởi: {loc['created_by']}")

        with col2:
            st.write(loc["desc"])
            if voters_list:
                st.caption(f"👤 Đã vote ({len(voters_list)}): {', '.join(voters_list)}")

        with col3:
            st.metric("Số phiếu", loc["votes"])

        with col4:
            btn_label = "✅ Đã vote (Hủy)" if has_voted else "👍 Bầu chọn"
            if st.button(btn_label, key=f"vote_toggle_{loc_id}_{idx}"):
                if has_voted:
                    loc["voters"].remove(user)
                else:
                    loc["voters"].append(user)
                loc["votes"] = len(loc["voters"])
                if save_data(data):
                    st.rerun()

            if st.button("🗑️ Xóa", key=f"del_loc_btn_{loc_id}_{idx}"):
                data["locations"].pop(idx)
                if save_data(data):
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_requirements_tab(data, user):
    st.subheader("🎒 Danh Sách Đồ Cần Mang & Phân Công")

    with st.form("form_add_requirement_unique", clear_on_submit=True):
        r_col1, r_col2 = st.columns([3, 2])
        with r_col1:
            new_task = st.text_input("Đồ dùng / Yêu cầu cần chuẩn bị", placeholder="Ví dụ: 5 thùng nước suối...")
        with r_col2:
            new_assigned = st.text_input("Người nhận lo", value=user, placeholder="Tên anh em...")
        sub_req = st.form_submit_button("➕ Thêm Yêu Cầu")

        if sub_req:
            if new_task:
                data["requirements"].append(
                    {
                        "task": new_task,
                        "assigned": new_assigned or "Chưa phân công",
                        "done": False,
                    }
                )
                if save_data(data):
                    st.success("Đã thêm yêu cầu thành công!")
                    st.rerun()
            else:
                st.warning("Vui lòng nhập nội dung vật dụng!")

    st.markdown("### Danh sách đồ dùng:")
    if not data["requirements"]:
        st.info("Chưa có đồ dùng nào được thêm.")
        return

