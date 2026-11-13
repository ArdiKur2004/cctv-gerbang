# Build cost, difficulty, deployment and support burden: (A) factory QC vision tool vs (B) ALPR + make/model gate module — Indonesia, solo/small developer, as of 13 Oct 2026

Conventions used in these notes

- "A" = factory QC vision (cleanliness/hygiene, label/packaging/assembly conformity, fill level/counting). "B" = Indonesian plate + vehicle make/model on CCTV, opening a gate through a relay.
- Sub-designs referred to throughout: **A1** phone-photo audit app with VLM checks (no hardware); **A2** fixed camera + edge box, alert/log only, fixed-scope checks; **A3** inline station with trigger, PLC and physical reject. **B1** camera with on-board ANPR + thin whitelist/cloud app; **B2** own ALPR pipeline on a generic RTSP camera + edge box + relay; **B3** B1/B2 plus supplying the barrier/gate motor.
- All IDR prices are marketplace/distributor listings seen 13 Oct 2026 unless a month is given; they are street prices, not quotes, and exclude installation unless stated.
- USD→IDR conversions use **Rp 17,900/USD** (x-rates showed 17,946; its timestamp read "Jan 1 2026", so treat the rate as approximate and re-check) — [x-rates](https://www.x-rates.com/calculator/?from=USD&to=IDR&amount=1).
- Anything labelled **ESTIMATE** is this researcher's arithmetic or judgement, with the basis shown. It is not a sourced figure.
- Research limit: the shared web-search budget ran out before the last few lookups (build logs with person-week counts, lens/light/UPS/encoder prices, EN 12453 primary text). Those are listed under Gaps rather than filled in.

---

## 1. Software building blocks in 2026 and their licences/costs — detection, segmentation, counting, anomaly detection (mainly Option A, also the detector in B)

### Takeaway
The licence trap is Ultralytics: every YOLO from that repo (v8/11/12/26) and every model trained with it is AGPL-3.0 unless a quote-only Enterprise Licence is bought, and that explicitly covers closed products, SaaS, internal tools and embedded devices. A closed-source product can avoid it entirely with Apache-2.0 detectors (RF-DETR N–L, D-FINE, RT-DETR, YOLOX) and Apache-2.0 Anomalib, so licence cost is avoidable for both options; it is a design constraint, not a budget line.

### Cited Findings
- Ultralytics states "An Enterprise License is required if you want to use Ultralytics YOLO without open-sourcing your entire project", listing as triggers: any commercial product or service, internal business tools, SaaS/APIs that use YOLO behind the scenes, and embedded deployments in hardware/edge devices/cameras. It also states "All Ultralytics YOLO trained models fall under the AGPL-3.0 License by default" (fetched 13 Oct 2026) — [Ultralytics licence page](https://www.ultralytics.com/license)
- Enterprise Licence price is not published; it is quote-only via a request form, scoped per project or per organisation — [Ultralytics licence page](https://www.ultralytics.com/license); [request form](https://www.ultralytics.com/request-license)
- Ultralytics Platform (not the code licence) lists Pro at USD 29/seat/month with Free and Pro both under AGPL-3.0; Enterprise is custom — [Ultralytics pricing](https://ultralytics.com/pricing)
- A startup programme page mentions credits and first-year Enterprise licence savings "up to $10,000"; exact terms not confirmed — [Ultralytics startups](https://www.ultralytics.com/es/startups)
- A GitHub discussion asking about minimums and per-year vs per-project pricing has no clear answer — [Ultralytics discussion #1260](https://github.com/orgs/ultralytics/discussions/1260)
- Repository licences read from the GitHub API on 13 Oct 2026 (SPDX id, last push):
  - ultralytics/ultralytics — AGPL-3.0, pushed 2026-10-12 — [repo](https://github.com/ultralytics/ultralytics)
  - roboflow/rf-detr — Apache-2.0, pushed 2026-10-12 — [repo](https://github.com/roboflow/rf-detr)
  - Peterande/D-FINE — Apache-2.0, pushed 2026-10-05 — [repo](https://github.com/Peterande/D-FINE)
  - lyuwenyu/RT-DETR — Apache-2.0, pushed 2026-10-09 — [repo](https://github.com/lyuwenyu/RT-DETR)
  - Megvii-BaseDetection/YOLOX — Apache-2.0, last push 2025-06-08 (slow-moving) — [repo](https://github.com/Megvii-BaseDetection/YOLOX)
  - WongKinYiu/yolov9 — GPL-3.0, last push 2024-08-09 — [repo](https://github.com/WongKinYiu/yolov9)
  - open-edge-platform/anomalib — Apache-2.0, pushed 2026-10-10 — [repo](https://github.com/open-edge-platform/anomalib)
  - facebookresearch/sam2 — Apache-2.0, pushed 2026-05-30 — [repo](https://github.com/facebookresearch/sam2)
  - facebookresearch/sam3 — non-standard licence (GitHub reports "NOASSERTION", i.e. a custom licence file that must be read before commercial use), pushed 2026-10-07 — [repo](https://github.com/facebookresearch/sam3)
  - IDEA-Research/GroundingDINO — Apache-2.0, last push 2024-08-12 (stale) — [repo](https://github.com/IDEA-Research/GroundingDINO)
  - roboflow/inference — non-standard/mixed licence ("NOASSERTION"), pushed 2026-10-13 — [repo](https://github.com/roboflow/inference)
  - landing-ai/vision-agent — Apache-2.0, last push 2026-01-29 — [repo](https://github.com/landing-ai/vision-agent)
- RF-DETR: Roboflow states code and core models are Apache 2.0 and usable in closed-source commercial products; Nano–Large are Apache 2.0, while XL and 2XL are under Roboflow's Platform Model License 1.0 — [Roboflow blog](https://blog.roboflow.com/rf-detr-is-free-to-use-commercially/); [RF-DETR vs alternatives](https://blog.roboflow.com/rf-detr-vs-alternatives/)
- Roboflow pricing page (fetched 13 Oct 2026): Free tier USD 0 with 10 credits/month ("~30 models or 80,000 inferences"); Core USD 39/month; credit packs from USD 89 (35 credits) to USD 1,399 (500 credits); extra prepaid credits "starting at $4", on-demand USD 6; Enterprise custom — [Roboflow pricing](https://roboflow.com/pricing)
- Roboflow serverless inference per credit: 8,000 images (RF-DETR Nano, YOLO26 Nano, YOLOv8 Nano), 5,333 (RF-DETR Medium), 2,000 (SAM 3); Qwen3-VL billed by GPU time, 500 s per credit — [Roboflow pricing](https://roboflow.com/pricing)
- Roboflow: self-hosted inference is "Included" on Free and Core; "All Roboflow-hosted models come with a commercial license"; but Ultralytics models need a separate Ultralytics licence and RF-DETR 2XL a commercial add-on for self-hosting — [Roboflow pricing](https://roboflow.com/pricing)
- A Roboflow post dated 18 Sep 2026 says the Core plan "now starts at $0", serverless moved to cheaper per-image pricing and self-hosted Roboflow Inference became free — [Roboflow blog](https://blog.roboflow.com/making-it-easier-cheaper-to-deploy-with-roboflow/); this conflicts with third-party trackers still showing Core at USD 79/month — [PricingSaaS](https://pricingsaas.com/companies/roboflow)
- Edge Impulse: the Developer plan became the default free tier on 6 May 2025 and includes "production-ready model licensing"; staff state the free version can go to production with no licence fees and generated code is Apache 2.0; Enterprise pricing is contact-sales — [Edge Impulse blog](https://edgeimpulse.com/blog/introducing-the-developer-plan/); [forum](https://forum.edgeimpulse.com/t/license-price/784); [plans](https://www.edgeimpulse.com/plans)
- EfficientAD (WACV 2024) trains only on anomaly-free images and reports ~2 ms latency / 600 images/s on a GPU — [paper](https://openaccess.thecvf.com/content/WACV2024/papers/Batzner_EfficientAD_Accurate_Visual_Anomaly_Detection_at_Millisecond-Level_Latencies_WACV_2024_paper.pdf)
- PatchCore (CVPR 2022) claims high sample efficiency, matching other methods "using only a fraction of the nominal training data"; its memory bank is the deployment cost — [paper](https://openaccess.thecvf.com/content/CVPR2022/papers/Roth_Towards_Total_Recall_in_Industrial_Anomaly_Detection_CVPR_2022_paper.pdf)
- A 2026 arXiv paper reports PatchCore-Lite cutting total memory footprint by 79% with a product-quantised memory bank (not independently reproduced) — [arXiv 2603.20288](https://arxiv.org/abs/2603.20288)
- A vendor implementation guide puts data needs at 500–2,000 labelled images per defect class for supervised models and 100–300 known-good images for anomaly detection — [OxMaint guide (vendor)](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- Specialised counters such as CountGD "consistently outperform VLMs on controlled counting benchmarks" — [arXiv 2511.17722](https://arxiv.org/html/2511.17722v3)

### Inferences
- For a closed-source product the practical stack is: RF-DETR (N–L) or D-FINE for detection/counting, Anomalib (EfficientAD/PatchCore) for "looks different from good" checks, SAM 2 for labelling assistance. All Apache-2.0, so licence cost = Rp 0. Using `pip install ultralytics` anywhere in the shipped product reintroduces the AGPL obligation, including for weights trained with it.
- Roboflow hosted inference at USD 4–6 per credit and 8,000 nano-model images per credit works out to about USD 0.0005–0.00075 per image (≈ Rp 9–13) — ESTIMATE from the pricing page figures above. That is fine for audits (thousands of images/month), expensive for inline QC (millions/month).
- SAM 3's custom licence and Roboflow Inference's mixed licence need a human read of the licence text before bundling; the API only reports that they are not a standard SPDX licence.

### Gaps
- No public figure for the Ultralytics Enterprise Licence; only a quote request would settle it.
- Not researched in depth (search budget exhausted): OWLv2, Florence-2, zero-shot counting models (e.g. CountGD licence and edge speed), LandingAI LandingLens current pricing. I found no reliable source on these in this session.
- No Jetson/RK3588/Hailo benchmarks for Anomalib models were found; EfficientAD's speed figure is GPU-only.

---

## 2. Software building blocks — ALPR/ANPR for Indonesian plates (Option B)

### Takeaway
Plate reading is commodity in 2026 at three levels: a Rp ~9.9M Hikvision access-ANPR camera that lists Indonesia, holds a 100,000-entry allowlist, works offline and drives the barrier from its own relay; MIT-licensed open source (Frigate's built-in LPR, fast-alpr/fast-plate-ocr); and a paid SDK (Plate Recognizer). What is not off-the-shelf is evidence of accuracy on Indonesian plates: published Indonesian pipelines report only ~84–87% exact-match, and public Indonesian datasets are tiny.

### Cited Findings
- Hikvision DS-TCG406-E datasheet (dated 11 Aug 2026): "Supports relay output to control vehicle barrier gate"; 2-channel relay output; "Up to 100,000 blocklist and allowlist"; "Supports offline control of barrier gate under allowlist mode"; barrier control mode "By Camera/Platform"; loop, radar and video triggering; Wiegand, RS-485, RS-232, 3 triggered inputs; ISAPI, SDK, ISUP, ONVIF S/G/T; IP67 and IK10; 12–24 VDC or PoE 802.3af, 10 W max; built-in IR + warm-white LEDs with plate-capture range 10 m (2.8–12 mm lens) or 20 m (8–32 mm) — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Same datasheet: Indonesia is listed under Asia in "ANPR Supported Country/Region" (130+ countries/regions across baseline and customised versions); stated accuracy "under recommended installation and lighting conditions": plate recognition rate 98.5%, capture rate 99%, driving-direction accuracy 98% — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Community reports on Hikvision ISAPI: a TCP listener receives pushed ANPR events as multipart XML + images and the camera repeats an event until acknowledged; another user found polling the plate list works while generic HTTP host notification did not fire for plate detection, so the push path is firmware-dependent — [IPCamTalk thread](https://ipcamtalk.com/threads/get-passed-license-plate-numbers-using-isapi.79032/post-888496)
- A third-party access system (BAS-IP Link) integrates Hikvision ANPR by subscribing to recognition events, checking its own identifier database and commanding a relay; this shows the "whitelist on server, camera as sensor" pattern is an established integration — [BAS-IP docs](https://basip.atlassian.net/wiki/spaces/Integrations/pages/249856010/Integration+with+Hikvision)
- Dahua's ANPR page claims 95–98% recognition with alphanumeric plates and ~100 ms read time, and lists "Raise barriers for authorized vehicles" as a function (vendor claim, no test protocol) — [Dahua ANPR](https://www.dahuasecurity.com/id/products/key-technologies/anpr)
- Frigate (MIT, pushed 2026-10-12) has built-in LPR: a lightweight YOLOv9 plate detector when no plate-capable model is present, PaddleOCR for text; `small` model reads Latin + Chinese, `large` is Latin-only with an enhanced detector for multi-line plates; requires ≥4 GB RAM and a CPU with AVX + AVX2; "GPU acceleration only provides a slight performance increase" — [Frigate LPR docs](https://docs.frigate.video/configuration/license_plate_recognition); [repo](https://github.com/blakeblackshear/frigate)
- Frigate LPR supports `known_plates` with wildcards/regex, `match_distance` for fuzzy matching (not on regex entries), `min_plate_length`, a `format` regex that discards non-matching reads, `recognition_threshold` default 0.9, `replace_rules` for O/0-type confusions, and a dedicated `type: "lpr"` camera mode; recommended detect 1920×1080 at 5 fps (10 for fast vehicles); inference above 100 ms may hurt recognition — [Frigate LPR docs](https://docs.frigate.video/configuration/license_plate_recognition)
- Frigate docs caveats: "If you can't read the plate yourself, Frigate likely can't either"; night accuracy depends on camera quality, lighting and IR; camera timestamps can be misread as plates; LPR does not run on stationary vehicles — [Frigate LPR docs](https://docs.frigate.video/configuration/license_plate_recognition)
- A user reports Frigate LPR never working on 0.16.1 with a 4K stream and TensorRT — [Frigate discussion #20432](https://github.com/blakeblackshear/frigate/discussions/20432)
- fast-alpr (MIT, last push 2026-03-16) uses open-image-models (MIT) for plate detection and fast-plate-ocr (MIT) for OCR by default — [fast-alpr on PyPI](https://pypi.org/project/fast-alpr/0.1.0); [fast-alpr repo](https://github.com/ankandrew/fast-alpr); [open-image-models repo](https://github.com/ankandrew/open-image-models)
- fast-plate-ocr ships four "global" CCT models (cct-s/xs v1/v2); latency 0.32–0.68 ms per plate measured on an RTX 3090; the README does not list covered countries and does not mention Indonesia; fine-tuning is supported via `fast-plate-ocr[train]` and a tutorial notebook — [fast-plate-ocr repo](https://github.com/ankandrew/fast-plate-ocr)
- PaddleOCR is Apache-2.0 (pushed 2026-09-16); EasyOCR is Apache-2.0 (last push 2025-12-05) — [PaddleOCR repo](https://github.com/PaddlePaddle/PaddleOCR); [EasyOCR repo](https://github.com/JaidedAI/EasyOCR)
- OpenALPR open-source edition is AGPL-3.0 and last pushed 2024-01-11 (stale) — [repo](https://github.com/openalpr/openalpr)
- CodeProject.AI Server: non-standard licence ("NOASSERTION"), last push 2025-07-14 — [repo](https://github.com/codeproject/CodeProject.AI-Server)
- Plate Recognizer (paid shortcut; fetched 13 Oct 2026): Snapshot Cloud and on-premise SDK priced the same — free 2,500 lookups/month, USD 50 for 50,000, USD 150 for 250,000, USD 250 for 500,000; make/model/colour adds 50%; Stream is USD 35/camera/month, or USD 45 with make/model/colour; "trained in over 90 countries" with no country list on the page — [Plate Recognizer pricing](https://platerecognizer.com/pricing/)
- Doubango's ANPR SDK docs say its Latin-charset models work for countries using Latin characters, naming Indonesia — [Doubango supported countries](https://www.doubango.org/SDKs/anpr/docs/Supported_countries.html)
- Indonesian plate format: prefix letters + up to four digits + suffix letters, plus an "NN•NN" month/year expiry row above (older) or below (newer) the number; cars 460×135 mm, motorcycles 275×115 mm; private plates were white-on-black from April 2011 to July 2022 and black-on-white since June 2022; FE-Schrift typeface adopted November 2022 for regular four-wheel plates; yellow (public), red (government), green (free-trade zone) and blue-trimmed EV plates also exist — [Wikipedia](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Indonesia)
- Korlantas said the switch to white plates was so ETLE cameras read numbers clearly, because black plates risk misidentification; rollout is phased (new vehicles, five-yearly renewals, transfers) with a target of all vehicles on white plates by 2027 — [Medcom](https://www.medcom.id/otomotif/mobil/xkEZWP9K-pelat-nomor-putih-diterapkan-korlantas-tidak-usah-beli); [Medcom 2027 target](https://www.medcom.id/otomotif/mobil/GNlWlA2K-tahun-2027-seluruh-kendaraan-diharapkan-gunakan-pelat-putih); [Antara](https://jabar.antaranews.com/berita/352853/polri-ubah-warna-pelat-nomor-kendaraan-bertahap-tahun-2022)
- Reported accuracy of Indonesian academic pipelines:
  - YOLOv11 + TrOCR: 86.21% exact-match recognition, 87.07% end-to-end — [Sistemasi journal](https://sistemasi.ftik.unisi.ac.id/index.php/stmsi/article/view/6697)
  - YOLOv9 + EasyOCR with CLAHE and Real-ESRGAN: 84.36% on 100 real-world images — [IIETA](https://iieta.org/node/19971)
  - YOLO11 + EasyOCR with Gaussian blur: character error rate 7% on black plates and 11.5% on white plates (thesis abstract) — [Telkom University](https://repositori.telkomuniversity.ac.id/pustaka/files/240380/abstract/implementasi-optical-character-recognition-ocr-dalam-mendeteksi-pelat-nomor-kendaraan-pada-sistem-manajemen-tilang-elektronik-pelanggaran-lalu-lintas-dalam-bentuk-buku-karya-ilmiah.pdf)
  - A Gaussian YOLOv7 study covers black, white, yellow and red plates — [JIKI UI](https://jiki.cs.ui.ac.id/index.php/jiki/article/view/1320)
- Public Indonesian plate data found: a Kaggle "Indonesian License Plate" set with 1,000 images / 1,906 annotated plates and a "Commercial Vehicle License Plate Dataset" with 362 photos from Semarang (both as described in a UMN thesis); Roboflow Universe projects include one with 49 images and one whose exports are not public — [UMN thesis](https://kc.umn.ac.id/id/eprint/40144/4/BAB_III.pdf); [Roboflow Universe](https://universe.roboflow.com/vision-8tbf0/indonesian-plate); [Roboflow public](https://public.roboflow.com/object-detection/license-plate-indonesia)

### Inferences
- Every Indonesian plate has two text rows (registration number + expiry "MM•YY"), so any OCR pipeline must drop or parse the second row. Frigate's `format` regex and `min_plate_length` can do this by configuration; a custom fast-plate-ocr model would need it in training data or post-processing. I found no source describing a two-row registration number on motorcycle plates; the "second line" is the expiry row on all plates.
- Two plate generations coexist until at least 2027 (white-on-black 2011–2022, black-on-white with FE-Schrift since 2022), plus yellow/red/green variants. The one colour-split result found shows white plates read worse (11.5% vs 7% CER) with a generic OCR, which suggests generic OCR models are not yet tuned to the newer typeface — a fine-tuning task for B2, not an issue for B1 if the camera vendor's Indonesia model handles it (unverified).
- 84–87% exact-match from academic pipelines is far from gate-grade; a gate that fails 1 in 7 residents is unusable. The gap between that and the camera vendor's 98.5% (stated only for recommended installation and lighting) is the engineering work B2 would have to do and B1 buys.
- Frigate's AVX/AVX2 requirement points to x86 mini PCs (N100/N150) rather than ARM boards as the Frigate host.
- Frigate itself is MIT, but its default standalone plate detector is described as a YOLOv9 model and the YOLOv9 reference repo is GPL-3.0; anyone redistributing Frigate inside a closed commercial box should check the licence of the specific model weights. This is a flag to verify, not a confirmed problem.

### Gaps
- No independent field accuracy figure for any product on Indonesian plates (night, rain, dirty or modified plates, non-standard fonts). The vendor 98.5% and the academic 84–87% are the only numbers found.
- Whether fast-plate-ocr's "global" models include Indonesian plates is not stated in its README.
- Plate Recognizer's page does not confirm Indonesia support.
- Dahua ITC Indonesian-plate support and ISAPI/HTTP event documentation from Hikvision itself were not retrieved.
- No large (>10k) public Indonesian plate dataset with character-level labels was found.

---

## 3. Software building blocks — vehicle make/model recognition (Option B) and multimodal LLM APIs as a shortcut (both options)

### Takeaway
Make (brand) recognition is available on the ANPR camera itself; fine-grained model recognition for the Indonesian market is not off-the-shelf and would be an ongoing data-maintenance task. Hosted VLMs are now very cheap per image (≈ Rp 4 with Claude Haiku 5.5) and good enough for periodic audits and as a second opinion, but published benchmarks put them well below industrial requirement for defect/anomaly questions and unreliable for exact counting, and local VLMs take seconds per image on a Jetson — so neither real-time gate decisions nor inline QC should depend on them.

### Cited Findings
- Hikvision DS-TCG406-E: "Supports vehicle type, vehicle color, and vehicle brand recognition"; brand list covers 84 manufacturers including Toyota, Honda, Daihatsu, Suzuki, Mitsubishi, Isuzu, Hino, Nissan, Mazda, Hyundai, KIA, BYD, Chery, Perodua and Proton; vehicle types include Car/Van/Bus/Truck/SUV_MPV/Pickup/Motorcycle — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Plate Recognizer charges +50% on Snapshot or USD 45 vs 35 per camera/month on Stream for make/model/colour — [Plate Recognizer pricing](https://platerecognizer.com/pricing/)
- UGM work on Indonesian vehicles (InaV-Dash, dashboard-camera images, 10 models from 4 manufacturers) reports 98.73% manufacturer and 97.69% model accuracy with a multi-task VGG-16, and motivates the task by the visual similarity of e.g. Avanza and Xenia — [UGM repository](https://etd.repository.ugm.ac.id/penelitian/detail/229112)
- A YOLOv4 study on Yogyakarta CCTV with 8 classes (including Honda Brio and Toyota Avanza) from 7,034 images reports 82% accuracy — [KLIK journal](https://klik.ulm.ac.id/index.php/klik/article/view/625)
- An Indonesian highway dataset for make/model recognition provides 3,847 images (Data in Brief, 2022) — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9006761/)
- VMMRdb is a 2017 dataset (stale; pre-dates most current Indonesian-market models) — [CVPRW 2017](https://mlanthology.org/cvprw/2017/tafazzoli2017cvprw-large)
- A survey notes make/model methods are not comparable unless tested on the same dataset — [arXiv 2006.16400](https://arxiv.org/pdf/2006.16400)
- Claude API prices per million tokens (fetched 13 Oct 2026): Opus 5.5 USD 4 in / 20 out; Sonnet 5.5 USD 2 / 10; Haiku 5.5 USD 0.10 / 0.50 for prompts ≤100K tokens; Batch API 50% off — [Claude pricing](https://claude.com/pricing)
- Claude image cost: visual tokens = ⌈width/28⌉ × ⌈height/28⌉; a 1000×1000 px image is 1,296 tokens; 1920×1080 is 1,560 tokens on the standard tier (downsized) or 2,691 on the high-resolution tier (Claude 4.7 and later) — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Claude vision documented limitations: counts are approximate "especially with large numbers of small objects"; coordinate/localisation outputs are approximate; mistakes on low-quality, rotated or very small images; "Do not use Claude for tasks requiring perfect precision ... without human oversight" — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Gemini API paid tier per million tokens (page updated 9 Oct 2026): Gemini 3.8 Flash USD 0.75 in / 3.75 out (listed as doubling on 1 Jan 2027); Gemini 3.5 Flash-Lite 0.30 / 2.50; Gemini 3.1 Flash-Lite 0.25 / 1.50; Gemini 2.5 Flash-Lite 0.10 / 0.40; batch is 50% of standard; most Flash/Flash-Lite models have a free tier whose data may be used to improve Google products — [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
- OpenAI API per million tokens (fetched 13 Oct 2026): gpt-6-luna USD 0.10 in / 0.50 out; gpt-5.4-nano 0.20 / 1.25; gpt-5.4-mini 0.75 / 4.50; gpt-6-sol 2.00 / 10.00; batch 50% of standard; the page does not explain image tokenisation — [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- MMAD benchmark (ICLR 2025; 39,672 questions on 8,366 industrial images): GPT-4o averaged 74.9%, Gemini 1.5 Pro 73%, GPT-4o-mini 66.3%, Gemini 1.5 Flash 68.9%, best open model (InternVL2-76B) 70.8%; ordinary humans beat the best model by ~4 points and experts by ~12; the authors judge the result far short of industrial requirements. Models tested are 2024-generation, so the absolute numbers are stale — [arXiv 2410.09453](https://arxiv.org/abs/2410.09453)
- VLMCountBench (Oct 2025): VLMs count reliably with one shape type but "fail substantially" when several types are combined, with quantities of only 11–20 — [arXiv 2510.04401](https://arxiv.org/abs/2510.04401v1)
- Plate reading by VLMs, Nigerian study (July 2026, 88 hard real-world images): Gemini 2.0 Flash and Qwen2.5-VL-7B clearly best; reported average CER 0.322 for Qwen2.5-VL-7B vs 0.556 for GPT-4o and 0.682 for Claude 4 Sonnet — [arXiv 2607.02025](https://arxiv.org/abs/2607.02025); [PDF](https://arxiv.org/pdf/2607.02025)
- Plate reading by VLMs, Malaysian study (2024): GPT-4o 97.1% character accuracy, Gemini 1.5 Pro/Flash 93.8%; fine-tuned VehiclePaliGemma 87.6% — [arXiv 2412.14197](https://arxiv.org/abs/2412.14197)
- Local VLM speed (LearnOpenCV, 2 Sep 2025, Ollama 4-bit): Qwen2.5-VL 3B on Jetson Orin Nano 8GB took ~4 s for a counting question and 21.27 s for OCR; on Raspberry Pi 5 OCR took 145.43 s; Moondream2 was "much faster" but produced garbage output on the Orin Nano in their test — [LearnOpenCV](https://learnopencv.com/vlm-on-edge-devices/)

### Inferences
- **ESTIMATE, cost per image with Claude** (1000×1000 px image = 1,296 input tokens, ~300-token instruction, ~150-token answer, excluding any thinking tokens, which are billed as output and can multiply the output part): Haiku 5.5 ≈ USD 0.00024 (≈ Rp 4); Sonnet 5.5 ≈ USD 0.0047 (≈ Rp 84); Opus 5.5 ≈ USD 0.0094 (≈ Rp 168). Batch halves these but is asynchronous.
- **ESTIMATE, monthly VLM cost**: A1 audit at 200 photos/day × 26 days = 5,200 images → ≈ USD 1.2 (Haiku 5.5), USD 24 (Sonnet 5.5), USD 49 (Opus 5.5). B as second-opinion on 300 vehicle events/day = 9,000 images → ≈ USD 2 (Haiku 5.5) or USD 42 (Sonnet 5.5). Inline QC at 1 image/s for 16 h × 26 days ≈ 1.5 million images → ≈ USD 350/month even on Haiku 5.5, before latency is considered.
- The two VLM plate studies contradict each other on model ranking (GPT-4o best in Malaysia, near the bottom in Nigeria), on small datasets. The safe reading: VLMs can read plates zero-shot but accuracy is condition-dependent and none of the evidence is on Indonesian plates.
- Camera-supplied "brand" is not "model": the datasheet promises manufacturer, colour and type. Distinguishing Avanza from Xenia, or covering new launches, needs a custom classifier plus a retraining routine every time a model launches or is facelifted. Wuling does not appear in the manufacturer list as printed in the datasheet, which hints that Indonesia-popular brands may be patchy.
- A cheap way to deliver "make/model" without owning a classifier is to store it at enrolment (the resident declares plate + car) and use the camera's brand/colour/type only as a consistency check; a hosted VLM can be the asynchronous auditor of mismatches. This turns the hardest ML component of B into a database field.

### Gaps
- No benchmark of 2026-generation hosted VLMs on Indonesian plates, Indonesian-market vehicle models, fill level, hairnet/cleanliness or label conformity was found.
- No sourced latency figures for hosted VLM calls from Indonesia; real-time suitability is argued from architecture (network round trip, internet dependence), not measured.
- Gemini and OpenAI per-image token counts for current models were not on the pricing pages, so only Claude per-image cost could be computed.
- Stanford Cars and CompCars coverage of Indonesian models was not checked. SmolVLM, InternVL, PaliGemma and Moondream edge timings were not found in text form.

---

## 4. Hardware bill of materials with Indonesian street prices (IDR)

### Takeaway
In October 2026 the Raspberry Pi 5 is no longer the cheap option in Indonesia (8GB board Rp 5.22M after the memory price surge); an Orange Pi 5 8GB (from Rp 2.6M) or an N100/N150 mini PC (Rp 3.4–5.3M) is cheaper, and a Jetson Orin Nano Super is Rp 10.8–16.5M. Option B's whole sensing + decision + relay function is available in one Rp ~9.9M camera; Option A's cost is dominated not by compute but by the parts that could not be priced from marketplaces (lens, lighting, enclosure, mounting, trigger/reject hardware) and by integration labour.

### Cited Findings
Edge compute
- Raspberry Pi 5 8GB: Rp 5,220,000, in stock (6 pcs, Surabaya) — [Digiware](https://digiwarestore.com/en/product-categories/raspberry-pi-5-8gb-ram-made-in-uk-mini-pc-raspi-5-442499.html); bundle with official PSU and case Rp 5,867,800 (back order) — [Digiware kit](https://digiwarestore.com/en/raspberry-kit/paket-raspberry-pi-5-8gb-ram-with-official-power-supply-and-case-642702.html); a Japanese reseller attributes recent increases to a global memory price surge affecting 8GB/16GB models — [Switch Science](https://www.switch-science.com/products/9250)
- Raspberry Pi AI HAT+ 13 TOPS (Hailo-8L): Rp 1,872,000 — [Digiware](https://digiwarestore.com/en/raspberry-hat/official-raspberry-pi-ai-hat-built-in-hailo-8-ai-accelerator-13-tops.html); Rp 1,720,000 — [Tokopedia seller](https://www.tokopedia.com/badank/official-raspberry-pi-ai-hat-hailo-8l-13-tops-artificial-intelligence-module-for-raspberry-pi-5-1731250842210567310); 26 TOPS (Hailo-8) Rp 2.55–3.27M — [Tokopedia listing page, June 2026](https://www.tokopedia.com/find/raspberry-pi-ai-hat); AI HAT+ 2 (Hailo-10H, 40 TOPS, 8GB on-board RAM) Rp 4,880,000 — [Blibli, Aug 2026](https://www.blibli.com/jual/raspberry-pi-5-hat)
- AI HAT+ 2 uses Hailo-10H (40 TOPS INT4, 8GB RAM), Pi 5 only via PCIe, with computer-vision performance comparable to the older 26 TOPS HAT — [The Pi Hut](https://thepihut.com/collections/raspberry-pi-hats/products/raspberry-pi-ai-hat-2)
- Orange Pi 5 (RK3588S): 4GB Rp 2.47–2.80M; 8GB from Rp 2,635,000 (with case/PSU Rp 3.5–3.8M); 16GB Rp 3,887,800 — [Tokopedia RK3588S listings, June 2026](https://www.tokopedia.com/find/rk3588s); [seller listing](https://www.tokopedia.com/zeromedia/orange-pi-5-8gb-ram-single-board-computer-rk3588s?extParam=ivf%3Dfalse)
- NVIDIA Jetson Orin Nano Super 8GB developer kit: Rp 10,808,000 with 256GB NVMe and Rp 10,999,000 for the official kit — [Blibli, July 2026](https://www.blibli.com/jual/jetson-orin-nano); Rp 13.6–16.5M on other listings — [Tokopedia, Sep 2026](https://www.tokopedia.com/find/nvidia-jetson-nano-super); pre-order Rp 11,500,000 with 15-day lead time — [Tokopedia seller](https://www.tokopedia.com/tuluscs/nvidia-jetson-orin-nano-super-8gb-developer-kit-edge-ai-robotics-development-board-1732060467041568610); for comparison RS Taiwan lists it at TWD 11,072 excl. tax — [RS Online](https://twen.rs-online.com/web/p/processor-development-tools/2647384)
- N100/N150 mini PCs: ASUS NUC 14 Essential N150 full set ≈ Rp 3.4M; MSI Cubi N N100 barebone from Rp 2.3M; marketplace average for "N100 mini PC" Rp 6.26M — [Blibli, Sep 2026](https://www.blibli.com/jual/n100-minipc); OUMAX A1 N100 16GB/512GB Rp 4.4–5.25M — [Tokopedia, Oct 2026](https://www.tokopedia.com/find/mini-pc-n100); GMKtec G3 Plus N150 8GB/256GB ≈ Rp 4.8M — [Tokopedia, Oct 2026](https://www.tokopedia.com/find/gmktec-n150)
- Google Coral USB Accelerator is listed as retired/discontinued by a retailer with no direct replacement — [Core Electronics](https://core-electronics.com.au/google-coral-usb-accelerator.html.plain.md)

Inference speed
- Jetson Orin Nano Super, YOLO26n at 640 px, TensorRT: 4.57 ms/image FP16 and 3.80 ms INT8; Orin NX 16GB: 4.13 ms and 3.49 ms (Ultralytics 8.4.33; excludes pre/post-processing; note these are AGPL models) — [Ultralytics Jetson guide](https://docs.ultralytics.com/guides/nvidia-jetson/)
- RK3588 (Orange Pi 5), RKNN int8: mean total time ≈ 15.0 ms (YOLOv5), 17.3 ms (YOLOv8), 23.0 ms (YOLO11); model size and input resolution not stated — [PhotonVision RKNN benchmarks](https://docs.photonvision.org/en/latest/docs/benchmarks/rknn-model-benchmarks.html); a separate ncnn-based project reports 58.8 FPS (yolov5n) and 37.7 FPS (yolov5s) on RK3588 — [Q-engineering](https://github.com/Qengineering/YoloV5-NPU)
- Raspberry Pi 5 + Hailo: sources conflict. Forum users report 105 FPS (YOLOv8s, C++, no pre/post-processing) and cite a Hailo batch-8 figure of ~128 FPS, with replies warning that model-zoo numbers are raw chip throughput not comparable to application FPS — [Hailo community](https://community.hailo.ai/t/the-performance-on-the-raspberry-pi-5-with-the-hailo-8-chip-seems-not-good-as-he-official-results/17473); a third-party blog gives roughly 25–35 FPS at 640×640 on Hailo-8L — [mustafa.net, Mar 2026](https://mustafa.net/2026/03/12/hailo-8l-ai-accelerator-edge-ai-for-raspberry-pi-and-homelab-projects/)

Cameras
- Ordinary outdoor IP cameras: TP-Link Tapo C320WS Rp 629,000–649,000 — [Tokopedia official store](https://www.tokopedia.com/tp-linkindonesia/tp-link-tapo-c320ws-cctv-wifi-ip-kamera-outdoor-2k-qhd-full-color-camera-tahan-air-wireless-1731074158796178819); EZVIZ H3c Rp 808,000–1,099,000 — [Tokopedia, Sep 2026](https://www.tokopedia.com/find/ezviz-h3c); Hikvision DS-2CD1023G2 2MP Rp 955,000–1,144,000 — [Tokopedia, July 2026](https://www.tokopedia.com/find/hikvision-ds-2cd1023g2-liu-2mp); TP-Link VIGI C330 Rp 650,000–809,000 (seen in the same marketplace result set; exact listing page not confirmed) — [Blibli, July 2026](https://www.blibli.com/jual/kamera-cctv-tp-link-outdoor)
- ANPR cameras: Hikvision DS-TCG406-E 4MP ≈ Rp 9.9M, TCG405 ≈ Rp 17.5M, iDS-TCM403-BI(C) ≈ Rp 23.9M — [Tokopedia, Sep 2026](https://www.tokopedia.com/find/anpr-hikvision); Dahua DHI-ITC436-PW9H-IZP ≈ Rp 19.5M, DHI-ITC413-PW4D-Z1 ≈ Rp 21.6M, another 4MP ANPR Rp 14.5M — [Tokopedia, Sep 2026](https://www.tokopedia.com/find/anpr-camera)
- Incidental (market researchers own this): a local "ANPR untuk Sistem Gate" software + hardware bundle for 2 cameras that works with any RTSP camera is listed at Rp 11M, i.e. the B2 architecture is already sold locally — [Tokopedia seller](https://www.tokopedia.com/digi/anpr-untuk-sistem-gate-paket-basic-econo-hardware-2-kamera)
- Industrial cameras: Hikrobot MV-CU013-80GM GigE mono ≈ Rp 4.8M, MV-CE020-10GC colour ≈ Rp 5.6M, smart camera MV-SC2004EC ≈ Rp 12.2M — [Tokopedia, May 2026](https://www.tokopedia.com/find/hikrobot); Basler acA1300-30gm ≈ Rp 30M, acA2040-90uc ≈ Rp 42.5M (mix of reseller and used listings) — [Tokopedia, Sep 2026](https://www.tokopedia.com/find/basler-camera); European reference: Hikrobot MV-CA050-10GM 5MP global shutter EUR 280 excl. VAT (discontinued model) — [Maxxvision](https://www.maxxvision.com/produkte/kameras/abgekuendigte-kameras/318/mv-ca050-10gm)

Gate side (Option B)
- Barrier gates (unit only): BL50 24V BLDC ≈ Rp 4.51M, MX10 ≈ Rp 5.5M — [Blibli, July 2026](https://www.blibli.com/jual/parking-gate-otomatis); MX-50 Rp 6.8M, MX-51 Rp 7.0M, MX-80 Rp 8.8M, MX-81 Rp 9.0M — [Blibli, Nov 2025](https://www.blibli.com/jual/boom-gate-parkir); MX-10 4 m Rp 7,349,000 — [Indotrading](https://www.indotrading.com/putrasafetymandiri/barrier-gate-portal-palang-parkir-otomatis-mx-10-4-meter-p872279.aspx)
- Sliding-gate motors: local-brand 1000 kg opener Rp 2.5–2.8M — [Indotrading supplier](https://pagarotomatis.web.indotrading.com/); Gatech ≈ Rp 6.85M — [Indotrading](https://en.indotrading.com/bintangselatan/automatic-slidding-gate-p142624.aspx); BFT Deimos Rp 12.5–15.45M, BFT photocell ≈ Rp 2.85M, BFT remotes Rp 587,000–842,000 — [Tokopedia, Jan 2026](https://www.tokopedia.com/find/pagar-otomatis-bft); Beninca BULL 10M ≈ Rp 27.56M excluding civil works and cabling — [Tokopedia distributor](https://www.tokopedia.com/ptlautancipta/beninca-automatic-sliding-gate-bull-10-m); Beninca BULL 20M ≈ Rp 26.4M — [Indotrading](https://en.indotrading.com/lautanciptakreasi/mesin-otomatis-pagar-sliding-beninca-bull20m-p750228.aspx)
- Relays: Shelly 1 Gen3 (dry contact, 16 A) Rp 219,000–228,000 — [Tokopedia, Oct 2026](https://www.tokopedia.com/find/shelly-1-gen3); Shelly 1 Mini Gen3 Rp 252,000 from the official store — [Tokopedia official store](https://www.tokopedia.com/shelly-official-store/shelly-1-mini-gen3-wifi-smart-relay-switch-with-potential-free-contacts-1-channel-8a-light-control-and-garage-door-opener-alexa-and-google-home-no-hub-required-1734020285102982291); Sonoff MINI-D dry contact Rp 364,000 — [Tokopedia, Aug 2026](https://www.tokopedia.com/find/smart-relay)
- How gates are triggered: potential-free (dry) relay contacts wired to the controller's trigger/push-button input, pulsed for ~1 s to simulate a button press; the relay is galvanically isolated — [ESPHome device page](https://devices.esphome.io/devices/Shelly-1-Gen4/); reading the gate's status back is harder (one user's controller output 4.8 V where the relay input needed ≥12 V, needing an opto-coupler or a separate reed switch) — [Node-RED forum](https://discourse.nodered.org/t/trying-to-automate-my-gate-opener/89928)
- ANPR cameras can replace the separate relay and the loop-detector logic: the DS-TCG406-E has 2 relay outputs for barrier open/close, Wiegand to access controllers, and loop/radar/video triggering — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)

Factory side (Option A)
- A vendor guide breaks a single inspection station into cameras + lighting USD 3K–15K, edge compute USD 2K–8K, software/model development USD 15K–80K, total USD 25K–120K (vendor figures) — [OxMaint guide](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- Late lighting decisions "often lead to cost overruns, inferior lighting, and delays in production timelines" — [Control Design](https://www.controldesign.com/sensing/vision-systems/article/55089765/common-pitfalls-in-machine-vision-lighting)

### Inferences
**ESTIMATE — hardware BOM per site, built only from the listed prices above (excludes cabling, PSU, enclosure, mounting, UPS, labour unless noted):**

| Design | Low | Typical | High |
|---|---|---|---|
| A1 phone audit | Rp 0 (customer phones) | Rp 0 | Rp 0 |
| A2 fixed camera, alert-only | Rp 3.3–4.9M (IP cam Rp 0.63–1.14M + Orange Pi 5 8GB Rp 2.6–3.8M) | Rp 4.0–6.4M (IP cam + N100/N150 mini PC Rp 3.4–5.25M) | Rp 7.6–8.2M (IP cam + Pi 5 8GB Rp 5.22M + AI HAT+ 13 TOPS Rp 1.72–1.87M) — lighting not priced |
| A3 inline station | Rp 8.2–10.9M (Hikrobot GigE Rp 4.8–5.6M + mini PC) before lens/light/trigger/enclosure | Rp 15.6–19.6M (Hikrobot + Jetson Orin Nano Super Rp 10.8–14M) before lens/light/trigger/enclosure | Vendor all-in USD 25K–120K ≈ Rp 0.45–2.15 billion including software and integration |
| B2 own ALPR on RTSP camera (customer already has a gate motor) | Rp 3.5–5.2M (IP cam + Orange Pi 5 8GB + Shelly Rp 0.22–0.25M) | Rp 4.3–6.6M (IP cam + N100/N150 mini PC + Shelly) | Rp 12–16M (IP cam + Jetson + Shelly) |
| B1 on-board ANPR camera (customer already has a gate motor) | Rp 9.9M (DS-TCG406-E, relay and allowlist built in) | Rp 12.5–13.7M (camera + Orange Pi 5 gateway for cloud sync) | Rp 14.5–23.9M (higher Hikvision/Dahua models) |
| B3 including gate hardware | Rp 14.4M (DS-TCG406-E + BL50 barrier Rp 4.51M) | Rp 19–22M (camera + MX-series barrier Rp 6.8–9M + photocell Rp 2.85M) | ≈ Rp 52M (Dahua Rp 21.6M + Beninca BULL 10M Rp 27.56M + photocell Rp 2.85M) plus civil works |

- On compute cost alone, Orange Pi 5 8GB (≈17–23 ms per YOLO-class inference on its NPU) is the best price/performance in Indonesia right now; but RK3588 needs RKNN model conversion and Frigate needs AVX2, so the N100/N150 mini PC is the lower-effort choice for a solo developer and comes with a case, PSU and SSD.
- A Jetson is only justified where many models or high frame rates run on one box (multi-camera A3). For a single gate lane or a periodic A2 check it is 2–3× the cost of what is needed.
- B1 costs more in hardware than B2 (≈ Rp 10M vs ≈ Rp 4–6M) but removes the developer's ML, night-tuning and relay-safety engineering; it also moves the product warranty for the sensing part onto a brand with local distribution.

### Gaps
- Not priced from Indonesian sources (search budget exhausted): machine-vision lenses, bar/ring/dome lights, IR illuminators, IP65/IP69K camera enclosures, UPS units, loop detectors, generic photocells, trigger sensors, encoders, air-blow/pusher reject mechanisms, PLC I/O modules, stack lights, industrial tablets/HMI, ESP32 relay boards, USB/Modbus relays.
- Daheng camera prices in Indonesia: none found.
- Used office mini PCs, Android TV boxes and old phones as edge devices: no sourced price or performance data.
- Digiware's Jetson Orin Nano Super page returned a server error; the Jetson range rests on Blibli and Tokopedia listings.
- Orange Pi 5 Plus (RK3588, non-S) IDR price not found; only non-Indonesian prices surfaced.
- Hailo official model-zoo FPS table and Seeed's benchmark values (images only, page last updated July 2024) were not extractable.

---

## 5. Per-site deployment effort and customisation

### Takeaway
B is the same problem at every site (one national plate format, one camera geometry rule set, one relay wiring pattern), so per-site work is physical installation and plate enrolment. A is a different problem at every site (different products, defects, lighting and line integration), and vendor guidance puts one inspection station at 8–16 weeks with hundreds to thousands of labelled images per defect class. The only A design with B-like or lower per-site effort is the hardware-free audit app, where the customisation moves into checklist/prompt configuration.

### Cited Findings
- Vendor timeline for one AI inspection station: 8–16 weeks from kickoff to production — defect taxonomy weeks 1–2, cameras and lighting weeks 2–4, image collection and labelling weeks 4–8, model weeks 6–10, false-reject tuning weeks 10–14, integration weeks 12–16 — [OxMaint guide (vendor)](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- Same guide: 500–2,000 labelled images per defect class (supervised) or 100–300 known-good images (anomaly detection); shadow mode 2–4 weeks before live rejection; quarterly revalidation; targets of 97–99%+ detection and <0.5–1% false rejects once tuned (vendor claims) — [OxMaint guide (vendor)](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- A confectionery case study ran AI vision in shadow mode alongside manual inspection for 4 weeks, had a second line with 22 SKUs requiring an expanded model library, and calibrated false positives below 0.8% (vendor case study) — [OxMaint case study](https://oxmaint.com/industries/fmcg/case-study-confectionery-brand-quality-rejects-38-percent-reduction)
- "Proving the inspection works well over many parts ... sometimes takes more time than the programming" — [Control Engineering](https://www.controleng.com/robust-vision-inspection-in-5-steps/)
- An inspection vendor reports 77% of customer challenges were about deployment and initial setup — connectivity (no WiFi, guest networks expiring, IT blocking downloads), installation (mounting hardware and sign-offs causing weeks of delay), lighting (shadows, glare) and inconsistent labelling; the remaining issues were missed rare defects and poor transfer to new product variants (colours, surfaces, profiles) — [Enao Vision, 26 Feb 2026](https://enaovision.com/blog/ai-visual-inspection-fails-easy-fixes)
- ANPR installation geometry (Dahua): plate needs 70–250 px width (EU 130–250); plate angle under 5°; camera horizontal angle under 30°; at 6 m mounting height minimum snapshot distance 10.2 m with 25 m recommended; side mount on a 2 m pole needs at least 7 m capture distance — [Dahua ANPR](https://www.dahuasecurity.com/id/products/key-technologies/anpr)
- Frigate's configuration-side requirements per camera: 1080p detect at 5–10 fps, tuned motion threshold/contour area, a motion mask over the timestamp, minimum plate area 1,000 px — [Frigate LPR docs](https://docs.frigate.video/configuration/license_plate_recognition)
- A practitioner running LPR gate control (Blue Iris + CodeProject.AI + Home Assistant over MQTT) says OCR is usually fine in daylight for stopped or slow cars and "the hardest part is tweaking your camera to return quality images at night" — [IPCamTalk](https://www.ipcamtalk.com/threads/gate-automation.74141)
- The Hikvision access-ANPR camera has an "entrance and exit dedicated exposure algorithm" for front/back light and built-in supplement lights sized for 10–20 m plate capture, i.e. the night-tuning problem is addressed in the product — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Beninca's distributor notes the motor price excludes civil works, wall/floor chasing and cable runs — [Tokopedia distributor](https://www.tokopedia.com/ptlautancipta/beninca-automatic-sliding-gate-bull-10-m)

### Inferences
**What differs per customer, and ESTIMATED effort (basis in brackets; no practitioner hour-logs were found):**

| Step | A1 phone audit | A2 fixed camera alert-only | A3 inline with reject | B1 on-board ANPR | B2 own ALPR |
|---|---|---|---|---|---|
| Data collection / labelling | 5–20 reference photos per check, no labelling | 100–300 good images per view (anomaly) or reuse a pretrained fixed-scope model | 500–2,000 labelled images per defect class | none | none per site once the national OCR model exists |
| Model retraining | none (prompt/config) | threshold tuning; retrain when SKU or background changes | per product/SKU | none | none per site; re-tune on problem cameras |
| Lighting and mounting | none | mount + often added light | controlled lighting rig, enclosure | pole/wall mount to vendor geometry | same, plus manual exposure/IR tuning at night |
| Integration | none (app) | network access on factory LAN | PLC/reject/trigger wiring | 2 wires to gate controller input | 2 wires + edge box |
| Acceptance testing | 1–2 weeks of side-by-side review (calendar) | 2–4 weeks shadow mode (calendar) | 2–4 weeks shadow mode + FAT | drive-through test day and night | several nights of observation |
| ESTIMATED labour per site | 2–6 h remote | 2–4 days | 8–16 weeks (vendor timeline) | 4–8 h on site + 1–2 h remote | 1–3 days incl. a likely return visit |

- Basis for B1's 4–8 h: one camera, one PoE cable, one relay pair, and plate enrolment; the datasheet shows exposure, lights, relay and allowlist are in the device. Basis for B2's extra time: the practitioner statement that night image tuning is the hardest part. Basis for A2: vendor's 100–300-image requirement and the 77% "deployment and setup" problem share. These are judgement estimates.
- Designs that minimise per-site work: for B, rely on the camera's on-board ANPR and allowlist and ship a cloud whitelist app (optionally with a small gateway); a self-install kit is plausible only where the customer's gate installer does the wiring. For A, either the phone audit app or a single SKU-agnostic check ("crate full / not full", "hairnet on / off") whose model is trained once and reused, sold as alert/log-only so that no PLC, trigger sensor, encoder or reject mechanism is needed.
- Alert/log-only A2 avoids: trigger sensors and encoders (use video motion or periodic sampling), reject mechanisms, PLC I/O and fieldbus protocols, and line-stop liability. It still needs a factory network path, a mounting point and stable lighting.
- The 50th-customer question turns on whether effort is in configuration or in engineering: B1 and A1 are configuration; B2 is configuration plus occasional tuning; A2 is light engineering each time; A3 is a project each time.

### Gaps
- No practitioner or system-integrator source with actual hours for an ANPR gate install or for an A2-style deployment was found; the labour figures are estimates.
- No source on how well a single pretrained "crate full" or "hairnet" model transfers across factories without retraining.
- Self-install success rates for camera-based gate kits: no data.

---

## 6. Reliability and failure modes in real conditions, and the support load they create

### Takeaway
A's failures are diffuse and recurring (lighting drift, new SKUs, labelling inconsistency, pilots that do not hold up in continuous running), which produces ongoing retuning work and erodes operator trust. B's failures are narrower and mostly physical (night image quality, dirty/modified plates, camera angle) but each one is visible to the customer immediately and one class of error — an unauthorised open or a gate closing on something — is a security or safety incident rather than a quality nuisance.

### Cited Findings
Factory (A)
- Inspection AI fails through poor training data, changes in product appearance, lighting problems and model limitations, leading to missed defects, false alarms and loss of confidence in automated checks — [Edge AI and Vision Alliance, Feb 2026](https://www.edge-ai-vision.com/2026/02/what-happens-when-the-inspection-ai-fails-learning-from-production-line-mistakes/)
- "Detection rates from a controlled pilot rarely match what a system sustains once it is running continuously against real production variation" — [MachineFi blog](https://machinefi.com/blog/computer-vision-manufacturing-quality-inspection)
- Models that worked on one variant failed on new colours, surfaces or profiles and sometimes produced false positives; rare or subtle defects were missed where too few samples had been collected — [Enao Vision](https://enaovision.com/blog/ai-visual-inspection-fails-easy-fixes)
- Site connectivity is itself a failure mode: no WiFi, expiring guest networks, IT policies blocking downloads — [Enao Vision](https://enaovision.com/blog/ai-visual-inspection-fails-easy-fixes)
- Vendor guidance expects quarterly revalidation and a false-reject tuning phase of about four weeks per station — [OxMaint guide (vendor)](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- Best VLM on the MMAD industrial benchmark reached 74.9%, judged far short of industrial requirements (2024 models) — [arXiv 2410.09453](https://arxiv.org/abs/2410.09453)

Gate (B)
- Vendor accuracy is conditional: Hikvision's 98.5% recognition and 99% capture are stated "under recommended installation and lighting conditions"; Dahua's 95–98% carries no test protocol — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf); [Dahua ANPR](https://www.dahuasecurity.com/id/products/key-technologies/anpr)
- Night image quality is the hard part in practice — [IPCamTalk](https://www.ipcamtalk.com/threads/gate-automation.74141); Frigate: night accuracy depends on camera quality, lighting and IR; timestamps and overlays can be read as plates — [Frigate LPR docs](https://docs.frigate.video/configuration/license_plate_recognition)
- Frigate warns its occupancy sensors have fewer checks so "false positives can sometimes trigger these sensors", recommending filtered MQTT event topics instead — [Frigate discussion #16697](https://github.com/blakeblackshear/frigate/discussions/16697)
- Camera firmware matters: Hikvision event push for plates behaves differently from generic HTTP notifications depending on model/firmware — [IPCamTalk](https://ipcamtalk.com/threads/get-passed-license-plate-numbers-using-isapi.79032/post-888496)
- The Hikvision camera supports "dirty license plate recognition", multi-frame LPR, offline barrier control under allowlist mode, and a mode that keeps the boom open for following vehicles — the last one is tailgating by design, for throughput — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- EN 12453 (as summarised in a gate-opener manufacturer's manual) sets minimum protection by use case: a force limiter alone when the user operates the gate in view; force limiter plus two photocell pairs when operated out of sight; force limiter plus one photocell pair on the closing movement for automatic timed closing — [Avidsen manual](https://pim.avidsen.com/documentsproduits/en/510064-user-guide-v7.pdf)
- Layered gate safety (photocells across the opening, safety edges on the leaf, force monitoring) is described as necessary because no single device is sufficient (commercial sources) — [Quantek](https://quantek.co.uk/blog/automatic-gate-regulations/); [home security guide](https://home-security-guide.readthedocs.io/en/latest/access-control/09-gate-safety-sensors-and-obstruction-detection/)
- Indonesian academic end-to-end plate reading sits at 84–87% exact match, and white plates showed higher character error than black in one study — [Sistemasi](https://sistemasi.ftik.unisi.ac.id/index.php/stmsi/article/view/6697); [Telkom University](https://repositori.telkomuniversity.ac.id/pustaka/files/240380/abstract/implementasi-optical-character-recognition-ocr-dalam-mendeteksi-pelat-nomor-kendaraan-pada-sistem-manajemen-tilang-elektronik-pelanggaran-lalu-lintas-dalam-bentuk-buku-karya-ilmiah.pdf)

### Inferences
- A plate is a weak credential: it is printed, visible and copyable, and fuzzy matching (`match_distance`) widens the acceptance set. A plate-only gate is a convenience control, not a security control; pairing it with a second factor for sensitive sites (remote tag, app confirmation, guard) and logging every open with an image limits the exposure. Make/model/colour mismatch is a useful anti-cloning signal, which is the real argument for the make/model feature.
- A camera-triggered open is, in EN 12453 terms, operation with the user out of sight of whoever (or whatever) issued the command. A relay product that pulses the open input on a gate without working photocells or force limiting inherits responsibility for the consequence in the customer's eyes even if the motor was installed by someone else. A written precondition ("gate must have working photocells; we only open, never close; closing stays with the gate controller's own timer and safety inputs") reduces this.
- Power and internet outages: B1 keeps working without internet because the allowlist is in the camera; B2 keeps working only if the edge box holds the whitelist locally; any design where the open decision needs the cloud fails closed during an outage, which generates immediate support calls. A UPS for camera + edge box + gate controller is part of a credible kit.
- Support-load shape (judgement): A2/A3 create a steady stream of "it flags good product / it missed one" tickets that need engineering attention and retraining; B creates fewer tickets, clustered in the first weeks (night reads, a few problem plates) and after power or firmware events, but with higher urgency because a resident is stuck at a gate.
- Operator distrust in A is self-reinforcing: once false rejects annoy operators the system gets ignored or bypassed, so alert-only products need a visible, low false-alarm rate to survive past the pilot.

### Gaps
- No published field accuracy for ANPR in Indonesian conditions (rain, glare, motorcycles, modified or decorative plates, missing plates).
- No injury or liability data for automatic gates in Indonesia, and the EN 12453 text itself was not read (only a manufacturer's summary); whether any SNI standard applies to gate automation was not established.
- No practitioner source quantifying operator distrust or false-reject line stoppages; the statements above are qualitative vendor/blog material.
- No source on plate-spoofing incidents against ANPR gates.

---

## 7. Development effort (person-weeks) — what is commodity and what is genuinely hard

### Takeaway
No build log with explicit person-week counts was found, so the figures below are estimates built from what the cited components already do. On that basis the cheapest things to build are B1 (no computer vision work at all — an ISAPI integration plus a multi-tenant whitelist app) and A1 (no hardware — a checklist app calling a VLM); B2 and A2 are each roughly twice that; A3 is not a product but a per-customer project.

### Cited Findings
- On-board ANPR cameras already implement plate reading, brand/colour/type, a 100,000-entry allowlist, offline barrier control and relay output, with ISAPI/SDK interfaces — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Integrating by subscribing to camera recognition events, checking a server-side identifier database and commanding a relay is an existing commercial pattern — [BAS-IP docs](https://basip.atlassian.net/wiki/spaces/Integrations/pages/249856010/Integration+with+Hikvision)
- The ISAPI event path has rough edges (multipart XML + images, re-sent until acknowledged, firmware-specific behaviour) — [IPCamTalk](https://ipcamtalk.com/threads/get-passed-license-plate-numbers-using-isapi.79032/post-888496)
- Frigate ships a complete LPR pipeline (detector, OCR, known plates, fuzzy match, format regex, MQTT) under MIT — [Frigate LPR docs](https://docs.frigate.video/configuration/license_plate_recognition)
- fast-alpr/fast-plate-ocr provide an MIT detector + OCR with a fine-tuning path — [fast-plate-ocr repo](https://github.com/ankandrew/fast-plate-ocr)
- A hobbyist gate-control stack built from Blue Iris + CodeProject.AI + Home Assistant over MQTT exists and its author identifies night image tuning as the difficult part — [IPCamTalk](https://www.ipcamtalk.com/threads/gate-automation.74141)
- Published Indonesian plate pipelines reach 84–87% exact match — [Sistemasi](https://sistemasi.ftik.unisi.ac.id/index.php/stmsi/article/view/6697); [IIETA](https://iieta.org/node/19971)
- Fine-grained Indonesian make/model results exist only for 8–10 classes — [UGM](https://etd.repository.ugm.ac.id/penelitian/detail/229112); [KLIK](https://klik.ulm.ac.id/index.php/klik/article/view/625)
- One inspection station takes 8–16 weeks including 4 weeks of data collection/labelling and ~4 weeks of false-reject tuning (vendor) — [OxMaint guide](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- Apache-2.0 detectors and anomaly-detection libraries are actively maintained (RF-DETR, D-FINE, Anomalib all pushed in October 2026) — [RF-DETR](https://github.com/roboflow/rf-detr); [D-FINE](https://github.com/Peterande/D-FINE); [Anomalib](https://github.com/open-edge-platform/anomalib)
- Hosted VLM calls cost fractions of a cent per image, but benchmarks show weak defect/anomaly and counting reliability — [Claude pricing](https://claude.com/pricing); [arXiv 2410.09453](https://arxiv.org/abs/2410.09453); [arXiv 2510.04401](https://arxiv.org/abs/2510.04401v1)

### Inferences
**ESTIMATE — person-weeks for one experienced web/Android/server developer (basis: decomposition of remaining work after the commodity parts cited above; not from a build log):**

| Design | MVP (works at one friendly site) | Sellable v1 (multi-tenant, billing, monitoring/OTA, installer docs) | Genuinely hard part |
|---|---|---|---|
| B1 on-board ANPR + whitelist app | 3–5 | 8–12 | Camera/firmware quirks in event push and allowlist sync; supporting a second camera brand |
| B2 own ALPR on RTSP + edge box | 6–10 | 16–24 | Getting from ~85% to gate-grade on Indonesian plates at night with two plate generations; collecting data; device fleet management |
| B make/model add-on (own classifier) | +4–8 | +ongoing (retrain per model launch) | Dataset for Indonesian-market models; look-alike twins (e.g. Avanza/Xenia); upkeep |
| A1 phone audit + VLM | 3–5 | 8–12 | Proving accuracy per check type; prompt/reference management per customer; offline capture in factories |
| A2 fixed-scope alert-only (one check family) | 6–10 | 16–24 | A model that transfers across sites; lighting robustness; false-alarm rate low enough to keep operators' trust |
| A3 inline with reject/PLC | 8–16 weeks per station (vendor timeline), repeated per customer | not productisable by a solo developer without an integrator partner | Timing, PLC integration, line-stop liability, hygiene-rated hardware |

- Commodity now: object detection and anomaly detection training (A), plate detection + OCR (B), on-camera ANPR with relay (B), hosted VLM inference (both), relay hardware (B), edge compute (both).
- Still hard: (A) per-site data, lighting and acceptance — the problem is not the model but making it hold in production; (B2) night-time accuracy on Indonesian plates and fleet operations; (B) fine-grained make/model; (both) remote device management at 50 sites.
- B1's and A1's MVP estimates are close; the difference is in what "done" means. B1 has a crisp correctness test (the plate string matched or not, the gate opened or not) and a vendor-stated accuracy to lean on. A1's correctness is per-check and has to be demonstrated to each customer, with benchmark evidence pointing the wrong way for defect-type questions.

### Gaps
- No public build log or post-mortem giving person-weeks for an ANPR gate product or a factory QC product was retrieved (search budget exhausted before this lookup). All person-week numbers are estimates.
- No evidence on how much effort supporting a second camera vendor (Dahua, Uniview) adds for B1.

---

## 8. Running costs per customer per month, and warranty/RMA

### Takeaway
Cloud costs are negligible for both options at audit/gate volumes (single-digit USD per site per month); they only become material if A does inline inspection through a hosted API. The recurring cost that matters is people: remote monitoring, support and — for anything with hardware — replacement units and site visits, where B and A2/A3 carry an obligation that A1 does not.

### Cited Findings
- Claude Haiku 5.5 USD 0.10/0.50, Sonnet 5.5 USD 2/10, Opus 5.5 USD 4/20 per million input/output tokens; batch 50% off — [Claude pricing](https://claude.com/pricing)
- A 1000×1000 px image is 1,296 visual tokens — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Roboflow serverless: 8,000 nano-model images per credit; prepaid credits from USD 4, on-demand USD 6; Core plan USD 39/month — [Roboflow pricing](https://roboflow.com/pricing)
- Plate Recognizer: Stream USD 35/camera/month (USD 45 with make/model/colour); on-premise Snapshot SDK USD 50/month for 50,000 lookups — [Plate Recognizer pricing](https://platerecognizer.com/pricing/)
- Cloudflare R2: USD 0.015 per GB-month, free egress, free tier 10 GB-month plus 1 million Class A and 10 million Class B operations — [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/)
- Tailscale: Personal plan is free for up to 6 users but "only suitable for non-commercial use"; Standard USD 8/user/month, Premium USD 18; 50 tagged resources included on Personal with add-ons at USD 1/month each — [Tailscale pricing](https://tailscale.com/pricing)
- The on-board ANPR camera stores to a TF card up to 1 TB and to NAS, so evidence images need not go to the cloud — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Indonesian after-sales rules for electronics/telematics products: a Bahasa Indonesia user manual and warranty card are mandatory (Permendag 19/2009, later Permendag 38/2019 as amended by 78/2019, covering 75 product types), producers/importers must register them and provide after-sales service during and after the warranty period (sources 2019 or older — verify current status) — [Undip law journal](https://ejournal3.undip.ac.id/index.php/dlr/article/download/12254/11904); [Medcom](https://www.medcom.id/ekonomi/mikro/DkqVOdZK-kemendag-awasi-penerapan-kewajiban-imei)
- A mini PC brand comparison notes warranty length differs by brand (Beelink 3 years vs GMKtec 1 year, US market) — [SmartHomeCompared](https://smarthomecompared.com/mini-pcs/beelink-mini-s12-pro-n100-16gb-500gb-vs-gmktec-g10-16gb-512gb)

### Inferences
**ESTIMATE — recurring cost per customer site per month (arithmetic from the prices above at Rp 17,900/USD; volumes are assumptions stated in each row):**

| Item | A1 phone audit | A2 fixed camera | B1 on-board ANPR | B2 own ALPR |
|---|---|---|---|---|
| Inference | 5,200 photos: ≈ Rp 22k (Haiku 5.5) to ≈ Rp 870k (Opus 5.5) | Rp 0 on edge; or ≈ Rp 9–13 per image if hosted | Rp 0 (in camera) | Rp 0 on edge; optional VLM audit of 9,000 events ≈ Rp 38k (Haiku 5.5) |
| Image storage | 5,200 × ~0.5 MB = 2.6 GB/month; 12-month retention ≈ 31 GB ≈ USD 0.47 | similar order | in camera (TF card) or 300 events/day × ~0.2 MB ≈ 1.8 GB/month — inside R2 free tier | same as B1 |
| Remote access | none | VPN seat or self-hosted WireGuard | none needed if cloud-push only; else as A2 | VPN seat or self-hosted WireGuard |
| Paid SDK alternative | n/a | n/a | n/a | Plate Recognizer Stream ≈ Rp 626k–806k per camera |
| Hardware reserve | none | spare-unit pool | spare-unit pool; camera under vendor warranty | spare-unit pool (camera, box, relay) |

- A paid ALPR SDK at USD 35–45 per camera per month costs more each year (≈ Rp 7.5–9.7M) than the price difference between a generic camera and an on-board ANPR camera, so B1 hardware beats "B2 + paid SDK" within the first year.
- Tailscale's free plan cannot be used for a commercial fleet; budget either per-user seats (cheap — the developer is one or two users, devices are tagged) or self-host WireGuard. Either way the cost is small; the work is in provisioning and key rotation.
- **ESTIMATE, hardware reserve**: for B and A2 a solo vendor realistically needs spare units on the shelf (one spare per 10–20 deployed is a common-sense starting point, not a sourced ratio) and must budget for site visits to swap them; with a Rp 4–10M BOM this ties up Rp 10–25M of capital at 50 sites.
- Support hours cannot be sourced; the structural difference is that A1 support is remote-only, B and A2 include occasional travel, and A3 includes scheduled revalidation.

### Gaps
- No sourced data on support hours per site for either product type, on device failure rates in Indonesian heat/humidity/lightning conditions, or on typical RMA turnaround from Indonesian distributors.
- Current legal status and exact product scope of Permendag 38/2019 jo. 78/2019 (does a custom relay/edge box fall in the listed product types?) not verified.
- Balena/other OTA service pricing not researched.

---

## 9. Compliance and safety

### Takeaway
Selling software plus third-party, already-certified hardware keeps both options out of the heaviest compliance work. The moment the developer puts their own brand on a box with a radio (an ESP32 relay unit, for instance), Indonesian type approval applies to the end product, takes on the order of two months and needs a local legal entity as applicant. Personal-data rules now have teeth on paper: the implementing regulation (PP 33/2026) takes effect on 16 January 2027 with fines up to 2% of annual revenue, and it bites B (plates tied to residents, systematic monitoring) and the hygiene/PPE part of A (worker images) more than product-only QC images.

### Cited Findings
Radio/telecom certification
- A certificate of approval is required for telecommunication and IT equipment entering Indonesia; the process involves testing at an accredited lab, registering a local importer/applicant and issuing the approval to that entity; approvals are valid for three years — [TÜV SÜD](https://www.tuvsud.com/en-us/services/product-certification/indonesia-sdppi)
- A consultancy describes the process as taking eight to ten weeks, requiring a local representative and local on-site testing, with the applicant registered as an official company in Indonesia, and an SDPPI label showing certificate number and PLG-ID (article dated 13 Sep 2018 — stale, verify) — [Cetecom Advanced](https://cetecomadvanced.com/en/news/sdppi-certification-for-market-approval-in-indonesia/)
- Certification is granted at host/system level per type or model, and where a product uses a radio module, the module's test reports must be submitted too — [Teltonika wiki](https://wiki.teltonika-gps.com/view/FMB920_SDPPI_(POSTEL)_certificate); [IB-Lenhardt](https://ib-lenhardt.com/news/module-name-indication-on-certificate)
- Official tariff page for certificate issuance (as extracted by search, table truncated — verify): about Rp 12,000,000 for a new certificate in the domestic non-HKT category, with foreign-made categories in bands from Rp 30,000,000 to Rp 80,000,000; fee payable within 14 days of the payment notice; lab testing and EMC fees are separate — [SDPPI service portal](https://pelayanansdppi.postel.go.id/panduan-tutorial/download?id=80)
- Foreign test-lab recognition lapsed at the start of 2025 pending re-accreditation rules, and 6 GHz RLAN devices had to be tested at BBPPT until 15 Jan 2026 — [TÜV SÜD newsletter 2025](https://www.tuvsud.com/zh-tw/services/global-market-access/gma-newsletter-2025/tw-articles/01-wireless-indonesia); [Eleos Compliance](https://www.eleoscompliance.com/en/article/indonesia-komdigi-opens-6-ghz-wifi-bands)

Personal data
- PP 33/2026, the implementing regulation of UU PDP 27/2022, was signed 16 July 2026 and takes effect 16 January 2027 — [Katadata](https://katadata.co.id/finansial/makro/6a9979b7c5745/pp-pelindungan-data-pribadi-berlaku-januari-2027-ini-aturan-baru-data-anak)
- Per a legal summary of PP 33/2026: a legal basis is required before processing (consent, contract, legal obligation, vital interest, public interest, legitimate interest); an impact assessment is required for high-risk processing including large-scale processing, new technologies, systematic monitoring and automated decisions with significant effect; a data protection officer is required where regular, systematic, large-scale monitoring is a core activity; breach notification in writing within 3 × 24 hours to data subjects and the authority; administrative sanctions include suspension of processing, deletion of data and fines up to 2% of annual revenue; cross-border transfers need equivalent protection, binding safeguards or consent — [Veritask summary](https://veritask.ai/en/artikel/technical-regulation-on-personal-data-protection-and-the-obligations-of-controllers-and-processors-finally-issued-through-government-regulation-no-33-of-2026)
- The supervisory agency is not yet operating: the draft presidential regulation was submitted in May 2026, Komdigi supervises in the interim, and the agency is projected to be effective around 2028 — [Bisnis, 13 Sep 2026](https://teknologi.bisnis.com/read/20260913/84/2003698/pembentukan-badan-pdp-dipercepat-implementasi-uu-pdp-dinilai-belum-efektif)
- Claude's usage policy and docs: the model cannot be used to name people in images — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision); Gemini free-tier data may be used to improve Google products, paid tier not — [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)

Gate safety
- EN 12453 minimum protection levels by use case, including force limiter plus photocells for out-of-sight and automatic operation (manufacturer's summary) — [Avidsen manual](https://pim.avidsen.com/documentsproduits/en/510064-user-guide-v7.pdf)
- Dry-contact relays keep the add-on galvanically isolated from the gate controller's supply — [ESPHome device page](https://devices.esphome.io/devices/Shelly-1-Gen4/)

Food-factory equipment
- Indonesian food GMP is set by Permenperin 75/M-IND/PER/7/2010 (CPPOB), covering sanitation of buildings, personnel and machinery/equipment (2010 regulation — verify currency) — [Berita Negara PDF](https://peraturan.go.id/files/bn358-2010.pdf); [regulation record](https://pasal.id/peraturan/permen/permenperin-no-75-m-ind-per-7-2010-tahun-2010)
- Reference point for outdoor-rated cameras: the Hikvision ANPR unit is IP67/IK10, rated −30 to 70 °C — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)

### Inferences
- Compliance-light path for B: resell an already-approved branded camera and, if a relay is needed, a branded relay that already carries Indonesian approval (to be checked per product), and sell the software and service. Building and branding an ESP32 relay box triggers end-product type approval even if the ESP32 module is certified, plus the warranty-card/manual obligations.
- **ESTIMATE, own-brand radio box**: roughly 2–3 months and, on the truncated tariff extract, Rp 12M in certificate fees plus lab testing and EMC fees and consultant costs that could not be sourced. Treat "Rp 20–50M all-in per model" as an unverified order of magnitude to be replaced by a quote.
- PDP exposure: B stores plates linked to named residents and timestamps of their movements — personal data, systematic monitoring. A's hygiene/PPE checks (hairnet, handwashing) capture identifiable workers; fill-level/label checks capture product only. For both, the customer is normally the controller and the developer a processor, which still requires a processing agreement, retention limits, breach procedures and attention to cross-border transfer when images go to a foreign VLM API. Edge processing or on-camera storage avoids the transfer question.
- Food plants: A2/A3 hardware mounted over or near open product has to be cleanable and must not shed; a consumer IP camera in a plastic housing above a washdown line will be challenged by the customer's QA. A1 (handheld phone) and cameras placed outside the product zone avoid this. IP69K/stainless enclosures are a cost line that B does not have.
- Gate electrical safety: keep the add-on on the low-voltage control side (dry contact only), never on mains or motor circuits, and never drive "close".

### Gaps
- No official current fee schedule for lab testing (BBPPT) or a per-model total for Wi-Fi/BLE devices; no confirmation of current rules on foreign test reports.
- Whether specific Shelly/Sonoff/Tapo/EZVIZ models sold in Indonesia hold Indonesian type approval was not checked.
- The official text of PP 33/2026 was not read; article-level statements come from secondary legal summaries. No Indonesian guidance specific to CCTV, plates or worker images was found.
- BPOM/CPPOB clause text on equipment near product, and any IP69K or stainless requirement, was not retrieved; SNI or other Indonesian standards for gate automation were not identified.

---

## 10. Side-by-side comparison and verdict: which is cheaper/easier to build, and which is cheaper/easier to roll out to the 50th customer

### Takeaway
B, built as "on-board ANPR camera + cloud whitelist app" (B1), is the cheaper and easier of the two to build and to repeat at fifty sites when compared with any camera-on-the-line version of A, because the recognition problem is identical everywhere and already solved in a Rp ~9.9M device; the price of that ease is hardware capital, site visits and security/safety liability. The only version of A that is as cheap to build and cheaper to roll out is the hardware-free phone audit app (A1), which is a different product from inline QC and rests on VLM accuracy that current evidence does not yet support for defect-type checks.

### Cited Findings
- One camera provides plate reading for Indonesia, brand/colour/type, a 100,000-entry allowlist, offline barrier control and relay output; vendor-stated 98.5% recognition under recommended conditions — [Hikvision datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf); street price ≈ Rp 9.9M — [Tokopedia, Sep 2026](https://www.tokopedia.com/find/anpr-hikvision)
- One AI inspection station: 8–16 weeks, 500–2,000 labelled images per defect class, 2–4 weeks shadow mode, quarterly revalidation, USD 25K–120K all-in (vendor) — [OxMaint guide](https://oxmaint.com/industries/manufacturing-plant/ai-visual-inspection-implementation-guide-manufacturing)
- 77% of one inspection vendor's customer problems were deployment and setup; models transferred poorly to new product variants — [Enao Vision](https://enaovision.com/blog/ai-visual-inspection-fails-easy-fixes)
- Best VLM at 74.9% on industrial anomaly questions (2024 models), below ordinary humans; VLM counting unreliable beyond simple cases — [arXiv 2410.09453](https://arxiv.org/abs/2410.09453); [arXiv 2510.04401](https://arxiv.org/abs/2510.04401v1)
- Indonesian open/academic plate pipelines at 84–87% exact match; night tuning is the hard part for self-built ALPR — [Sistemasi](https://sistemasi.ftik.unisi.ac.id/index.php/stmsi/article/view/6697); [IPCamTalk](https://www.ipcamtalk.com/threads/gate-automation.74141)
- Ultralytics AGPL/Enterprise constraint applies to both options and is avoidable with Apache-2.0 models — [Ultralytics licence](https://www.ultralytics.com/license); [RF-DETR licence post](https://blog.roboflow.com/rf-detr-is-free-to-use-commercially/)
- PP 33/2026 effective 16 Jan 2027, fines up to 2% of revenue — [Katadata](https://katadata.co.id/finansial/makro/6a9979b7c5745/pp-pelindungan-data-pribadi-berlaku-januari-2027-ini-aturan-baru-data-anak); [Veritask](https://veritask.ai/en/artikel/technical-regulation-on-personal-data-protection-and-the-obligations-of-controllers-and-processors-finally-issued-through-government-regulation-no-33-of-2026)

### Inferences
**Side-by-side (all effort and cost cells are ESTIMATES derived in sections 4–8; sources for the inputs are cited there):**

| Dimension | A — factory QC vision | B — ALPR + make/model gate |
|---|---|---|
| Upfront R&D effort | A1: 3–5 pw MVP, 8–12 pw v1. A2: 6–10 pw MVP, 16–24 pw v1 per check family. A3: 8–16 weeks per station, per customer | B1: 3–5 pw MVP, 8–12 pw v1. B2: 6–10 pw MVP, 16–24 pw v1. Own make/model classifier: +4–8 pw and continuing upkeep |
| Hardware BOM per site — low | Rp 0 (A1) | Rp 3.5–5.2M (B2: IP cam + Orange Pi 5 + relay; existing gate) |
| Hardware BOM per site — typical | Rp 4.0–8.2M (A2: IP cam + mini PC or Pi 5 with AI HAT), lighting extra | Rp 9.9–13.7M (B1: on-board ANPR camera, optional gateway; existing gate) |
| Hardware BOM per site — high | Rp 15.6–19.6M before lens/light/enclosure (A3 parts); vendor all-in Rp 0.45–2.15 billion | Rp 19–52M (B3: ANPR camera + new barrier or branded sliding motor + photocell) |
| Per-site install + customisation | A1: 2–6 h remote. A2: 2–4 days + 2–4 weeks shadow. A3: 8–16 weeks | B1: 4–8 h on site + 1–2 h remote. B2: 1–3 days incl. night tuning |
| What changes per customer | Products, defects, SKUs, lighting, line layout, acceptance criteria — data and model change | Mounting geometry and the plate list — data and model do not change |
| Recurring cost per site/month | A1: ≈ Rp 22k–870k VLM depending on model tier. A2: near zero cloud; retraining labour | Near zero cloud for B1; B2 optional VLM audit ≈ Rp 38k; paid SDK alternative ≈ Rp 626k–806k per camera |
| Main technical risk | Accuracy does not hold outside the pilot (lighting, new SKUs); VLM reliability for defect/counting checks | B1: dependence on one camera vendor's firmware/API and its real accuracy on Indonesian plates. B2: night accuracy; make/model coverage |
| Support burden | A1 low and remote. A2/A3 steady stream of false-alarm/missed-defect tickets needing retraining; revalidation visits | Lower volume, front-loaded, but urgent (someone is stuck at a gate); hardware swaps and travel |
| Liability exposure | Mostly commercial (missed defect, false reject) if alert-only; rises sharply with physical reject/line stop; worker-image privacy for hygiene checks | Security (unauthorised open on a copied or misread plate), physical safety around a moving gate, resident movement data under PDP |
| Compliance | Food-zone hardware hygiene (A2/A3); PDP for worker images | Type approval if own-brand radio box; PDP for plates; gate safety preconditions |

**Which is cheaper/easier to build**
- Tie on raw effort between B1 and A1 (both ≈ 3–5 person-weeks to MVP by estimate), with B1 the lower-risk build: no ML to own, a pass/fail correctness criterion, and vendor-stated accuracy to start from. A1's build is as small but its accuracy has to be proven check by check.
- If the developer insists on owning the vision model, B2 and A2 are similar in effort (≈ 6–10 person-weeks MVP), but B2 trains one national model once while A2 trains per check family and tunes per site.
- Fine-grained make/model is the one part of B that is not cheap; treating make/model as enrolment data verified by the camera's brand/colour output removes it from the critical path.

**Which is cheaper/easier to roll out to the 50th customer**
- Against camera-based QC (A2, A3): B wins clearly. Fifty B1 sites are fifty near-identical installs of about a day each; fifty A2 sites are fifty small engineering engagements; fifty A3 sites are beyond a 1–3 person team.
- Against the phone audit app (A1): A1 wins on rollout mechanics — no hardware, no travel, no stock, no warranty — at ≈ 2–6 remote hours per customer. Its constraint is evidence, not logistics: it is periodic audit rather than continuous QC, and published benchmarks do not yet show VLMs meeting industrial accuracy for defect and exact-count questions.
- Capital: 50 B1 sites mean ≈ Rp 500M of cameras passing through the business (customer-paid or financed) plus a spares pool; 50 A1 sites mean none.

**Reasoning in one line each**
- B's task is standardised nationally (one plate format, two colour generations), so effort does not scale with customer variety; A's task is defined by each customer's product.
- B's hard part can be bought as a device; A's hard part (making inspection hold in production) cannot.
- B concentrates risk in liability and hardware logistics; A concentrates risk in accuracy and per-site labour.

### Gaps
- The verdict rests on vendor-stated ANPR accuracy for Indonesia that was not independently verified, and on effort estimates with no build-log evidence; a one-camera field test over several nights with real resident plates would test the first, and a time-boxed spike would test the second.
- Whether customers accept alert-only A2 or audit-style A1 as "QC", and what they will pay, is outside this note (market researchers).
- Unpriced items (lighting, enclosures, UPS, reject/PLC hardware, certification lab fees) would raise A2/A3 and own-brand-hardware B totals; they do not change the ordering.
