import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def adres_koordinata_cevirmeci(adres_metni):
    geolocator = Nominatim(user_agent="turkiye_deprem_uygulamasi")
    try:
        location = geolocator.geocode(f"{adres_metni}, Turkey")
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Adres dönüştürme hatası: {e}")
        return None, None

def sismik_hafiza_hesapla(hedef_lat, hedef_lng, csv_path="guncel_veriler.csv", yaricap_km=50):
    """
    Belirtilen koordinatın etrafındaki (örn: 50 km yarıçap) son 7, 30 ve 90 gündeki deprem sayılarını otomatik hesaplar.
    """
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return 0, 0, 0
        
        df['date_time'] = pd.to_datetime(df['date_time'])
        simdi = pd.Timestamp.now()
        
        def mesafe_bul(row):
            return geodesic((hedef_lat, hedef_lng), (row['lat'], row['lng'])).km
        
        df['mesafe_km'] = df.apply(mesafe_bul, axis=1)
        
        yakin_depremler = df[df['mesafe_km'] <= yaricap_km].copy()
        
        yakin_depremler['gun_farki'] = (simdi - yakin_depremler['date_time']).dt.days
        
        events_7d = int((yakin_depremler['gun_farki'] <= 7).sum())
        events_30d = int((yakin_depremler['gun_farki'] <= 30).sum())
        events_90d = int((yakin_depremler['gun_farki'] <= 90).sum())
        
        return events_7d, events_30d, events_90d
    except Exception as e:
        print(f"Sismik hafıza hesaplama hatası: {e}")
        return 0, 0, 0