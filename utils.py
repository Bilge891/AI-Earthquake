import pandas as pd
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
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return 0, 0, 0, 10.0  # 7d, 30d, 90d, ortalama_derinlik
        
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
        
        # O bölgedeki depremlerin ortalama derinliğini hesapla (yoksa genel ortalama / 10km)
        if not yakin_depremler.empty and 'depth' in yakin_depremler.columns:
            ort_derinlik = float(yakin_depremler['depth'].mean())
        elif 'depth' in df.columns:
            ort_derinlik = float(df['depth'].mean())
        else:
            ort_derinlik = 10.0
            
        return events_7d, events_30d, events_90d, round(ort_derinlik, 1)
    except Exception as e:
        print(f"Sismik hafıza hesaplama hatası: {e}")
        return 0, 0, 0, 10.0

def toplanma_alanlari_bul(adres_metni, limit=4):
    """
    Girilen adres çevresindeki park ve toplanma alanlarınıOpenStreetMap üzerinden sorgular.
    """
    geolocator = Nominatim(user_agent="turkiye_deprem_uygulamasi")
    try:
        # Adres çevresindeki parkları arayalım
        sorgu = f"Park, {adres_metni}, Turkey"
        konumlar = geolocator.geocode(sorgu, exactly_one=False, limit=limit)
        
        if konumlar:
            alanlar = []
            for k in konumlar:
                # Adres metnini sadeleştirelim
                parcalar = k.address.split(",")
                sade_isim = ", ".join(parcalar[:3])
                alanlar.append(sade_isim)
            return alanlar
        else:
            return [f"{adres_metni} yakınlarında kayıtlı açık park alanı tespit edilemedi."]
    except Exception as e:
        print(f"Toplanma alanı hatası: {e}")
        return ["Toplanma alanları sorgulanırken bir hata oluştu."]
    