import streamlit as st
import uuid
import json

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
