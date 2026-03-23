# Diyanet Vakitleri Otonom Motoru - Teknik ve Astrofizik Raporu

Bu rapor, `Diyanet_Offline_Motor.html` projesinde kullanılan yüksek hassasiyetli astronomik rektifikasyon dizilimlerini, "Harmonic Delta İmzası" mimarisini ve IEEE-754 sistemlerindeki spesifik Kayan Nokta (Floating Point) çözünürlük güncellemelerini detaylandırmaktadır.

## 1. Veritabanı Topolojisi ve Otonom Tespiti
Motor, Türkiye'deki 81 İlin tamamını ve 972 İlçesini evrensel bir veritabanında toplar.
- **Birinci Derece Kapsam (820 İlçe):** Diyanet'in yörünge eğrilerine %100 uyumu sağlayan şifrelenmiş `Harmonic Delta String` dizgilerine sahiptir.
- **İkinci Derece Kapsam (152 Fallback İlçesi):** Eğer özel Diyanet imzası yoksa (Örn: İstanbul/Adalar), Jean Meeus otonom motorumuz İlçe enlem (Latitude), boylam (Longitude) ve kesin Hiypsometrik Rakım (Altitude) değerlerini matematiksel olarak `transit` matrisinden geçirerek gerçek zamanı hesaplar.
- **Küresel Kapsam (Universal Timezone):** Sistem artık GMT+3 parametresinden kurtarılarak `Eugene, Oregon` (Amerika) gibi okyanus ötesi koordinatları algılayacak esnekliğe kavuşturulmuştur. `Intl.DateTimeFormat` kullanılarak Yaz Saati/Kış Saati (DST) periyotları offline olarak parse edilir.

## 2. Gök Mekaniği ve Jean Meeus İhlal Çözümleri
Güneşin konumsal deklinesini (`decl`) bulmak için Julian Date (JD) ve Equation of Time (`eqt` - Tadil-i Zaman) uygulanmaktadır.

### Dini Açı Geometrisi ve Yarıçap Kırılmaları (Refraction Anomalies)
1. **İmsak:** Güneş ufkun **18°** altında.
2. **Güneş Doğuş / Batış:** Güneşin üst diskinin ufuk çizgisinde belirmesi.
   - **Mühendislik Düzeltmesi (Refraction Precision Bugfix):** Daha önce `-0.833°` olarak hardcode edilen ufuk kırılması değeri, Python'un makine tabanlı float değerinden (Banker's Rounding çelişkisi yüzünden) Güneş vaktinde çok nadir 1 dakikalık sapma (Örn. Esenyurt 8 Ocak) yaratıyordu. Bu durum Diyanet'in tam rasyonel astronomik değeri olan **-50 yay dakikasına `-(50/60.0)`** eşitlenerek JS ile Python arasındaki .5000000 sınır asimetrisi tamamen yokedildi.
   - **Yükseklik (Rakım/Dip) Çarpanı:** Optik ufuk çizgisi sapması formüle dahil edilmiştir: `- (0.0347 * √Rakım)`.
3. **Zeval (Öğle):** Güneşin `transit` tepe noktasına ulaşması.
4. **İkindi:** Cisimlerin gölge boyunun, `Asr-ı Evvel` geometrisine ulaşması durumu (Arctangent fonksiyonu olan `ACOS(an/(COS(co.lat)*COS(s.decl)))` ile).
5. **Yatsı:** Güneş ufkun **17°** altında.

## 3. Harmonic Delta İmzası (VSOP87 Bypass)
Sistemin en can alıcı noktası: Gigabaytlarca veri gerektiren Diyanet VSOP87 Gezegen Teorisini (Planet Theory) bypass etmek.
- Python ile hazırlanan AI kalibratörümüz, Diyanet'in 365 günlük 2026 devirsel hatasını Meeus matematiğinden (Float limitlerine kadar inerek) çıkarmıştır.
- Her günün sapması `-5, +2, +1` gibi rasyonel sayılara çevrilip ASCII tablosunda `(M = 0)` baz alınarak şifrelenmiştir (`har` string).

### İndeks Çakışması (Off-By-One Day Alignment) Çözümü
Karşılaşılan en kompleks senkronizasyon hatalarından biri olan dizilim kayması giderilmiştir. JS motorunun `getDayOfYear()` metodunun 1 Ocak için `1` (veya `float > 0`) dönmesi sebebiyle sistem, Python'un 0 tabanlı (0‑indexed) matrisinde sürekli 1 GÜN İLERİ (`(doy*6)`) sıçrıyordu.  
Bu durum kod bloğunda **`(doy - 1) * 6`** mantığına çekilerek zaman/mekan uyumsuzluğu kökünden kazındı. Artık şifreler, ait olduğu günün astronomik floatına nokta atışı entegre edilmektedir!

*(Bu yazılım, algoritma gizliliğini korumak amacıyla `npx javascript-obfuscator` ile endüstriyel karartmaya tabi tutulmuştur. Kod çözümü yalnızca ana geliştirici tarafından deşifre edilebilir.)*
