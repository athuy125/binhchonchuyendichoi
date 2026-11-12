import json
import requests
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Sát Hạch & Cắm Trại 24/11 - Đội",
    page_icon="⛺",
    layout="wide",
)

# Bin ID của npoint.io đã được cấu hình sẵn
BIN_ID = "89fea106b426901294dd"

# Giao diện CSS tùy chỉnh Dark Mode chuyên nghiệp
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .card { background: #1f2937; padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #374151; }
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
            "locations": res_data.get("locations", []),
            "requirements": res_data.get("requirements", []),
        }
  except Exception as e:
    st.error(f"Lỗi kết nối Cloud: {e}")
  return {"locations": [], "requirements": []}


# Hàm lưu dữ liệu lên Cloud
def save_data(data):
  try:
    url = f"https://api.npoint.io/{BIN_ID}"
    response = requests.put(url, json=data, timeout=5)
    return response.status_code == 200
  except Exception as e:
    st.error(f"Không thể lưu lên Cloud: {e}")
    return False


# Khởi tạo dữ liệu
data = load_data()

# --- TIÊU ĐỀ CHÍNH ---
st.title("⛺ KẾ HOẠCH DÃ NGOẠI & SÁT HẠCH TOÀN ĐỘI (24/11)")
st.markdown(
    """
> **Thông báo chính thức:** Ngày **24/11** tới đây anh em sẽ được nghỉ trọn vẹn nguyên ngày! Chúng ta sẽ tổ chức chuyến cắm trại dã ngoại kết hợp làm Vòng 2 sát hạch nhân sự mới. 
> Mọi thông tin bình chọn địa điểm, đề xuất và chuẩn bị vật dụng sẽ được cập nhật đồng bộ trực tuyến tại đây.
"""
)

st.success(
    "🟢 **Đã kết nối Database Cloud thành công!** Mọi người truy cập link là"
    " đồng bộ thời gian thực."
)
st.divider()

# Chia tab giao diện
tab1, tab2, tab3 = st.tabs(
    ["🗳️ Bình Chọn Địa Điểm", "📋 Danh Sách Đồ Cần Chuẩn Bị", "ℹ️ Hướng Dẫn"]
)

# --- TAB 1: BÌNH CHỌN ĐỊA ĐIỂM ---
with tab1:
  st.subheader("📍 Đề Xuất & Bình Chọn Địa Điểm Cắm Trại")

  # Form thêm địa điểm mới (dùng key riêng biệt)
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

      voter_name = st.text_input(
          f"Tên của bạn để vote cho '{loc['name']}'",
          key=f"voter_input_{loc_id}_{idx}",
          placeholder="Nhập tên bạn...",
      )
      if st.button(f"👍 Bầu chọn cho {loc['name']}", key=f"vote_btn_{loc_id}_{idx}"):
        if voter_name:
          if voter_name not in loc["voters"]:
            loc["voters"].append(voter_name)
            loc["votes"] = len(loc["voters"])
            if save_data(data):
              st.success(f"Cảm ơn {voter_name} đã bỏ phiếu thành công!")
              st.rerun()
            else:
              st.error("Lỗi khi lưu phiếu bầu lên Cloud.")
          else:
            st.warning("Bạn đã bỏ phiếu cho địa điểm này rồi!")
        else:
          st.warning("Vui lòng nhập tên của bạn trước khi bấm vote!")

      if loc["voters"]:
        st.caption(
            f"👤 Đã vote: {', '.join(loc['voters']) if isinstance(loc['voters'], list) else loc['voters']}"
        )
      st.markdown("---")

# --- TAB 2: QUẢN LÝ VẬT DỤNG & YÊU CẦU ---
with tab2:
  st.subheader("🎒 Danh Sách Đồ Cần Mang & Phân Công")

  # Form thêm yêu cầu (dùng key riêng biệt tránh trùng lặp)
  with st.form("form_add_requirement_unique", clear_on_submit=True):
    r_col1, r_col2 = st.columns([3, 2])
    with r_col1:
      new_task = st.text_input(
          "Đồ dùng / Yêu cầu cần chuẩn bị", placeholder="Ví dụ: 5 thùng nước suối..."
      )
    with r_col2:
      new_assigned = st.text_input("Người nhận lo", placeholder="Tên anh em...")
    sub_req = st.form_submit_button("➕ Thêm Yêu Cầu")

    if sub_req:
      if new_task:
        data["requirements"].append({
            "task": new_task,
            "assigned": new_assigned or "Chưa phân công",
            "done": False,
        })
        if save_data(data):
          st.success("Đã thêm yêu cầu thành công!")
          st.rerun()
        else:
          st.error("Lỗi lưu dữ liệu lên Cloud.")
      else:
        st.warning("Vui lòng nhập nội dung vật dụng!")

  st.markdown("### Danh sách đồ dùng:")
  if not data["requirements"]:
    st.info("Chưa có đồ dùng nào được thêm.")

  for idx, req in enumerate(data["requirements"]):
    col_r1, col_r2, col_r3 = st.columns([5, 3, 2])
    with col_r1:
      done_status = st.checkbox(
          f"**{req['task']}**",
          value=req["done"],
          key=f"req_check_box_{idx}",
      )
      if done_status != req["done"]:
        data["requirements"][idx]["done"] = done_status
        save_data(data)
    with col_r2:
      st.text(f"👤 Phụ trách: {req['assigned']}")
    with col_r3:
      if st.button("🗑️ Xóa", key=f"del_req_btn_{idx}"):
        data["requirements"].pop(idx)
        if save_data(data):
          st.success("Đã xóa yêu cầu!")
          st.rerun()

# --- TAB 3: HƯỚNG DẪN ---
with tab3:
  st.subheader("🔗 Hướng Dẫn Gửi Link Cho Đội")
  st.markdown(
      """
  1. Copy đường link ứng dụng trên trình duyệt và gửi vào group chat của anh em.
  2. Mọi thao tác thêm địa điểm, vote hoặc phân công vật dụng đều được lưu trực tiếp vào cơ sở dữ liệu chung và tự động cập nhật thời gian thực trên mọi thiết bị!
  """
  )
