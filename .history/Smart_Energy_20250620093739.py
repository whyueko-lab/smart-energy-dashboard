import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime, timedelta
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Konfigurasi halaman
st.set_page_config(page_title="Smart Energy Dashboard", layout="centered")
st.title("\U0001F3E0 Dashboard Energi Rumah Pintar + AI")

# Model ML (dilatih dari data simulasi)
def train_ml_model():
    data = []
    for _ in range(1000):
        suhu = random.uniform(20, 35)
        jam = random.randint(0, 23)
        penghuni = random.choice([0, 1])
        cuaca = random.choice(["cerah", "hujan", "mendung"])
        hari_libur = random.choice([0, 1])
        cahaya = random.uniform(0, 100)
        ac_on = 1 if (suhu > 30 or (suhu > 27 and cuaca == "cerah")) and penghuni else 0
        tv_on = 1 if penghuni and ((18 <= jam <= 22) or (hari_libur and 9 <= jam <= 23)) else 0
        lampu_on = 1 if penghuni and (jam >= 18 or jam < 6 or cahaya < 30) else 0
        data.append([suhu, jam, penghuni, cuaca, hari_libur, cahaya, ac_on, tv_on, lampu_on])
    df = pd.DataFrame(data, columns=["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya", "ac", "tv", "lampu"])

    X = df[["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya"]]
    y_ac = df["ac"]
    y_tv = df["tv"]
    y_lampu = df["lampu"]

    transformer = ColumnTransformer([
        ("cuaca", OneHotEncoder(), ["cuaca"])
    ], remainder="passthrough")

    model_ac = Pipeline([("pre", transformer), ("clf", RandomForestClassifier())]).fit(X, y_ac)
    model_tv = Pipeline([("pre", transformer), ("clf", RandomForestClassifier())]).fit(X, y_tv)
    model_lampu = Pipeline([("pre", transformer), ("clf", RandomForestClassifier())]).fit(X, y_lampu)

    return model_ac, model_tv, model_lampu

model_ac, model_tv, model_lampu = train_ml_model()

# Nama file log CSV
LOG_FILE = "log_energi.csv"
if "log" not in st.session_state:
    st.session_state["log"] = []

# Tombol
if st.button("\U0001F504 Refresh Data"):
    st.session_state["refresh_key"] = random.random()
if st.button("\U0001F5D1️ Reset Log Data"):
    st.session_state["log"] = []
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    st.success("✅ Log data berhasil direset.")

# --- Simulasi Sensor ---
suhu = round(random.uniform(24.0, 33.0), 1)
cahaya = random.randint(0, 100)
penghuni_ada = random.choice([1, 0])
jam = datetime.now().hour
cuaca = random.choice(["cerah", "hujan", "mendung"])
hari_libur = random.choice([0, 1])

# Prediksi ML
input_data = pd.DataFrame([{
    "suhu": suhu,
    "jam": jam,
    "penghuni": penghuni_ada,
    "cuaca": cuaca,
    "hari_libur": hari_libur,
    "cahaya": cahaya
}])

ac_status_pred = "ON" if model_ac.predict(input_data)[0] else "OFF"
tv_status_pred = "ON" if model_tv.predict(input_data)[0] else "OFF"
lampu_status_pred = "ON" if model_lampu.predict(input_data)[0] else "OFF"

# Kontrol manual
st.subheader("\U0001F527 Kontrol Manual Perangkat")
manual_ac = st.radio("Kontrol AC", ["Auto", "OFF", "ON"], horizontal=True)
manual_tv = st.radio("Kontrol TV", ["Auto", "OFF", "ON"], horizontal=True)
manual_lampu = st.radio("Kontrol Lampu", ["Auto", "OFF", "ON"], horizontal=True)

ac_status = manual_ac if manual_ac != "Auto" else ac_status_pred
tv_status = manual_tv if manual_tv != "Auto" else tv_status_pred
lampu_status = manual_lampu if manual_lampu != "Auto" else lampu_status_pred

# Tampilan
st.subheader("\U0001F4CD Kondisi Terkini")
col1, col2 = st.columns(2)
col1.metric("Suhu Ruangan", f"{suhu:.1f} °C")
col2.metric("Intensitas Cahaya", f"{cahaya} %")

col3, col4 = st.columns(2)
col3.metric("Penghuni Terdeteksi", "Ya" if penghuni_ada else "Tidak")
col4.metric("Status Cuaca", cuaca.capitalize())

col5, col6, col7 = st.columns(3)
col5.metric("Status AC", ac_status)
col6.metric("Status TV", tv_status)
col7.metric("Status Lampu", lampu_status)

# Estimasi Daya
daya_ac = 500 if ac_status == "ON" else 0
daya_tv = 100 if tv_status == "ON" else 0
daya_lampu = 10 if lampu_status == "ON" else 0
daya_lain = random.uniform(5, 15)
daya_total = daya_ac + daya_tv + daya_lampu + daya_lain
kwh = daya_total / 1000
tarif = 1500
biaya = kwh * tarif

col8, col9, col10, col11 = st.columns(4)
col8.metric("Lampu", f"{daya_lampu} W")
col9.metric("AC", f"{daya_ac} W")
col10.metric("TV", f"{daya_tv} W")
col11.metric("Total", f"{daya_total:.1f} W")
st.metric("\U0001F4B0 Estimasi Biaya Energi/Jam", f"Rp {biaya:,.0f}")

# Logging
waktu_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_entry = {
    "Waktu": waktu_log,
    "Suhu (°C)": suhu,
    "Cahaya (%)": cahaya,
    "Penghuni": "Ya" if penghuni_ada else "Tidak",
    "Cuaca": cuaca,
    "Hari Libur": "Ya" if hari_libur else "Tidak",
    "AC": ac_status,
    "TV": tv_status,
    "Lampu": lampu_status,
    "Daya Total (W)": round(daya_total, 1),
    "Biaya/Jam (Rp)": int(biaya)
}
st.session_state["log"].append(log_entry)
df_log = pd.DataFrame(st.session_state["log"])
df_log.to_csv(LOG_FILE, index=False)

# Grafik Harian
st.subheader("\U0001F4C8 Penggunaan Energi Hari Ini")
df_log_copy = df_log.copy()
df_log_copy["Waktu Jam"] = pd.to_datetime(df_log_copy["Waktu"]).dt.floor("H")
df_per_jam = df_log_copy.drop_duplicates("Waktu Jam", keep="last")
st.line_chart(df_per_jam.set_index("Waktu Jam")["Daya Total (W)"])

# Simulasi grafik mingguan
mingguan = pd.DataFrame({
    "Hari": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
    "Energi (kWh)": [3.2, 2.8, 3.5, 3.1, 3.9, 4.5, 2.6]
})
st.subheader("\U0001F4C5 Konsumsi Energi Mingguan")
fig1 = px.bar(mingguan, x="Hari", y="Energi (kWh)", text="Energi (kWh)", color="Energi (kWh)")
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# Simulasi grafik bulanan
bulanan = pd.DataFrame({
    "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
    "Energi (kWh)": [22.5, 24.0, 23.3, 21.9]
})
st.subheader("\U0001F5D3️ Konsumsi Energi Bulanan")
fig2 = px.line(bulanan, x="Minggu", y="Energi (kWh)", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# Log Tabel + Unduh
st.subheader("\U0001F4DD Log Energi")
st.dataframe(df_log, use_container_width=True)
with open(LOG_FILE, "rb") as f:
    st.download_button("📥 Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# Footer
st.caption("© 2025 - Smart Energy Monitoring by Wahyu Eko Suroso. All rights reserved.")
