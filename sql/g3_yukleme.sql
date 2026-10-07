-- =====================================================
-- Föy 02 / Görev 3 — Dört CSV'nin yüklenmesi
-- COPY komutlarını FK sırasına dikkat ederek yazın.
-- Doğrulama sorgusunun çıktısını sonuc/g3.txt'ye kaydedin.
-- =====================================================

-- Yükleme sırası yabancı anahtar bağımlılıklarına göre belirlendi:
-- 1. egitmenler  (hiçbir FK taşımaz; dersler tarafından referans alınır)
-- 2. uyeler      (hiçbir FK taşımaz; kayitlar tarafından referans alınır)
-- 3. dersler     (egitmenler'i referans alır → önce egitmenler yüklenmeli)
-- 4. kayitlar    (hem uyeler hem dersler'i referans alır → en son yüklenir)

COPY egitmenler (egitmen_id, ad, brans)
FROM '/veri/egitmenler.csv'
WITH (FORMAT CSV, HEADER true);

COPY uyeler (uye_id, ad, dogum_yili)
FROM '/veri/uyeler.csv'
WITH (FORMAT CSV, HEADER true);

COPY dersler (ders_id, ad, egitmen_id, kontenjan)
FROM '/veri/dersler.csv'
WITH (FORMAT CSV, HEADER true);

COPY kayitlar (kayit_id, uye_id, ders_id, tarih)
FROM '/veri/kayitlar.csv'
WITH (FORMAT CSV, HEADER true);

-- Doğrulama sorgusu — çıktıyı sonuc/g3.txt dosyasına kaydedin
SELECT (SELECT COUNT(*) FROM egitmenler) AS egitmen,
       (SELECT COUNT(*) FROM uyeler)     AS uye,
       (SELECT COUNT(*) FROM dersler)    AS ders,
       (SELECT COUNT(*) FROM kayitlar)   AS kayit;
