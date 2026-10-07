-- =====================================================
-- Föy 02 / Görev 5 — Referans bütünlüğünü sınama
-- 1) Var olmayan bir ders_id ile kayitlar'a INSERT deneyin.
-- 2) Kaydı olan bir dersi dersler'den DELETE etmeyi deneyin.
-- Aldığınız HATA mesajlarını sonuc/g5.txt dosyasına yapıştırın
-- ve dosyanın sonuna 1-2 cümleyle neden engellendiğini yazın.
-- =====================================================

-- Deneme 1: Var olmayan bir ders_id (9999) ile kayıt eklemeye çalışıyoruz.
-- dersler tablosunda ders_id=9999 diye bir kayıt yoktur.
-- PostgreSQL yabancı anahtar ihlali hatası verecektir.
INSERT INTO kayitlar (kayit_id, uye_id, ders_id, tarih)
VALUES (9999, 1, 9999, '2026-01-01');

-- Deneme 2: Kaydı bulunan bir dersi (ders_id=4, Core Güçlendirme) silmeye çalışıyoruz.
-- kayitlar tablosunda bu ders_id'ye ait satırlar bulunduğundan
-- PostgreSQL silme işlemini reddedecektir.
DELETE FROM dersler WHERE ders_id = 4;
