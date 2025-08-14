import streamlit as st
import pandas as pd
import math
from utils import get_conn, save_upload
from PIL import Image
import io
import base64

# ------------------ Fungsi Thumbnail ------------------
def image_to_bytes(file_path, size=(40,40)):
    if not file_path:
        return None
    try:
        img = Image.open(file_path)
        img.thumbnail(size)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except:
        return None

# ------------------ CSS Dark Mode + Responsive ------------------
st.markdown("""
<style>
.row-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    margin-bottom: 2px;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.1);
    flex-wrap: wrap;
    transition: background-color 0.2s;
}
.row-container:hover {
    background-color: rgba(255,255,255,0.05);
}
button, input, select {
    background-color: #1E222A !important;
    color: #E0E0E0 !important;
    border-radius: 4px;
    border: 1px solid #3A3F4B !important;
    padding: 2px 6px;
}
.stApp {
    background-color: #0E1117;
    color: #E0E0E0;
}
@media (max-width:480px){ .row-container { flex-direction: row !important; justify-content: space-between !important; } }
@media (min-width:481px) and (max-width:1024px){ .row-container { flex-direction: row !important; flex-wrap: wrap; } .row-actions { margin-top: 4px; } }
@media (min-width:1025px){ .row-container { flex-direction: row !important; flex-wrap: nowrap; } }
</style>
""", unsafe_allow_html=True)

# ------------------ Halaman ------------------
def page():
    st.title("Kelola Fasilitas")

    if 'page' not in st.session_state: st.session_state.page = 1
    if 'data_hash' not in st.session_state: st.session_state.data_hash = 0
    if 'edit_row' not in st.session_state: st.session_state.edit_row = None
    if '_rerun' not in st.session_state: st.session_state._rerun = False

    # ------------------ Form Tambah Fasilitas ------------------
    with st.expander("Tambah", expanded=True):
        with st.form("add_fac", clear_on_submit=True):
            cols = st.columns([2,2,1,2,2])
            nama = cols[0].text_input("Nama Fasilitas")
            kategori = cols[1].text_input("Kategori")
            kondisi = cols[2].selectbox("Kondisi", ["baik","butuh_perbaikan","rusak"])
            lokasi = cols[3].text_input("Lokasi")
            foto = cols[4].file_uploader("Foto", type=["jpg","jpeg","png","webp"])
            submit = st.form_submit_button("Tambah")
            if submit and nama:
                foto_path = save_upload(foto, "fasilitas") if foto else None
                conn = get_conn()
                conn.execute(
                    "INSERT INTO fasilitas(nama,kategori,kondisi,lokasi,foto) VALUES (?,?,?,?,?)",
                    (nama, kategori, kondisi, lokasi, foto_path)
                )
                conn.commit()
                conn.close()
                st.success("Fasilitas ditambahkan.")
                st.session_state.data_hash += 1
                st.session_state._rerun = not st.session_state._rerun

    # ------------------ Ambil Data ------------------
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM fasilitas ORDER BY id DESC", conn)
    conn.close()
    if df.empty: st.info("Belum ada data fasilitas."); return

    # ------------------ Filter ------------------
    filter_kategori = st.selectbox("Filter kategori", ["Semua"] + sorted(df['kategori'].dropna().unique().tolist()))
    if filter_kategori != "Semua": df = df[df['kategori'] == filter_kategori]

    # ------------------ Pagination ------------------
    per_page = 6
    total_pages = math.ceil(len(df)/per_page)
    col1,col2,col3 = st.columns([1,2,1])
    with col1: 
        if st.button("⬅️ Prev") and st.session_state.page>1: st.session_state.page-=1
    with col3: 
        if st.button("Next ➡️") and st.session_state.page<total_pages: st.session_state.page+=1
    start_idx = (st.session_state.page-1)*per_page
    end_idx = start_idx + per_page
    df_page = df.iloc[start_idx:end_idx].copy()
    df_page['Thumb'] = df_page['foto'].apply(image_to_bytes)

    # ------------------ Header ------------------
    st.markdown("### Daftar Fasilitas")
    cols_header = st.columns([0.1,0.4,0.25,0.25])
    cols_header[0].markdown("**Foto**"); cols_header[1].markdown("**Nama**")
    cols_header[2].markdown("**Detail**"); cols_header[3].markdown("**Hapus**")

    # ------------------ Loop Data ------------------
    for idx,row in df_page.iterrows():
        with st.container():
            st.markdown('<div class="row-container">', unsafe_allow_html=True)
            cols = st.columns([0.1,0.4,0.25,0.25])
            cols[0].image(row['Thumb'] or "", width=40)
            cols[1].markdown(f"**{row['nama']}**")
            # Tombol detail (popup)
            if cols[2].button("✏️ Edit", key=f"edit_{row['id']}"):
                st.session_state.edit_row=row['id']
                st.session_state._rerun = not st.session_state._rerun
            # Tombol delete
            if cols[3].button("🗑️", key=f"del_{row['id']}"):
                conn = get_conn()
                conn.execute("DELETE FROM fasilitas WHERE id=?",(row['id'],))
                conn.commit()
                conn.close()
                st.warning("Data dihapus.")
                st.session_state.data_hash+=1
                st.session_state._rerun = not st.session_state._rerun
            st.markdown("</div>", unsafe_allow_html=True)

        # ------------------ Popup Edit ------------------
        if st.session_state.edit_row==row['id']:
            with st.expander(f"Edit Fasilitas: {row['nama']}", expanded=True):
                nama_val = st.text_input("Nama", value=row['nama'], key=f"edit_nama_{row['id']}")
                kat_val = st.text_input("Kategori", value=row['kategori'] or "", key=f"edit_kat_{row['id']}")
                kond_val = st.selectbox("Kondisi", ["baik","butuh_perbaikan","rusak"], index=["baik","butuh_perbaikan","rusak"].index(row['kondisi'] or "baik"), key=f"edit_kond_{row['id']}")
                lok_val = st.text_input("Lokasi", value=row['lokasi'] or "", key=f"edit_lok_{row['id']}")
                # Ganti Foto
                uploaded_foto = st.file_uploader("Pilih foto baru", type=["jpg","jpeg","png","webp"], key=f"foto_upload_{row['id']}")
                if uploaded_foto and st.button("💾 Simpan Foto", key=f"save_foto_{row['id']}"):
                    foto_path = save_upload(uploaded_foto,"fasilitas")
                    conn = get_conn()
                    conn.execute("UPDATE fasilitas SET foto=? WHERE id=?",(foto_path,row['id']))
                    conn.commit(); conn.close()
                    st.success("Foto diperbarui.")
                    st.session_state.data_hash+=1
                    st.session_state.edit_row=None
                    st.session_state._rerun = not st.session_state._rerun
                # Simpan detail
                if st.button("💾 Simpan Perubahan", key=f"save_edit_{row['id']}"):
                    conn = get_conn()
                    conn.execute("UPDATE fasilitas SET nama=?, kategori=?, kondisi=?, lokasi=? WHERE id=?",
                                 (nama_val, kat_val, kond_val, lok_val, row['id']))
                    conn.commit(); conn.close()
                    st.success("Perubahan tersimpan.")
                    st.session_state.data_hash+=1
                    st.session_state.edit_row=None
                    st.session_state._rerun = not st.session_state._rerun

    st.write(f"Halaman {st.session_state.page} dari {total_pages}")
