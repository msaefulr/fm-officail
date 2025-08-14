import streamlit as st, pandas as pd
from datetime import date
from utils import get_conn, save_upload, format_rp
def page():
    st.header("Kelola Keuangan")
    with st.form("add_ledger", clear_on_submit=True):
        c = st.columns(4)
        tipe = c[0].selectbox("Tipe", ["pemasukan","pengeluaran"])
        kategori = c[1].text_input("Kategori")
        jumlah = c[2].number_input("Jumlah (Rp)", min_value=0.0, step=10000.0)
        tanggal = c[3].date_input("Tanggal", value=date.today())
        ket = st.text_input("Keterangan")
        bukti = st.file_uploader("Bukti (opsional)", type=["jpg","jpeg","png","webp","pdf"])
        sub = st.form_submit_button("Simpan")
        if sub and jumlah>0:
            bukti_path = save_upload(bukti, "bukti") if bukti else None
            conn = get_conn(); conn.execute("INSERT INTO keuangan(tipe,kategori,jumlah,tanggal,keterangan,bukti) VALUES (?,?,?,?,?,?)",
                                            (tipe,kategori,jumlah,str(tanggal),ket,bukti_path)); conn.commit(); conn.close()
            st.success("Transaksi disimpan.")
    conn = get_conn(); df = pd.read_sql_query("SELECT * FROM keuangan ORDER BY tanggal DESC, id DESC", conn); conn.close()
    if not df.empty:
        st.metric("Total Pemasukan", format_rp(df[df.tipe=='pemasukan']['jumlah'].sum()))
        st.metric("Total Pengeluaran", format_rp(df[df.tipe=='pengeluaran']['jumlah'].sum()))
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        sel = st.selectbox("Pilih ID", df['id'].tolist())
        row = df[df['id']==sel].iloc[0]
        with st.form("edit_ledger"):
            tipe = st.selectbox("Tipe", ["pemasukan","pengeluaran"], index=0 if row['tipe']=="pemasukan" else 1)
            kategori = st.text_input("Kategori", value=row['kategori'] or "")
            jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, value=float(row['jumlah']))
            tanggal = st.date_input("Tanggal", value=pd.to_datetime(row['tanggal']).date())
            ket = st.text_input("Keterangan", value=row['keterangan'] or "")
            bukti = st.file_uploader("Ganti Bukti (opsional)", type=["jpg","jpeg","png","webp","pdf"])
            save = st.form_submit_button("Simpan"); delete = st.form_submit_button("Hapus")
            if save:
                bukti_path = row['bukti']
                if bukti is not None: bukti_path = save_upload(bukti, "bukti")
                conn = get_conn(); conn.execute("UPDATE keuangan SET tipe=?,kategori=?,jumlah=?,tanggal=?,keterangan=?,bukti=? WHERE id=?",
                                                (tipe,kategori,jumlah,str(tanggal),ket,bukti_path,int(row['id']))); conn.commit(); conn.close()
                st.success("Perubahan tersimpan.")
            if delete:
                conn = get_conn(); conn.execute("DELETE FROM keuangan WHERE id=?", (int(row['id']),)); conn.commit(); conn.close()
                st.warning("Data dihapus.")