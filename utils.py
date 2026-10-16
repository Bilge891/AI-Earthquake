from geopy.geocoders import Nominatim

def adres_koordinata_cevirmeci(adres_metni):
    # OpenStreetMap Nominatim servisini başlatıyoruz
    geolocator = Nominatim(user_agent="turkiye_deprem_uygulamasi")
    try:
        # Türkiye içinde daha isabetli arama yapmak için adrese ", Turkey" ekliyoruz
        location = geolocator.geocode(f"{adres_metni}, Turkey")
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Adres dönüştürme hatası: {e}")
        return None, None
    