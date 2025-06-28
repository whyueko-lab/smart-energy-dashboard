import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

# --- Training simulasi data
def generate_data(n=1000):
    data = []
    for _ in range(n):
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
    return pd.DataFrame(data, columns=["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya", "ac_on", "tv_on", "lampu_on"])

df = generate_data()

X = df[["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya"]]
y_ac = df["ac_on"]
y_tv = df["tv_on"]
y_lampu = df["lampu_on"]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(), ["cuaca"])
], remainder="passthrough")

model_ac = Pipeline([("pre", preprocessor), ("clf", RandomForestClassifier())]).fit(X, y_ac)
model_tv = Pipeline([("pre", preprocessor), ("clf", RandomForestClassifier())]).fit(X, y_tv)
model_lampu = Pipeline([("pre", preprocessor), ("clf", RandomForestClassifier())]).fit(X, y_lampu)

# --- Streamlit UI
st.set_page_config(page_title="Smart Home AI Dashboard", layout="centered")
st.title("🏠 Smart Home AI Dashboard")

# Simulasi data
if st.button("🔄 Simulasi Data Baru"):
    suhu = round(random.uniform(20, 35), 1)
    jam = datetime.now().hour
    penghuni = random.choice([0, 1])
    cuaca = random.choice(["cerah", "hujan", "mendung"])
    hari_libur = random.choice([0, 1])
    cahaya = round(random.uniform(0, 100), 1)

    data = pd.DataFrame([{
        "suhu": suhu,
        "jam": jam,
        "penghuni": penghuni,
        "cuaca": cuaca,
        "hari_libur": hari_libur,
        "cahaya": cahaya
    }])

    pred_ac = model_ac.predict(data)[0]
    pred_tv = model_tv.predict(data)[0]
    pred_lampu = model_lampu.predict(data)[0]

    st.write("### 📈 Data Sensor")
    st.write(data)

    st.write("### ⚙️ Prediksi Perangkat:")
    col1, col2, col3 = st.columns(3)
    col1.metric("AC", "✅ ON" if pred_ac else "❌ OFF")
    col2.metric("TV", "✅ ON" if pred_tv else "❌ OFF")
    col3.metric("Lampu", "✅ ON" if pred_lampu else "❌ OFF")

    # --- Simpan ke CSV (opsional)
    log_data = data.copy()
    log_data["pred_ac"] = pred_ac
    log_data["pred_tv"] = pred_tv
    log_data["pred_lampu"] = pred_lampu
    log_data["waktu"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log_prediksi.csv", "a") as f:
        log_data.to_csv(f, header=f.tell() == 0, index=False)
    st.success("Data dan prediksi berhasil disimpan ke log_prediksi.csv")