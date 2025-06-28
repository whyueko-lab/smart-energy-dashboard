import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Konfigurasi halaman
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("🏠 Smart Energy Dashboard (Regresi)")
st.markdown("Selamat datang di sistem monitoring energi rumah pintar berbasis AI regresi.")

# ---------------------------------------------
# Fungsi untuk melatih model regresi konsumsi daya
@st.cache_resource
def train_regression_model():
    data = []
    for _ in range(1000):
        suhu = random.uniform(20, 35)
        jam = random.randint(0, 23)
        penghuni = random.choice([0, 1])
        cuaca = random.choice(["cerah", "hujan", "mendung"])
        hari_libur = random.choice([0, 1])
        cahaya = random.uniform(0, 100)

        daya = 0
        if penghuni:
            if suhu > 30 or (suhu > 27 and cuaca == "cerah"):
                daya += 1500
            if 18 <= jam <= 22 or (hari_libur and 9 <= jam <= 23):
                daya += 100
            if jam >= 18 or jam < 6 or cahaya < 30:
                daya += 250
        daya += random.uniform(5, 15)

        data.append([suhu, jam, penghuni, cuaca, hari_libur, cahaya, daya])

    df = pd.DataFrame(data, columns=["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya", "daya"])

    X = df[["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya"]]
    y = df["daya"]

    transformer = ColumnTransformer([
        ("cuaca", OneHotEncoder(), ["cuaca"])
    ], remainder="passthrough")

    model = Pipeline([
        ("pre", transformer),
        ("reg", RandomForestRegressor())
    ]).fit(X, y)

    return model

model = train_regression_model()

# ---------------------------------------------
# Inisialisasi log
LOG_FILE = "log_energi.csv"
if "log" not in st.session_state:
    st.session_state["log"] = []

# ---------------------------------------------
# Kontrol tombol
col1, col2 = st.columns(2)
with col1:
    if st.button("🔁 Refresh Data"):
        st.session_state["refresh_key"] = random.random()
with col2:
    if st.button("🗑️ Reset Log Data"):
        st.session_state["log"] = []
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        st.success("Log berhasil direset.")

# ---------------------------------------------
# Simulasi Sensor
suhu = round(random.uniform(24.0, 33.0), 1)
cahaya = random.randint(0, 100)
penghuni_ada = random.choice([1, 0])
jam = datetime.now().hour
cuaca = random.choice(["cerah", "hujan", "mendung"])
hari_libur = random.choice([0, 1])

# Prediksi konsumsi daya
input_data = pd.DataFrame([{
    "suhu": suhu,
    "jam": jam,
    "penghuni": penghuni_ada,
    "cuaca": cuaca,
    "hari_libur": hari_libur,
    "cahaya": cahaya
}])
daya_total = model.predict(input_data)[0]
biaya = (daya_total / 1000) * 1900

# ---------------------------------------------
# Tampilkan hasil sensor
st.subheader("📍 Kondisi Terkini")
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Suhu", f"{suhu:.1f} °C")
col2.metric("💡 Cahaya", f"{cahaya} %")
col3.metric("👥 Penghuni", "Ya" if penghuni_ada else "Tidak")

col4, col5 = st.columns(2)
col4.metric("☁️ Cuaca", cuaca.capitalize())
col5.metric("📅 Hari Libur", "Ya" if hari_libur else "Tidak")

# Estimasi konsumsi
st.subheader("⚡ Konsumsi Energi")
st.metric("🔋 Konsumsi Total (W)", f"{daya_total:.1f} W")
st.metric("💰 Estimasi Biaya per Jam", f"Rp {biaya:,.0f}")

# ---------------------------------------------
# Logging ke sesi + file
log_entry = {
    "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Suhu (°C)": suhu,
    "Cahaya (%)": cahaya,
    "Penghuni": "Ya" if penghuni_ada else "Tidak",
    "Cuaca": cuaca,
    "Hari Libur": "Ya" if hari_libur else "Tidak",
    "Daya Total (W)": round(daya_total, 1),
    "Biaya/Jam (Rp)": int(biaya)
}
st.session_state["log"].append(log_entry)
df_log = pd.DataFrame(st.session_state["log"])
df_log.to_csv(LOG_FILE, index=False)

# ---------------------------------------------
# Statistik log
if not df_log.empty:
    rata_rata_daya = df_log["Daya Total (W)"].mean()
    st.metric("📊 Rata-rata Daya dari Log", f"{rata_rata_daya:.1f} W")

# ---------------------------------------------
# Grafik Harian
st.subheader("📊 Penggunaan Energi Hari Ini")
df_log_copy = df_log.copy()
df_log_copy["Waktu Jam"] = pd.to_datetime(df_log_copy["Waktu"]).dt.floor("H")
df_per_jam = df_log_copy.drop_duplicates("Waktu Jam", keep="last")
st.line_chart(df_per_jam.set_index("Waktu Jam")["Daya Total (W)"])

# ---------------------------------------------
# Grafik Periode (dalam Tab)
st.subheader("📆 Konsumsi Energi Periodik")
tab1, tab2 = st.tabs(["📆 Mingguan", "🗓️ Bulanan"])

with tab1:
    mingguan = pd.DataFrame({
        "Hari": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
        "Energi (kWh)": [3.2, 2.8, 3.5, 3.1, 3.9, 4.5, 2.6]
    })
    fig1 = px.bar(mingguan, x="Hari", y="Energi (kWh)", text="Energi (kWh)", color="Energi (kWh)")
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    bulanan = pd.DataFrame({
        "Minggu": ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
        "Energi (kWh)": [22.5, 24.0, 23.3, 21.9]
    })
    fig2 = px.line(bulanan, x="Minggu", y="Energi (kWh)", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------
# Tampilkan log dan unduh
st.subheader("📄 Log Energi")
st.dataframe(df_log, use_container_width=True)
with open(LOG_FILE, "rb") as f:
    st.download_button("📥 Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# Footer
st.markdown("---")
st.caption("© 2025 - Smart Energy Monitoring by Wahyu Eko Suroso. All rights reserved.")
