#!/usr/bin/env python3
"""Kişiye özel veri üreteci — Föy 02 (FıratFit Spor Merkezi)

Kullanım:
    python3 veri/uret.py <ogrenci_no>

Dört CSV üretir: egitmenler.csv, uyeler.csv, dersler.csv, kayitlar.csv
Aynı öğrenci numarası her çalıştırmada AYNI veri setini üretir.
"""
import csv
import random
import sys
from pathlib import Path

ADLAR = ["Ahmet", "Ayşe", "Mehmet", "Elif", "Mustafa", "Zeynep", "Ali",
         "Fatma", "Hasan", "Emine", "Murat", "Hülya", "Kemal", "Nazlı",
         "Selim", "Leyla", "Orhan", "Sevgi", "Yakup", "Melek", "Deniz",
         "Ece", "Burak", "Ceren", "Tolga", "İpek", "Serkan", "Gül"]

SOYADLAR = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Aydın",
            "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Koç", "Kurt",
            "Özdemir", "Erdoğan", "Polat", "Güneş", "Taş", "Bulut"]

BRANSLAR = ["Fitness", "Yoga", "Pilates", "Yüzme", "Boks", "Crossfit"]

DERS_TEMEL = ["Sabah Yogası", "Fonksiyonel Antrenman", "Yüzme Teknikleri",
              "Pilates Matwork", "Boks Temelleri", "Crossfit WOD",
              "Core Güçlendirme", "Esneklik ve Denge", "Kardiyo Dayanıklılık",
              "Kuvvet Antrenmanı", "Hamile Yogası", "Kıdemli Fitness",
              "Gençlik Yüzme", "İleri Pilates", "Kickboks"]

SEVIYELER = ["Başlangıç", "Orta", "İleri"]


def uret(ogrno: str):
    """Öğrenci numarasından deterministik dört tablo üretir."""
    tohum = int(ogrno)
    rnd = random.Random(tohum)

    # --- eğitmenler (8–12) ---
    egitmen_sayisi = 8 + tohum % 5
    egitmenler = []
    for eid in range(1, egitmen_sayisi + 1):
        egitmenler.append({
            "egitmen_id": eid,
            "ad": f"{rnd.choice(ADLAR)} {rnd.choice(SOYADLAR)}",
            "brans": rnd.choice(BRANSLAR),
        })

    # --- dersler (25–33), her ders bir eğitmene bağlı (1:N) ---
    ders_sayisi = 25 + tohum % 9
    ders_adlari = set()
    dersler = []
    for did in range(1, ders_sayisi + 1):
        while True:
            ad = f"{rnd.choice(DERS_TEMEL)} — {rnd.choice(SEVIYELER)}"
            if ad not in ders_adlari:
                ders_adlari.add(ad)
                break
        dersler.append({
            "ders_id": did,
            "ad": ad,
            "egitmen_id": rnd.randint(1, egitmen_sayisi),
            "kontenjan": rnd.choice([10, 12, 15, 20, 25]),
        })

    # --- üyeler (170–220) ---
    uye_sayisi = 170 + tohum % 51
    uyeler = []
    for uid in range(1, uye_sayisi + 1):
        uyeler.append({
            "uye_id": uid,
            "ad": f"{rnd.choice(ADLAR)} {rnd.choice(SOYADLAR)}",
            "dogum_yili": rnd.randint(1965, 2008),
        })

    # --- kayıtlar (N:M ara tablo, 320–420) ---
    # Bazı dersler bilerek boş bırakılır (Görev 4.4 için).
    bos_ders_sayisi = 2 + tohum % 3
    bos_dersler = set(rnd.sample(range(1, ders_sayisi + 1), bos_ders_sayisi))
    kayit_alan = [d for d in range(1, ders_sayisi + 1) if d not in bos_dersler]

    kayit_sayisi = 320 + tohum % 101
    ikili_kume = set()
    kayitlar = []
    kid = 0
    while kid < kayit_sayisi:
        uye = rnd.randint(1, uye_sayisi)
        ders = rnd.choice(kayit_alan)
        if (uye, ders) in ikili_kume:      # aynı üye aynı derse bir kez
            continue
        ikili_kume.add((uye, ders))
        kid += 1
        ay = rnd.randint(1, 12)
        gun = rnd.randint(1, 28)
        kayitlar.append({
            "kayit_id": kid,
            "uye_id": uye,
            "ders_id": ders,
            "tarih": f"2026-{ay:02d}-{gun:02d}",
        })

    return {"egitmenler": egitmenler, "uyeler": uyeler,
            "dersler": dersler, "kayitlar": kayitlar}


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Kullanım: python3 veri/uret.py <ogrenci_no>")
        print("Örnek   : python3 veri/uret.py 230541001")
        sys.exit(1)

    ogrno = sys.argv[1]
    klasor = Path(__file__).resolve().parent
    tablolar = uret(ogrno)

    for ad, satirlar in tablolar.items():
        hedef = klasor / f"{ad}.csv"
        with open(hedef, "w", newline="", encoding="utf-8") as f:
            yazici = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()))
            yazici.writeheader()
            yazici.writerows(satirlar)
        print(f"Üretildi: {hedef.name:16s} ({len(satirlar)} satır)")

    print("Bu dosyalar size özeldir; sonuçlarınız sınıftaki herkesten farklıdır.")


if __name__ == "__main__":
    main()
