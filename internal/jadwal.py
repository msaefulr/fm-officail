import streamlit as st, pandas as pd
from datetime import date
from utils import get_conn
def page():
    st.header("Kelola Jadwal Tampil")
    with st.form("add_jadwal", clear_on_submit=True):
        c = st.columns(4)
        tanggal = c[0].date_input("Tanggal", value=date.today())
        acara = c[1].text_input("Acara")
        lokasi = c[2].text_input("Lokasi")
        status = c[3].selectbox("Status", ["kosong","terisi"], index=1)
        sub = st.form_submit_button("Simpan")
        if sub:
            conn = get_conn(); cur = conn.cursor(); cur.execute("SELECT id FROM jadwal WHERE tanggal=?", (str(tanggal),))
            row = cur.fetchone()
            if row:
                conn.execute("UPDATE jadwal SET acara=?,lokasi=?,status=? WHERE id=?", (acara,lokasi,status,row['id']))
            else:
                conn.execute("INSERT INTO jadwal(tanggal,acara,lokasi,status) VALUES (?,?,?,?)", (str(tanggal),acara,lokasi,status))
            conn.commit(); conn.close(); st.success("Jadwal tersimpan.")
    conn = get_conn(); df = pd.read_sql_query("SELECT * FROM jadwal ORDER BY tanggal ASC", conn); conn.close()
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        sel = st.selectbox("Pilih ID", df['id'].tolist())
        row = df[df['id']==sel].iloc[0]
        with st.form("edit_jadwal"):
            tanggal = st.date_input("Tanggal", value=pd.to_datetime(row['tanggal']).date())
            acara = st.text_input("Acara", value=row['acara'] or "")
            lokasi = st.text_input("Lokasi", value=row['lokasi'] or "")
            status = st.selectbox("Status", ["kosong","terisi"], index=0 if row['status']=="kosong" else 1)
            save = st.form_submit_button("Simpan"); delete = st.form_submit_button("Hapus")
            if save:
                conn = get_conn(); conn.execute("UPDATE jadwal SET tanggal=?,acara=?,lokasi=?,status=? WHERE id=?",
                                                (str(tanggal),acara,lokasi,status,int(row['id']))); conn.commit(); conn.close(); st.success("Perubahan tersimpan.")
            if delete:
                conn = get_conn(); conn.execute("DELETE FROM jadwal WHERE id=?", (int(row['id']),)); conn.commit(); conn.close(); st.warning("Data dihapus.")