#!/usr/bin/env python3
"""Föy 02 — Otomatik Değerlendirici

GitHub Actions içinde çalışır. Öğrencinin ER diyagramını, DDL'ini ve
sorgularını, ogrno.txt'deki numaradan yeniden üretilen KİŞİYE ÖZEL
veri setine karşı kontrol eder. Beklenen değerler veri üretecinden
Python ile hesaplanır; bu dosyada hazır SQL cevabı yoktur.

ER diyagramı ve AI köşesi ayrıca asistan tarafından okunur; buradaki
kontroller bir taban puandır.
"""
import os
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "veri"))
from uret import uret  # noqa: E402

try:
    import psycopg
except ImportError:
    print("HATA: psycopg kurulu değil (pip install 'psycopg[binary]').")
    sys.exit(2)

SONUCLAR = []


def kaydet(gorev, alinan, tam, mesaj):
    SONUCLAR.append((gorev, alinan, tam, mesaj))
    durum = "✓" if alinan == tam else ("~" if alinan > 0 else "✗")
    print(f"[{durum}] {gorev}: {alinan}/{tam} — {mesaj}")


def oku(yol):
    p = KOK / yol
    if not p.exists():
        return None
    ham = p.read_bytes()
    # Windows'ta PowerShell'in ">" yonlendirmesi UTF-16 yazar; Not Defteri de
    # UTF-8'e BOM ekler. Bunlari cozmezsek ogrencinin dogru cikti dosyasi
    # taninmaz ve haksiz puan kaybi olur.
    if ham[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return ham.decode("utf-16", errors="replace")
    return ham.decode("utf-8-sig", errors="replace")

def sql_kodu(metin):
    """SQL metninden yorumlari atar.

    Sablon dosyalarinin KENDI yorumlarinda "CREATE TABLE komutunuzu yazin"
    gibi ifadeler gectigi icin, ham metinde anahtar kelime aramak bos teslimi
    gecerli sayiyordu. Denetimler bu fonksiyonun ciktisi uzerinde yapilir.
    """
    metin = re.sub(r"/\*.*?\*/", " ", metin or "", flags=re.S)
    return re.sub("--.*", " ", metin)


def baglanti():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "vtys"),
        password=os.environ.get("PGPASSWORD", "vtys2026"),
        dbname=os.environ.get("PGDATABASE", "vtysdb"),
        autocommit=True,
    )


def ogrno_al():
    icerik = oku("ogrno.txt")
    if icerik is None:
        return None
    icerik = icerik.strip()
    return icerik if icerik.isdigit() else None


# ---------------------------------------------------------- Görev 1: ER (Mermaid)
def kontrol_g1():
    icerik = oku("er/diyagram.mmd")
    if not icerik:
        kaydet("Görev 1 (ER)", 0, 15, "er/diyagram.mmd bulunamadı.")
        return
    kucuk = icerik.lower()
    puan = 0
    mesajlar = []

    if "erdiagram" in kucuk.replace(" ", ""):
        puan += 3
    else:
        mesajlar.append("Dosya bir 'erDiagram' bloğu içermiyor.")

    varliklar = ["uye", "egitmen", "ders", "kayit"]
    bulunan = [v for v in varliklar if v in kucuk]
    puan += 2 * len(bulunan)
    if len(bulunan) < 4:
        eksik = set(varliklar) - set(bulunan)
        mesajlar.append(f"Eksik varlık(lar): {', '.join(sorted(eksik))}.")

    iliski_sayisi = len(re.findall(r"[|}o][|{o]?--", icerik))
    if iliski_sayisi >= 3:
        puan += 2
    else:
        mesajlar.append("En az 3 ilişki çizgisi bekleniyor.")

    # eğitmen—ders hattında 1:N kardinalitesi
    birN = False
    for satir in icerik.splitlines():
        s = satir.lower()
        if "egitmen" in s and "ders" in s and "--" in s:
            if re.search(r"\|\|--o\{|\}o--\|\||\|\|--\|\{|\}\|--\|\|", satir):
                birN = True
    if birN:
        puan += 2
        mesajlar.append("Eğitmen—ders kardinalitesi (1:N) doğru.")
    else:
        mesajlar.append("Eğitmen—ders hattında 1:N kardinalitesi bulunamadı.")

    kaydet("Görev 1 (ER)", min(puan, 15), 15,
           " ".join(mesajlar) or "Diyagram yapısal kontrolleri geçti.")


# ---------------------------------------------------------- Görev 2: DDL
def kontrol_g2(con):
    sql = oku("sql/g2_ddl.sql")
    if not sql or "CREATE" not in sql_kodu(sql).upper():
        kaydet("Görev 2 (DDL)", 0, 25, "sql/g2_ddl.sql bulunamadı veya CREATE içermiyor.")
        return False
    try:
        for t in ("kayitlar", "dersler", "uyeler", "egitmenler"):
            con.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
        con.execute(sql)
    except Exception as e:
        kaydet("Görev 2 (DDL)", 0, 25, f"DDL çalıştırılamadı: {e}")
        return False

    puan = 0
    mesajlar = []
    tablolar = {r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'")}
    gerekli = {"egitmenler", "uyeler", "dersler", "kayitlar"}
    eksik = gerekli - tablolar
    if eksik:
        kaydet("Görev 2 (DDL)", 5, 25, f"Eksik tablo(lar): {', '.join(sorted(eksik))}.")
        return False
    puan += 10

    pk_tablolari = {r[0] for r in con.execute(
        """SELECT tc.table_name FROM information_schema.table_constraints tc
           WHERE tc.constraint_type='PRIMARY KEY' AND tc.table_schema='public'""")}
    if gerekli <= pk_tablolari:
        puan += 5
    else:
        mesajlar.append(f"Birincil anahtarı olmayan tablo(lar): "
                        f"{', '.join(sorted(gerekli - pk_tablolari))}.")

    fkler = {(r[0], r[1]) for r in con.execute(
        """SELECT tc.table_name, ccu.table_name
           FROM information_schema.table_constraints tc
           JOIN information_schema.constraint_column_usage ccu
             ON tc.constraint_name = ccu.constraint_name
           WHERE tc.constraint_type='FOREIGN KEY'""")}
    beklenen_fk = {("dersler", "egitmenler"),
                   ("kayitlar", "uyeler"),
                   ("kayitlar", "dersler")}
    dogru_fk = beklenen_fk & fkler
    puan += len(dogru_fk) * 3
    if len(dogru_fk) == 3:
        puan += 1
        mesajlar.append("Üç yabancı anahtar da doğru.")
    else:
        eksik_fk = beklenen_fk - fkler
        mesajlar.append("Eksik yabancı anahtar(lar): " +
                        ", ".join(f"{a}→{b}" for a, b in sorted(eksik_fk)) + ".")

    kaydet("Görev 2 (DDL)", min(puan, 25), 25, " ".join(mesajlar))
    return True


# ---------------------------------------------------------- veri yükleme
def veri_yukle(con, tablolar):
    """Beklenen veriyi FK sırasına uyarak değerlendirici yükler."""
    con.execute("TRUNCATE kayitlar, dersler, uyeler, egitmenler CASCADE")
    sira = [
        ("egitmenler", ["egitmen_id", "ad", "brans"]),
        ("uyeler", ["uye_id", "ad", "dogum_yili"]),
        ("dersler", ["ders_id", "ad", "egitmen_id", "kontenjan"]),
        ("kayitlar", ["kayit_id", "uye_id", "ders_id", "tarih"]),
    ]
    with con.cursor() as cur:
        for tablo, kolonlar in sira:
            with cur.copy(f"COPY {tablo} ({', '.join(kolonlar)}) FROM STDIN") as cp:
                for s in tablolar[tablo]:
                    cp.write_row(tuple(s[k] for k in kolonlar))


def kontrol_g3(tablolar):
    puan = 0
    sql = oku("sql/g3_yukleme.sql") or ""
    copy_sayisi = len(re.findall(r"\bCOPY\b", sql, re.IGNORECASE))
    if copy_sayisi >= 4:
        puan += 8
        m1 = "Dört COPY komutu yerinde."
    elif copy_sayisi > 0:
        puan += 4
        m1 = f"{copy_sayisi} COPY bulundu; dört tablo için dört yükleme bekleniyor."
    else:
        m1 = "sql/g3_yukleme.sql içinde COPY bulunamadı."

    beklenen = [str(len(tablolar["uyeler"])), str(len(tablolar["egitmenler"])),
                str(len(tablolar["dersler"])), str(len(tablolar["kayitlar"]))]
    icerik = oku("sonuc/g3.txt") or ""
    if all(b in icerik for b in beklenen):
        puan += 12
        m2 = "Satır sayıları sizin veri setinizle uyumlu."
    elif icerik:
        m2 = ("Satır sayıları sizin veri setinizle uyuşmuyor. ogrno.txt'deki "
              "numara ile uret.py'a verdiğiniz numaranın aynı olduğundan emin olun.")
    else:
        m2 = "sonuc/g3.txt bulunamadı."
    kaydet("Görev 3 (Yükleme)", puan, 20, f"{m1} {m2}")


# ---------------------------------------------------------- Görev 4: JOIN
def g4_beklenenler(t):
    egitmen_adi = {e["egitmen_id"]: e["ad"] for e in t["egitmenler"]}
    ders = {d["ders_id"]: d for d in t["dersler"]}

    b = {}
    b[1] = Counter((d["ad"], egitmen_adi[d["egitmen_id"]]) for d in t["dersler"])

    ders_sayaci = Counter(egitmen_adi[d["egitmen_id"]] for d in t["dersler"])
    b[2] = ders_sayaci

    kayit_sayaci = Counter(k["ders_id"] for k in t["kayitlar"])
    sirali = kayit_sayaci.most_common()
    esik = sirali[4][1]
    b[3] = {"esikler": [n for _, n in sirali[:5]],
            "adaylar": {(ders[d]["ad"], n) for d, n in sirali if n >= esik}}

    kayitli = set(kayit_sayaci)
    b[4] = Counter(d["ad"] for d in t["dersler"] if d["ders_id"] not in kayitli)
    return b


def kontrol_g4(con, t):
    sql = oku("sql/g4_sorgular.sql")
    if not sql:
        kaydet("Görev 4 (JOIN)", 0, 25, "sql/g4_sorgular.sql bulunamadı.")
        return
    parcalar = re.split(r"--\s*Soru\s*4\.(\d)[^\n]*", sql)
    sorgular = {}
    for i in range(1, len(parcalar) - 1, 2):
        sorgular[int(parcalar[i])] = parcalar[i + 1].strip()

    beklenen = g4_beklenenler(t)
    puanlar = {1: 6, 2: 6, 3: 6, 4: 7}
    toplam = 0
    mesajlar = []

    for no in (1, 2, 3, 4):
        q = sorgular.get(no, "").rstrip().rstrip(";")
        if not q:
            mesajlar.append(f"4.{no}: sorgu yok.")
            continue
        try:
            rows = con.execute(q).fetchall()
        except Exception as e:
            mesajlar.append(f"4.{no}: sorgu hatası ({str(e).splitlines()[0]}).")
            continue

        if no == 1:
            dogru = Counter((str(r[0]), str(r[1])) for r in rows) == beklenen[1]
        elif no == 2:
            sayilar = [r[-1] for r in rows]
            dogru = (Counter({str(r[0]): r[-1] for r in rows}) == beklenen[2]
                     and sayilar == sorted(sayilar, reverse=True))
        elif no == 3:
            dogru = (len(rows) == 5
                     and [r[-1] for r in rows] == beklenen[3]["esikler"]
                     and all((str(r[0]), r[-1]) in beklenen[3]["adaylar"] for r in rows))
        else:
            dogru = Counter(str(r[0]) for r in rows) == beklenen[4]

        if dogru:
            toplam += puanlar[no]
            mesajlar.append(f"4.{no}: doğru.")
        else:
            mesajlar.append(f"4.{no}: sonuç beklenenden farklı.")

    kaydet("Görev 4 (JOIN)", toplam, 25, " ".join(mesajlar))


# ---------------------------------------------------------- Görev 5: bütünlük
def kontrol_g5():
    sql = oku("sql/g5_butunluk.sql") or ""
    cikti = oku("sonuc/g5.txt") or ""
    puan = 0
    mesajlar = []
    if re.search(r"\bINSERT\b", sql, re.IGNORECASE) and re.search(r"\bDELETE\b", sql, re.IGNORECASE):
        puan += 4
    else:
        mesajlar.append("Dosyada hem INSERT hem DELETE denemesi bekleniyor.")
    if re.search(r"foreign key|yabanc", cikti, re.IGNORECASE):
        puan += 6
        mesajlar.append("Yabancı anahtar hata çıktısı belgelenmiş.")
    else:
        mesajlar.append("sonuc/g5.txt içinde yabancı anahtar hata mesajı bulunamadı.")
    kaydet("Görev 5 (Bütünlük)", puan, 10, " ".join(mesajlar))


def ogrenci_metni(markdown):
    """Markdown'dan kod bloklarini atip ogrencinin KENDI yazdigi metni birakir.

    Yapay zekanin urettigi SQL'i yapistirip tek satir elestiri yazmayan
    teslimler yalnizca uzunluga bakildiginda esigi gecip tam puan aliyordu
    (gercek teslimlerde tespit edildi). Puan artik duz metne gore verilir.
    """
    m = markdown or ""
    m = re.sub(r"```.*?```", " ", m, flags=re.S)
    m = re.sub(r"```.*", " ", m, flags=re.S)
    m = re.sub(r"^\s{4,}\S.*$", " ", m, flags=re.M)
    m = re.sub(r"`[^`]*`", " ", m)
    return re.sub(r"\s+", " ", m).strip()


def kontrol_ai():
    icerik = oku("sonuc/ai_elestiri.md")
    if not icerik or len(ogrenci_metni(icerik)) < 300:
        kaydet("AI Köşesi", 0, 10,
               "sonuc/ai_elestiri.md yok ya da eleştiri metniniz 300 karakterden kısa "
               "(yapıştırdığınız kod blokları sayılmaz). Föyde istenen iki "
               "somut eleştiriyi yazdığınızda bu uzunluk zaten aşılır "
               "(içerik ayrıca asistan tarafından okunur).")
    else:
        kaydet("AI Köşesi", 10, 10,
               "Dosya teslim edildi (isabet puanı asistan değerlendirmesiyle kesinleşir).")


# ---------------------------------------------------------- ana akış
def main():
    print("=" * 64)
    print("Föy 02 — Otomatik Değerlendirme")
    print("=" * 64)

    ogrno = ogrno_al()
    if not ogrno:
        print("HATA: ogrno.txt bulunamadı ya da geçerli bir numara içermiyor.")
        sys.exit(1)
    print(f"Öğrenci no: {ogrno} (veri seti bu numaradan yeniden üretiliyor)\n")

    t = uret(ogrno)

    kontrol_g1()
    with baglanti() as con:
        hazir = kontrol_g2(con)
        if hazir:
            try:
                veri_yukle(con, t)
            except Exception as e:
                print(f"    (veri yüklenemedi, Görev 3–4 atlanıyor: {e})")
                hazir = False
        if hazir:
            kontrol_g3(t)
            kontrol_g4(con, t)
        else:
            kaydet("Görev 3 (Yükleme)", 0, 20, "Şema hazır olmadığı için kontrol edilemedi.")
            kaydet("Görev 4 (JOIN)", 0, 25, "Şema hazır olmadığı için kontrol edilemedi.")
    kontrol_g5()
    kontrol_ai()

    alinan = sum(s[1] for s in SONUCLAR)
    tam = sum(s[2] for s in SONUCLAR)
    print("\n" + "=" * 64)
    print(f"TOPLAM (otomatik kontrol edilen kısım): {alinan}/{tam}")
    print("Ön quiz (5p) bu rapora dahil değildir; ER diyagramı ve AI köşesi")
    print("asistan tarafından ayrıca değerlendirilir.")
    print("=" * 64)

    ozet = os.environ.get("GITHUB_STEP_SUMMARY")
    if ozet:
        with open(ozet, "a", encoding="utf-8") as f:
            f.write("## Föy 02 — Otomatik Değerlendirme\n\n")
            f.write("| Bileşen | Puan | Açıklama |\n|---|---|---|\n")
            for gorev, a, tp, m in SONUCLAR:
                f.write(f"| {gorev} | {a}/{tp} | {m} |\n")
            f.write(f"| **Toplam** | **{alinan}/{tam}** | |\n")

    sys.exit(0 if alinan == tam else 1)


if __name__ == "__main__":
    main()
