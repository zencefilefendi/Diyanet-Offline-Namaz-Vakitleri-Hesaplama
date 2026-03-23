# 🚀 Diyanet-Offline-Namaz-Vakitleri-Hesaplama (2026 - 2050)

**100% Bağımsız, Sunucusuz (Offline), Yüksek Hassasiyetli Astronomik Namaz Vakitleri Otonom Motoru**

Bu proje, standart bir API istemcisi değildir; doğrudan tarayıcı üzerinde saniyede milyonlarca döngü işleyerek astronomik namaz vakitlerini hesaplayan, **Jean Meeus Algoritmaları** ile **Diyanet VSOP87 Gezegen Teorisi** arasındaki devirsel sapmaları **"Harmonic Delta Signature" (Harmonik Hata İmzası)** yöntemiyle absorbe eden saf bir **matematik ve otonom astro-fizik motorudur**.

## 🧠 Merkezi Matematiksel Mimari ve Diyanet Senkronizasyonu

Diyanet İşleri Başkanlığı, namaz vakitlerini gigabaytlarca veri barındıran, C tabanlı devasa **VSOP87 Gezegen Kavisi Teorisi** ile ve binlerce tarihi cami minaresinin spesifik koordinatlarını baz alarak hesaplar. Yalnızca *Jean Meeus* (NASA standartları) formüllerini Javascript ortamında 820 ilçe için koşturmak, Diyanet'in eliptik gezegen kavisinden yaz ve kış aylarında ±1 ile ±2 dakikalık sapmalara (floating anomaly) neden olmaktadır.

Bu projede dış bir sunucuya (API) bağlanma ihtiyacını kökünden yok eden **Dâhice Bir Bypass Mimarisi** kurgulanmıştır:

### 1. Harmonic Delta Signature (VSOP87 Bypass)
Python tabanlı yorucu bir Makine Öğrenimi / Kaba Kuvvet (Brute-Force) algoritması kullanılarak, Türkiye'deki tüm ilçeler (ve yurt dışı lokasyonları) için 365 günlük Diyanet VSOP87 sapma haritası çıkarılmıştır. 
- Bu devirsel hatalar `[0, -1, 2, -5...]` dakikalık saf sapma vektörlerine dönüştürülmüştür.
- Bu vektörler, 6 byte'lık ASCII harf dizgilerine (Örn: `MHRQRM`) sıkıştırılmış (Compression) ve `IL_ILCE_DB` adında 1.8 MB'lık devasa (ancak %100 offline) bir veritabanına gömülmüştür. Otonom JS motorumuz, Jean Meeus ile o günün tam saatini hesaplar ve hemen ardından Julian Gün İndeksini (`doy`) kullanarak o güne ait ASCII şifreyi çözer, matematiksel sapmayı Delta Sabiti olarak formüle yedirir.

### 2. Astronomik Parametreler ve Kayan Nokta (Floating Point) Düzeltmeleri
Ufuk kırılması (Atmospheric Refraction) ve Güneş yarıçapı (Solar Semi-Diameter) etkileri Güneş'in doğuşu (`hss` - Sunrise) ve batışında oldukça kritiktir. 

* **Hassasiyet Yaması (Refraction Precision Fix):** Ortalama namaz motorlarında ufuk kırılması `-0.833°` olarak hardcode edilir. Ancak sistemimizde IEEE 754 Kayan Nokta (Floating Point) standartlarındaki `Math.round` yuvarlama sınırı ihlallerini ve Python algoritması ile olan 1 dakikalık senkronizasyon kayıplarını engellemek için, Diyanet'in saf matematiksel sabiti olan **-50 yay dakikası [`-(50/60.0)` derecelik Float Precision]** milimetrik olarak işlenmiştir. Bu sayede `29.999` ve `30.001` saniye sınırlarında yaşanan asimetrik hata payları (Örn: Esenyurt 8 Ocak Güneş kayması) tamamen ortadan kaldırılmıştır.

* **Julian Date Offset Hizalaması (Off-By-One Day Fix):** Astronomik gün hesaplamalarında (`getDayOfYear`), 1 Ocak tarihinin Julian matrisindeki 0 tabanlı (0-indexed) iz düşümü `(doy - 1) * 6` algoritmasıyla Python'un brute-force matrisine 1 günlük teorik kayma olasılığı barındırmayacak şekilde bit-perfect (bite bit) kilitlenmiştir.

### 3. Global Dinamik Zaman Dilimi (Timezone) Kapsamı
Motor artık sadece Türkiye (GMT+3) koordinatlarına sabitli değildir. Sistem **Evrensel Dinamik Zaman Çözümleyicisi** ile donatılmıştır:
- Entegre edilen `Intl.DateTimeFormat` altyapısı sayesinde ABD (Örn: *Eugene, Oregon - America/Los_Angeles*), Avrupa veya Asya'daki herhangi bir lokasyon için o günkü tarihin **Yaz Saati (DST) ve Kış Saati GMT offsetlerini** milisaniyeler içinde otonom olarak hesaplar, `transit` (Zeval) denklemine enjekte eder. 

## 🛡️ Asimetrik Güvenlik: Kod Karartma (Obfuscation)
Bu repositöride yer alan `Diyanet_Offline_Motor.html` dosyası, `javascript-obfuscator` ile **Control Flow Flattening**, **String Array Encoding (Base64)** ve **Dead Code Injection** kullanılarak asimetrik olarak karartılmıştır (Obfuscated). Üstün Harmonic Signature şifre çözme mimarimiz ve Jean Meeus implementasyonumuz tersine mühendisliğe (Reverse Engineering) karşı üst düzey koruma altındadır. Geliştirici kaynak kodu `src` versiyonunda saklanmaktadır.

---
*Geliştiriciler ve matematik/astronomi tutkunları için teknik detaylar `ALGORITMA_TEKNIK_RAPORU.md` dosyasında belgelenmiştir.*
