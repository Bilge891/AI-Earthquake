import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from utils import adres_koordinata_cevirmeci

st.set_page_config(
    page_title="Sismik Risk Analiz Paneli",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #D32F2F;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Kontrol Paneli")
st.sidebar.markdown("---")

st.sidebar.subheader("Konum Bilgisi")

adres_input = st.sidebar.text_input("Adres / İlçe Girin:", placeholder="Örn: Kadıköy, İstanbul")

enlem = 40.80
boylam = 28.50

if adres_input:
    lat_bulunan, lng_bulunan = adres_koordinata_cevirmeci(adres_input)
    if lat_bulunan and lng_bulunan:
        enlem = lat_bulunan
        boylam = lng_bulunan
        st.sidebar.success(f"Adres Bulundu!\nEnlem: {enlem:.2f}, Boylam: {boylam:.2f}")
    else:
        st.sidebar.error("Adres bulunamadı, varsayılan konum kullanılıyor.")

derinlik = st.sidebar.number_input("Derinlik (km)", min_value=1.0, max_value=100.0, value=15.0)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Son 50 km Sismik Hafıza")
events_7d = st.sidebar.number_input("Son 7 Gün Deprem Sayısı", value=3, min_value=0)
events_30d = st.sidebar.number_input("Son 30 Gün Deprem Sayısı", value=14, min_value=0)
events_90d = st.sidebar.number_input("Son 90 Gün Deprem Sayısı", value=45, min_value=0)

st.title("Yapay Zeka Destekli Sismik Risk Tahmin Motoru")
st.caption("XGBoost Modeli & Fizik Tabanlı Sismik Enerji Birikim Analizi")
st.divider()

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("Risk Tahmin Alanı")
    
    if st.button("Sismik Riski Hesapla", use_container_width=True):
        with st.spinner("Model çalıştırılıyor..."):
            try:
                model = joblib.load('seismic_xgb_model.pkl')
                
                
                e7 = events_7d * (10 ** (1.5 * 3.0 + 4.8))
                e30 = events_30d * (10 ** (1.5 * 3.0 + 4.8))
                e90 = events_90d * (10 ** (1.5 * 3.0 + 4.8))

                input_df = pd.DataFrame([{
                    'Enlem': enlem,
                    'Boylam': boylam,
                    'Der(km)': derinlik,
                    'Events_7d': events_7d,
                    'Events_30d': events_30d,
                    'Events_90d': events_90d,
                    'Energy_7d': e7,
                    'Energy_30d': e30,
                    'Energy_90d': e90
                }])

                olasilik = model.predict_proba(input_df)[0][1]
                yuzde = olasilik * 100

                st.metric(label="M ≥ 4.0 Deprem Olasılığı", value=f"%{yuzde:.1f}")

                if olasilik >= 0.35:
                    st.error("**YÜKSEK SİSMİK RİSK**: Bölgede gerilim birikimi tespit edildi.")
                else:
                    st.success("🟢 **DÜŞÜK SİSMİK RİSK**: Normal arka plan hareketliliği gözlemleniyor.")
                    
                st.info(f"**Seçili Konum:** {enlem}°N, {boylam}°E | **Derinlik:** {derinlik} km")

            except Exception as e:
                st.error(f"Model yüklenirken bir hata oluştu: {e}")
    else:
        st.info("👈 Sol menüden parametreleri ayarlayıp **'Sismik Riski Hesapla'** butonuna tıklayın.")

with col2:
    st.subheader("🗺️ Merkez Üssü Konum Haritası")
    
    map_df = pd.DataFrame({
        'lat': [enlem],
        'lon': [boylam]
    })

    st.map(map_df, zoom=7, size=200)

