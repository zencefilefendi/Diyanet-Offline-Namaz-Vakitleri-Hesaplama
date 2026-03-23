# Diyanet Vakitleri Otonom Motoru - Teknik ve Astrofizik Raporu

Bu rapor, `Diyanet_Offline_Motor.html` projesinde kullanılan yüksek hassasiyetli astronomik rektifikasyon dizilimlerini, "Harmonic Delta İmzası" mimarisini ve IEEE-754 sistemlerindeki Kayan Nokta (Floating Point) çözünürlük güncellemelerini teknik hatlarıyla belgelemektedir.

## 1. Veritabanı Topolojisi ve Otonom Tespiti
Motor, Türkiye'deki 81 İlin tamamını ve 972 İlçesini, ayrıca global referans noktalarını kendi içerisinde taşır.
- **Birinci Derece Kapsam (820 İlçe):** Diyanet'in özel yörünge eğrilerine doğrudan uyumu sağlayan `Harmonic Delta String` dizgilerine sahiptir.
- **İkinci Derece Kapsam (152 Fallback İlçesi):** Eğer tanımlanmış özel bir imza yoksa (Örn: İstanbul/Adalar), otonom Jean Meeus algoritması söz konusu noktanın enlem (Latitude), boylam (Longitude) ve kesin Hiypsometrik Rakım (Altitude) koordinatlarını matematiksel olarak `transit` hesabına katarak gerçek zamanı üretir.
- **Küresel Kapsam (Universal Timezone):** Sistem spesifik olarak GMT+3'ten bağımsız çalışacak global bir altyapıya çekilmiştir. `Intl.DateTimeFormat` altyapısı kurularak bölgelerin (Örn: `Eugene, Oregon`) Yaz Saati (DST) sapmaları formüle doğrudan otomatik entegre edilmektedir.
- **Dinamik GPS Geometrisi (Autonomous Virtual District Matrix):** Sisteme, internetten bağımsız çalışan ve donanımsal ping atan bir `navigator.geolocation` modülü eklenmiştir. Mevcut `IL_ILCE_DB` veritabanında yer almayan koordinatlar için, anlık `[lat, lng, alt]` telemetrisi Jean Meeus mimarisine `on-the-fly` (anında üretilen) sanal bir lokasyon düğümü olarak eklenir ve mutlak astronomik hesaplama gerçekleştirilir.

## 2. Gök Mekaniği ve Jean Meeus Regülasyonları
Güneşin konumsal deklinesini (`decl`) hesaplamak amacıyla Julian Date (JD) ve Equation of Time (`eqt` - Tadil-i Zaman) kullanılmaktadır.

### Dini Açı Geometrisi ve Yarıçap Kırılmaları (Refraction Anomalies)
1. **İmsak:** Güneş ufkun **18°** altında.
2. **Güneş Doğuş / Batış:** Güneşin üst diskinin ufuk çizgisinde belirmesi.
   - **Mühendislik Düzeltmesi (Refraction Precision Fix):** Geleneksel hesaplamalarda `-0.833°` şeklindeki rasyonelliği kısıtlanmış Float, nadiren Banker's Rounding asimetrileri nedeniyle `+1` dakikalık hatalar verebiliyordu (Örn: Esenyurt Güneş vakti sınırı). Sorun, astronomik standartlardaki **-50 yay dakikasının** tam dönüşümü olan **`-(50/60.0)`** floatı ile stabilize edilerek JS ve backend Python çıktıları kesinkes eşitlenmiştir.
   - **Yükseklik (Rakım/Dip) Çarpanı:** Optik ufuk çizgisi hesabı formüle katılır: `- (0.0347 * √Rakım)`.
3. **Zeval (Öğle):** Güneşin `transit` tepe noktasına ulaşması.
4. **İkindi:** Asr-ı Evvel kuralını işleten Arctangent fonksiyonu `ACOS(an/(COS(co.lat)*COS(s.decl)))` izdüşümü.
5. **Yatsı:** Güneş ufkun **17°** altında.

## 3. Harmonic Delta İmzası (VSOP87 Bypass) Yapısı
Sistemin mimarisinde asıl rol oynayan özellik, devasa boyutlardaki Diyanet VSOP87 Gezegen Teorisinin çıktısına minimal boyutta entegre olmaktır.
- Python kalibratör komut dosyalarıyla Diyanet'in tam 365 günlük devirsel istatistiksel hatası Meeus referansından çıkarılır.
- Her günün kendi astronomik sapması `-5, +2, +1` şeklinde harita haline getirilip ASCII tablosunda `(M = 0)` karakteri ile kaydırılarak encode edilir (`har` string).

### İndeks Çakışması (Off-By-One Day Alignment) Çözümü
Karşılaşılan en önemli dizi (array) kaymalarından olan gün ofseti giderilmiştir. JS tabanlı `getDayOfYear()` modülü 1 Ocak için `1` değerini (veya 0'dan büyük bir float) verdiğinden, backend makinesinin 0 tabanlı (0‑indexed) ürettiği matriste sistemin `1` döngü ileri bakmasına (`(doy*6)`) neden oluyordu.  
Bu ofset kayması doğrudan **`(doy - 1) * 6`** eşitliği ile giderilerek her harf dizgisinin ilgili günün Julian izdüşümüne noktası noktasına uyması kesinleştirildi.

*(Yazılım mimarisinin güvenliği ve spesifik veri entegrasyonu kod tabanını korumak için `javascript-obfuscator` ile endüstriyel karartma (obfuscation) işlemine tabi tutulmuştur. İşlem gören üretim kodu `Diyanet_Offline_Motor.html` üzerinden yayımlanmaktadır.)*
