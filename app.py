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

# Giao diện CSS tùy chỉnh Dark Mode cực kỳ sang trọng và mượt mà
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 45px; transition: 0.3s; }
    .stButton>button:hover { border-color: #3b82f6; color: #3b82f6; }
    .card { background: #1f2937; padding: 24px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #374151; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .auth-container { max-width: 450px; margin: 40px auto; padding: 30px; background: #1f2937; border-radius: 20px; border: 1px solid #374151; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
    </style>
""",
    unsafe_allow_html=True,
)


# Hàm tải dữ liệu từ Cloud
def load_data():
  try:
    url = f"https://api.npoint.io/{BIN_ID}"
    response = requests.get(url, timeout=5)
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


# Hàm lưu dữ liệu lên Cloud
def save_data(data):
  try:
    url = f"https://api.npoint.io/{BIN_ID}"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=data, headers=headers, timeout=5)
    if response.status_code in [200, 204]:
      return True
    else:
      st.error(f"Lưu thất bại! Mã lỗi từ npoint: {response.status_code}")
      return False
  except Exception as e:
    st.error(f"Không thể kết nối Cloud: {e}")
    return False


# Khởi tạo session state cho đăng nhập
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""

# Tải dữ liệu hiện tại từ Cloud
data = load_data()
if not isinstance(data.get("users"), dict):
  data["users"] = {}

# --- GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ (NẾU CHƯA ĐĂNG NHẬP) ---
if not st.session_state.logged_in:
  st.markdown("<br><br>", unsafe_allow_html=True)
  col1, col2, col3 = st.columns([1, 2, 1])

  with col2:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1>⛺ CẮM TRẠI & SÁT HẠCH 24/11</h1>
            <p style="color: #9ca3af;">Đăng nhập hoặc đăng ký tài khoản để tham gia hệ thống chung của đội</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auth_tab1, auth_tab2 = st.tabs(["🔐 Đăng Nhập", "📝 Đăng Ký Tài Khoản"])

    # TAB ĐĂNG NHẬP
    with auth_tab1:
      with st.form("login_form"):
        login_user = st.text_input(
            "Tên tài khoản", placeholder="Nhập tên của bạn..."
        )
        login_pass = st.text_input(
            "Mật khẩu", type="password", placeholder="Nhập mật khẩu..."
        )
        submit_login = st.form_submit_button("🚀 Đăng Nhập Ngay")

        if submit_login:
          if not login_user or not login_pass:
            st.warning("Vui lòng nhập đầy đủ tên và mật khẩu!")
          elif (
              login_user in data["users"]
              and data["users"][login_user] == login_pass
          ):
            st.session_state.logged_in = True
            st.session_state.username = login_user
            st.success(f"Chào mừng trở lại, {login_user}!")
            st.rerun()
          else:
            st.error("Sai tên tài khoản hoặc mật khẩu!")

    # TAB ĐĂNG KÝ
    with auth_tab2:
      with st.form("register_form"):
        reg_user = st.text_input(
            "Chọn tên tài khoản", placeholder="Tên hiển thị của bạn..."
        )
        reg_pass = st.text_input(
            "Mật khẩu bảo mật",
            type="password",
            placeholder="Tạo mật khẩu...",
        )
        reg_pass_confirm = st.text_input(
            "Xác nhận mật khẩu", type="password", placeholder="Nhập lại mật khẩu..."
        )
        submit_reg = st.form_submit_button("✨ Đăng Ký Tài Khoản Mới")

        if submit_reg:
          if not reg_user or not reg_pass:
            st.warning("Vui lòng điền đầy đủ thông tin!")
          elif reg_user in data["users"]:
            st.error("Tên tài khoản này đã có người sử dụng. Hãy chọn tên khác!")
          elif reg_pass != reg_pass_confirm:
            st.error("Mật khẩu xác nhận không khớp!")
          else:
            data["users"][reg_user] = reg_pass
            if save_data(data):
              st.success(
                  "Đăng ký tài khoản thành công! Bây giờ bạn có thể chuyển qua"
                  " tab Đăng Nhập."
              )
            else:
              st.error("Lỗi đăng ký lên Cloud.")

  st.stop()  # Dừng code phía dưới nếu chưa đăng nhập

# --- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ---

# Thanh Sidebar hiển thị thông tin user & đăng xuất
with st.sidebar:
  st.markdown(f"### 👤 Xin chào, **{st.session_state.username}**!")
  st.success("🟢 Trạng thái: Đã kết nối Cloud")
  st.markdown("---")
  if st.button("🚪 Đăng Xuất Tài Khoản"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# Tiêu đề chính ứng dụng
st.title("⛺ KẾ HOẠCH DÃ NGOẠI & SÁT HẠCH TOÀN ĐỘI (24/11)")
st.markdown(
    """
> **Thông báo chính thức:** Ngày **24/11** tới đây anh em sẽ được nghỉ trọn vẹn nguyên ngày! Chúng ta sẽ tổ chức chuyến cắm trại dã ngoại kết hợp làm Vòng 2 sát hạch nhân sự mới. 
> Mọi thông tin bình chọn địa điểm, đề xuất và chuẩn bị vật dụng được đồng bộ thời gian thực trên toàn cầu.
"""
)
st.divider()

# Chia tab giao diện
tab1, tab2, tab3 = st.tabs(
    ["🗳️ Bình Chọn Địa Điểm", "📋 Danh Sách Đồ Cần Chuẩn Bị", "ℹ️ Hướng Dẫn"]
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
        data["locations"].append({
            "id": new_id,
            "name": new_loc_name,
            "desc": new_loc_desc or "Chưa có mô tả",
            "votes": 0,
            "voters": [],
        })
        if save_data(data):
          st.success(f"Đã thêm địa điểm '{new_loc_name}' thành công!")
          st.rerun()
      else:
        st.warning("Vui lòng nhập tên địa điểm!")

  st.markdown("### Danh sách các địa điểm hiện tại:")

  if not data["locations"]:
    st.info(
        "Chưa có địa điểm nào được thêm. Hãy là người đầu tiên đề xuất địa điểm"
        " bên trên!"
    )

  for idx, loc in enumerate(data["locations"]):
    loc_id = loc.get("id", str(idx))
    with st.container():
      col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
      with col1:
        st.markdown(f"**🔥 {loc['name']}**")
      with col2:
        st.text(loc["desc"])
      with col3:
        st.metric("Số phiếu", loc["votes"])
      with col4:
        if st.button("🗑️ Xóa", key=f"del_loc_btn_{loc_id}_{idx}"):
          data["locations"].pop(idx)
          if save_data(data):
            st.success("Đã xóa địa điểm thành công!")
            st.rerun()

      # Nút vote trực tiếp bằng tài khoản đang đăng nhập
      if st.button(
          f"👍 Bầu chọn cho {loc['name']}", key=f"vote_btn_{loc_id}_{idx}"
      ):
        if st.session_state.username not in loc["voters"]:
          loc["voters"].append(st.session_state.username)
          loc["votes"] = len(loc["voters"])
          if save_data(data):
            st.success(
                f"Cảm ơn {st.session_state.username} đã bỏ phiếu thành công!"
            )
            st.rerun()
        else:
          st.warning("Bạn đã bỏ phiếu cho địa điểm này rồi!")

      if loc["voters"]:
        st.caption(f"👤 Đã vote: {', '.join(loc['voters'])}")
      st.markdown("---")

# --- TAB 2: QUẢN LÝ VẬT DỤNG & YÊU CẦU ---
with tab2:
  st.subheader("🎒 Danh Sách
