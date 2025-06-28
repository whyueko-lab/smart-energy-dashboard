import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import random
import time
from datetime import datetime

# ---------------------------
# Simulasi dataset cerdas
# ---------------------------
def generate_smart_data(n=1000):
    data = []
    for _ in range(n):
        suhu = random.uniform(20, 35)
        jam = random.randint(0, 23)
        penghuni = random.choice([0, 1])
        cuaca = random.choice(["cerah", "hujan", "mendung"])
        hari_libur = random.choice([0, 1])
        cahaya_lingkungan = random.uniform(0, 100)

        # AC
        ac_on = 1 if (suhu > 30 or (suhu > 27 and cuaca == "cerah")) and penghuni else 0
        # TV
        tv_on = 1 if penghuni and ((18 <= jam <= 22) or (hari_libur and 9 <= jam <= 23)) else 0
        # Lampu
        lampu_on = 1 if penghuni and (jam >= 18 or jam < 6 or cahaya_lingkungan < 30) else 0

        data.append([suhu, jam, penghuni, cuaca, hari_libur, cahaya_lingkungan, ac_on, tv_on, lampu_on])

    return pd.DataFrame(data, columns=[
        "suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya", "ac_on", "tv_on", "lampu_on"
    ])

# ---------------------------
# Latih model ML
# ---------------------------
df = generate_smart_data()

X = df[["suhu", "jam", "penghuni", "cuaca", "hari_libur", "cahaya"]]
y_ac = df["ac_on"]
y_tv = df["tv_on"]
y_lampu = df["lampu_on"]

# Transformasi cuaca (one-hot encoding)
categorical = ["cuaca"]
numerical = ["suhu", "jam", "penghuni", "hari_libur", "cahaya"]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(), categorical)
], remainder="passthrough")

model_ac = Pipeline([("pre", preprocessor), ("clf", RandomForestClassifier())]).fit(X, y_ac)
model_tv = Pipeline([("pre", preprocessor), ("clf", RandomForestClassifier())]).fit(X, y_tv)
model_lampu = Pipeline([("pre", preprocessor), ("clf", RandomForestClassifier())]).fit(X, y_lampu)

# ---------------------------
# Simulasi Prediksi Smart Home
# ---------------------------
def simulasi_smart_home_ml():
    try:
        while True:
            suhu = random.uniform(20, 35)
            jam = datetime.now().hour
            penghuni = random.choice([0, 1])
            cuaca = random.choice(["cerah", "hujan", "mendung"])
            hari_libur = random.choice([0, 1])
            cahaya = random.uniform(0, 100)

            fitur = pd.DataFrame([{
                "suhu": suhu,
                "jam": jam,
                "penghuni": penghuni,
                "cuaca": cuaca,
                "hari_libur": hari_libur,
                "cahaya": cahaya
            }])

            pred_ac = model_ac.predict(fitur)[0]
            pred_tv = model_tv.predict(fitur)[0]
            pred_lampu = model_lampu.predict(fitur)[0]

            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"Suhu           : {suhu:.1f}°C")
            print(f"Jam            : {jam}")
            print(f"Penghuni       : {'YA' if penghuni else 'TIDAK'}")
            print(f"Cuaca          : {cuaca}")
            print(f"Hari Libur     : {'YA' if hari_libur else 'TIDAK'}")
            print(f"Cahaya         : {cahaya:.1f}")

            print(f"AC             : {'✅ NYALA' if pred_ac else '❌ MATI'}")
            print(f"TV             : {'✅ NYALA' if pred_tv else '❌ MATI'}")
            print(f"Lampu          : {'✅ NYALA' if pred_lampu else '❌ MATI'}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nSimulasi dihentikan.")

simulasi_smart_home_ml()
