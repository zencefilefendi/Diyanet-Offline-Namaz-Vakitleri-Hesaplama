#!/usr/bin/env python3
"""
HAR STRING YENİDEN KALİBRASYON ARACI
=====================================
Bu araç, Diyanet'in resmi namaz vakitleri kullanılarak har string'lerini
JavaScript motorunun kendi matematiğiyle uyumlu şekilde yeniden üretir.

KULLANIM:
  python3 har_recalibrate.py <il> <ilce> <yil>

Örnek:
  python3 har_recalibrate.py "Istanbul" "Arnavutkoy" 2026

Giriş dosyası: diyanet_<il>_<ilce>_<yil>.csv
  - Virgülle ayrılmış: tarih,imsak,gunes,ogle,ikindi,aksam,yatsi
  - Örnek satır: 2026-01-01,06:24,08:04,13:10,15:38,18:04,19:36

Çıktı: Güncellenmiş har string'i (kopyalayıp HTML'e yapıştırın)
"""
import sys
import math
import csv
import datetime
import argparse

# ============================================================
# JS ile birebir aynı formüller (floating-point bit düzeyinde)
# ============================================================
R = math.pi / 180
D = 180 / math.pi
SIN  = lambda a: math.sin(a * R)
COS  = lambda a: math.cos(a * R)
TAN  = lambda a: math.tan(a * R)
ASIN = lambda x: math.asin(x) * D
ACOS = lambda x: math.acos(max(-1.0, min(1.0, x))) * D
ACOT = lambda x: math.atan(1.0 / x) * D
fxa  = lambda a: a - 360 * math.floor(a / 360)

def jd(y, m, d):
    if m <= 2: y -= 1; m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    return (math.floor(365.25 * (y + 4716))
            + math.floor(30.6001 * (m + 1))
            + d + B - 1524.5)

def sun_pos(j):
    T  = (j - 2451545) / 36525
    L0 = fxa(280.46646 + 36000.76983 * T + 0.0003032 * T * T)
    M  = fxa(357.52911 + 35999.05029 * T - 0.0001537 * T * T)
    e  = 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T
    C  = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * SIN(M)
          + (0.019993 - 0.000101 * T) * SIN(2 * M)
          + 0.000289 * SIN(3 * M))
    om  = fxa(125.04 - 1934.136 * T)
    lam = L0 + C - 0.00569 - 0.00478 * SIN(om)
    eps = (23 + (26 + (21.448 - 46.815*T - 0.00059*T*T
                        + 0.001813*T*T*T) / 60) / 60
           + 0.00256 * COS(om))
    decl = ASIN(SIN(eps) * SIN(lam))
    y2   = TAN(eps / 2) ** 2
    eqt  = (y2 * SIN(2 * L0)
            - 2 * e * SIN(M)
            + 4 * e * y2 * SIN(M) * COS(2 * L0)
            - 0.5 * y2 * y2 * SIN(4 * L0)
            - 1.25 * e * e * SIN(2 * M))
    return {'decl': decl, 'eqt': eqt * D * 4 / 60}

def ha(a, lat, decl):
    n = -SIN(a) - SIN(lat) * SIN(decl)
    dn = COS(lat) * COS(decl)
    r = n / dn
    if r > 1 or r < -1:
        return 0
    return ACOS(r) / 15

def compute_base_times(y, m, d, lat, lng, alt, tz=3):
    j   = jd(y, m, d)
    s   = sun_pos(j)
    t   = 12 + tz - (lng / 15.0) - s['eqt']
    dip = 0.0347 * math.sqrt(max(0, alt))
    sr  = (50 / 60.0) + dip
    hf  = ha(18.0, lat, s['decl'])
    hss = ha(sr,   lat, s['decl'])
    hi  = ha(17.0, lat, s['decl'])
    an  = (SIN(ACOT(1 + TAN(abs(s['decl'] - lat))))
           - SIN(lat) * SIN(s['decl']))
    hasr = ACOS(an / (COS(lat) * COS(s['decl']))) / 15.0
    return [t - hf, t - hss, t, t + hasr, t + hss, t + hi]

def getDayOfYear_JS(y, m, d):
    """JS getDayOfYear fonksiyonunun Python karşılığı (0-indexed)"""
    start  = datetime.date(y - 1, 12, 31)
    target = datetime.date(y, m, d)
    return (target - start).days - 1

def hhmm_to_frac(s):
    """'HH:MM' → saat cinsinden kesirli sayı"""
    h, m = map(int, s.split(':'))
    return h + m / 60.0

def compute_delta(base_h, diyanet_hhmm):
    """JS base saati ve Diyanet HH:MM'i verince gerekli delta (dakika) hesapla"""
    diyanet_frac = hhmm_to_frac(diyanet_hhmm)
    # Gerekli: round(base_frac_min + delta) == diyanet_minute
    base_min  = (base_h - math.floor(base_h)) * 60
    diyanet_m = int(diyanet_hhmm.split(':')[1])
    for delta in range(-20, 21):
        result_frac = base_min + delta
        if round(result_frac) % 60 == diyanet_m:
            # Check hour too
            corrected_h = base_h + delta / 60.0
            corrected_hh = int(math.floor(corrected_h))
            corrected_min = round((corrected_h - math.floor(corrected_h)) * 60)
            if corrected_min == 60:
                corrected_min = 0
                corrected_hh += 1
            diyanet_hh = int(diyanet_hhmm.split(':')[0])
            if corrected_hh == diyanet_hh and corrected_min == diyanet_m:
                return delta
    raise ValueError(f"Delta bulunamadı: base={base_h:.4f}h, diyanet={diyanet_hhmm}")

def main():
    parser = argparse.ArgumentParser(description='har string yeniden kalibrasyon aracı')
    parser.add_argument('il',    help='İl adı (ör: Istanbul)')
    parser.add_argument('ilce',  help='İlçe adı (ör: Arnavutkoy)')
    parser.add_argument('yil',   type=int, help='Yıl (ör: 2026)')
    parser.add_argument('--lat', type=float, required=True, help='Enlem')
    parser.add_argument('--lng', type=float, required=True, help='Boylam')
    parser.add_argument('--alt', type=float, default=0,    help='Rakım (metre)')
    parser.add_argument('--tz',  type=float, default=3,    help='Saat dilimi (ör: 3)')
    parser.add_argument('--csv', required=True, help='Diyanet veri dosyası (CSV)')
    args = parser.parse_args()

    # CSV oku
    rows = []
    with open(args.csv, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            # Beklenen format: tarih,imsak,gunes,ogle,ikindi,aksam,yatsi
            date_str = row[0].strip()
            times    = [x.strip() for x in row[1:7]]
            rows.append((date_str, times))

    print(f"\n{'='*60}")
    print(f"  {args.il} - {args.ilce} {args.yil} HAR KALİBRASYONU")
    print(f"  Lat={args.lat}, Lng={args.lng}, Alt={args.alt}m, TZ=+{args.tz}")
    print(f"  Toplam gün: {len(rows)}")
    print(f"{'='*60}\n")

    har_chars = []
    errors = []

    for date_str, diyanet_times in rows:
        try:
            dt  = datetime.date.fromisoformat(date_str)
            y, m, d = dt.year, dt.month, dt.day
            bases = compute_base_times(y, m, d, args.lat, args.lng, args.alt, args.tz)
            deltas = []
            for i, base in enumerate(bases):
                delta = compute_delta(base, diyanet_times[i])
                deltas.append(delta)
            # Her delta bir char olarak encode et (77 = 'M' = 0)
            for delta in deltas:
                char_val = 77 + delta
                if char_val < 65 or char_val > 90:
                    print(f"  UYARI: {date_str} delta={delta} sınır dışı, kırpılıyor")
                    char_val = max(65, min(90, char_val))
                har_chars.append(chr(char_val))
        except Exception as ex:
            errors.append(f"  HATA {date_str}: {ex}")
            # Hata durumunda nötr karakter
            for _ in range(6):
                har_chars.append('M')

    har_string = ''.join(har_chars)

    print(f"Oluşturulan har string (ilk 60 char): {har_string[:60]}...")
    print(f"Toplam uzunluk: {len(har_string)} char ({len(har_string)//6} gün)")
    print()

    if errors:
        print("HATALAR:")
        for e in errors:
            print(e)
        print()

    # HTML'e yapıştırma için hazır çıktı
    print("HTML'e yapıştırılacak har değeri:")
    print(f'  "har": "{har_string}"')
    print()

    # Doğruluk kontrolü: her günü geri hesapla
    print("Doğruluk kontrolü (ilk 5 gün):")
    print(f"{'Tarih':<12} {'İmsak':>6} {'Güneş':>6} {'Öğle':>6} {'İkindi':>7} {'Akşam':>7} {'Yatsı':>7}")
    print("-"*58)
    for i, (date_str, diyanet_times) in enumerate(rows[:5]):
        dt = datetime.date.fromisoformat(date_str)
        y, m, d = dt.year, dt.month, dt.day
        doy = getDayOfYear_JS(y, m, d)
        idx = max(0, min(364, doy)) * 6
        if idx + 5 < len(har_string):
            deltas = [ord(har_string[idx+j])-77 for j in range(6)]
        else:
            deltas = [0]*6
        bases = compute_base_times(y, m, d, args.lat, args.lng, args.alt, args.tz)
        results = []
        for j, base in enumerate(bases):
            corrected = base + deltas[j]/60.0
            mins = round((corrected - math.floor(corrected)) * 60)
            hrs  = int(math.floor(corrected))
            if mins == 60: mins = 0; hrs += 1
            results.append(f"{hrs:02d}:{mins:02d}")
        ok = all(results[j] == diyanet_times[j] for j in range(6))
        status = "✅" if ok else "⚠️"
        print(f"{date_str:<12} {' '.join(results)} {status}")

if __name__ == '__main__':
    main()
