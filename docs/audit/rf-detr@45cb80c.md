# Audit statis: `rf-detr`

- Commit: `45cb80cb1f5622d9d8838bfa85ff04ba93fe6d55` · berkas kode dipindai: **386** · dilewati: 0
- TINGGI: **3** · SEDANG: **140** · INFO: 14

## Ringkasan per aturan

| Aturan | Tingkat | Jumlah | Arti |
|---|---|---|---|
| `ip-publik` | TINGGI | 1 | alamat IP publik tertanam (server tak bernama) |
| `ci-pr-target` | TINGGI | 2 | workflow pull_request_target (jalur serangan insiden Ultralytics 2024) |
| `telemetri` | SEDANG | 7 | pustaka/kata kunci analitik & pelacakan pemakaian |
| `pustaka-jaringan` | SEDANG | 23 | kode yang bisa membuka koneksi jaringan |
| `eksekusi-dinamis` | SEDANG | 24 | exec/eval/subprocess (sering sah, tapi jalur favorit backdoor) |
| `deserialisasi-tak-aman` | SEDANG | 86 | memuat pickle/torch/yaml dengan cara yang bisa menjalankan kode |
| `unduh-otomatis` | INFO | 14 | mengunduh bobot/berkas saat berjalan (periksa sumber & hash) |

## Domain yang disebut di KODE

- **Perlu dicek (bukan domain umum):** `rfdetr.roboflow.com` (29) · `storage.googleapis.com` (22) · `example.com` (22) · `universe.roboflow.com` (17) · `images.cocodataset.org` (10) · `media.roboflow.com` (7) · `roboflow.com` (7) · `schema.org` (5) · `legacy.com` (4) · `example.invalid` (4) · `docs.codecov.io` (2) · `www.linkedin.com` (2) · `twitter.com` (2) · `www.youtube.com` (2) · `pypistats.org` (2) · `giou.stanford.edu` (2) · `codecov.io` (1) · `codecov.readme.io` (1) · `docs.codecov.com` (1) · `api.indexnow.org` (1) · `prettier.io` (1) · `aiinfra.pkgs.visualstudio.com` (1) · `www.googletagmanager.com` (1) · `en.wikipedia.org` (1) · `www.crunchbase.com` (1) · `cdnjs.cloudflare.com` (1) · `t.ly` (1) · `blog.roboflow.com` (1) · `discuss.roboflow.com` (1) · `inference.roboflow.com` (1) · `supervision.roboflow.com` (1) · `trackers.roboflow.com` (1) · `maestro.roboflow.com` (1) · `docs.roboflow.com` (1) · `gitlab.baidu.com` (1) · `plus.example.com` (1)
- Domain umum: `github.com` (135) · `pypi.org` (5) · `api.github.com` (3) · `arxiv.org` (3) · `download.pytorch.org` (2) · `huggingface.co` (2) · `www.apache.org` (1) · `www.w3.org` (1) · `pytorch.org` (1)

## Berkas biner / bobot (0)


## Temuan

### `ip-publik` — TINGGI (1)
- `tests/export/test_tensorrt_export.py:1162` — `("11.2.1.2", 11),`

### `ci-pr-target` — TINGGI (2)
- `.github/workflows/pr-conflict-labeler.yml:8` — `# We recommend 'pull_request_target' so that github secrets are available.`
- `.github/workflows/pr-conflict-labeler.yml:10` — `pull_request_target:`

### `telemetri` — SEDANG (7)
- `docs/theme/main.html:38` — `<script async src="https://www.googletagmanager.com/gtag/js?id={{ ga4_measurement_id }}"></script>`
- `docs/theme/main.html:41` — `function gtag(){window.dataLayer.push(arguments);}`
- `docs/theme/main.html:42` — `gtag('js', new Date());`
- `docs/theme/main.html:44` — `gtag('config', '{{ ga4_measurement_id }}');`
- `tests/training/test_cuda_graph_te.py:414` — `for amplitude in (1.5, 2.5, 0.25):`
- `tests/training/test_cuda_graph_te.py:418` — `eager_output = eager(_fp8_samples(amplitude, device="cuda"))["pred"]`
- `tests/training/test_cuda_graph_te.py:421` — `graphed_output = runner(_fp8_samples(amplitude, device="cuda"))["pred"]`

### `pustaka-jaringan` — SEDANG (23)
- `docs/cookbooks/custom-augmentations.ipynb:sel 22` — `import requests`
- `docs/cookbooks/export-apple.ipynb:sel 8` — `import urllib.request`
- `docs/cookbooks/export-cpu.ipynb:sel 7` — `import urllib.request`
- `docs/cookbooks/export-cuda.ipynb:sel 7` — `import urllib.request`
- `docs/cookbooks/export-mobile.ipynb:sel 8` — `import urllib.request`
- `docs/cookbooks/export-mobile.ipynb:sel 24` — `import urllib.request`
- `docs/javascripts/cookbooks-card.js:58` — `const response = await fetch('https://api.github.com/users/${login}');`
- `docs/javascripts/version-banner.js:214` — `fetch(new URL("../versions.json", versionBase))`
- `scripts/update_weekly_metrics.py:20` — `from urllib.error import HTTPError, URLError`
- `scripts/update_weekly_metrics.py:21` — `from urllib.parse import quote`
- `scripts/update_weekly_metrics.py:22` — `from urllib.request import Request, urlopen`
- `src/rfdetr/datasets/_develop.py:23` — `from urllib.request import urlretrieve`
- `src/rfdetr/detr.py:22` — `from urllib.parse import urlparse`
- `src/rfdetr/detr.py:25` — `import requests`
- `src/rfdetr/utilities/files.py:15` — `import requests`
- `tests/_online.py:10` — `import socket`
- `tests/datasets/test_webdataset.py:23` — `from urllib.parse import urlparse`
- `tests/inference/test_predict.py:16` — `import requests`
- `tests/legacy/generate_checkpoint.py:99` — `import requests`
- `tests/legacy/generate_checkpoint.py:340` — `import requests`
- `tests/legacy/test_generate_checkpoint.py:24` — `import requests`
- `tests/test_weekly_metrics.py:16` — `from urllib.error import HTTPError, URLError`
- `tests/utilities/test_file_validation.py:14` — `import requests`

### `eksekusi-dinamis` — SEDANG (24)
- `.github/_tests/test_update_metrics_workflow.py:99` — `return subprocess.run(["bash", str(script)], cwd=workspace, env=env, text=True, capture_output=True, check=False)`
- `src/rfdetr/detr.py:2560` — `every call, but ''eval()'' is only applied when at least one module is in training mode. This covers both a`
- `src/rfdetr/detr.py:2581` — `# ''eval()'' recursively reassigns ''training'' through ''nn.Module.__setattr__'' on every node. Reading the`
- `src/rfdetr/detr.py:2583` — `# If the root is in training mode, ''any'' stops on its first item before ''eval()'' performs the required walk.`
- `src/rfdetr/utilities/package.py:69` — `return subprocess.check_output(command, cwd=cwd).decode("ascii").strip()`
- `src/rfdetr/utilities/package.py:73` — `diff_result = subprocess.run(`
- `tests/cli/test_smoke.py:93` — `result = subprocess.run(`
- `tests/cli/test_webdataset_cli.py:25` — `result = subprocess.run(`
- `tests/cli/test_webdataset_cli.py:38` — `result = subprocess.run(`
- `tests/cli/test_webdataset_cli.py:47` — `result = subprocess.run(`
- `tests/cli/test_webdataset_cli.py:84` — `result = subprocess.run(`
- `tests/export/test_export.py:66` — `def eval(self):`
- `tests/export/test_openvino_export.py:235` — `result = subprocess.run(`
- `tests/export/test_tflite_export.py:1653` — `result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)`
- `tests/inference/test_predict_eval_mode.py:108` — `The compiled inference_model snapshot is already in eval mode; calling eval() on the stale self.model.model`
- `tests/inference/test_predict_eval_mode.py:138` — `that ''eval()'' is still applied to a current module whose root reports training mode.`
- `tests/utilities/test_distributed.py:155` — `result = subprocess.run(`
- `tests/utilities/test_package.py:64` — `patch("rfdetr.utilities.package.subprocess.check_output", side_effect=_fake_check_output),`
- `tests/utilities/test_package.py:65` — `patch("rfdetr.utilities.package.subprocess.run", return_value=_RunResult(returncode=1)),`
- `tests/utilities/test_package.py:78` — `result = subprocess.run(`
- `tests/utilities/test_package.py:131` — `result = subprocess.run(`
- `tests/utilities/test_package.py:209` — `result = subprocess.run(`
- `tests/utilities/test_package.py:242` — `result = subprocess.run(`
- `tests/utilities/test_package.py:333` — `result = subprocess.run(`

### `deserialisasi-tak-aman` — SEDANG (86)
- `docs/cookbooks/fine-tune_detection.ipynb:sel 25` — `_ckpt = torch.load(OUTPUT_DIR / "checkpoint_best_total.pth", map_location="cpu", weights_only=False)`
- `docs/cookbooks/fine-tune_keypoints.ipynb:sel 29` — `_ckpt = torch.load(OUTPUT_DIR / "checkpoint_best_total.pth", map_location="cpu", weights_only=False)`
- `docs/cookbooks/fine-tune_segmentation.ipynb:sel 25` — `_ckpt = torch.load(OUTPUT_DIR / "checkpoint_best_total.pth", map_location="cpu", weights_only=False)`
- `src/rfdetr/export/_tflite/exporter.py:41` — `:func:'numpy.load' on pickled data without ''allow_pickle=True''.`
- `src/rfdetr/export/_tflite/exporter.py:540` — `"""Temporarily patch :func:'numpy.load' to set ''allow_pickle=True''.`
- `src/rfdetr/export/_tflite/exporter.py:542` — `''onnx2tf'' 1.x calls ''np.load()'' on its bundled calibration data without passing ''allow_pickle=True''.  NumPy ≥`
- `src/rfdetr/export/_tflite/exporter.py:634` — `# intentional here; allow_pickle=True is handled by _numpy_allow_pickle()`
- `src/rfdetr/utilities/distributed.py:172` — `data_list.append(pickle.loads(buffer))`
- `src/rfdetr/utilities/io.py:102` — `return torch.load(path, map_location="cpu", weights_only=False)`
- `src/rfdetr/utilities/state_dict.py:175` — `>>> torch.load(path, weights_only=False)["best_total_source"]`
- `tests/export/test_export_for_roboflow.py:51` — `bundle = torch.load(tmp_path / "weights.pt", map_location="cpu", weights_only=False)`
- `tests/export/test_export_for_roboflow.py:70` — `bundle = torch.load(tmp_path / "weights.pt", map_location="cpu", weights_only=False)`
- `tests/export/test_export_for_roboflow.py:80` — `bundle = torch.load(tmp_path / "weights.pt", map_location="cpu", weights_only=False)`
- `tests/export/test_export_for_roboflow.py:92` — `bundle = torch.load(tmp_path / "weights.pt", map_location="cpu", weights_only=False)`
- `tests/inference/test_from_checkpoint.py:1141` — `stripped = torch.load(path, weights_only=False)`
- `tests/legacy/test_checkpoint_compat.py:219` — `ckpt: dict = torch.load(ckpt_path, map_location="cpu", weights_only=False)`
- `tests/legacy/test_checkpoint_compat.py:227` — `calling ''torch.load(...)'' directly with no error wrapping — a present-but-corrupt checkpoint`
- `tests/legacy/test_checkpoint_compat.py:240` — `torch.load(corrupt_path, map_location="cpu", weights_only=False)`
- `tests/legacy/test_generate_checkpoint.py:321` — `ckpt: dict = torch.load(out, map_location="cpu", weights_only=False)`
- `tests/models/test_criterion.py:1392` — `restored = pickle.loads(pickle.dumps(criterion))`
- `tests/training/callbacks/test_best_model_callback.py:768` — `checkpoint = torch.load(tmp_path / "checkpoint_best_ema.pth", map_location="cpu", weights_only=False)`
- `tests/training/callbacks/test_best_model_callback.py:793` — `checkpoint = torch.load(tmp_path / "checkpoint_best_regular.pth", map_location="cpu", weights_only=False)`
- `tests/training/callbacks/test_best_model_callback.py:813` — `data = torch.load(total, map_location="cpu", weights_only=False)`
- `tests/training/callbacks/test_best_model_callback.py:836` — `ema_data = torch.load(`
- `tests/training/callbacks/test_best_model_callback.py:841` — `total_data = torch.load(total, map_location="cpu", weights_only=False)`
- … +61 lagi

### `unduh-otomatis` — INFO (14)
- `docs/cookbooks/export-apple.ipynb:sel 8` — `urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)`
- `docs/cookbooks/export-cpu.ipynb:sel 7` — `urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)`
- `docs/cookbooks/export-cuda.ipynb:sel 7` — `urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)`
- `docs/cookbooks/export-cuda.ipynb:sel 19` — `trt_model = AutoModel.from_pretrained("rfdetr-small", backend=BackendType.TRT)`
- `docs/cookbooks/export-cuda.ipynb:sel 23` — `trt_fp32_model = AutoModel.from_pretrained("rfdetr-small", backend=BackendType.TRT, quantization="fp32")`
- `docs/cookbooks/export-mobile.ipynb:sel 8` — `urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)`
- `docs/cookbooks/export-mobile.ipynb:sel 24` — `urllib.request.urlretrieve(IMAGE_URL, IMAGE_PATH)`
- `src/rfdetr/datasets/_develop.py:198` — `_, headers = urlretrieve(url, str(zip_path))`
- `src/rfdetr/export/_tensorrt/exporter.py:20` — `model = AutoModel.from_pretrained("rfdetr-small")`
- `src/rfdetr/models/backbone/dinov2.py:137` — `self.encoder = AutoBackbone.from_pretrained(  # type: ignore[no-untyped-call]`
- `src/rfdetr/models/backbone/dinov2.py:198` — `WindowedDinov2WithRegistersBackbone.from_pretrained(`
- `tests/conftest.py:40` — `from huggingface_hub import snapshot_download`
- `tests/conftest.py:43` — `snapshot_download(`
- `tests/conftest.py:48` — `pytest.skip(f"Skipping DINOv2 cache prewarm (snapshot_download failed): {exc}")`

> Pemindai statis = **petunjuk, bukan vonis**. Tak menemukan pola ≠ terbukti aman (kode bisa disamarkan, dependensi tak ikut
> dipindai, bobot pickle tak dibuka). Temuan SEDANG wajib dibaca konteksnya oleh manusia. Lihat `docs/PROTOKOL-KEAMANAN-REPO.md`.

## Dibaca manual (2026-10-13)

| Temuan | Berkas | Isi sebenarnya | Sikap |
|---|---|---|---|
| `ip-publik` | `tests/export/test_tensorrt_export.py:1162` | `"11.2.1.2"` adalah nomor versi TensorRT di data uji fungsi `_tensorrt_major`, bukan alamat IP | Wajar (salah tangkap pemindai) |
| `ci-pr-target` ×2 | `.github/workflows/pr-conflict-labeler.yml:8,10` | Workflow `pull_request_target` yang **tidak** meng-checkout kode PR: satu langkah, memakai action pihak ketiga yang dikunci ke commit penuh, izinnya hanya menulis label PR dan issue | Wajar. Bukan pola insiden Ultralytics, dan workflow itu berjalan di repo hulu, bukan di mesin kita |

**Unduhan otomatis:** `src/rfdetr/utilities/files.py` (`_download_file`) mengunduh bobot dari `storage.googleapis.com/rfdetr/…` dan
memeriksa MD5 yang tercatat di `src/rfdetr/assets/model_weights.py`. `src/rfdetr/models/backbone/dinov2.py:137,198` memuat backbone
DINOv2 lewat `from_pretrained`, yang mengunduh dari Hugging Face bila belum ada di cache. `src/rfdetr/datasets/_develop.py:198`
mengunduh arsip zip dan hanya membandingkan ukurannya dengan `Content-Length`. `src/rfdetr/detr.py:2743` mengambil gambar dari
alamat bila masukannya berupa URL. Di lab tanpa jaringan semua jalur ini gagal, tidak mengunduh.
**Bergantung pada `ultralytics`:** tidak. `pyproject.toml` tidak memuatnya; `src/rfdetr/datasets/yolo.py` hanya menyebut kata itu
di komentar tentang tata letak dataset YOLO, tanpa baris impor.
**Batas:** pemindai statis hanya petunjuk; 386 berkas tidak dibaca baris demi baris. 86 temuan `deserialisasi-tak-aman` (memuat
`.pth`) tidak dibaca satu per satu: bobot `.pth` adalah pickle dan wajib dipindai atau dikonversi sebelum dimuat (CLAUDE.md §6).
