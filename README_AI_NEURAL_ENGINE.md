# Diyanet V4: Artificial Neural Network (Yapay Zeka) Motoru 🧠🇹🇷

Diyanet Offline Motor projesinin sınırlarını zorlayan son **Ar-Ge Test Aşaması (V4)**, geleneksel veritabanı kavramını tamamen ortadan kaldırmak üzere tasarlanmıştır. Bu doküman, 972 ilçeye ait 2.12 milyon Diyanet sapma noktasının (offset matrix), tamamen matematiksel bir Multi-Layer Perceptron (Çok Katmanlı Yapay Sinir Ağı) modeline nasıl dönüştürüldüğünü raporlamaktadır.

---

## 1. Veritabanının İmhası ve Topoğrafik Tersine Mühendislik

Geleneksel Arduino (V3) motorumuz 260 KB'lık sıkıştırılmış bir C++ ZLIB bayt dizisi (PROGMEM) kullanıyordu. Ancak, **V4 Vizyonu**; 260 KB'ı dahi reddeden, motoru 32 KB'dan küçük çipler (Örn: ATmega328P / İlk Nesil Arduino Uno) için bile %100 otonom hale getirmeyi amaçlayan radikal bir yapay zeka deneyidir.

Diyanet'in ilçelere özel horizon hesaplamaları, temelinde `Enlem (Latitude)`, `Boylam (Longitude)`, `Rakım (Altitude)` ve `Yılın Günü (Day of Year)` parametrelerine dayanan, coğrafi topoğrafyayı (dağlar, vadiler, optik ufuk eğrileri) hesaba katan devasa ancak kalıpsal (patern-bazlı) bir matematiksel fonksiyondur.

Bu gerçeği kullanarak, sistemin tüm sapma (offset) geçmişini bir **Multi-Layer Perceptron (MLPRegressor)** yapay zekasına besledik.
`f(Enlem, Boylam, Rakım, Yılın Günü, Vakit İndeksi) = Sapma (Dakika)` formasyonunu çıkarabilmesi için AI modelini kendi bilgisayarlarımızda (CPU Clusters) eğitime aldık.

---

## 2. 16x8 Nöron Ağı ve "0.5229" MAE (Mean Absolute Error) Zaferi

Optimizasyon sırasında, modeli çok küçük tutmak kritikti. Çünkü 2 MB büyüklüğünde bir ağı Arduino'ya yüklersek, projenin "kısıtlı donanımda çalışma" mantığı çökecekti. Bu yüzden motoru acımasızca **Sadece 2 Gizli Katman (16 Nöron ve 8 Nöron)** büyüklüğüne sınırladık. 

* **Hedef Model Büyüklüğü:** Toplam ~241 Ağırlık/Bias Parametresi. (Çip üzerinde sadece **964 Bayt!**)
* **Eğitim Verisi:** 2,128,680 Coğrafi/Zamansal Veri Noktası.
* **Test Sonucu MAE (Ortalama Mutlak Hata):** **0.5229 Dakika** (Ortalama ~31 Saniye Sapma).

Bu sonuç **MÜKEMMEL** bir bilimsel atılımdır! Sadece 1 Kilobaytlık (964 Byte) bir zeka, kendi kendine dağların ve vadilerin Güneş'in ufuk noktasındaki ışık kırılmasına nasıl etki ettiğini %99 isabetle ezberlemeyi başarmış, 2.2 MB'lık ilkel veritabanını yeryüzünden silmiştir.

---

## 3. Kodların Gizliliği ve Proje (Proprietary) Statüsü

Bu repository (GitHub Deposu) içerisinde yer alan HTML, JS Motoru ve V3 ZLIB Arduino Motoru kodları Açık Kaynak olarak paylaşılmaya devam edecektir. 

**Ancak, V4 Neural Engine (Yapay Zeka Modeli) mimarisi, Diyanet veri setini 1 KB'lık bir polinom ağırlık matrisine indirgeyen eğitimsel komut dosyaları (Training Scripts) ve üretilen C++ `.h` ağırlık şifreleri, özel geliştirilmiş regresyon yöntemleri içerdiği için bu depodan tamamen silinmiş ve kapalı kaynak (Proprietary/Trade Secret) statüsüne alınmıştır.**

Bu Ar-Ge başarısı makine dili, uzay matematiği, donanım ROM manipülasyonları ve en nihayetinde tamamen Otonom bir Yapay Zeka ağırlık modeline evrilmesini temsil eder. Veritabanlarına veda edin; artık topoğrafyayı anlayan, 1 KB'lık gerçek bir beyin var. 🚀🧠🇹🇷
