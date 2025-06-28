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

# Konfigurasi halaman
autorefresh_interval = 40000  # dalam milidetik
st_autorefresh(interval=autorefresh_interval, key="auto_refresh")
st.title("\U0001F3E0 **Smart Energy Dashboard**")
st.markdown("Selamat datang di sistem monitoring energi rumah pintar berbasis AI.")

# Fungsi untuk melatih model
@st.cache_resource
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

# Inisialisasi model
model_ac, model_tv, model_lampu = train_ml_model()

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
daya_lain = 150  # standby atau kulkas
daya_total = daya_ac + daya_tv + daya_lampu + daya_lain
biaya = (daya_total / 1000) * 1900

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
    daya_lain = 150
    daya_total = round(daya_ac + daya_tv + daya_lampu + daya_lain, 1)

    prediksi_data.append({
        "Jam": jam,
        "Suhu (\u00b0C)": round(suhu, 1),
        "Penghuni": penghuni,
        "Cahaya (%)": round(cahaya),
        "Cuaca": cuaca,
        "Daya Prediksi (W)": daya_total
    })

df_prediksi = pd.DataFrame(prediksi_data)
fig_prediksi = px.scatter(
    df_prediksi,
    x="Jam",
    y="Daya Prediksi (W)",
    color="Suhu (\u00b0C)",
    size=[10]*24,
    hover_data=["Penghuni", "Cahaya (%)", "Cuaca"],
    title="Prediksi Energi Tiap Jam Berdasarkan Kondisi Realistis"
)
fig_prediksi.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig_prediksi, use_container_width=True)

# Log dan Unduh
st.markdown("### \U0001F9FE **Log Energi**")
st.dataframe(df_log, use_container_width=True)
with open(LOG_FILE, "rb") as f:
    st.download_button("\U0001F4E5 Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# Footer
st.markdown("---")
st.caption("© 2025 - Smart Energy Monitoring by Wahyu Eko Suroso. All rights reserved.")