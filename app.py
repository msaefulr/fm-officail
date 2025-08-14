import streamlit as st
import plotly.express as px
from utils import init_db, get_conn, verify_password
from internal import fasilitas, keuangan, jadwal as int_jadwal, laporan

# --------------------------
# Page config
# --------------------------
st.set_page_config(page_title="Fityanul Musthofa", page_icon="🦐", layout="wide")

# --------------------------
# Style custom
# --------------------------
st.markdown("""
<style>
.card-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 20px;
    justify-content: center;
}
.card-responsive {
    flex: 1 1 100px;
    padding: 12px;
    text-align: center;
    border-radius: 10px;
    color: white;
    font-family: sans-serif;
}

/* Warna kartu */
.card-anggota { background: #198754; }
.card-event { background: #0d6efd; }
.card-pengumuman { background: #c9a227; }

/* Ukuran font di mobile */
@media (max-width: 480px) {
    .card-responsive h3 { font-size: 16px; margin: 2px 0; }
    .card-responsive p { font-size: 10px; margin: 0; }
}

/* Ukuran font di tablet */
@media (min-width: 481px) and (max-width: 768px) {
    .card-responsive h3 { font-size: 18px; margin: 3px 0; }
    .card-responsive p { font-size: 12px; margin: 0; }
}

/* Ukuran font desktop */
@media (min-width: 769px) {
    .card-responsive h3 { font-size: 24px; margin: 0; }
    .card-responsive p { font-size: 14px; margin: 3px 0 0 0; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Init DB
# --------------------------
init_db()

# --------------------------
# Fungsi login
# --------------------------
def login_box():
    st.sidebar.subheader("Login Anggota")
    if "auth" not in st.session_state:
        st.session_state.auth = None

    if st.session_state.auth:
        st.sidebar.success(f"Masuk sebagai {st.session_state.auth['username']} ({st.session_state.auth['role']})")
        if st.sidebar.button("Logout"):
            st.session_state.auth = None
            st.rerun()
        return True

    with st.sidebar.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        sub = st.form_submit_button("Login")
        if sub and u and p:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id,username,password_hash,role FROM users WHERE username=?", (u,))
            row = cur.fetchone()
            conn.close()

            if row and verify_password(p, row["password_hash"]):
                st.session_state.auth = {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"]
                }
                st.sidebar.success("Login berhasil.")
                st.rerun()
            else:
                st.sidebar.error("Username atau password salah.")
    return False

# --------------------------
# Main internal
# --------------------------
_ = login_box()

if not st.session_state.get("auth"):
    # Halaman sebelum login
    st.title("FM Official")
    st.markdown("""
    Selamat datang di Sistem Hadroh!  
    Silakan login untuk mengakses panel internal.

    Sistem ini digunakan untuk:
    - Manajemen fasilitas
    - Keuangan
    - Jadwal kegiatan
    - Laporan kegiatan
    """)
    st.info("Silakan login untuk mengakses sistem.")

else:
    # Menu internal
    menu = ["Dashboard", "Fasilitas", "Keuangan", "Jadwal", "Laporan"]
    page = st.sidebar.radio("Menu Sistem", menu)

    if page == "Dashboard":
        st.markdown("<br>", unsafe_allow_html=True)
        st.title("DASHBOARD")
        st.write(f"Halo, **{st.session_state.auth['username']}** 👋 Selamat datang di panel internal.")

        # --- Card Statistik Responsive ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card-container">
            <div class="card-responsive card-anggota">
                <h3>20</h3>
                <p>Anggota</p>
            </div>
            <div class="card-responsive card-event">
                <h3>8</h3>
                <p>Event</p>
            </div>
            <div class="card-responsive card-pengumuman">
                <h3>3</h3>
                <p>Pengumuman</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Statistik Kegiatan Mingguan")

        # --- Bar chart ---
        df_bar = {
            "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
            "Event": [3, 5, 2, 4],
            "Anggota": [10, 15, 20, 25]
        }
        fig_bar = px.bar(df_bar, x="Minggu", y=["Event", "Anggota"], barmode="group",
                         title="Jumlah Event & Anggota per Minggu")
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Line chart ---
        st.subheader("Tren Kehadiran Anggota")
        df_line = {
            "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
            "Hadir": [8, 12, 15, 20]
        }
        fig_line = px.line(df_line, x="Minggu", y="Hadir", markers=True,
                           title="Tren Kehadiran Anggota")
        st.plotly_chart(fig_line, use_container_width=True)

    elif page == "Fasilitas":
        fasilitas.page()
    elif page == "Keuangan":
        keuangan.page()
    elif page == "Jadwal":
        int_jadwal.page()
    elif page == "Laporan":
        laporan.page()
