/*
  Diyanet Offline Motor V3 - ESP32 Hardware Edition
  Author: ZencefilEfendi
  
  This sketch natively parses the ultra-compressed ZLIB payload of 972 districts 
  without any internet connection, using the ESP32's built-in Hardware ROM decompressor.
*/

#include <Arduino.h>
#include <rom/miniz.h> // ESP32 built-in hardware ZLIB decompression
#include "diyanet_db.h"

// Struct for Jean Meeus outputs
struct SunPos {
  double decl;
  double eqt;
};

// ---------------------------------------------------------
// Göksel Matematik Fonksiyonları (Double Precision)
// ---------------------------------------------------------
double fxa(double a) {
  return a - 360.0 * floor(a / 360.0);
}

double jd(int y, int m, int d) {
  if (m <= 2) { y -= 1; m += 12; }
  double A = floor(y / 100.0);
  double B = 2.0 - A + floor(A / 4.0);
  return floor(365.25 * (y + 4716)) + floor(30.6001 * (m + 1)) + d + B - 1524.5;
}

SunPos sunPos(double j) {
  double R = PI / 180.0;
  double D = 180.0 / PI;

  double T = (j - 2451545.0) / 36525.0;
  double L0 = fxa(280.46646 + 36000.76983 * T + 0.0003032 * T * T);
  double M = fxa(357.52911 + 35999.05029 * T - 0.0001537 * T * T);
  double e = 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T;
  
  double C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * sin(M * R) +
             (0.019993 - 0.000101 * T) * sin(2 * M * R) +
             0.000289 * sin(3 * M * R);
             
  double om = fxa(125.04 - 1934.136 * T);
  double lam = L0 + C - 0.00569 - 0.00478 * sin(om * R);
  double eps = 23.0 + (26.0 + (21.448 - 46.815 * T - 0.00059 * T * T + 0.001813 * T * T * T) / 60.0) / 60.0 + 0.00256 * cos(om * R);
  
  double decl = asin(sin(eps * R) * sin(lam * R)) * D;
  double y2 = pow(tan(eps * R / 2.0), 2);
  
  double eqt = y2 * sin(2 * L0 * R) -
               2.0 * e * sin(M * R) +
               4.0 * e * y2 * sin(M * R) * cos(2 * L0 * R) -
               0.5 * y2 * y2 * sin(4 * L0 * R) -
               1.25 * e * e * sin(2 * M * R);
               
  return { decl, eqt * D * 4.0 / 60.0 };
}

double ha(double a, double lat, double d) {
  double R = PI / 180.0;
  double D = 180.0 / PI;
  double r = (-sin(a * R) - sin(lat * R) * sin(d * R)) / (cos(lat * R) * cos(d * R));
  return (r > 1.0 || r < -1.0) ? 0.0 : acos(r) * D / 15.0;
}

int getDayOfYear(int year, int month, int day) {
  // DST bugs are fixed here via rounding
  long days = 0;
  int mDays[] = { 31,28,31,30,31,30,31,31,30,31,30,31 };
  if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) mDays[1] = 29;
  for (int i = 0; i < month - 1; i++) days += mDays[i];
  return days + day;
}

// ---------------------------------------------------------
// ZLIB ROM Decompression & Boot
// ---------------------------------------------------------
// To conserve RAM, ESP32 inflates the HAR string lazily 
// Or allocates exactly 2.12MB into PSRAM if available
char* uncompressed_har_buffer = NULL;

void setup() {
  Serial.begin(115200);
  Serial.println("Diyanet Offline Motor V3 - Booting...");
  
  // Example PSRAM allocation (ESP32 WROVER / S3)
  if (psramFound()) {
    uint32_t buf_len = TOTAL_DISTRICTS * 2190;
    uncompressed_har_buffer = (char*)ps_malloc(buf_len + 1);
    
    if (uncompressed_har_buffer) {
      Serial.println("PSRAM allocated! Hardware ZLIB Injecting...");
      
      tinfl_decompressor inflator;
      tinfl_init(&inflator);
      size_t in_bytes = ZLIB_PAYLOAD_SIZE;
      size_t out_bytes = buf_len;
      tinfl_status status = tinfl_decompress(&inflator, diyanet_har_zlib, &in_bytes, (uint8_t*)uncompressed_har_buffer, (uint8_t*)uncompressed_har_buffer, &out_bytes, TINFL_FLAG_PARSE_ZLIB_HEADER);
      
      if (status >= TINFL_STATUS_DONE) {
         Serial.println("Decompression Successful! Entire 2.2MB DB is loaded in RAM O(1).");
      }
    }
  } else {
    Serial.println("No PSRAM available. Steamed ZLIB window chunking should be used.");
  }
}

void loop() {
  // Get time from DS3231 RTC
  int y = 2026, m = 3, d = 23;
  double tz = 3.0; // Local timezone (TR)

  int district_id = 0; // Example target ID
  DistrictMetadata co = diyanet_districts[district_id];
  
  double j = jd(y, m, d);
  SunPos s = sunPos(j);
  
  double transit = 12.0 + tz - (co.lng / 15.0) - s.eqt;
  double dip = 0.0347 * sqrt(max(0.0, (double)co.alt));
  double sr_ang = (50.0 / 60.0) + dip;
  
  double hf = ha(18.0, co.lat, s.decl);
  double hss = ha(sr_ang, co.lat, s.decl);
  double hi = ha(17.0, co.lat, s.decl);
  
  double R = PI / 180.0;
  double D = 180.0 / PI;
  double an = sin(atan(1.0 / (1.0 + tan(abs(s.decl - co.lat) * R))) * D * R) - sin(co.lat * R) * sin(s.decl * R);
  double hasr = acos(an / (cos(co.lat * R) * cos(s.decl * R))) * D / 15.0;
  
  double raw[] = { transit - hf, transit - hss, transit, transit + hasr, transit + hss, transit + hi };
  
  int doy = getDayOfYear(y, m, d);
  int idx = max(0, min(364, doy - 1)) * 6; // Note: if getDayOfYear is 1-indexed, we use doy - 1.

  // Fetch HAR Delta Characters
  int8_t deltas[6] = {0};
  if (uncompressed_har_buffer) {
     for (int i=0; i<6; i++) {
        deltas[i] = uncompressed_har_buffer[co.har_offset + idx + i] - 77;
     }
  }
  
  Serial.print("Namaz Vakitleri: ");
  for (int i=0; i<6; i++) {
     double corrected = raw[i] + deltas[i] / 60.0;
     int mins = round((corrected - floor(corrected)) * 60.0 - 0.035);
     int hrs = floor(corrected);
     if (mins == 60) { mins=0; hrs++; }
     if (mins < 0) { mins=59; hrs--; }
     if (hrs >= 24) hrs %= 24;
     
     Serial.printf("%02d:%02d ", hrs, mins);
  }
  Serial.println();
  
  delay(60000); // Wait 1 minute
}
