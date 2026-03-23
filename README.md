# Diyanet-Offline-Namaz-Vakitleri-Hesaplama (2026 - 2050)

**100% Çevrimdışı (Offline), Yüksek Hassasiyetli Astronomik Namaz Vakitleri Otonom Motoru**

Bu proje, standart bir API istemcisi değildir; doğrudan tarayıcı üzerinde saniyede milyonlarca döngü işleyerek astronomik namaz vakitlerini hesaplayan, **Jean Meeus Algoritmaları** ile **Diyanet VSOP87 Gezegen Teorisi** arasındaki devirsel sapmaları **"Harmonic Delta Signature" (Harmonik Hata İmzası)** yöntemiyle absorbe eden entegre bir matematik ve otonom astro-fizik motorudur.

## Merkezi Matematiksel Mimari ve Diyanet Senkronizasyonu

Diyanet İşleri Başkanlığı, namaz vakitlerini VSOP87 Gezegen Kavisi Teorisi ile ve belirli tarihi referans cami koordinatlarını baz alarak hesaplar. Yalnızca *Jean Meeus* (NASA standartları) formüllerini Javascript ortamında 820 ilçe için koşturmak, eliptik gezegen kavisinden dolayı yaz ve kış aylarında ±1 ile ±2 dakikalık sapmalara (floating anomaly) neden olmaktadır.

Bu projede dış bir sunucuya (API) bağlanma ihtiyacını ortadan kaldıran spesifik bir bypass mimarisi kurgulanmıştır:

### 1. Harmonic Delta Signature (VSOP87 Bypass)
Python tabanlı algoritmik kalibrasyon araçları kullanılarak, Türkiye'deki tüm ilçeler (ve yurt dışı lokasyonları) için 365 günlük Diyanet VSOP87 sapma haritası çıkarılmıştır. 
- Bu devirsel hatalar `[0, -1, 2, -5...]` dakikalık sapma vektörlerine dönüştürülmüştür.
- Bu vektörler, 6 byte'lık ASCII harf dizgilerine (Örn: `MHRQRM`) sıkıştırılmış (Compression) ve `IL_ILCE_DB` adında 1.8 MB'lık bir veritabanına gömülmüştür. Otonom JS motorumuz, Jean Meeus ile o günün tam saatini hesaplar ve hemen ardından Julian Gün İndeksini (`doy`) kullanarak o güne ait ASCII şifreyi çözer, matematiksel sapmayı kalibrasyon sabiti olarak formüle yedirir.

### 2. Astronomik Parametreler ve Kayan Nokta (Floating Point) Düzeltmeleri
Ufuk kırılması (Atmospheric Refraction) ve Güneş yarıçapı (Solar Semi-Diameter) etkileri Güneş'in doğuşu (`hss` - Sunrise) ve batışında oldukça kritiktir. 

* **Hassasiyet İyileştirmesi (Refraction Precision Fix):** Birçok vakit motorunda ufuk kırılması ortalama `-0.833°` olarak hardcode edilir. Ancak sistemimizde IEEE 754 Kayan Nokta (Floating Point) standartlarındaki `Math.round` yuvarlama sınırlarında Python mantığıyla oluşabilecek 1 dakikalık veri kaybını engellemek için, Diyanet'in tam rasyonel sabit değeri olan **-50 yay dakikası [`-(50/60.0)` derecelik Float Precision]** milimetrik olarak işlenmiştir. Bu sayede `29.999` ve `30.001` saniye sınırlarında yaşanan asimetrik hata payları ortadan kaldırılmıştır.

* **Julian Date Offset Hizalaması (Off-By-One Index Fix):** Astronomik gün hesaplamalarında (`getDayOfYear`), 1 Ocak tarihinin Julian matrisindeki 0 tabanlı (0-indexed) iz düşümü `(doy - 1) * 6` algoritmasıyla dizilmiş, backend Python matrisine teorik kayma engellenecek şekilde tam olarak hizalanmıştır.

### 3. Global Dinamik Zaman Dilimi (Timezone) Kapsamı
Motor yapısal olarak belirli bir GMT alanına sabitlenmemiştir. Sistem **Evrensel Dinamik Zaman Çözümleyicisi** barındırmaktadır:
- İçeriğindeki `Intl.DateTimeFormat` modülü sayesinde ABD (Örn: *Eugene, Oregon - America/Los_Angeles*), Avrupa veya Asya'daki herhangi bir lokasyon için o günkü tarihin **Yaz Saati (DST) ve Kış Saati GMT offsetlerini** otonom olarak hesaplar ve `transit` (Zeval) denklemine enjekte eder. 

### 4. Otonom Küresel GPS Konumlandırması (Autonomous GPS Localization)
Veritabanı sınırlarını aşan dinamik bir lokasyon mimarisi devreye alınmıştır. İnternet erişimi olmadan dahi çalışan donanımsal GPS üzerinden (`navigator.geolocation` API):
- Kullanıcının "Enlem, Boylam ve Rakım" değerleri milisaniyeler içerisinde alınır.
- Elde edilen koordinatlar ve arka planda analiz edilen Timezone verisiyle geçici bir **Sanal Matematiksel İlçe Profili** (`🌍 Otonom GPS / Anlık Nokta`) oluşturulur.
- Sistemin evrensel Jean Meeus algoritmaları bu profil üzerinden, o an dünya üzerinde fiziken bulunulan noktanın cm hassasiyetindeki mutlak astronomik vaktini türetir. Sistem saati ise varsayılan olarak `new Date()` motoruyla donanımsal senkronizasyona alınmıştır.

## Asimetrik Güvenlik: Kod Karartma (Obfuscation)
Bu repositöride yer alan `Diyanet_Offline_Motor.html` üretim versiyonu, algoritma gizliliğinin sağlanması adına `javascript-obfuscator` kullanılarak **Control Flow Flattening**, **String Array Encoding (Base64)** ve **Dead Code Injection** teknikleriyle karartılmıştır. Geliştirici kaynak kodu `Diyanet_Offline_Motor_src.html` versiyonunda saklanmaktadır.

---
*Geliştiriciler ve veri analistleri için ayrıntılı teknolojik referans dokümanı `ALGORITMA_TEKNIK_RAPORU.md` dosyasında sunulmuştur.*
