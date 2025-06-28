import streamlit as st
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")

# Import libraries
import pandas as pd
import random
import os
from datetime import datetime
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from streamlit_autorefresh import st_autorefresh

# ------------------- CACHING MODEL TRAINING -------------------
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
    y_ac, y_tv, y_lampu = df["ac"], df["tv"], df["lampu"]

    transformer = ColumnTransformer([("cuaca", OneHotEncoder(), ["cuaca"])], remainder="passthrough")

    X_train, X_test, y_ac_train, y_ac_test = train_test_split(X, y_ac, test_size=0.2, random_state=42)
    _, _, y_tv_train, y_tv_test = train_test_split(X, y_tv, test_size=0.2, random_state=42)
    _, _, y_lampu_train, y_lampu_test = train_test_split(X, y_lampu, test_size=0.2, random_state=42)

    model_params = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
    model_ac = Pipeline([("pre", transformer), ("clf", RandomForestClassifier(**model_params))]).fit(X_train, y_ac_train)
    model_tv = Pipeline([("pre", transformer), ("clf", RandomForestClassifier(**model_params))]).fit(X_train, y_tv_train)
    model_lampu = Pipeline([("pre", transformer), ("clf", RandomForestClassifier(**model_params))]).fit(X_train, y_lampu_train)

    acc_ac = accuracy_score(y_ac_test, model_ac.predict(X_test))
    acc_tv = accuracy_score(y_tv_test, model_tv.predict(X_test))
    acc_lampu = accuracy_score(y_lampu_test, model_lampu.predict(X_test))

    return model_ac, model_tv, model_lampu, acc_ac, acc_tv, acc_lampu, df

# ------------------- TRAIN MODEL -------------------
st_autorefresh(interval=40000, key="auto_refresh")
st.title("🏠 Smart Energy Dashboard")
st.markdown("Selamat datang di sistem monitoring energi rumah pintar berbasis AI.")

model_ac, model_tv, model_lampu, acc_ac, acc_tv, acc_lampu, df_all = train_ml_model()

# ------------------- KONTROL ATAS -------------------
LOG_FILE = "log_energi.csv"
if "log" not in st.session_state:
    st.session_state["log"] = []

colA, colB = st.columns(2)
with colA:
    if st.button("🔄 Refresh Data"):
        st.session_state["refresh_key"] = random.random()
with colB:
    if st.button("🗑️ Reset Log Data"):
        st.session_state["log"] = []
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        st.success("Log data berhasil dihapus.")

# ------------------- SIMULASI SENSOR -------------------
suhu = round(random.uniform(24.0, 33.0), 1)
cahaya = random.randint(0, 100)
penghuni_ada = random.choice([1, 0])
jam = datetime.now().hour
cuaca = random.choice(["cerah", "hujan", "mendung"])
hari_libur = random.choice([0, 1])

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

# ------------------- KONTROL MANUAL -------------------
st.markdown("### 🧑‍🔧 Kontrol Manual Perangkat")
col1, col2, col3 = st.columns(3)
manual_ac = col1.radio("AC", ["Auto", "OFF", "ON"], horizontal=True)
manual_tv = col2.radio("TV", ["Auto", "OFF", "ON"], horizontal=True)
manual_lampu = col3.radio("Lampu", ["Auto", "OFF", "ON"], horizontal=True)

ac_status = manual_ac if manual_ac != "Auto" else ac_status_pred
tv_status = manual_tv if manual_tv != "Auto" else tv_status_pred
lampu_status = manual_lampu if manual_lampu != "Auto" else lampu_status_pred

daya_ac = 1500 if ac_status == "ON" else 0
daya_tv = 100 if tv_status == "ON" else 0
daya_lampu = 250 if lampu_status == "ON" else 0
daya_lain = 250
daya_total = daya_ac + daya_tv + daya_lampu + daya_lain
biaya = (daya_total / 1000) * 1900

# ------------------- INFO KONDISI -------------------
st.markdown("### 📊 Kondisi Terkini")
cols = st.columns(6)
info = [
    ("🌡️ Suhu", f"{suhu:.1f} °C"),
    ("💡 Cahaya", f"{cahaya}%"),
    ("👥 Penghuni", "Ya" if penghuni_ada else "Tidak"),
    ("☁️ Cuaca", cuaca.capitalize()),
    ("📅 Hari Libur", "Ya" if hari_libur else "Tidak"),
    ("🕐 Jam Sekarang", f"{jam}:00")
]
for col, (label, value) in zip(cols, info):
    col.metric(label, value)

cols_status = st.columns(5)
cols_status[0].metric("🌀 AC", ac_status)
cols_status[1].metric("📺 TV", tv_status)
cols_status[2].metric("💡 Lampu", lampu_status)
cols_status[3].metric("⚡ Konsumsi", f"{daya_total:.1f} W")
cols_status[4].metric("💰 Estimasi Biaya", f"Rp {biaya:,.0f}")

# ------------------- LOGGING -------------------
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

# ------------------- GRAFIK PREDIKSI 24 JAM -------------------
st.markdown("### 🕐 Prediksi Energi 24 Jam")
jam_list = list(range(2))
prediksi_data = []

for j in jam_list:
    suhu = random.uniform(23, 33)
    penghuni = 1 if (5 <= j <= 7 or 18 <= j <= 23) else 0
    cahaya = random.uniform(70, 100) if 6 <= j <= 17 else random.uniform(0, 30)
    cuaca = random.choice(["cerah", "mendung", "hujan"])
    hari_libur = 0

    data_input = pd.DataFrame([{
        "suhu": suhu,
        "jam": j,
        "penghuni": penghuni,
        "cuaca": cuaca,
        "hari_libur": hari_libur,
        "cahaya": cahaya
    }])

    ac_pred = model_ac.predict(data_input)[0]
    tv_pred = model_tv.predict(data_input)[0]
    lampu_pred = model_lampu.predict(data_input)[0]

    daya_total = sum([
        1500 if ac_pred == 1 else 0,
        100 if tv_pred == 1 else 0,
        250 if lampu_pred == 1 else 0,
        250
    ])

    prediksi_data.append({
        "Jam": j,
        "Suhu (°C)": round(suhu, 1),
        "Daya Prediksi (W)": daya_total
    })

df_prediksi = pd.DataFrame(prediksi_data)
fig = px.bar(df_prediksi, x="Jam", y="Daya Prediksi (W)", text="Daya Prediksi (W)", color="Suhu (°C)", title="Prediksi Konsumsi Energi per Jam")
fig.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig, use_container_width=True)

# ------------------- LOG DOWNLOAD -------------------
st.markdown("### 🧾 Log Energi")
st.dataframe(df_log, use_container_width=True)
with open(LOG_FILE, "rb") as f:
    st.download_button("⬇️ Download Log CSV", f, file_name=LOG_FILE, mime="text/csv")

# ------------------- SIDEBAR ANALISIS MODEL -------------------
st.sidebar.header("📈 Evaluasi Model")
st.sidebar.metric("Akurasi AC", f"{acc_ac * 100:.2f}%")
st.sidebar.metric("Akurasi TV", f"{acc_tv * 100:.2f}%")
st.sidebar.metric("Akurasi Lampu", f"{acc_lampu * 100:.2f}%")

st.sidebar.subheader("Distribusi Target")
st.sidebar.bar_chart(df_all[["ac", "tv", "lampu"]].apply(pd.Series.value_counts).fillna(0))

st.sidebar.subheader("Heatmap Korelasi")
fig_corr, ax = plt.subplots()
sns.heatmap(df_all.corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax)
st.sidebar.pyplot(fig_corr)

input_features = ["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya"]
st.sidebar.text(classification_report(df_all["ac"], model_ac.predict(df_all[input_features])))
st.sidebar.text(classification_report(df_all["tv"], model_tv.predict(df_all[input_features])))
st.sidebar.text(classification_report(df_all["lampu"], model_lampu.predict(df_all[input_features])))
# ------------------- FOOTER -------------------
st.markdown("---")
st.markdown("Copyright © 2025 - Smart Energy Dashboard by Wahyu Eko Suroso. All rights reserved.")
