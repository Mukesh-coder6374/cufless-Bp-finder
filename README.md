# 🩺 Cuffless Blood Pressure Monitoring System

This project demonstrates a **real-time cuffless blood pressure prediction system** using:
- ✅ **MAX30102 PPG sensor**
- ✅ **ESP32 microcontroller**
- ✅ **Machine Learning** (Random Forest)
- ✅ **Python server with feature extraction and prediction**

The system predicts **Systolic (SP)** and **Diastolic (DP)** blood pressure from raw IR signals collected from a finger — all without a cuff.

---

## 🚀 Project Workflow

1. **PPG Signal Acquisition**  
   - The **MAX30102** sensor captures **infrared (IR) waveform** from a finger.

2. **Data Transmission**  
   - The **ESP32** sends IR values over **TCP/IP** to a local Python server.

3. **Feature Extraction**  
   - From a buffer of 500 IR values, features like:
     - `p2p_0`, `AI`, `bd`, `bcda`, `sdoo`, and **FFT peaks** are computed.

4. **Model Prediction**  
   - A **RandomForestRegressor** model predicts **Systolic (SP)** and **Diastolic (DP)** BP.

5. **Display & Output**  
   - Predicted values are sent back to the ESP32 or visualized via a mobile app like **Blynk**.

---

## 🧠 Model Details

- **Type:** `RandomForestRegressor`
- **Input Features:** PPG waveform features (`p2p_0`, `AI`, `bd`, `bcda`, `sdoo`, FFT peaks)
- **Labels:** `SP`, `DP`
- **Training:** Patient-wise group split to prevent leakage
- **Saved As:** `PPG_bp_model.joblib` (compatible with joblib and sk-learn)

---

## 📦 Requirements

Install dependencies:

```bash
pip install -r requirements.txt

