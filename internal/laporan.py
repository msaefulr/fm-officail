import streamlit as st, pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from utils import get_conn
def df_to_excel_bytes(df, sheet_name="Sheet1"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()
def df_to_pdf_bytes(df, title="Laporan"):
    output = BytesIO(); c = canvas.Canvas(output, pagesize=landscape(A4)); width, height = landscape(A4)
    c.setFont("Helvetica-Bold", 14); c.drawString(40, height-40, title); c.setFont("Helvetica", 9)
    if df.empty:
        c.drawString(40, height-70, "Tidak ada data."); c.save(); return output.getvalue()
    x, y = 40, height-80; row_h = 16; cols = list(df.columns)
    for i, col in enumerate(cols): c.drawString(x + i*150, y, str(col))
    y -= row_h
    for _, row in df.iterrows():
        for i, col in enumerate(cols): c.drawString(x + i*150, y, str(row[col]))
        y -= row_h
        if y < 40: c.showPage(); c.setFont("Helvetica", 9); y = height-40
    c.save(); return output.getvalue()
def page():
    st.header("Generate Laporan (PDF/Excel)")
    conn = get_conn(); df_f = pd.read_sql_query("SELECT * FROM fasilitas", conn); df_k = pd.read_sql_query("SELECT * FROM keuangan", conn); df_j = pd.read_sql_query("SELECT * FROM jadwal", conn); conn.close()
    tab1, tab2, tab3 = st.tabs(["Fasilitas","Keuangan","Jadwal"])
    with tab1:
        st.dataframe(df_f, use_container_width=True)
        if st.button("Unduh Excel (Fasilitas)"): st.download_button("Download Excel", data=df_to_excel_bytes(df_f,"Fasilitas"), file_name="fasilitas.xlsx")
        if st.button("Unduh PDF (Fasilitas)"): st.download_button("Download PDF", data=df_to_pdf_bytes(df_f,"Laporan Fasilitas"), file_name="fasilitas.pdf")
    with tab2:
        st.dataframe(df_k, use_container_width=True)
        if st.button("Unduh Excel (Keuangan)"): st.download_button("Download Excel", data=df_to_excel_bytes(df_k,"Keuangan"), file_name="keuangan.xlsx")
        if st.button("Unduh PDF (Keuangan)"): st.download_button("Download PDF", data=df_to_pdf_bytes(df_k,"Laporan Keuangan"), file_name="keuangan.pdf")
    with tab3:
        st.dataframe(df_j, use_container_width=True)
        if st.button("Unduh Excel (Jadwal)"): st.download_button("Download Excel", data=df_to_excel_bytes(df_j,"Jadwal"), file_name="jadwal.xlsx")
        if st.button("Unduh PDF (Jadwal)"): st.download_button("Download PDF", data=df_to_pdf_bytes(df_j,"Laporan Jadwal"), file_name="jadwal.pdf")