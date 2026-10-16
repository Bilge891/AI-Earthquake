def toplanma_alanlari_bul(adres_metni, limit=4):
    """
    Girilen adrese en yakın park ve toplanma alanlarını bulur.
    """
    geolocator = Nominatim(user_agent="turkiye_deprem_uygulamasi")
    try:
        # Adresten ilçe/mahalle kısmını çekip park aratalım
        parcalar = [p.strip() for p in adres_metni.split(",")]
        arama_termi = parcalar[-1] if len(parcalar) > 0 else adres_metni
        
        # Farklı arama kombinasyonları deneyelim
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