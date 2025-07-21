import socket
import joblib
import numpy as np
from scipy.signal import find_peaks
from scipy.fft import fft

model = joblib.load("PPG_bp_model.joblib")
print("Model loaded!")

BUFFER_SIZE = 500
ppg_signal = []

HOST = "0.0.0.0"
PORT = 8888

def extract_features(ppg):
    p2p_0 = np.ptp(ppg)
    peaks, _ = find_peaks(ppg)
    valleys, _ = find_peaks(-ppg)
    AI = (np.max(ppg[peaks]) - np.min(ppg[valleys])) / p2p_0 if peaks.size > 0 and valleys.size > 0 else 0
    bd = np.std(ppg) / np.mean(ppg) if np.mean(ppg) != 0 else 0
    bcda = np.mean(np.diff(ppg))
    sdoo = np.std(np.diff(ppg))
    fft_vals = np.abs(fft(ppg))
    fft_peaks, _ = find_peaks(fft_vals)
    top_fft = sorted(fft_vals[fft_peaks], reverse=True)[:3]
    top_fft += [0] * (3 - len(top_fft))
    return [p2p_0, AI, bd, bcda, sdoo] + top_fft

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"TCP Server listening on port {PORT}...")

while True:
    client_socket, addr = server.accept()
    data = client_socket.recv(1024).decode().strip()

    if data.isdigit():
        ir_value = int(data)
        ppg_signal.append(ir_value)
        print(f"IR: {ir_value} | Buffer: {len(ppg_signal)}/500")

        if len(ppg_signal) >= BUFFER_SIZE:
            features = extract_features(np.array(ppg_signal[:BUFFER_SIZE]))
            sp, dp = model.predict([features])[0]
            response = f\"{int(sp)},{int(dp)}\\n\"
            ppg_signal = []  # Reset
        else:
            response = \"0,0\\n\"  # Default response

        client_socket.sendall(response.encode())
    else:
        print(f\"Invalid data from {addr}: {data}\")

    client_socket.close()