# Föy 02 — ER Diyagramları ve İlişkisel Tasarım

Modern Veritabanı Yönetim Sistemleri — Laboratuvar teslim deposu.
Görevlerin tam açıklaması **Föy 02 PDF**'indedir; bu dosya kısa bir hatırlatmadır.

## Senaryo

**FıratFit Spor Merkezi**: eğitmenler ders verir (bir eğitmen birden çok ders — 1:N),
üyeler derslere kaydolur (bir üye birden çok derse, bir derste birden çok üye — N:M,
`kayitlar` ara tablosu).

## Hızlı başlangıç

```bash
echo "230541001" > ogrno.txt              # kendi numaranız
docker compose up -d
python3 veri/uret.py 230541001            # kendi numaranız → 4 CSV üretir
docker exec -it vtys-postgres psql -U vtys -d vtysdb
```

## Depo yapısı

| Yol | Ne |
|---|---|
| `ogrno.txt` | 240541142 |
| `er/diyagram.mmd` | Görev 1 — Mermaid ER diyagramınız |
| `sql/` | Görev 2–5 SQL dosyaları |
| `sonuc/` | Sorgu çıktılarınız ve AI köşesi teslimi |
| `veri/uret.py` | Kişiye özel 4 CSV üreteci |


## Push etmeden önce kendinizi kontrol edin

Değerlendiriciyi kendi bilgisayarınızda çalıştırabilirsiniz — GitHub'daki ile
**aynı dosya, aynı puan**:

```bash
docker compose run --rm kontrol
```

Ekrana görev görev puanınız ve eksikleriniz düşer. İlk çalıştırma birkaç
saniye sürer, sonrakiler ~2 saniye. Ayrıca bir şey kurmanız gerekmez; Docker
zaten kurulu.

**Önce burada tam puan alın, sonra push edin.** Her push GitHub'da sınıfın
ortak Actions kotasından dakika harcar; deneme-yanılmayı buraya taşırsanız
kota dönem sonuna kadar yeter.

## Teslim

```bash
git add ogrno.txt er/ sql/ sonuc/
git commit -m "Foy 02 teslimi"
git push
```

Push sonrası **Actions** sekmesinden sonucu görün. Düzeltmeleri önce
`docker compose run --rm kontrol` ile yerelde doğrulayın, sonra push edin. ER diyagramı ve AI köşesi ayrıca asistan tarafından okunur.
