import hashlib
import requests
import streamlit as st

st.set_page_config(
    page_title="Dã Ngoại & Sát Hạch 24/11",
    page_icon="⛺",
    layout="centered",
)

# Sử dụng JSONBlob làm máy chủ lưu trữ đám mây ổn định cho Streamlit
BLOB_ID = "1306249854114570240"
API_URL = f"https://jsonblob.com{BLOB_ID}"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .card-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .hero-box {
        background: linear-gradient(135deg, #059669 0%, #2563eb 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        color: white;
    }
    .badge {
        display: inline-block;
        background-color: #0f172a;
        color: #38bdf8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def make_hash(text):
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def fetch_cloud_data():
    default_data = {"users": {}, "locations": [], "requirements": []}
    try:
        res = requests.get(API_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            raw = res.json()
            if isinstance(raw, dict):
                default_data["users"] = raw.get("users", {})
                default_data["locations"] = raw.get("locations", [])
                default_data["requirements"] = raw.get("requirements", [])
    except Exception:
        pass
    return default_data


def push_cloud_data(payload):
    try:
        res = requests.put(API_URL, json=payload, headers=HEADERS, timeout=10)
        if res.status_code in
                return True
        st.error(f"Lỗi máy chủ (Mã {res.status_code}): {res.text}")
        return False
    except Exception as e:
        st.error(f"Lỗi kết nối mạng: {e}")
        return False


if "user" not in st.session_state:
    st.session_state.user = None

db = fetch_cloud_data()

# ==========================================
# GIAO DIỆN 1: ĐĂNG NHẬP & ĐĂNG KÝ
# ==========================================
if st.session_state.user is None:
    st.markdown(
        """
        <div class="hero-box" style="text-align: center;">
            <h2 style="margin:0;">⛺ CỔNG THÀNH VIÊN ĐỘI</h2>
            <p style="margin:8px 0 0 0; opacity: 0.9;">
                Đăng nhập hoặc tạo tài khoản mới để tham gia kế hoạch 24/11
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_in, tab_up = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Lần Đầu"])

    with tab_in:
        with st.form("form_login"):
            u_name = st.text_input("Tên của bạn", placeholder="Nhập tên đã đăng ký...").strip()
            u_pass = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            submit_in = st.form_submit_button("🚀 Vào Ứng Dụng", use_container_width=True)

            if submit_in:
                if not u_name or not u_pass:
                    st.warning("Vui lòng nhập đầy đủ tên và mật khẩu.")
                elif u_name not in db["users"]:
                    st.error("Tài khoản chưa tồn tại. Hãy qua tab Đăng Ký Lần Đầu nhé!")
                elif db["users"][u_name] != make_hash(u_pass):
                    st.error("Sai mật khẩu rồi!")
                else:
                    st.session_state.user = u_name
                    st.rerun()

    with tab_up:
        with st.form("form_register"):
            new_name = st.text_input("Tên hiển thị của bạn", placeholder="Ví dụ: Huy Đỗ...").strip()
            new_pass = st.text_input("Tạo mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            re_pass = st.text_input("Nhập lại mật khẩu", type="password", placeholder="Xác nhận mật khẩu...")
            submit_up = st.form_submit_button("✅ Đăng Ký & Lưu Online", use_container_width=True)

            if submit_up:
                if not new_name or not new_pass:
                    st.warning("Không được để trống tên hoặc mật khẩu.")
                elif new_pass != re_pass:
                    st.error("Hai mật khẩu chưa khớp nhau.")
                elif new_name in db["users"]:
                    st.error("Tên này đã có người dùng. Bạn hãy thêm tên đệm hoặc đăng nhập nhé!")
                else:
                    db["users"][new_name] = make_hash(new_pass)
                    if push_cloud_data(db):
                        st.session_state.user = new_name
                        st.success("Đăng ký thành công!")
                        st.rerun()

# ==========================================
# GIAO DIỆN 2: TRANG CHÍNH SAU KHI VÀO
# ==========================================
else:
    me = st.session_state.user

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"🟢 Xin chào, **{me}**!")
    with c2:
        if st.button("Đăng xuất", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.markdown(
        """
        <div class="hero-box">
            <h2 style="margin:0;">⛺ DÃ NGOẠI & SÁT HẠCH ĐỘI (24/11)</h2>
            <p style="margin:8px 0 0 0; font-size:15px;">
                Ngày <b>24/11</b> anh em nghỉ trọn vẹn nguyên ngày để đi cắm trại kết hợp Vòng 2 sát hạch nhân sự mới.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["🗳️ Bình Chọn Địa Điểm", "🎒 Đồ Cần Chuẩn Bị", "👥 Thành Viên"])

    # --- TAB 1: ĐỊA ĐIỂM ---
    with t1:
        with st.expander("➕ Đề xuất thêm địa điểm mới", expanded=False):
            with st.form("add_loc", clear_on_submit=True):
                loc_title = st.text_input("Tên địa điểm", placeholder="Ví dụ: Hồ Trị An, Núi Chứa Chan...")
                loc_note = st.text_input("Ghi chú / Khoảng cách", placeholder="Cách trung tâm bao xa, cảnh đẹp...")
                if st.form_submit_button("Lưu Địa Điểm", use_container_width=True):
                    if loc_title.strip():
                        db["locations"].append(
                            {
                                "name": loc_title.strip(),
                                "desc": loc_note.strip() or "Chưa có mô tả",
                                "voters": [me],
                                "by": me,
                            }
                        )
                        if push_cloud_data(db):
                            st.rerun()
                    else:
                        st.warning("Bạn chưa nhập tên địa điểm.")

        if not db["locations"]:
            st.info("Chưa có địa điểm nào. Bấm vào mục 'Đề xuất thêm địa điểm mới' ở trên để tạo nhé!")

        for i, item in enumerate(db["locations"]):
            voters = item.get("voters", [])
            voted = me in voters

            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="margin:0 0 6px 0; color:#34d399;">📍 {item['name']}</h4>
                    <p style="margin:0 0 8px 0; color:#cbd5e1; font-size:14px;">{item.get('desc', '')}</p>
                    <span class="badge">🔥 {len(voters)} phiếu bầu</span>
                    <p style="margin:8px 0 0 0; font-size:13px; color:#94a3b8;">
                        <b>Đã chọn:</b> {', '.join(voters) if voters else 'Chưa có ai'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            b1, b2 = st.columns([3, 1])
            with b1:
                label = "✅ Đã Vote (Bấm để hủy)" if voted else "👍 Bầu Chọn Địa Điểm Này"
                if st.button(label, key=f"v_{i}", use_container_width=True):
                    if voted:
                        voters.remove(me)
                    else:
                        voters.append(me)
                    item["voters"] = voters
                    if push_cloud_data(db):
                        st.rerun()
            with b2:
                if st.button("🗑️ Xóa", key=f"del_l_{i}", use_container_width=True):
                    db["locations"].pop(i)
                    if push_cloud_data(db):
                        st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

    # --- TAB 2: ĐỒ DÙNG ---
    with t2:
        with st.form("add_req", clear_on_submit=True):
            task_name = st.text_input("Món đồ / Công việc cần chuẩn bị", placeholder="Ví dụ: Lều trại, than nướng, nước suối...")
            person = st.text_input("Người phụ trách", value=me)
            if st.form_submit_button("➕ Thêm Vào Danh Sách", use_container_width=True):
                if task_name.strip():
                    db["requirements"].append(
                        {
                            "task": task_name.strip(),
                            "assigned": person.strip() or "Chưa phân công",
                            "done": False,
                        }
                    )
                    if push_cloud_data(db):
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập tên món đồ.")

        st.divider()
        if not db["requirements"]:
            st.info("Danh sách đồ cần chuẩn bị đang trống.")

        for i, req in enumerate(db["requirements"]):
            rc1, rc2 = st.columns([4, 1])
            with rc1:
                checked = st.checkbox(
                    f"**{req['task']}** — *(Phụ trách: {req['assigned']})*",
