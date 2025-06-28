import streamlit as st
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")

# Import libraries
import pandas as pd  # noqa: E402
import random  # noqa: E402
import os  # noqa: E402
from datetime import datetime  # noqa: E402
import plotly.express as px  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.preprocessing import OneHotEncoder  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from streamlit_autorefresh import st_autorefresh   # noqa: E402



# Konfigurasi halaman
st_autorefresh(interval=40000, key="auto_refresh")
st.title("🏠 **Smart Energy Dashboard**")
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
st.markdown("### 🔧 **Kontrol Sistem**")
colA, colB = st.columns(2)
with colA:
    if st.button("🔁 Refresh Data"):
        st.session_state["refresh_key"] = random.random()
with colB:
    if st.button("🗑️ Reset Log Data"):
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
st.markdown("### 🧭 **Kontrol Manual Perangkat**")
col1, col2, col3 = st.columns(3)
manual_ac = col1.radio("AC", ["Auto", "OFF", "ON"], horizontal=True)
manual_tv = col2.radio("TV", ["Auto", "OFF", "ON"], horizontal=True)
manual_lampu = col3.radio("Lampu", ["Auto", "OFF", "ON"], horizontal=True)

ac_status = manual_ac if manual_ac != "Auto" else ac_status_pred
tv_status = manual_tv if manual_tv != "Auto" else tv_status_pred
lampu_status = manual_lampu if manual_lampu != "Auto" else lampu_status_pred

# Tampilan kondisi
st.markdown("### 📍 **Kondisi Terkini**")
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Suhu", f"{suhu:.1f} °C")
col2.metric("💡 Cahaya", f"{cahaya} %")
col3.metric("👥 Penghuni", "Ya" if penghuni_ada else "Tidak")

col4, col5, col6 = st.columns(3)
col4.metric("☁️ Cuaca", cuaca.capitalize())
col5.metric("🌀 AC", ac_status)
col6.metric("📺 TV", tv_status)

col7, col8 = st.columns(2)
col7.metric("💡 Lampu", lampu_status)
col8.metric("📅 Hari Libur", "Ya" if hari_libur else "Tidak")

# Estimasi konsumsi energi
daya_ac = 1500 if ac_status == "ON" else 0
daya_tv = 100 if tv_status == "ON" else 0
daya_lampu = 250 if lampu_status == "ON" else 0
daya_lain = random.uniform(5, 15)
daya_total = daya_ac + daya_tv + daya_lampu + daya_lain
biaya = (daya_total / 1000) * 1900

# Logging
log_entry = {
    "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

# Estimasi Energi + Rata-rata
st.markdown("### ⚡ **Estimasi Konsumsi Energi**")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Lampu", f"{daya_lampu} W")
col2.metric("AC", f"{daya_ac} W")
col3.metric("TV", f"{daya_tv} W")
col4.metric("Total", f"{daya_total:.1f} W")

col5, col6 = st.columns(2)
col5.metric("💰 Estimasi Biaya/Jam", f"Rp {biaya:,.0f}")
if not df_log.empty:
    rata_rata_daya = df_log["Daya Total (W)"].mean()
    col6.metric("📊 Rata-rata Energi (Log)", f"{rata_rata_daya:.1f} W")

# Grafik Harian
st.markdown("### 📊 **Penggunaan Energi Hari Ini**")
df_log_copy = df_log.copy()
df_log_copy["Waktu Jam"] = pd.to_datetime(df_log_copy["Waktu"]).dt.floor("H")
df_per_jam = df_log_copy.drop_duplicates("Waktu Jam", keep="last")
st.line_chart(df_per_jam.set_index("Waktu Jam")["Daya Total (W)"])


# Grafik Per Jam berdasarkan prediksi
st.markdown("### 🕒 **Total Penggunaan Energi Tiap Jam (Prediksi)**")

# Simulasi kondisi untuk setiap jam
jam_list = list(range(24))
prediksi_data = []

for jam in jam_list:
    suhu = 30  # asumsikan suhu stabil
    cahaya = 50  # nilai cahaya sedang
    penghuni = 1  # asumsikan ada penghuni
    cuaca = "cerah"  # cuaca diasumsikan cerah
    hari_libur = 0  # asumsikan bukan hari libur

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
    daya_total = daya_ac + daya_tv + daya_lampu

    prediksi_data.append({
        "Jam": jam,
        "Daya Prediksi (W)": daya_total
    })

df_prediksi = pd.DataFrame(prediksi_data)

# Tampilkan grafik
fig_prediksi = px.bar(
    df_prediksi,
    x="Jam",
    y="Daya Prediksi (W)",
    text="Daya Prediksi (W)",
    title="Prediksi Total Penggunaan Energi per Jam (Simulasi AI)"
)
fig_prediksi.update_traces(textposition="outside")
fig_prediksi.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig_prediksi, use_container_width=True)

# Log + download
st.markdown("### 🧾 **Log Energi**")
st.dataframe(df_log, use_container_width=True)
with open(LOG_FILE, "rb") as f:
    st.download_button("📥 Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# Footer
st.markdown("---")
st.caption("© 2025 - Smart Energy Monitoring by Wahyu Eko Suroso. All rights reserved.")
