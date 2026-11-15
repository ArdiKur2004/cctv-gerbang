"""Lembar periksa: plat Bardi 'yakin' yang bacaannya BERBEDA antara pembaca publik dan pembaca dummy.
HTML lokal di data/ (tidak diunggah). Layar hanya hitungan; teks plat hanya ada di HTML untuk dibaca manusia.

  python tools/lab/lembar_beda.py <repo>   (sesudah pembaca_dummy.py nilai)
"""
import base64, csv, html, json, os, sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "tools" / "lab"))
os.environ.setdefault("KERAS_BACKEND", "torch")
import cv2  # noqa: E402
import latih_fpo as L  # noqa: E402
from plat import bersihkan  # noqa: E402

OUT = REPO / "data" / "keluaran" / "pembaca-dummy-1"
jalur = L.jalur_terkunci(REPO / "data" / "unduhan")
pub = L.PembacaKeras(jalur["keras"], jalur["plat"])
dum = L.PembacaKeras(OUT / "mesin.keras", jalur["plat"])

baris = []
for r in csv.DictReader(open(OUT / "nilai-bardi-yakin.csv", encoding="utf-8")):
    p = os.path.realpath(str(OUT) + os.sep + r["image_path"])
    g = cv2.imread(p)
    a, ya = pub.dengan_yakin(g)
    b, yb = dum.dengan_yakin(g)
    if bersihkan(a) != bersihkan(b):
        ok, png = cv2.imencode(".png", cv2.resize(g, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC))
        baris.append({"no": len(baris) + 1, "berkas": Path(p).name, "tipe": r["kondisi"], "img": base64.b64encode(png).decode(),
                      "publik": bersihkan(a), "ypub": round(ya, 2), "dummy": bersihkan(b), "ydum": round(yb, 2)})

kartu = "\n".join(f"""
<div class="k" data-no="{x['no']}" data-berkas="{html.escape(x['berkas'])}">
 <div class="h">#{x['no']} · {html.escape(x['tipe'])} · {html.escape(x['berkas'])}</div>
 <img src="data:image/png;base64,{x['img']}">
 <label><input type="radio" name="p{x['no']}" value="publik"> A: <b>{x['publik']}</b> <small>(publik, yakin {x['ypub']})</small></label>
 <label><input type="radio" name="p{x['no']}" value="dummy"> B: <b>{x['dummy']}</b> <small>(dummy, yakin {x['ydum']})</small></label>
 <label><input type="radio" name="p{x['no']}" value="lain"> Lain: <input type="text" class="t" placeholder="ketik plat yang benar"></label>
 <label><input type="radio" name="p{x['no']}" value="tak_terbaca"> Tidak terbaca mata</label>
</div>""" for x in baris)

halaman = f"""<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Periksa Plat Berbeda</title>
<style>
:root{{--bg:#f6f5f2;--card:#fff;--fg:#1d1d1b;--mut:#6b6b66;--acc:#b8860b;--bd:#ddd9cf}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151513;--card:#1f1f1c;--fg:#eceae4;--mut:#a3a29b;--bd:#34332e}}}}
body{{background:var(--bg);color:var(--fg);font:15px system-ui,sans-serif;margin:0;padding:16px;max-width:760px;margin:auto}}
h1{{font-size:20px}} p{{color:var(--mut)}}
.k{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px;margin:12px 0}}
.h{{font-size:13px;color:var(--mut);margin-bottom:6px}} img{{max-width:100%;image-rendering:auto;border-radius:6px;display:block;margin-bottom:8px}}
label{{display:block;padding:6px 0}} b{{font-family:ui-monospace,monospace;font-size:17px;letter-spacing:1px}}
.t{{font-family:ui-monospace,monospace;text-transform:uppercase;padding:4px;width:12em}}
button{{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:12px 18px;font-size:16px;margin:16px 0}}
</style>
<h1>Periksa {len(baris)} plat Bardi yang bacaannya berbeda</h1>
<p>Pilih bacaan yang BENAR menurut mata Anda (A, B, atau ketik sendiri). Lalu tekan Simpan: berkas <code>periksa-beda.json</code> terunduh
ke folder Downloads. Halaman ini hanya di laptop, tidak dikirim ke mana pun.</p>
{kartu}
<button onclick="simpan()">Simpan jawaban</button>
<script>
function simpan(){{
 const h=[...document.querySelectorAll('.k')].map(k=>{{const no=k.dataset.no;const r=k.querySelector('input[type=radio]:checked');
  return {{no:+no,berkas:k.dataset.berkas,pilih:r?r.value:null,teks:r&&r.value==='lain'?k.querySelector('.t').value.toUpperCase().replace(/[^A-Z0-9]/g,''):null}}}});
 const kosong=h.filter(x=>!x.pilih).length; if(kosong&&!confirm(kosong+' plat belum dijawab. Tetap simpan?'))return;
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(h,null,1)],{{type:'application/json'}}));
 a.download='periksa-beda.json';a.click();}}
</script></html>"""
(OUT / "periksa-beda.html").write_text(halaman, encoding="utf-8")
print("plat berbeda:", len(baris), "| lembar:", OUT / "periksa-beda.html")
