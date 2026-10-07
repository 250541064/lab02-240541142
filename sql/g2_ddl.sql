-- =====================================================
-- Föy 02 / Görev 2 — Dört tablonun DDL'i
-- ER diyagramını tablolara dönüştürün: egitmenler,
-- uyeler, dersler, kayitlar. Birincil ve yabancı
-- anahtarları unutmayın. Tablo oluşturma SIRASI önemlidir!
-- =====================================================

-- 1. Önce referans verilen (ana) tablolar oluşturulur.
--    egitmenler ve uyeler hiçbir yabancı anahtar taşımaz.

CREATE TABLE egitmenler (
    egitmen_id  INTEGER      PRIMARY KEY,
    ad          VARCHAR(100) NOT NULL,
    brans       VARCHAR(100) NOT NULL
);

CREATE TABLE uyeler (
    uye_id      INTEGER      PRIMARY KEY,
    ad          VARCHAR(100) NOT NULL,
    dogum_yili  INTEGER      NOT NULL
);

-- 2. dersler; egitmenler tablosuna referans verir (1:N ilişkisi).
--    Bir eğitmen birden çok ders verebilir; her dersin tek eğitmeni vardır.

CREATE TABLE dersler (
    ders_id     INTEGER      PRIMARY KEY,
    ad          VARCHAR(200) NOT NULL,
    egitmen_id  INTEGER      NOT NULL REFERENCES egitmenler(egitmen_id),
    kontenjan   INTEGER      NOT NULL
);

-- 3. kayitlar; N:M ilişkiyi çözen ara tablo.
--    Her kayıt bir üyeyi ve bir dersi bağlar; kayıt tarihini de taşır.

CREATE TABLE kayitlar (
    kayit_id    INTEGER      PRIMARY KEY,
    uye_id      INTEGER      NOT NULL REFERENCES uyeler(uye_id),
    ders_id     INTEGER      NOT NULL REFERENCES dersler(ders_id),
    tarih       DATE         NOT NULL
);
