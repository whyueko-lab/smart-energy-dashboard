import streamlit as st
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")

# Import libraries
import pandas as pd
import random
import os
from datetime import datetime
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from streamlit_autorefresh import st_autorefresh
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Konfigurasi halaman
autorefresh_interval = 40000  # dalam milidetik
st_autorefresh(interval=autorefresh_interval, key="auto_refresh")
st.title("\U0001F3E0 **Smart Energy Dashboard**")
st.markdown("Selamat datang di sistem monitoring energi rumah pintar berbasis AI.")

# Fungsi untuk melatih model
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

    # Split
    X_train, X_test, y_ac_train, y_ac_test = train_test_split(X, y_ac, test_size=0.2, random_state=42)
    _, _, y_tv_train, y_tv_test = train_test_split(X, y_tv, test_size=0.2, random_state=42)
    _, _, y_lampu_train, y_lampu_test = train_test_split(X, y_lampu, test_size=0.2, random_state=42)

    model_ac = Pipeline([("pre", transformer), ("clf", RandomForestClassifier())]).fit(X_train, y_ac_train)
    model_tv = Pipeline([("pre", transformer), ("clf", RandomForestClassifier())]).fit(X_train, y_tv_train)
    model_lampu = Pipeline([("pre", transformer), ("clf", RandomForestClassifier())]).fit(X_train, y_lampu_train)

    acc_ac = accuracy_score(y_ac_test, model_ac.predict(X_test))
    acc_tv = accuracy_score(y_tv_test, model_tv.predict(X_test))
    acc_lampu = accuracy_score(y_lampu_test, model_lampu.predict(X_test))

    return model_ac, model_tv, model_lampu, acc_ac, acc_tv, acc_lampu


# Inisialisasi model
model_ac, model_tv, model_lampu, acc_ac, acc_tv, acc_lampu = train_ml_model()

# Inisialisasi log
LOG_FILE = "log_energi.csv"
if "log" not in st.session_state:
    st.session_state["log"] = []

# Tombol kontrol atas
st.markdown("### \U0001F527 **Kontrol Sistem**")
colA, colB = st.columns(2)
with colA:
    if st.button("\U0001F501 Refresh Data"):
        st.session_state["refresh_key"] = random.random()
with colB:
    if st.button("\U0001F5D1️ Reset Log Data"):
        st.session_state["log"] = []
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        st.success("Log data berhasil dihapus.")

# Simulasi Sensor
suhu = round(random.uniform(24.0, 33.0), 1)
cahaya = random.randint(0, 100)
penghuni_ada = random.choice([1, 0])
jam = datetime.now().hour
cuaca = random.choice(["cerah", "hujan", "mendung"])
hari_libur = random.choice([0, 1])

# Prediksi
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

# Kontrol Manual
st.markdown("### \U0001F9CD **Kontrol Manual Perangkat**")
col1, col2, col3 = st.columns(3)
manual_ac = col1.radio("AC", ["Auto", "OFF", "ON"], horizontal=True)
manual_tv = col2.radio("TV", ["Auto", "OFF", "ON"], horizontal=True)
manual_lampu = col3.radio("Lampu", ["Auto", "OFF", "ON"], horizontal=True)

ac_status = manual_ac if manual_ac != "Auto" else ac_status_pred
tv_status = manual_tv if manual_tv != "Auto" else tv_status_pred
lampu_status = manual_lampu if manual_lampu != "Auto" else lampu_status_pred

# Estimasi konsumsi energi
daya_ac = 1500 if ac_status == "ON" else 0
daya_tv = 100 if tv_status == "ON" else 0
daya_lampu = 250 if lampu_status == "ON" else 0
daya_lain = 250  # standby atau kulkas
daya_total = daya_ac + daya_tv + daya_lampu + daya_lain
biaya = (daya_total / 1000) * 1900

# Informasi Kondisi Terkini
st.markdown("### \U0001F4C8 **Kondisi Terkini**")
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Suhu", f"{suhu:.1f} °C")
col2.metric("💡 Cahaya", f"{cahaya} %")
col3.metric("👥 Penghuni", "Ya" if penghuni_ada else "Tidak")

col4, col5, col6 = st.columns(3)
col4.metric("☁️ Cuaca", cuaca.capitalize())
col5.metric("📅 Hari Libur", "Ya" if hari_libur else "Tidak")
col6.metric("🕐 Jam Sekarang", f"{jam}:00")

col7, col8, col9 = st.columns(3)
col7.metric("🌀 AC", ac_status)
col8.metric("📺 TV", tv_status)
col9.metric("💡 Lampu", lampu_status)

col10, col11 = st.columns(2)
col10.metric("⚡ Total Konsumsi", f"{daya_total:.1f} W")
col11.metric("💰 Estimasi Biaya/Jam", f"Rp {biaya:,.0f}")


# Logging
log_entry = {
    "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Suhu (\u00b0C)": suhu,
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

# Grafik Prediksi Energi Realistis
st.markdown("### \U0001F551 **Total Penggunaan Energi Tiap Jam (Prediksi Realistis)**")
jam_list = list(range(24))
prediksi_data = []

for jam in jam_list:
    if 0 <= jam < 6:
        suhu = random.uniform(23, 26)
    elif 6 <= jam < 12:
        suhu = random.uniform(26, 30)
    elif 12 <= jam < 15:
        suhu = random.uniform(30, 33)
    elif 15 <= jam < 18:
        suhu = random.uniform(28, 31)
    else:
        suhu = random.uniform(26, 29)

    penghuni = 1 if (5 <= jam <= 7 or 18 <= jam <= 23) else 0
    cahaya = random.uniform(70, 100) if 6 <= jam <= 17 else random.uniform(0, 30)
    cuaca = random.choice(["cerah", "mendung", "hujan"])
    hari_libur = 0

    data_input = pd.DataFrame([{
        "suhu": suhu,
        "jam": jam,
        "penghuni": penghuni,
        "cuaca": cuaca,
        "hari_libur": hari_libur,
        "cahaya": cahaya
    }])

    ac_pred = model_ac.predict(data_input)[0]
    tv_pred = model_tv.predict(data_input)[0]
    lampu_pred = model_lampu.predict(data_input)[0]

    daya_ac = 1500 if ac_pred == 1 else 0
    daya_tv = 100 if tv_pred == 1 else 0
    daya_lampu = 250 if lampu_pred == 1 else 0
    daya_lain = 250
    daya_total = round(daya_ac + daya_tv + daya_lampu + daya_lain, 1)

    prediksi_data.append({
        "Jam": int(jam),
        "Suhu (\u00b0C)": round(suhu, 1),
        "Penghuni": penghuni,
        "Cahaya (%)": round(cahaya),
        "Cuaca": cuaca,
        "Daya Prediksi (W)": round(daya_total, 1)
    })

df_prediksi = pd.DataFrame(prediksi_data)
df_prediksi = df_prediksi[(df_prediksi["Jam"] >= 0) & (df_prediksi["Jam"] <= 23)]

# plotly scatter plot
fig_prediksi = px.bar(
    df_prediksi,
    x="Jam",
    y="Daya Prediksi (W)",
    text="Daya Prediksi (W)",
    color="Suhu (°C)",
    labels={"Jam": "Jam (0-23)", "Daya Prediksi (W)": "Daya (Watt)"},
    title="Prediksi Energi Tiap Jam Berdasarkan Kondisi Realistis"
)
fig_prediksi.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig_prediksi, use_container_width=True)

# Log dan Unduh
st.markdown("### \U0001F9FE **Log Energi**")
st.dataframe(df_log, use_container_width=True)
with open(LOG_FILE, "rb") as f:
    st.download_button("\U0001F4E5 Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# Sidebar
st.sidebar.header("Informasi Model AI")
st.sidebar.markdown("Akurasi dihitung dari pembagian data pelatihan dan pengujian secara acak (80:20)")
st.sidebar.metric("AC", f"{acc_ac * 100:.2f}%")
st.sidebar.metric("TV", f"{acc_tv * 100:.2f}%")
st.sidebar.metric("Lampu", f"{acc_lampu * 100:.2f}%")

# Footer
st.markdown("---")
st.caption("© 2025 - Smart Energy Monitoring by Wahyu Eko Suroso. All rights reserved.")