import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# -------------------------------
#ACESSING THE FOLDER
# -------------------------------
base_folder = "/content/drive/MyDrive/PROJECT _E/data"

fold_files = [
    os.path.join(base_folder, "feat_fold_0.csv"),
    os.path.join(base_folder, "feat_fold_1.csv"),
    os.path.join(base_folder, "feat_fold_2.csv"),
    os.path.join(base_folder, "feat_fold_3.csv"),
    os.path.join(base_folder, "feat_fold_4.csv")
]

# -------------------------------
# Load all folds
# -------------------------------
dfs = [pd.read_csv(file) for file in fold_files]
df = pd.concat(dfs, ignore_index=True)

print(f"Loaded data shape: {df.shape}")

# -------------------------------
# Select input & output
# -------------------------------
ppg_fft_cols = [col for col in df.columns if col.startswith('ppg_fft_peaks')]

static_features = ['p2p_0', 'AI', 'bd', 'bcda', 'sdoo']

input_features = static_features + ppg_fft_cols
output_labels = ['SP', 'DP']

X = df[input_features]
y = df[output_labels]

groups = df['patient']  # Group by patient ID

print(f"Features: {input_features}")
print(f"X shape: {X.shape} | y shape: {y.shape}")

# -------------------------------
# Patient-wise split
# -------------------------------
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

for train_idx, test_idx in splitter.split(X, y, groups):
    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]
    train_patients = groups.iloc[train_idx].unique()
    test_patients = groups.iloc[test_idx].unique()

print(f"Unique train patients: {len(train_patients)}")
print(f"Unique test patients: {len(test_patients)}")

# -------------------------------
# Train Random Forest
# -------------------------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("Model training done!")

# -------------------------------
# Evaluate
# -------------------------------
y_pred = model.predict(X_test)

mse_sp = mean_squared_error(y_test['SP'], y_pred[:, 0])
mse_dp = mean_squared_error(y_test['DP'], y_pred[:, 1])

r2_sp = r2_score(y_test['SP'], y_pred[:, 0])
r2_dp = r2_score(y_test['DP'], y_pred[:, 1])

print(f"SP → MSE: {mse_sp:.2f} | R²: {r2_sp:.2f}")
print(f"DP → MSE: {mse_dp:.2f} | R²: {r2_dp:.2f}")

# -------------------------------
# Save the model
# -------------------------------
model_path = "/content/drive/MyDrive/PROJECT _E/MODELS"
save_path = os.path.join(model_path, "PPG_bp_model.joblib")
joblib.dump(model, save_path)

print(f"Model saved at: {save_path}")