import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime, timedelta
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(page_title="Smart Energy Dashboard", layout="centered")
st.title("🏠 Dashboard Energi Rumah Pintar")

# Nama file log CSV
LOG_FILE = "log_energi.csv"

# Inisialisasi session_state
if "log" not in st.session_state:
    st.session_state["log"] = []

# Tombol Refresh
if st.button("🔄 Refresh Data"):
    st.session_state["refresh_key"] = random.random()

_ = st.session_state.get("refresh_key", 0)

# --- Simulasi Sensor dan Status Perangkat ---
suhu = random.uniform(24.0, 33.0)
cahaya = random.randint(0, 100)
penghuni_ada = random.choice([True, False])
ac_status = "ON" if suhu > 30 and penghuni_ada else "OFF"

# --- Tampilan Kondisi Terkini ---
st.subheader("📍 Kondisi Terkini")
col1, col2 = st.columns(2)
col1.metric("Suhu Ruangan", f"{suhu:.1f} °C")
col2.metric("Intensitas Cahaya", f"{cahaya} %")

col3, col4 = st.columns(2)
col3.metric("Penghuni Terdeteksi", "Ya" if penghuni_ada else "Tidak")
col4.metric("Status AC", ac_status)

# --- Kontrol Manual (Simulasi) ---
st.subheader("🎮 Kontrol Manual Perangkat")
lampu_state = st.radio("Status Lampu", ["OFF", "ON"], index=0, horizontal=True)
if lampu_state == "ON":
    st.success("Lampu Dinyalakan")
else:
    st.warning("Lampu Dimatikan")

# --- Simulasi Energi Saat Ini ---
st.subheader("⚡ Penggunaan Energi Saat Ini")
daya_lampu = 10 if lampu_state == "ON" else 0
daya_ac = 500 if ac_status == "ON" else 0
daya_lain = random.uniform(5, 15)
daya_tv = 100 if tv_state == "ON" else 0  # Misalnya TV mengonsumsi 100 W
daya_total = daya_lampu + daya_ac + daya_tv + daya_lain


tarif_per_kwh = 1500
kwh_per_jam = daya_total / 1000
biaya_per_jam = kwh_per_jam * tarif_per_kwh


col5, col6, col7, col8 = st.columns(4)
col5.metric("Lampu", f"{daya_lampu} W")
col6.metric("AC", f"{daya_ac} W")
col7.metric("TV", f"{daya_tv} W")
col8.metric("Total", f"{daya_total:.1f} W")
st.metric("💰 Estimasi Biaya Energi/Jam", f"Rp {biaya_per_jam:,.0f}")

# --- Simpan ke log ---
waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_entry = {
    "Waktu": waktu_log,
    "Suhu (°C)": round(suhu, 1),
    "Cahaya (%)": cahaya,
    "Penghuni": "Ya" if penghuni_ada else "Tidak",
    "AC": ac_status,
    "Lampu": lampu_state,
    "TV": tv_state,
    "Daya Total (W)": round(daya_total, 1),
    "Biaya/Jam (Rp)": int(biaya_per_jam)
}
st.session_state["log"].append(log_entry)

# Simpan ke file CSV
df_log_entry = pd.DataFrame([log_entry])
if not os.path.exists(LOG_FILE):
    df_log_entry.to_csv(LOG_FILE, index=False)
else:
    df_log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)

# --- Grafik Energi 10 Jam Terakhir (Simulasi) ---
data = {
    "Waktu": [datetime.now() - timedelta(hours=i) for i in range(9, -1, -1)],
    "Energi (kWh)": [round(random.uniform(0.2, 0.7), 2) for _ in range(10)]
}
df = pd.DataFrame(data)
st.subheader("📊 Penggunaan Energi (10 Jam Terakhir)")
st.line_chart(df.set_index("Waktu"))

# --- Grafik Mingguan ---
mingguan = pd.DataFrame({
    "Hari": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
    "Energi (kWh)": [3.2, 2.8, 3.5, 3.1, 3.9, 4.5, 2.6]
})
st.subheader("📅 Konsumsi Energi Mingguan")
fig1 = px.bar(mingguan, x="Hari", y="Energi (kWh)", color="Energi (kWh)",
              title="Energi Harian dalam Seminggu", text="Energi (kWh)")
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# --- Grafik Bulanan ---
bulanan = pd.DataFrame({
    "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
    "Energi (kWh)": [22.5, 24.0, 23.3, 21.9]
})
st.subheader("🗓️ Konsumsi Energi Bulanan")
fig2 = px.line(bulanan, x="Minggu", y="Energi (kWh)", markers=True,
               title="Total Energi per Minggu")
st.plotly_chart(fig2, use_container_width=True)

# --- Tampilkan Log & Unduh ---
st.subheader("📝 Log Data Energi (Sesi Ini)")
df_log = pd.DataFrame(st.session_state["log"])
st.dataframe(df_log, use_container_width=True)

# Tombol download log sebagai file CSV
with open(LOG_FILE, "rb") as f:
    st.download_button("📥 Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# Footer
st.caption("© 2025 - Smart Energy Monitoring by Wahyu Eko Suroso")
