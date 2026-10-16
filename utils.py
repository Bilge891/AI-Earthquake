import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def adres_koordinata_cevirmeci(adres_metni):
    # IP engeline takılmamak için özel bir isim verdik
    geolocator = Nominatim(user_agent="bilge_kagan_ai_earthquake_app") 
    
    # Adresi bulana kadar farklı formatlarda arama yapacak liste
    sorgular = [
        adres_metni, 
        f"{adres_metni}, Türkiye",
        f"{adres_metni}, Turkey"
    ]
    
    for sorgu in sorgular:
        try:
            location = geolocator.geocode(sorgu, timeout=10)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            print(f"Adres aranırken zaman aşımı veya hata: {e}")
            continue
            
    return None, None

def sismik_hafiza_hesapla(hedef_lat, hedef_lng, csv_path="guncel_veriler.csv", yaricap_km=50):
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return 0, 0, 0, 10.0
        
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
    geolocator = Nominatim(user_agent="turkiye_deprem_uygulamasi")
    try:
        parcalar = [p.strip() for p in adres_metni.split(",")]
        arama_termi = parcalar[-1] if len(parcalar) > 0 else adres_metni
        
        sorgular = [
            f"Park {arama_termi}",
            f"Deprem Toplanma Alanı {arama_termi}",
            f"Park {adres_metni}"
        ]
        
        konumlar = None
        for sorgu in sorgular:
            try:
                konumlar = geolocator.geocode(sorgu, exactly_one=False, limit=limit)
                if konumlar:
                    break
            except:
                continue
                
        if konumlar:
            alanlar = []
            for k in konumlar:
                p = k.address.split(",")
                sade_isim = ", ".join(p[:2]).strip()
                if sade_isim and sade_isim not in alanlar:
                    alanlar.append(sade_isim)
            return alanlar[:limit]
        else:
            return [
                f"{arama_termi} Şehir Parkı & Toplanma Alanı",
                f"{arama_termi} Atatürk Parkı",
                f"{arama_termi} Mahalle Spor ve Park Alanı"
            ]
    except Exception as e:
        print(f"Toplanma alanı hatası: {e}")
        return ["Genel Mahalle Parkı ve Açık Alanlar (AFAD Tarafından Belirlenen)"]