import streamlit as st
import uuid
import json
import json
import requests
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Sát Hạch & Cắm Trại 24/11 - Đội",
    page_icon="⛺",
    layout="wide",
)

# Đã cấu hình sẵn Bin ID của anh để tự động đồng bộ trực tuyến
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
      return response.json()
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
if not data:
  data = {"locations": [], "requirements": []}

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

  # Form thêm địa điểm mới
  with st.form("add_loc_form", clear_on_submit=True):
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
    with st.container():
      col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
      with col1:
        st.markdown(f"**🔥 {loc['name']}**")
      with col2:
        st.text(loc["desc"])
      with col3:
        st.metric("Số phiếu", loc["votes"])
      with col4:
        if st.button("🗑️ Xóa", key=f"del_loc_{loc['id']}"):
          data["locations"].pop(idx)
          if save_data(data):
            st.success("Đã xóa địa điểm thành công!")
            st.rerun()

      voter_name = st.text_input(
          f"Tên của bạn để vote cho '{loc['name']}'",
          key=f"voter_name_{loc['id']}",
          placeholder="Nhập tên bạn...",
      )
      if st.button(f"👍 Bầu chọn cho {loc['name']}", key=f"vote_{loc['id']}"):
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

  with st.form("add_req_form", clear_on_submit=True):
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
  for idx, req in enumerate(data["requirements"]):
    col_r1, col_r2, col_r3 = st.columns([5, 3, 2])
    with col_r1:
      done_status = st.checkbox(
          f"**{req['task']}**",
          value=req["done"],
          key=f"req_check_{idx}",
      )
      if done_status != req["done"]:
        data["requirements"][idx]["done"] = done_status
        save_data(data)
    with col_r2:
      st.text(f"👤 Phụ trách: {req['assigned']}")
    with col_r3:
      if st.button("🗑️ Xóa", key=f"del_req_{idx}"):
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
st.set_page_config(
    page_title="Hệ Thống Sát Hạch & Cắm Trại 24/11",
    page_icon="⛺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for modern dark theme aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #090d16;
        color: #f1f5f9;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input {
        background-color: #0f172a;
        color: #f1f5f9;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if "locations" not in st.session_state:
    st.session_state.locations = [
        {"id": "loc_1", "name": "Hồ Trị An", "desc": "Cách TP.HCM 65km, view hồ cực chill ngắm hoàng hôn", "votes": 2, "voters": []},
        {"id": "loc_2", "name": "Khu du lịch Suối Mơ", "desc": "Nước suối tự nhiên trong vắt, rộng rãi thoải mái", "votes": 1, "voters": []}
    ]

if "requirements" not in st.session_state:
    st.session_state.requirements = [
        {"id": "req_1", "text": "Lều trại lớn (6-8 người) + Tấm cách nhiệt", "category": "gear", "completed": True},
        {"id": "req_2", "text": "Thịt bò ướp, xúc xích và đồ nướng 3kg", "category": "food", "completed": False},
        {"id": "req_3", "text": "Thành viên mới phải có mặt đúng giờ xuất phát (06:00)", "category": "rules", "completed": True}
    ]

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Header Title
st.title("⛺ Hệ Thống Sát Hạch & Cắm Trại Toàn Đội (24/11)")
st.markdown("---")

# Official Announcement Banner
st.info("📢 **THÔNG BÁO CHÍNH THỨC:** Ngày **24/11** tới đây anh em sẽ được nghỉ trọn vẹn nguyên ngày! Chúng ta sẽ tổ chức chuyến cắm trại dã ngoại kết hợp làm Vòng 2 sát hạch nhân sự mới. Mọi đề xuất địa điểm, bình chọn và chuẩn bị vật dụng được cập nhật trực tiếp tại đây.")

# Tabs Layout
tab1, tab2, tab3 = st.tabs(["📍 Bình Chọn Địa Điểm", "📋 Danh Sách Yêu Cầu & Vật Dụng", "🚀 Hướng Dẫn GitHub & Deploy"])

with tab1:
    st.subheader("Bình Chọn Địa Điểm Cắm Trại (24/11)")
    st.write("Đề xuất địa điểm mới hoặc bình chọn cho địa điểm anh em muốn đi nhất.")
    
    # Add Location Form
    with st.form("add_location_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 3])
        with col1:
            new_loc_name = st.text_input("Tên địa điểm (VD: Núi Chứa Chan, Vườn Quốc Gia Cát Tiên)")
        with col2:
            new_loc_desc = st.text_input("Mô tả / Khoảng cách / Tiện ích")
        submitted_loc = st.form_submit_button("➕ Thêm Địa Điểm Mới")
        if submitted_loc:
            if new_loc_name and new_loc_desc:
                new_id = "loc_" + str(uuid.uuid4())[:8]
                st.session_state.locations.append({
                    "id": new_id,
                    "name": new_loc_name,
                    "desc": new_loc_desc,
                    "votes": 1,
                    "voters": [st.session_state.user_id]
                })
                st.success(f"Đã thêm địa điểm '{new_loc_name}' thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng điền đầy đủ tên và mô tả địa điểm!")

    st.markdown("### Danh Sách Địa Điểm Đề Xuất")
    if not st.session_state.locations:
        st.info("Chưa có địa điểm nào được đề xuất.")
    else:
        max_votes = max([l["votes"] for l in st.session_state.locations], default=0)
        
        for loc in st.session_state.locations:
            is_leading = (loc["votes"] == max_votes and max_votes > 0)
            has_voted = st.session_state.user_id in loc.get("voters", [])
            
            with st.container():
                col_info, col_btn, col_del = st.columns([4, 2, 1])
                with col_info:
                    badge = " 👑 **[DẪN ĐẦU]**" if is_leading else ""
                    st.markdown(f"**{loc['name']}**{badge}\n\n*{loc['desc']}*\n\n🔥 **{loc['votes']} phiếu bình chọn**")
                with col_btn:
                    btn_label = "✅ Đã bình chọn" if has_voted else "👍 Bình chọn"
                    if st.button(btn_label, key=f"vote_{loc['id']}"):
                        if has_voted:
                            loc["voters"].remove(st.session_state.user_id)
                            loc["votes"] = max(0, loc["votes"] - 1)
                        else:
                            loc.setdefault("voters", []).append(st.session_state.user_id)
                            loc["votes"] += 1
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Xóa", key=f"del_loc_{loc['id']}"):
                        st.session_state.locations = [l for l in st.session_state.locations if l["id"] != loc["id"]]
                        st.success("Đã xóa địa điểm.")
                        st.rerun()
                st.divider()

with tab2:
    st.subheader("Danh Sách Yêu Cầu & Phân Công Vật Dụng")
    
    filter_cat = st.selectbox("Lọc theo danh mục", ["Tất cả", "Dụng cụ (gear)", "Thực phẩm (food)", "Nội quy (rules)"])
    
    # Add Requirement Form
    with st.form("add_req_form", clear_on_submit=True):
        col_r1, col_r2 = st.columns([3, 2])
        with col_r1:
            req_text = st.text_input("Nội dung vật dụng / Yêu cầu / Ghi chú")
        with col_r2:
            req_cat = st.selectbox("Phân loại", ["gear", "food", "rules"], format_func=lambda x: {"gear": "⛺ Dụng cụ", "food": "🍖 Thực phẩm", "rules": "📜 Nội quy"}[x])
        submitted_req = st.form_submit_button("➕ Thêm Yêu Cầu Mới")
        if submitted_req:
            if req_text:
                new_req_id = "req_" + str(uuid.uuid4())[:8]
                st.session_state.requirements.append({
                    "id": new_req_id,
                    "text": req_text,
                    "category": req_cat,
                    "completed": False
                })
                st.success("Đã thêm yêu cầu mới thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập nội dung yêu cầu!")

    st.markdown("### Danh Sách Cần Chuẩn Bị")
    for req in st.session_state.requirements:
        if filter_cat != "Tất cả":
            cat_code = filter_cat.split("(")[1].replace(")", "").strip()
            if req["category"] != cat_code:
                continue
        
        col_chk, col_txt, col_del = st.columns([0.5, 4.5, 1])
        with col_chk:
            is_completed = st.checkbox("", value=req["completed"], key=f"chk_{req['id']}")
            if is_completed != req["completed"]:
                req["completed"] = is_completed
                st.rerun()
        with col_txt:
            cat_labels = {"gear": "⛺ Dụng cụ", "food": "🍖 Thực phẩm", "rules": "📜 Nội quy"}
            st.markdown(f"~~{req['text']}~~" if req["completed"] else f"**{req['text']}** `[{cat_labels.get(req['category'], 'Khác')}]`")
        with col_del:
            if st.button("🗑️", key=f"del_req_{req['id']}"):
                st.session_state.requirements = [r for r in st.session_state.requirements if r["id"] != req["id"]]
                st.rerun()

with tab3:
    st.subheader("🚀 Hướng Dẫn Đưa Lên GitHub & Triển Khai Streamlit Cloud")
    st.markdown("""
    Để đưa ứng dụng này lên GitHub và xuất bản thành một trang web online hoàn toàn miễn phí cho anh em truy cập, hãy thực hiện các bước sau:

    ### Bước 1: Tạo Repository trên GitHub
    1. Đăng ký/Đăng nhập vào [GitHub](https://github.com).
    2. Tạo một **Repository mới** (ví dụ đặt tên: `camping-24-11`, để chế độ *Public*).
    3. Tạo file `app.py` trên GitHub và dán toàn bộ mã nguồn python ở trên vào.
    4. Tạo thêm một file tên là `requirements.txt` trong repository đó với nội dung duy nhất:
       ```text
       streamlit
       ```

    ### Bước 2: Đưa lên Streamlit Community Cloud (Miễn phí)
    1. Truy cập [share.streamlit.io](https://share.streamlit.io) và đăng nhập bằng tài khoản GitHub của bạn.
    2. Bấm vào nút **New app**.
    3. Chọn Repository vừa tạo (`camping-24-11`), branch `main`, và đường dẫn file chính là `app.py`.
    4. Bấm **Deploy!**

    Sau khoảng 1 phút, Streamlit sẽ cung cấp cho bạn một đường link web chính thức (ví dụ: `https://camping-24-11.streamlit.app`). Bạn chỉ cần copy link đó gửi vào group cho anh em truy cập, bình chọn địa điểm và thêm vật dụng trực tuyến cực kỳ mượt mà!
    """)
