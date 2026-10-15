import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib

df = pd.read_csv('veriler.csv')
df['Olus tarihi'] = pd.to_datetime(df['Olus tarihi'])
df = df.sort_values(by='Olus tarihi').reset_index(drop=True)

df['Energy_Released'] = 10 ** (1.5 * df['xM'] + 4.8)

R = 6371.0
df['x_km'] = R * np.radians(df['Boylam']) * np.cos(np.radians(df['Enlem']))
df['y_km'] = R * np.radians(df['Enlem'])

coords = df[['x_km', 'y_km']].values
tree = cKDTree(coords)
radius_km = 50.0
neighbor_indices = tree.query_ball_tree(tree, r=radius_km)

timestamps = df['Olus tarihi'].values
energies = df['Energy_Released'].values

c_7d, c_30d, c_90d = [], [], []
e_7d, e_30d, e_90d = [], [], []

print("Çoklu zaman penceresi özellikleri hesaplanıyor...")

for i, neighbors in enumerate(neighbor_indices):
    current_time = timestamps[i]
    
    
    p_7 = (timestamps[neighbors] < current_time) & (timestamps[neighbors] >= current_time - np.timedelta64(7, 'D'))
    p_30 = (timestamps[neighbors] < current_time) & (timestamps[neighbors] >= current_time - np.timedelta64(30, 'D'))
    p_90 = (timestamps[neighbors] < current_time) & (timestamps[neighbors] >= current_time - np.timedelta64(90, 'D'))
    
    c_7d.append(np.sum(p_7))
    c_30d.append(np.sum(p_30))
    c_90d.append(np.sum(p_90))
    
    e_7d.append(np.sum(energies[neighbors][p_7]) if np.any(p_7) else 0.0)
    e_30d.append(np.sum(energies[neighbors][p_30]) if np.any(p_30) else 0.0)
    e_90d.append(np.sum(energies[neighbors][p_90]) if np.any(p_90) else 0.0)

df['Events_7d'] = c_7d
df['Events_30d'] = c_30d
df['Events_90d'] = c_90d
df['Energy_7d'] = e_7d
df['Energy_30d'] = e_30d
df['Energy_90d'] = e_90d

df['Target_Significant'] = (df['xM'] >= 4.0).astype(int)

feature_cols = [
    'Enlem', 'Boylam', 'Der(km)', 
    'Events_7d', 'Events_30d', 'Events_90d',
    'Energy_7d', 'Energy_30d', 'Energy_90d'
]

split_idx = int(len(df) * 0.8)
train_df, test_df = df.iloc[:split_idx], df.iloc[split_idx:]

X_train, y_train = train_df[feature_cols], train_df['Target_Significant']
X_test, y_test = test_df[feature_cols], test_df['Target_Significant']

scale_weight = (len(y_train) - sum(y_train)) / sum(y_train)

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.03,
    scale_pos_weight=scale_weight,
    random_state=42,
    n_jobs=-1
)

print("XGBoost Modeli Eğitiliyor...")
model.fit(X_train, y_train)

y_probs = model.predict_proba(X_test)[:, 1]
y_pred = (y_probs >= 0.35).astype(int) 

print("\n" + "="*40)
print(f"GELİŞTİRİLMİŞ ROC-AUC SCORE: {roc_auc_score(y_test, y_probs):.4f}")
print("="*40)
print("\nClassification Report:\n", classification_report(y_test, y_pred))


joblib.dump(model, 'seismic_xgb_model.pkl')
print("\n[BAŞARILI] Model 'seismic_xgb_model.pkl' olarak kaydedildi!")