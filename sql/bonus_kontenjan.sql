-- =====================================================
-- Meydan Okuma — Kontenjan Kısıtı (+5 puan)
-- ALTER TABLE ile kontenjanın 0'dan büyük olmasını zorunlu
-- kılan bir CHECK kısıtı ekleyin. Kısıtı ihlal eden bir
-- INSERT deneyin ve hata mesajını sonuc/bonus.txt'e kaydedin.
-- =====================================================

-- Kontenjanın sıfırdan büyük olmasını zorunlu kılan CHECK kısıtını ekle
ALTER TABLE dersler
    ADD CONSTRAINT chk_kontenjan_pozitif CHECK (kontenjan > 0);

-- Kısıtı ihlal eden bir INSERT denemesi (kontenjan = 0):
INSERT INTO dersler (ders_id, ad, egitmen_id, kontenjan)
VALUES (999, 'Test Dersi', 1, 0);
