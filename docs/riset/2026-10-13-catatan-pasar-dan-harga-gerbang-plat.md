# ALPR/ANPR + vehicle make/model recognition + automatic gate: market, competitors and pricing (Indonesia focus, as of 13 October 2026)

Reading notes for the report writer:

- Research date: 13 October 2026. Every price carries the date of the page or the date it was observed. Anything dated before 2024 is flagged STALE.
- Evidence grades used below: **[opened]** = I opened the page and read the figure; **[snippet]** = the figure came from a search-result summary of that URL and the page itself was not opened (Tokopedia pages timed out, two vendor pages returned 404, one news page returned 403). Treat [snippet] figures as indicative until re-checked.
- Exchange rate used for USD: JISDOR Rp17,917 per USD on 6 October 2026, rounded to Rp17,900 — [Journalarta, 6 Oct 2026](https://journalarta.com/news/2026/10/06/rupiah-hari-ini-6-oktober-2026/). GBP, AUD and MYR conversions use my own unsourced working assumptions (about Rp24,000/GBP, Rp11,600/AUD, Rp4,000/MYR) and are marked "assumed rate".

---

## Key question 1 — Competitors in four groups, with concrete prices

### Takeaway
In Indonesia a camera that already reads plates on-board, holds a 100,000-entry allowlist and closes a relay to open a barrier costs about Rp8–17.5 million street price (Hikvision DS-TCG405/406, generic and Cardteck units), and Dahua's access ANPR line explicitly lists Indonesia in its baseline plate algorithm and adds brand-logo, colour and vehicle-type recognition at no extra licence. That leaves a software-only product very little room at the lane itself; the gaps I could find are (a) running on cheap ordinary cameras, (b) the resident/visitor management layer, and (c) motorcycles and non-standard plates, none of which the commodity cameras or local parking integrators document well.

### Cited Findings

#### Group 1 — Cameras with built-in ANPR and gate relay

Indonesian street prices (IDR):

- Hikvision DS-TCG406-E "4 MP Access ANPR Camera": Rp16,189,381 at a Nale online store; page shows no update date, observed October 2026 **[snippet]** — [toko.nale.co.id](https://toko.nale.co.id/?p=82380)
- Hikvision DS-TCG406-E on Tokopedia: listings from about Rp9,934,392 up to Rp16,558,000 (12V/PoE variant); DS-TCG405 about Rp17,500,000; a higher-end Hikvision ANPR unit about Rp21,799,000. Page title reads "Harga Terbaru September 2026" **[snippet — page timed out when opened]** — [Tokopedia find: anpr-hikvision](https://www.tokopedia.com/find/anpr-hikvision)
- BigGo price aggregator, page titled "Harga kamera anpr Terbaru Okt 2026" **[opened]**: "Kamera ANPR Hikvision DS-TCG405-E/H" Rp9,000,000 (Shopee, seller Sfu St0re, Jakarta Timur); unbranded "kamera ANPR (Automatic Number Plate Recognition)" Rp8,094,690 (Shopee, JAYA CIPTA DIGITAL); "CARDTECK F8300 LPR ANPR Outdoor CCTV Camera" Rp12,375,000 (Shopee, AUTOGATE STORE) — [BigGo](https://biggo.id/s/kamera%20anpr)
- Traffic-enforcement class (not gate class): Hikvision 9 MP ANPR unit for intersection violations / E-TLE listed at Rp99,000,000 by Tokosekuriti, Jakarta Utara **[snippet]** — [Tokopedia / Tokosekuriti](https://www.tokopedia.com/tokosekuriti/anpr-camera)
- Dahua-based ANPR/LPR camera with whitelist-to-barrier control listed at Rp28.5 million by MSM Parking **[snippet — page returned 404 when opened, so unverified]** — [msmparking.com](https://msmparking.com/shop/sistem-parkir-manless/kamera-anpr-lpr-dahua/)
- Dahua's Indonesian distributor site lists the Access ANPR models ITC237-PU1B-IR, ITC237-PU1B-L and ITC237-PW1B-IRZ with no prices shown ("not published") **[snippet]** — [cctvdahua.co.id](https://www.cctvdahua.co.id/product-category/mobile-traffic/entrance-exit-control-products/access-anpr-cameras/)
- Tiandy TC-C34LQ 4 MP LPR camera is offered by MSM Parking with "hubungi admin" instead of a price ("not published") **[snippet]** — [msmparking.com](https://msmparking.com/harga-camera-lpr-anpr-tc-c34lq-4mp-motorized-2-8-12mm-pro-series/)
- For scale: an ordinary (non-ANPR) Hikvision camera in Indonesia runs from about Rp350,000 (analog) to about Rp2,500,000 (advanced IP), excluding DVR/NVR, per a 2026 reseller blog **[snippet]** — [hikvision-indonesia.com](https://hikvision-indonesia.com/estimasi-harga-kamera-cctv-hikvision-dan-standar-tahun-2026/)

What the commodity cameras already include:

- Hikvision DS-TCG406-E: relay output "to control vehicle barrier gate", Wiegand to an access controller, motorised 2.8–12 mm or 8–32 mm lens, loop / radar / video triggering; vehicle type, colour and brand recognition; up to 100,000 allowlist and blocklist entries; "offline control of barrier gate under allowlist mode"; effective recognition distance about 10 m (2.8–12 mm) or 20 m (8–32 mm). One hosted datasheet notes the allowlist/blocklist only takes effect when a TF (microSD) card is present **[snippet of datasheets dated 2026]** — [Hikvision DS-TCG406-E datasheet, Aug 2026](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf); [Hikvision product page](https://www.hikvision.com/en/products/parking-management/vehicle-access-control-management/anpr-cameras/ds-tcg406-e-es-/); [Dicomp-hosted datasheet](https://dicomp.com.br/downloads/materiais_apoio/datasheet/33357-1.pdf)
- Dahua ITC413-PW4D series **[opened]**: 4 MP; "120+ countries license plate recognition with high accuracy ≥ 98% (EU) & 96% (others)"; **Indonesia is listed among the 19 countries in the baseline algorithm** (alongside Singapore, Thailand, Viet Nam, the Philippines, Japan); logo recognition for 147 brands, 12 colours, 10 vehicle types; allowlist and blocklist of 110,000 entries each; two relay outputs "can connect to devices such as barriers"; two RS-485, one Wiegand; 433/868 MHz remote controller with about 15 m range. The page does **not** mention vehicle model (only brand/colour/type) and its vehicle-type list does **not** include motorcycles — [Dahua ITC413-PW4D](https://www.dahuasecurity.com/products/intelligent-traffic/smart-parking-products/entrance-and-exit/access-anpr-cameras/itc413-pw4d-series)
- Hikvision's deep-learning ANPR line (iDS-2CD7A26G0/P-IZHSY) supports separate blocklist and allowlist triggers, IP67/IK10 **[snippet]** — [use-IP UK listing](https://www.use-ip.co.uk/bestsellers/bestseller-cameras/hikvision-ids-2cd7a26g0-p-izhsy.html)
- Hikvision marketing claim: ≥98% recognition accuracy, plates of "over 120 countries and regions" **[snippet]** — [Hikvision ANPR technology page](https://www.hikvision.com/en/core-technologies/see-smarter-technology/anpr-automatic-number-plate-recognition/)
- Dahua Indonesia's ANPR page states 95–98% read accuracy for alphanumeric plates in about 100 ms, and requires the plate to be 70–250 pixels wide with a plate angle under 5° for best results **[snippet]** — [Dahua Indonesia ANPR](https://www.dahuasecurity.com/id/products/keyTechnologies/352)

Indonesian plate support — evidence and conflicts:

- Dahua: Indonesia explicitly listed (see above) — [Dahua ITC413-PW4D](https://www.dahuasecurity.com/products/intelligent-traffic/smart-parking-products/entrance-and-exit/access-anpr-cameras/itc413-pw4d-series)
- Hikvision: a search summary reported that Hikvision's ISAPI country/region code table for the plate algorithm includes Indonesia (code 87 in the table, 88 in the description text, i.e. internally inconsistent); when I opened the same URL the country list was not visible, so this is **unconfirmed** — [Hikvision TPP ISAPI wiki](https://tpp.hikvision.com/wiki/isapi/anpr/GUID-75F741E6-C2DD-45CF-A51C-BE9F05650E92.html)
- Region-specific firmware matters: an ipcamtalk user reported an Australian-region Hikvision build misreading New Zealand plates until Hikvision supplied a separate NZ build ("Be careful to get the correct region") **[snippet; forum post, date not captured, likely pre-2024 → STALE]** — [ipcamtalk](https://ipcamtalk.com/threads/cameras-with-built-in-anpr-or-lpr-function.18028/post-171468)
- A 2020 Hikvision PTZ ANPR installation guide says the overseas firmware "only supports Vehicle Detection, does not support Mixed-traffic Detection" **[snippet; 2020 → STALE]** — [Hikvision PTZ ANPR guide 2020](https://www.hikvision.com/content/dam/hikvision/uk/support/download/how-to/ptz/Installation-and-Configuration-Guidance-for-PTZ-ANPR-Camera-202007.pdf)
- Background on the plate formats: Indonesia began switching private vehicles to white plates with black characters from mid-2022 under Peraturan Kepolisian No. 7/2021, phased in with the five-yearly STNK renewal; Korlantas said cameras misread the old black plates (5 read as S, 1 read as I) and that black plates remained acceptable during the transition **[snippet; 2021–2022 articles → STALE for current status]** — [detikOto](https://oto.detik.com/berita/d-5682525/ini-alasan-pelat-nomor-diganti-warna-putih-tulisan-hitam); [Antara: 5-year target](https://gorontalo.antaranews.com/berita/198169/korlantas-target-5-tahun-semua-kendaraan-gunakan-pelat-putih)
- I found **no** published complaint, review or field test of Hikvision/Dahua/Uniview ANPR on Indonesian plates (white or black, motorcycle, two-line); Indonesian-language pages are reseller marketing repeating the >98% "optimal conditions" claim — [hikvision-indonesia.com](https://hikvision-indonesia.com/hikvision-plate-recognition-solusi-anpr-ai-akurasi-tinggi/)

Global reference prices for the same class:

- Alibaba supplier listings: Dahua ITC413-type access cameras USD 180–260 (≈ Rp3.2–4.7 million); ITC237-PW6M-IRLZF1050 USD 200–300 (≈ Rp3.6–5.4 million), ex-China, before freight, duty, warranty **[snippet]** — [Alibaba](https://www.alibaba.com/supplier/access-anpr-camera.html)
- Dahua publishes no worldwide retail price for the ITC413 family **[snippet]** — [trafficenforcementcamera.com guide](https://www.trafficenforcementcamera.com/blog/dahua-anpr-camera-guide)
- Hikvision DS-2CD7A26G0/P-IZHSWG in Australia: AUD 1,344.61 incl. GST (≈ Rp15.6 million, assumed rate) **[snippet]** — [POSMarket AU](https://www.posmarket.com.au/productpage.asp?id=14285)
- Viewtron LPR-IP4 (on-camera recognition, built-in dry-contact relay, HTTP POST webhook, no NVR needed): USD 699.99 sale / USD 899.99 list (≈ Rp12.5–16.1 million) **[snippet]** — [CCTV Camera Pros](https://www.cctvcamerapros.com/License-Plate-Recognition-Systems-s/1518.htm); [vendor forum](https://videos.cctvcamerapros.com/?p=43114)
- Amcrest IP4M-1072EW-AI 4 MP LPR bullet: USD 769.99 at Walmart (≈ Rp13.8 million) **[snippet]** — [Walmart](https://www.walmart.com/c/kp/lpr-camera)
- UK: basic standalone ANPR camera £600–1,200 hardware only (≈ Rp14–29 million, assumed rate); dedicated commercial ANPR camera £3,000–5,000 per unit; article updated 9 June 2026 **[opened]** — [Nortech ANPR cost guide](https://blog.nortechcontrol.com/anpr-system-cost/)
- Cheapest capable non-LPR camera hobbyists use with separate software: EmpireTech (Dahua OEM) IPC-B52IR-Z12E at about USD 259 (≈ Rp4.6 million) **[snippet; forum]** — [ipcamtalk](https://ipcamtalk.com/threads/best-cheap-hikvsion-lpr-camera.76981/latest)

#### Group 2 — ALPR software / API / SDK

- Plate Recognizer **[opened, prices as displayed 13 Oct 2026]** — [platerecognizer.com/pricing](https://platerecognizer.com/pricing/):
  - Snapshot (per-lookup; same price cloud or on-premise SDK): free 2,500 lookups/month (evaluation only, not for production); USD 50/month for 50,000 (≈ Rp895,000); USD 150/month for 250,000 (≈ Rp2.69 million); USD 250/month for 500,000 (≈ Rp4.48 million).
  - Make, model, colour and orientation: **+50% on the subscription fee**.
  - Stream (video, unlimited lookups): USD 35 per camera per month (≈ Rp627,000); Stream + MMC USD 45 per camera per month (≈ Rp806,000).
  - ParkPow dashboard USD 20 per camera per month (≈ Rp358,000). **Gate Opener / Gate Controller USD 10 per gate per month** (≈ Rp179,000), pre-integrated with Stream and ParkPow.
  - Perpetual licence: custom price on request; annual maintenance 20% of the perpetual price. Annual billing = 2 months free. Professional services USD 500 per session (≈ Rp8.95 million).
  - "Trained in over 90 countries"; Indonesia is not named on the pricing page.
- Rekor Scout (ex-OpenALPR): Basic USD 10 per camera per month (≈ Rp179,000), Pro USD 65 per camera per month (≈ Rp1.16 million), Enterprise by sales contract, 14-day trial; official docs page is undated **[snippet]** — [Rekor docs](https://docs.rekor.ai/scout/getting-started/subscriptions-and-licensing). Forum history shows the entry tier rising from USD 5 to USD 8 to USD 10 — [ipcamtalk](https://www.ipcamtalk.com/goto/post?id=745718)
- Sighthound ALPR+: quote-only today ("contact us for a custom quote"); an older launch release gave "starts at just $29 per camera per month" (≈ Rp519,000) **[snippet; release about three years old → treat as STALE]** — [Sighthound FAQ](https://www.sighthound.com/faqs); [Sighthound launch release](https://www.sighthound.com/news/sighthound-launches-automatic-license-plate-recognition-products)
- Milestone XProtect LPR: three licences needed — base LPR licence, a per-camera LPR licence, and a country-module licence per country/region (five included in the base); prices "not published" **[snippet]** — [Milestone](https://www.milestonesys.com/articles/license-plate-recognition-xprotect-briefcam-arcules/)
- UK benchmark for server-side LPR: licence £500–1,200 per year (≈ Rp12–29 million, assumed rate); cloud management platform £30–80 per month (≈ Rp0.7–1.9 million); "on-camera software (dedicated ANPR): included in camera price" **[opened]** — [Nortech](https://blog.nortechcontrol.com/anpr-system-cost/)
- Free / open source: Frigate NVR has built-in licence plate recognition that writes the characters to `recognized_license_plate` or a known name as `sub_label`; it is disabled by default and "does not run on stationary vehicles" **[snippet of docs mirror]** — [Frigate LPR docs (mirror)](https://git.laurivan.com/Mirrors/blakeblackshear.frigate/src/commit/a6c8bcd87849d5b5779daa2fa3a77fcd9bcde0a1/docs/docs/configuration/license_plate_recognition.md)
- Free DIY chains that already open gates: `frigate_plate_recognizer` (Frigate + Plate Recognizer or CodeProject.AI) — [GitHub](https://github.com/ljmerza/frigate_plate_recognizer); a Home Assistant blueprint that sends a camera snapshot to a general-purpose LLM vision API and toggles the gate switch for known plates — [Home Assistant community](https://community.home-assistant.io/t/license-plate-recognition-using-gemini-3-5-flash-api-gate-opener-notifications-with-lights/1011751); Dahua camera + Blue Iris + CodeProject.AI + Home Assistant — [ipcamtalk gate automation](https://www.ipcamtalk.com/threads/gate-automation.74141)
- Indonesian vendor Nodeflux: VisionAIre LPR ships as a Docker stream analytic and an on-premise GPU "frontal" variant gated by access/deployment keys; says the model was adapted to Indonesian plate variety; price "not published" **[snippet]** — [Nodeflux docs](https://docs.nodeflux.io/stream/analytics/license-plate-recognition). Jakarta ran it across "nearly 8,000 cameras" after a four-month proof of concept for vehicle-tax recovery **[snippet; NVIDIA blog, date not captured, likely pre-2024 → STALE]** — [NVIDIA blog](https://blogs.nvidia.com/?p=44453)
- Indonesian integrator SistemParkir.com gives its ALPR software away: "kami berikan gratis untuk semua software sistem parkir kami", no monthly fee ("tidak memiliki biaya iuran bulanan"), runs without internet, and "bekerja tanpa memerlukan IP camera mahal puluhan juta rupiah"; uses a top camera for motorcycle plates and a bottom camera for car plates **[opened]** — [sistemparkir.com](https://sistemparkir.com/proyek/detail/sistem-parkir-manless-tempat-rekreasi-tirta-mas-waterpark)

#### Group 3 — Indonesian parking / access-control vendors

Package prices found (all vendor "starting from" figures; final price is quoted per project):

- SistemParkir.com (Medan + Jakarta) **[opened; page undated, observed Oct 2026]**: Basic 1 in / 1 out **Rp89,900,000**; Standard 2 in / 2 out **Rp179,800,000**; includes barrier gate, pos parkir, computer and software, IP camera, training, QRIS payment; ALPR software included free; no recurring software fee; "price may be lower or higher depending on field conditions" — [sistemparkir.com](https://sistemparkir.com/proyek/detail/sistem-parkir-manless-tempat-rekreasi-tirta-mas-waterpark)
- MSM Parking (Bandung) price page, August 2026 **[opened]**: Paket Manless Starter from Rp75,000,000 (hardware only: barrier, ticket dispenser, controller, loop detector, push button, interface; software and installation excluded); remote barrier MX series unit only from Rp6 million; Heavy Duty M Gate from Rp11.7 million; Semi Manless System (software + semi-automatic system) from Rp65 million; Full Cashless System from Rp100 million; **ANPR/LPR camera listed only as an expansion option with no price** — [palangparkirbandung.com](https://www.palangparkirbandung.com/2026/08/paket-harga-hardware-sistem-parkir.html)
- MSM "Ultra Guard" page, updated 24 July 2026 **[opened]**: barrier unit from Rp28 million; **complete 2 In 2 Out package Rp108 million including barrier, ANPR, manless and software**; rental from Rp3.7 million per month per unit; installation and commissioning listed as a separate cost; one year free maintenance; software "lifetime guarantee" — [palangparkir.msmparking.com](https://palangparkir.msmparking.com/palang-parkir-merk-ultra-guard-solusi-canggih-untuk-sistem-parkir-otomatis-modern-di-indonesia/)
- MSM ANPR article, 5 June 2026 **[opened]**: barrier from Rp28 million per unit, rental Rp3.7 million per month; 1 In 1 Out and 2 In 2 Out ANPR packages "available" with no price; claims recognition at night and in rain, no accuracy figure — [msmparkinggroup.com](https://msmparkinggroup.com/sistem-parkir-berbasis-anpr-masa-depan-parkir-tanpa-tiket-yang-lebih-cepat-dan-transparan/)
- A search summary attributed "Premium ≈ Rp99.9 million including ANPR" and "Ultimate ≈ Rp135 million" (2025 promo) to msm-cv.com; **I could not find those figures when I opened the pages**, so treat as unverified — [msm-cv.com](https://www.msm-cv.com/)
- RFID barrier package for housing clusters "mulai dari Rp 18 jutaan": barrier gate, integrated RFID with access cards, loop detector, warranty; aimed at cluster managers and RT/RW; published 29 June 2026 **[opened]** — [rentalatparkir.com](https://rentalatparkir.com/pressrelease/investasi-cerdas-cluster-perumahan-sistem-palang-parkir-rfid-mulai-rp-18-jutaan-bebas-ribet/)
- MSM "paket portal parkir perumahan dengan sistem kartu RFID online" Rp45–55 million depending on card count and features **[snippet — page returned 404, unverified]** — [msmparkinggroup.com](https://msmparkinggroup.com/shop/barrier-gate/palang-parkir/paket-portal-parkir-perumahan-dengan-system-kartu-rfid-online/)
- Marketplace barrier kits (undated listings, observed Oct 2026) **[snippet]**: barrier MX 50 + vehicle loop detector + remote, 3/4/6 m arm, Rp8,412,500 — [Tokopedia / Putra Safety Mandiri](https://www.tokopedia.com/putrasafetymandiri2/paket-manual-barrier-gate-mx-50-mesin-buka-tutup-palang-otomatis); barrier E10 AC + 4 m arm + 2 remotes + VLD + 2 RFID readers + 200 cards Rp7,538,000 (out of stock) — [Tokopedia / Solusi Parking](https://www.tokopedia.com/solusi-parking/paket-barrier-gate-1-mesin-e10-ac-dan-2-rfid)

Vendors offering plate-based access with no published price ("not published"):

- BSS Parking: "VLOWX LPR" for housing, offices, hospitals; ANPR for one-gate systems with "akurasi tinggi hingga 98%", usable as the main system or as backup to RFID, positioned at premium residential; article dated 9 December 2025 **[opened]** — [bssparking.com](https://www.bssparking.com/news/item/5972-teknologi-anpr-untuk-one-gate-system-solusi-akses-yang-cepat-akurat-tanpa-kartu)
- PT Mabruka Inovasi Indonesia: "Barrier Gate ANPR Jabodetabek", 19 Aug 2026; targets offices, apartments and housing, malls, hospitals, hotels, industrial estates and warehouses; no price, no camera brand, no accuracy figure **[opened]** — [mabruka.id](https://www.mabruka.id/barrier-gate-anpr-jabodetabek-sistem-akses-kendaraan-berbasis-pengenalan-nomor-polisi/)
- Sinergi Akses: LPR inside a "Manless System"; reference at Mall Matahari Singosaren Solo; lists housing/apartments where "gates open upon recognizing a registered plate" **[opened]** — [sinergiakses.com](https://sinergiakses.com/index.php/sistem-parkir/sistem-parkir-lpr)
- Titantek (Medan / Jabodetabek): barrier with tap card, long-range RFID (sticker tags, UHF reader 5–10 m, gooseneck mount), remote, LPR, ticket dispenser; 1-year warranty; installation covers concrete foundation, loop sensor, cabling; extra transport and accommodation cost outside Medan/Jabodetabek **[opened]** — [titantek.id](https://titantek.id/palang-parkir/); [titantek.id/harga](https://titantek.id/harga/)
- PT Zona Teknologi Indonesia "ZCluster": one-gate package combining IXHA barrier with ZSoft application, resident database, guest logging, photo capture at card tap, and automatic blocking of cards when dues are unpaid **[snippet; Kontan, date not captured]** — [Kontan](https://industri.kontan.co.id/news/zona-teknologi-indonesia-rilis-produk-barrier-gates-canggih)
- Parkee: LPR where "the plate is the digital ticket", retrofits existing parking infrastructure, headline target "Medium-to-Large Enterprises"; no accuracy figure, no price, no site count **[opened]** — [parkee.app](https://parkee.app/en/license-plate-recognition-lpr)
- Sky Parking lists LPR with ticketless entry and automatic gate opening among its technology — [skyparking.co.id](https://www.skyparking.co.id/about); Secure Parking (operating since 1992, self-described largest operator) lists CCTV/LPR in its Epsilon system — [secureparking.co.id](https://secureparking.co.id/en/products-services/) **[both snippet]**
- Soul Parking uses QR check-in and e-wallet payment for stacked motorcycle storage, not LPR **[snippet]** — [soulparking.co.id](https://soulparking.co.id/)
- Toll context: Roatex's multi-lane free-flow (MLFF) toll system was still not operating commercially in mid-2026, more than four years after the contract, with trial location and schedule unset — [Bisnis.com, 21 Jun 2026](https://ekonomi.bisnis.com/read/20260621/45/1982181/proyek-tol-nirsentuh-mlff-tak-kunjung-realisasi-investor-buka-suara); the December 2023 limited trial at Ngurah Rai failed with barriers dropping on cars — [Indonesia Business Post](https://indonesiabusinesspost.com/4972/corporate-affairs/mlff-project-implementation-delayed-due-to-unresolved-business-model) **[both snippet]**

Gate motors in Indonesia (the thing a home product would have to trigger):

- Sliding-gate machines on Tokopedia about Rp1.5–5.44 million (machine only, up to 2,000 kg); an extra remote Rp215,000; page title April 2026 **[snippet]** — [Tokopedia find: mesin-pagar-otomatis](https://www.tokopedia.com/find/mesin-pagar-otomatis)
- Griya Tekno distributor: swing-gate motor Rp7,875,000; sliding motor for up to 3,000 kg Rp8,837,500 **[snippet]** — [griyatekno.com](https://www.griyatekno.com/automatic-gate-c-72_100/)
- Installer Maxima: flat-machine automatic sliding gate Rp7,850,000–9,000,000, excluding sensors and indicator lamp; article about 440 days old at time of search (mid-2025) **[snippet]** — [Maxima Usaha Mandiri](https://www.maximausahamandiri.co.id/pintu-otomatis/harga-automatic-sliding-gate/)
- Jaya Technology: installed automatic gate "mulai dari Rp 8,5 jutaan hingga Rp 50 juta" depending on machine capacity, material, area and add-ons **[snippet]** — [jayatechnolog.com](https://jayatechnolog.com/pagar-otomatis-sliding/)

#### Group 4 — Consumer smart-gate products and substitutes

Plate-recognition gate opening abroad:

- UK installer guide: ANPR as a driveway-gate add-on "£1,000–£2,500+ ... a premium feature for larger homes" (≈ Rp24–60 million, assumed rate) **[snippet; 2026]** — [Home security guide (UK)](https://home-security-guide.readthedocs.io/en/latest/access-control/01-driveway-gate-installation-guide-uk/)
- London driveway installer: residential ANPR from about £1,500 fully installed (≈ Rp36 million, assumed rate) **[snippet]** — [Driveway Gates London](https://www.drivewaygateslondon.co.uk/services/access-control/anpr-systems/)
- UK gate retailer ANPR kit (2 MP camera + NVR + 1 TB disk + junction box) £1,066.34–£1,089.43 (≈ Rp25.6–26.1 million, assumed rate); a Hikvision single-lane kit on the same site is "trade only" **[snippet]** — [The Electric Gate Shop](https://www.theelectricgateshop.co.uk/ANPR-Number-Plate-Recognition-System)
- UK commercial single-lane ANPR + barrier installed "from around £7,000"; £7,000–12,000 typical; multi-lane £15,000–30,000 **[opened; updated 9 June 2026]** — [Nortech](https://blog.nortechcontrol.com/anpr-system-cost/)
- A hobbyist wanting an LPR camera to open a driveway gate: "everything I've seen from trusted brands so far is 600€ or more" **[snippet; forum]** — [ipcamtalk](https://ipcamtalk.com/threads/aliexpress-lpr-camera.77367/latest)
- Hobby reference design: an offline licence-plate gate opener shared as an open project — [Elecrow community project](https://www.elecrow.com/sharepj/gate-offline-license-plate-recognition-gate-opener-975.html)

Smart-relay openers (no plate recognition; phone/app/geofence):

- Chamberlain myQ USD 29.98 (≈ Rp537,000; Alexa needs a USD 1/month add-on); Meross Wi-Fi opener USD 31.53 list, USD 26.80 on sale in March 2026 (≈ Rp480,000–564,000), no subscription; Meross HomeKit USD 49.99; ismartgate PRO USD 141.90 (≈ Rp2.54 million) **[snippet; March 2026]** — [Smart Home Unlocked comparison](https://smarthomeunlocked.com/articles/smart-garage-door-opener-review); [Slickdeals](https://slickdeals.net/f/19280601-26-80-meross-smart-wifi-garage-door-opener-remote-w-app-control-alexa-google-at-amazon)
- Remootio: price not found ("not published" in the sources reached).

Cheap substitutes in Indonesia:

- Long-range UHF RFID readers on Tokopedia (page titles Sept–Oct 2026) **[snippet]**: 5–8 m, TCP/IP + RS232 + Wiegand, about Rp1,650,000; max 5 m, Wiegand 26, about Rp1,395,000; up to 15 m about Rp2,700,000–2,900,000; Cardteck CT-I802 integrated reader Rp4,380,000 — [Tokopedia find: long-range-rfid](https://www.tokopedia.com/find/long-range-rfid); [Tokopedia / Multi Akses](https://www.tokopedia.com/multi-akses/long-range-uhf-rfid-reader-uhf-reader-wiegand-26-max-5m)
- UHF windshield tag (Alien H3, ISO18000-6C, anti-duplication label) Rp4,500 each; generic UHF sticker tags Rp1,500–3,000 **[snippet]** — [Tokopedia find: uhf-rfid](https://www.tokopedia.com/find/uhf-rfid)
- UHF readers read stickers at up to 12 m (TimeTec UHF2-10F), connect to a boom gate over Wiegand or RS-485, and can use anti-tear stickers that cannot be moved to another vehicle **[snippet]** — [TimeTec UHF](https://timeteccloud.com/parking/uhf)
- Extra RF remote for a gate motor: Rp215,000 **[snippet]** — [Tokopedia find: mesin-pagar-otomatis](https://www.tokopedia.com/find/mesin-pagar-otomatis)
- I found no Indonesian consumer product that opens a home gate by plate recognition; what surfaced were commercial/cluster systems and a 2022 student prototype (Arduino + OCR + servo) **[snippet; 2022 → STALE]** — [JATI ITN journal, 2022](https://ejournal.itn.ac.id/jati/article/download/5403/3549)

### Inferences
- **Commodity hardware already contains the core feature.** For roughly Rp8–17.5 million a buyer gets on-camera plate reading, a 100,000+ allowlist, a relay to the barrier and offline operation, plus brand/colour/type tagging. A software-only product cannot charge for "read plate → open relay" where the buyer is already purchasing an ANPR camera; it can only charge for what sits around it.
- **The price gap a software product could capture is the difference between an ANPR camera and an ordinary one**, i.e. roughly Rp6–15 million per lane once (Rp8–17.5 million versus Rp0.35–2.5 million). At Plate Recognizer's list price, Stream + Gate Opener is USD 45 per month ≈ Rp806,000, about Rp9.7 million a year — roughly the purchase price of a Hikvision ANPR camera every year. That sets a hard ceiling on what a per-gate subscription can charge in Indonesia.
- **Vehicle make/model is a weaker differentiator than it looks.** Plate Recognizer charges +50% (or +USD 10/camera) for make/model/colour; Dahua and Hikvision include brand/colour/type free. True *model* recognition (Avanza versus Xenia) is the only piece not bundled in the commodity cameras I checked.
- **Plate recognition is the expensive way to open a gate.** For a 300-vehicle cluster, one UHF reader (≈ Rp1.65 million) plus 300 windshield tags (≈ Rp1.35 million at Rp4,500) is about Rp3 million per lane versus Rp9–16 million for one ANPR camera; a home owner's alternative is a Rp215,000 remote. What ANPR buys is: no tag to issue/replace, a searchable photo log, visitor handling, and blocking by plate.
- **Local integrators compete on bundles and give software away** (SistemParkir: free ALPR, no monthly fee; MSM: "lifetime" software). A solo developer selling software alone into this channel is selling against "free".
- Local package prices imply the installed price of an ANPR lane in Indonesia is roughly Rp45–90 million per in/out pair including barriers and software (SistemParkir Rp89.9 million per 1-in/1-out; MSM Rp108 million per 2-in/2-out, installation extra) — one to two orders of magnitude above a home budget.

### Gaps
- Tokopedia, Shopee, Blibli, Bukalapak and Indotrading listing pages could not be opened directly (timeouts), so marketplace prices rest on search summaries plus one aggregator page. Re-check before quoting.
- No Indonesian street price found for Hikvision iDS-2CD7A26G0/P-IZHS, Dahua ITC413/ITC237/ITC431, Uniview, TP-Link VIGI, Ezviz, Tiandy, Milesight, Axis or Hanwha LPR models ("not published"). Nearest proxies: Hikvision DS-TCG405/406 at Rp9–17.5 million; Alibaba ITC413-type at USD 180–260.
- Whether TP-Link VIGI and Ezviz sell an LPR camera at all was not established.
- No published prices found for Vaxtor, Carrida, SimpleLPR, DTK LPR, Anyline, Genetec AutoVu, Eocortex, Camlytics, Nx Witness LPR plug-ins; Milestone and Sighthound are quote-only.
- No published prices for Nodeflux, Parkee, Sky Parking, Secure Parking, Centrepark, ISS Parking, MKP, Bigvision or Qlue LPR offerings; Centrepark, ISS, MKP, Bigvision and Qlue were not verified as LPR vendors at all.
- No field evidence (complaints, reviews, benchmarks) on how Hikvision/Dahua cameras handle Indonesian motorcycle plates, two-line plates or old black plates. Hikvision's Indonesia support is unconfirmed (conflicting reads of the same page).
- Prices of Nice/BFT/Came/FAAC/Beninca motors and any LPR add-ons from those brands in Indonesia were not found; e-money/e-toll reader prices for housing gates were not found; Remootio price not found.

---

## Key question 2 — Customisation and installation burden per site

### Takeaway
Every Indonesian vendor I found sells plate-based access as a surveyed, per-project installation with "starting from" prices and separately charged installation, which is the opposite of "develop once, sell to many". The recognition software can be standardised, but camera geometry, lighting, the barrier/motor interface, the network and the fallback procedure are decided site by site.

### Cited Findings
- Geometry constraints from the manufacturer: plate must be 70–250 pixels wide and the plate angle under 5° for best results **[snippet]** — [Dahua Indonesia ANPR](https://www.dahuasecurity.com/id/products/keyTechnologies/352)
- Recognition distance is lens-dependent: about 10 m with a 2.8–12 mm lens, 20 m with 8–32 mm **[snippet]** — [Hikvision DS-TCG406-E datasheet](https://assets.hikvision.com/prd/normal/all/doc/m000078840/DS-TCG406-E_Datasheet_20260811.pdf)
- Dahua's accuracy claim is conditional: capture ≥99% and recognition ≥96% only "under recommended installation and lighting" **[opened]** — [Dahua ITC413-PW4D](https://www.dahuasecurity.com/products/intelligent-traffic/smart-parking-products/entrance-and-exit/access-anpr-cameras/itc413-pw4d-series)
- An Indonesian integrator's pre-sale survey covers lane width, turning radius, guard-post position, power source, cable routes, network, foundation, existing sensors, lighting and queue patterns; implementation needs foundation work, conduit, power and data cabling, panels and mounting; decisions depend on stable network and compatible controller/database/software, and a manual procedure is required for network failure **[opened; Aug 2026]** — [mabruka.id](https://www.mabruka.id/barrier-gate-anpr-jabodetabek-sistem-akses-kendaraan-berbasis-pengenalan-nomor-polisi/)
- Installation scope stated by another integrator: concrete foundation, mounting, embedding the loop sensor, cabling; extra transport and technician accommodation outside the home region **[opened]** — [titantek.id](https://titantek.id/palang-parkir/); [titantek.id/harga](https://titantek.id/harga/)
- Vendors state the price depends on gate count, barrier type, transaction method, camera and installation, and is finalised per project **[opened; Aug 2026]** — [palangparkirbandung.com](https://www.palangparkirbandung.com/2026/08/paket-harga-hardware-sistem-parkir.html)
- Loop detectors are standard so the arm does not drop on a vehicle **[opened; Jun 2026]** — [rentalatparkir.com](https://rentalatparkir.com/pressrelease/investasi-cerdas-cluster-perumahan-sistem-palang-parkir-rfid-mulai-rp-18-jutaan-bebas-ribet/)
- Motorcycles need separate treatment: one Indonesian integrator mounts a top camera for motorcycle plates and a bottom camera for car plates **[opened]** — [sistemparkir.com](https://sistemparkir.com/proyek/detail/sistem-parkir-manless-tempat-rekreasi-tirta-mas-waterpark); motorcycle plates are small in pixels and often bent, making detection harder **[snippet; blog]** — [Medium: ANPR mendeteksi lokasi plat nomor](https://cyb3rh3b.medium.com/anpr-mendeteksi-lokasi-plat-nomor-8f22f08edadd)
- Dirty, damaged or glare-affected plates and poor mounting angle/height reduce accuracy **[snippet; reseller blogs]** — [distributor-cctv.com, Feb 2025](https://www.distributor-cctv.com/blog/2025/02/08/cctv-bisa-baca-plat-nomor-begini-cara-kerjanya/); [harianesia.com](https://harianesia.com/apakah-cctv-bisa-baca-plat-kendaraan-begini-caranya/)
- Non-standard plates are a national-scale problem: Korlantas recorded 16,812 ETLE-captured violations of vehicles without plates or with fake plates in January–July 2026, and 77.24% of ETLE-recorded violations were by motorcyclists **[snippet]** — [Kumparan](https://kumparan.com/kumparannews/polri-catat-16-812-pelanggaran-pelat-nomor-palsu-kini-andalkan-face-recognition-27vRbIIbXv2); removed, partly covered, modified or sticker/paint-disguised plates and non-standard fonts hamper ETLE reading — [Kompas TV](https://www.kompas.tv/info-publik/673085/operasi-patuh-2026-mulai-8-juni-pelat-nomor-dimodifikasi-hingga-ditutup-jadi-target-etle); [detikOto](https://oto.detik.com/berita/d-8523172/modif-pelat-nomor-buat-hindari-etle-bisa-kena-sanksi-ini/amp)
- When the plate cannot be read, the police fall back to face recognition tied to Dukcapil, and are developing plates with a chip and QR code **[snippet]** — [detikOto](https://oto.detik.com/berita/d-8515543/3-kondisi-etle-pengenal-wajah-pengendara-bakal-berfungsi); [Antara](https://ambon.antaranews.com/berita/149730/korlantas-polri-kembangkan-pelat-nomor-kendaraan-gunakan-cip-dan-qr)
- Practitioner workaround for misreads: store common misread variants of each plate on the allowlist **[snippet; forum]** — [Home Assistant community](https://community.home-assistant.io/t/letting-my-house-cleaner-in/565475)
- Gate-motor integration is brand-specific enough that camera makers publish per-brand wiring guides (Amcrest LPR camera to LiftMaster) **[snippet]** — [Amcrest support](https://support.amcrest.com/hc/en-us/articles/18368347889293-How-To-Setup-an-Amcrest-License-Plate-Reader-Camera-with-Lift-Master-IP4M-1062EW-AI)
- Dedicated cameras keep working if the network drops because recognition runs on the camera; "standard camera with LPR software" is quoted at 85–95% versus 95–99%+ for dedicated ANPR **[opened; vendor guide]** — [Nortech](https://blog.nortechcontrol.com/anpr-system-cost/)

What installers charge:

- CCTV installation in Jakarta: Rp100,000–380,000 per point for 1–5 points including cable, bracket, connectors and testing; Rp50,000–450,000 per point above 10 points; camera-only mounting Rp20,000–180,000; DVR/NVR setup Rp90,000–400,000 per unit **[snippet; several pages one to four years old → partly STALE]** — [Master CCTV](https://mastercctv.co.id/harga-jasa-instalasi-cctv/); [Sentra CCTV](https://pasangcctvjakarta.co.id/); [Rabit: Rp250,000 per point](https://rabit.co.id/blog/berapa-harga-pasang-cctv-4-titik/)
- Nale service catalogue: NVR installation 4–12 channel Rp277,500, 16–32 channel Rp388,500; preventive maintenance of IP CCTV Rp25,000 per unit per month excluding parts, Rp50,000 with parts **[snippet]** — [toko.nale.co.id](https://toko.nale.co.id/?p=69281)
- UK reference: installation labour £1,000–2,000 for a single lane, £2,000–3,500 dual lane; network cabling £200–500 per lane; access controller £300–800 **[opened]** — [Nortech](https://blog.nortechcontrol.com/anpr-system-cost/)

### Inferences
- The standardisable part is a box: camera (or camera + mini-PC), a dry-contact relay, a fixed mounting recipe (height, distance, angle, lens) and a web/app allowlist. The non-standardisable part is everything the Indonesian vendors charge "per project" for: foundation, loop, conduit, the barrier/motor's own control board, lighting, queue geometry and the manual fallback.
- A dry contact is the universal interface across gate-motor brands (remote-button input), so a kit can be "one relay, any motor" in principle; in practice each site still needs someone to find the right terminals and add a safety loop/photocell. This is my inference from the wiring guides and package contents, not a tested claim.
- Indonesia-specific failure modes (motorcycle volume, modified/covered plates, mixed black and white plates, glare, rain, night) fall exactly where commodity cameras are least documented. That is both the technical opportunity and the main support-cost risk for a solo developer.
- Local CCTV labour is cheap (Rp100,000–450,000 per point), so the installation cost that matters is not labour but the site visit, survey and after-sales call-outs — the part that does not scale for one person.

### Gaps
- No published Indonesian tariff for installing a barrier gate or wiring an ANPR camera to a gate motor; vendors quote only after survey.
- No data on call-out frequency or support load per installed ANPR gate in Indonesia.
- No source on behaviour during power cuts (UPS sizing, fail-open versus fail-closed) for Indonesian residential gates.
- Whether a single mounting recipe works for both cars and motorcycles at one lane was not established; the only evidence is one vendor using two cameras.

---

## Key question 3 — Security, reliability and published accuracy (Indonesian plates and make/model)

### Takeaway
A plate alone is a weak credential: it is printed on the outside of the vehicle, and Indonesia already has a visible fake/modified-plate problem. Published Indonesian academic results for end-to-end plate reading sit around 70–87% exact match (far below vendor claims of 96–98%), while make/model recognition reaches about 98% only on a small, closed set of ten models.

### Cited Findings

Spoofing and mitigation:

- Installer-forum discussion of whether a cloned plate opens a Hikvision ANPR gate; the suggested fix is dual verification — plate must match the camera's allowlist **and** a Bluetooth card in the vehicle must be read before the gate opens **[snippet; forum, older thread → STALE]** — [ipcamtalk](https://ipcamtalk.com/threads/hikvision-anpr-camera.32739/)
- UK policing commentary describes the number plate as "a single and readily assailable point of failure" **[snippet]** — [West Midlands PCC](https://www.westmidlands-pcc.gov.uk/?p=81620)
- UK MPs warned that about one in 15 vehicles carries an illegal plate, and a parliamentary group reported criminals can readily obtain false plates or copies of legitimately displayed ones **[snippet]** — [Fleet News](https://www.fleetnews.co.uk/news/mps-warn-one-in-15-vehicles-have-illegal-number-plates); [Regtransfers summary of the APPG report](https://www.regtransfers.co.uk/content/appgts-number-plate-report)
- Vendor mitigation by vehicle fingerprint: capture size/shape, make and model, colour, stickers or dents and treat a plate-versus-vehicle mismatch as a potential clone **[snippet; vendor claim]** — [TitanHz](https://www.titanhz.com/blog/how-ai-anpr-detects-prevents-license-plate-cloning.aspx)
- Vendor mitigation by multi-spectrum check (colour image versus infrared image) aimed at tampered/"ghost" plates **[snippet; vendor claim]** — [MAV GhostPlate](https://www.anprcameras.com/technology/ghostplate/)
- Indonesian vendor positioning: ANPR as the main system *or* as backup to RFID, combining both to close security gaps in housing **[opened; Dec 2025]** — [BSS Parking](https://www.bssparking.com/news/item/5972-teknologi-anpr-untuk-one-gate-system-solusi-akses-yang-cepat-akurat-tanpa-kartu)
- UHF stickers can be anti-tear so they cannot be moved to another vehicle **[snippet]** — [TimeTec UHF](https://timeteccloud.com/parking/uhf)
- Indonesian context: 16,812 no-plate/fake-plate violations caught by ETLE in January–July 2026 **[snippet]** — [Kumparan](https://kumparan.com/kumparannews/polri-catat-16-812-pelanggaran-pelat-nomor-palsu-kini-andalkan-face-recognition-27vRbIIbXv2); fake-plate users described as still rampant **[snippet]** — [Otomotifnet / GridOto](https://otomotifnet.gridoto.com/read/233941375/kayak-nggak-takut-sama-kamera-etle-pengguna-pelat-palsu-masih-merajalela)

Accuracy — vendor claims:

- Dahua: ≥98% (EU) and ≥96% (other regions, which includes Indonesia) under recommended installation and lighting **[opened]** — [Dahua ITC413-PW4D](https://www.dahuasecurity.com/products/intelligent-traffic/smart-parking-products/entrance-and-exit/access-anpr-cameras/itc413-pw4d-series)
- Hikvision: ≥98% **[snippet]** — [Hikvision](https://www.hikvision.com/en/core-technologies/see-smarter-technology/anpr-automatic-number-plate-recognition/); older Hikvision LPR datasheet: capture up to 99%, recognition up to 95% **[snippet; 2020 datasheet → STALE]** — [Hikvision US legacy datasheet](https://us-legacy.hikvision.com/sites/default/files/data_sheet/lpr_ds-2cd4a26fwd-izhs8p_022420na.pdf)
- BSS Parking (Indonesia): "hingga 98%" **[opened]** — [BSS Parking](https://www.bssparking.com/news/item/5972-teknologi-anpr-untuk-one-gate-system-solusi-akses-yang-cepat-akurat-tanpa-kartu)
- Plate Recognizer says India accuracy "hovered around 70%" before country-specific retuning and exceeds 95% after — evidence that a generic engine underperforms on an untuned country **[snippet; vendor claim]** — [Plate Recognizer](https://platerecognizer.com/better-than-openalpr/)
- A UK parliamentary-report summary cites plate-reading accuracy of "only 97%" at national scale **[snippet]** — [Regtransfers](https://www.regtransfers.co.uk/content/appgts-number-plate-report)

Accuracy — Indonesian academic results:

- YOLOv11 detection + TrOCR recognition: **87.07% exact-match accuracy**, at 2.84 FPS on an NVIDIA L4 GPU (Sistemasi, 2026) **[snippet]** — [Sistemasi journal](https://sistemasi.ftik.unisi.ac.id/index.php/stmsi/article/download/6697/1353)
- YOLOv8 detection with three readers: EasyOCR 70% and Tesseract 68% on static images; on 100 video frames a TensorFlow CNN classifier got 75 correct versus 61 (EasyOCR) and 58 (Tesseract) **[snippet]** — [Horizon repository](https://repository.horizon.ac.id/items/show/10536)
- Gaussian YOLOv7 with a new Indonesian ALPR dataset: detection recall 83.8%, false positives down 50.13% versus YOLOv7; adding a spatial transformer for rectification *reduced* character-recognition accuracy (JIKI, 2025) **[snippet]** — [JIKI, Universitas Indonesia](https://jiki.cs.ui.ac.id/index.php/jiki/article/view/1320)
- YOLOv8 tuned with Optuna on toll-road camera images: character error rate 0.0344 **[snippet]** — [Undip thesis abstract](https://eprints2.undip.ac.id/39508/4/7.%20ABSTRACT.pdf)
- Telkom University LPR parking-gate prototype: about 95% accuracy **[snippet]** — [Telkom University open library](https://openlibrary.telkomuniversity.ac.id/pustaka/files/214991/abstraksi/pengenalan-pelat-nomor-untuk-gerbang-berbayar-otomatis-dalam-bentuk-buku-karya-ilmiah.pdf)
- YOLOv11 detection study with 4,000 plate images and 3,000 character images **[snippet]** — [Polibatam JAIC](https://jurnal.polibatam.ac.id/index.php/JAIC/article/view/11484)
- A review of ALPR "with Indonesian case study" notes developing countries remain far from sophisticated deployment **[snippet]** — [Scientific Journal of Informatics, UNNES](https://journal.unnes.ac.id/nju/index.php/sji/article/view/15804)

Vehicle make/model on Indonesian cars:

- UGM multi-task CNN (VGG-16 MT) on the InaV-Dash dashboard-camera dataset — 10 models from 4 manufacturers, chosen because Indonesian models such as Avanza and Xenia look alike: **98.73% manufacturer, 97.69% model** **[snippet]** — [UGM ETD](https://etd.repository.ugm.ac.id/penelitian/detail/229112)
- YOLOv4 on Yogyakarta CCTV footage, 7,034 images, 8 classes including Toyota Avanza: 82% **[snippet]** — [KLIK, ULM](https://klik.ulm.ac.id/index.php/klik/article/download/625/pdf_1)
- Survey caveat: results are not comparable unless tested on the same dataset **[snippet; 2020 → STALE]** — [arXiv 2006.16400](https://arxiv.org/pdf/2006.16400)

### Inferences
- At 87% exact match, roughly one legitimate arrival in eight would fail to open the gate on first read; at 96% it is one in 25. For a household making about four entries a day that is the difference between a failure every two days and one a week. Either way a fallback (remote, tag, phone) must exist, which weakens the "no more remote" selling point. (Arithmetic on the cited accuracy figures; real per-vehicle rates differ because the same plate is read on several frames.)
- Make/model matching as an anti-spoof layer is credible only for a small enrolled set of resident vehicles; the 98% figure is for ten classes from dashboard cameras, not a gate camera at night, and Avanza/Xenia-type twins are the stated hard case.
- The stronger security story for a paid product is two-factor (plate + UHF tag or phone) and an audit trail, not plate + model. That, however, re-imports the tag cost the buyer was trying to avoid.
- False accepts from near-miss plates rise if misread variants are added to the allowlist (the practitioner workaround), a direct trade-off between convenience and security.

### Gaps
- No public penetration test or vendor report showing a printed plate or photo opening (or failing to open) a specific ANPR gate; evidence is forum discussion and vendor marketing.
- No liveness/anti-photo feature was documented for Hikvision or Dahua access ANPR cameras in the pages I reached.
- No independent accuracy benchmark for commercial cameras on Indonesian plates, and no accuracy figures specific to motorcycle plates, two-line plates or the white versus black formats.
- No published make/model accuracy for Brio, Xpander or other specific models beyond the ten-model UGM set (the model list itself was not retrieved).

---

## Key question 4 — Demand and market size in Indonesia

### Takeaway
The vehicle base is very large and motorcycle-dominated (BPS: 172.9 million vehicles in 2025, most of them motorcycles), and housing clusters and apartments already pay for guards and one-gate systems through monthly IPL dues — but I found no count of gated clusters and no evidence at all that Indonesian homeowners pay for plate recognition. Demonstrated demand sits with estate managers and commercial parking, served by integrators.

### Cited Findings
- BPS: 172.9 million motor vehicles in Indonesia in 2025, up from 166.5 million the year before (motorcycles, passenger cars, goods vehicles, buses) **[snippet]** — [detikOto](https://oto.detik.com/berita/d-8534826/jangan-kaget-segini-jumlah-kendaraan-di-ri-paling-banyak-bukan-di-jakarta)
- Growth 2020–2024: all vehicles 5.16% per year; passenger cars 6.66% per year; motorcycles 4.93% per year **[snippet]** — [GoodStats](https://goodstats.id/article/jumlah-kendaraan-di-jawa-barat-tembus-28-juta-terbanyak-pada-2025-oaOky)
- An undated BPS-based composition figure: 148.21 million vehicles, of which about 125.27 million motorcycles and 17.18 million passenger cars **[snippet; year unclear → possibly STALE]** — [GoodStats data](https://data.goodstats.id/statistic/komposisi-teratas-kendaraan-bermotor-di-indonesia-5nnVJ)
- West Java 2025: 28.09 million vehicles, 24.26 million motorcycles and 2.98 million passenger cars **[snippet]** — [GoodStats](https://goodstats.id/article/jumlah-kendaraan-di-jawa-barat-tembus-28-juta-terbanyak-pada-2025-oaOky)
- Kota Bogor, 16 September 2026 (Korlantas ERI): 763,840 vehicles of which 627,260 motorcycles **[snippet]** — [Databoks](https://databoks.katadata.co.id/datapublish/2026/09/17/jumlah-kendaraan-bermotor-di-kota-bogor-16-september-2026)
- Apartments, DKI Jakarta, Q1 2026 (Colliers): about 206,000 units absorbed and about 29,000 unsold, 27,000 of them ready to occupy; only about 2,000 more units expected in Q2–Q4 2026 and about 3,100 new units over 2026–2029 **[snippet]** — [Bisnis.com, 8 Apr 2026](https://ekonomi.bisnis.com/read/20260408/47/1965046/pengembang-gigit-jari-29000-unit-apartemen-di-jakarta-belum-laku)
- Developers: REI had 4,165 developer members per 2018 data **[snippet; 2018 → STALE]** — [UMN thesis citing REI](https://kc.umn.ac.id/10347/3/BAB_III.pdf); REI has 38 regional boards **[snippet; May 2025]** — [detikProperti](https://www.detik.com/properti/berita/d-7915735/pengembang-se-indonesia-kumpul-di-kaltim-mau-lirik-ikn); REI expects subsidised-mortgage (FLPP) realisation of at most 300,000 units in 2026 against a 350,000 target **[snippet]** — [Investor Trust](https://investortrust.id/business/117717/rei-target-350000-kpr-subsidi-2026-tak-bisa-dicapai-mentok-300000)
- Smart home: an industry body projects 15.2 million Indonesian households using smart-home technology in 2026; a We Are Social series gives 9.58 million (2024) and 11 million (2025) **[snippet; projection, not measurement]** — [Babel Insight](https://www.babelinsight.id/prediksi-adopsi-rumah-pintar-indonesia-2026); Statista: revenue about EUR 585.7 million in 2025, household penetration 16.2% in 2025 projected to 23.2% by 2028, CAGR 10.74% **[snippet]** — [Statista](https://es.statista.com/outlook/dmo/smart-home/indonesia)
- Guard cost: Jakarta provincial minimum wage 2026 is Rp5,729,876 per month (up about 6.17%) **[snippet]** — [DataOn](https://dataon.com/id-id/blog/ump-jakarta-terbaru-2026/); outsourcing management fee typically 8–15% of take-home pay **[snippet]** — [Bin-Care](https://www.bin-care.com/outsourcing-security-untuk-perusahaan-jakarta/); North Jakarta packages from Rp5 million per month for one guard and Rp15 million per month for four **[snippet]** — [Bin Group](https://bin-group.co.id/daftar-harga-jasa-security-terbaru-di-jakarta-utara/); another provider quotes Rp3.5–6 million per guard per month including uniform and insurance **[snippet]** — [Amerta Bertiga Sejahtera](https://amertabertigasejahtera.com/Artikel/outsourcing-security); satpam salaries 2026 about Rp3.1–6.75 million **[snippet]** — [Kantorku](https://kantorku.id/blog/gaji-satpam/); a career site puts housing-estate guards at Rp1.7–3.5 million **[snippet; undated → possibly STALE]** — [KitaLulus](https://www.kitalulus.com/seputar-kerja/gaji-satpam)
- Cluster dues (IPL): about Rp100,000–1,000,000 per house per month depending on segment; "upper-middle" clusters with CCTV, one-gate system, clubhouse and pool Rp500,000–750,000 **[snippet]** — [Panduan Properti](https://panduanproperti.id/panduan-beli-properti/ipl-cluster-perumahan/); worked example Rp20,000/m² × 30 m² = Rp600,000 per month; IPL covers "jasa satpam, pos keamanan, dan CCTV" **[opened; edited 18 Jun 2026]** — [Cermati](https://www.cermati.com/artikel/ipl-rumah-cluster)
- What a cluster already pays for access hardware: RFID barrier package from about Rp18 million **[opened; Jun 2026]** — [rentalatparkir.com](https://rentalatparkir.com/pressrelease/investasi-cerdas-cluster-perumahan-sistem-palang-parkir-rfid-mulai-rp-18-jutaan-bebas-ribet/)
- What RT/RW administrators pay for software: RTPINTAR dues-management app Rp120,000 per month for up to 100 units and Rp300,000 per month for up to 600 units **[snippet]** — [rtpintar.com/harga](https://rtpintar.com/harga/)
- Segment signal from vendors: ANPR one-gate is pitched as "especially suited to premium residential developments" **[opened]** — [BSS Parking](https://www.bssparking.com/news/item/5972-teknologi-anpr-untuk-one-gate-system-solusi-akses-yang-cepat-akurat-tanpa-kartu); Parkee's LPR targets "Medium-to-Large Enterprises" **[opened]** — [parkee.app](https://parkee.app/en/license-plate-recognition-lpr)
- Homeowner segment: gate motors sell from about Rp1.5 million with a Rp215,000 remote, and no plate-recognition home product surfaced **[snippet]** — [Tokopedia find: mesin-pagar-otomatis](https://www.tokopedia.com/find/mesin-pagar-otomatis)

### Inferences
- Motorcycles are the majority of any Indonesian gate's traffic (roughly 80–85% of the fleet by the cited figures). A product that reads only car plates addresses a minority of entries in housing, kost, schools and factories; commodity cameras do not document motorcycle support. This is the single largest product-fit question.
- Budget arithmetic for a mid-size cluster: 200 houses × Rp500,000 IPL = Rp100 million per month; four guards cost roughly Rp15–25 million per month. An ANPR gate at Rp50–110 million installed equals two to seven months of guard cost — affordable for a managed cluster as capex, but it does **not** remove the guards (visitors, couriers, ojek online and motorcycles still need handling), so it is sold as convenience and logging, not as labour saving. (My calculation from cited ranges.)
- Willingness to pay for software alone in the RT/RW segment looks very low: RTPINTAR's Rp120,000 per month for 100 units is Rp1,200 per house per month.
- Homeowner willingness to pay is undemonstrated. The substitute costs Rp215,000; in the UK, where labour is expensive and ANPR is a "premium feature for larger homes", the add-on costs £1,000–2,500+. There is no sign of an Indonesian mass consumer market yet.

### Gaps
- No count of gated housing clusters/perumahan in Indonesia or Jabodetabek, and no current REI membership or project count.
- No national car versus motorcycle split for 2025 from BPS directly; the split quoted is from an undated secondary page.
- No survey or sales data on willingness to pay for plate-based access by homeowners, RT/RW, estate managers or parking operators in Indonesia.
- No data on how many clusters already run RFID/UHF one-gate systems (the installed base an ANPR upgrade would target).
- Apartment stock for Greater Jakarta and other cities not found; Jakarta figure is absorbed units, not total stock.
- No count of factories, warehouses, schools or kost with vehicle gates.

---

## Key question 5 — Business models and margins observed

### Takeaway
In Indonesia the observed model is one-off project sale (hardware + free "lifetime" software + separately charged installation), with rental as the only recurring variant; pure per-gate SaaS exists only abroad at USD 10–65 per camera per month. I found no published margin data for Indonesian integrators; the best unit economics for a solo developer on the evidence are in software sold *through* existing integrators or as a management layer for clusters, not in consumer kits.

### Cited Findings
- One-off, no recurring fee: SistemParkir sells Rp89.9 million (1 in/1 out) and Rp179.8 million (2 in/2 out) packages with free ALPR software and no monthly dues **[opened]** — [sistemparkir.com](https://sistemparkir.com/proyek/detail/sistem-parkir-manless-tempat-rekreasi-tirta-mas-waterpark)
- One-off with "lifetime" software and one year free maintenance: MSM Ultra Guard 2 In 2 Out at Rp108 million **[opened; Jul 2026]** — [palangparkir.msmparking.com](https://palangparkir.msmparking.com/palang-parkir-merk-ultra-guard-solusi-canggih-untuk-sistem-parkir-otomatis-modern-di-indonesia/)
- Rental: MSM barrier from Rp3.7 million per month per unit **[opened]** — [msmparkinggroup.com](https://msmparkinggroup.com/sistem-parkir-berbasis-anpr-masa-depan-parkir-tanpa-tiket-yang-lebih-cepat-dan-transparan/); TimeTec (Malaysia) markets residential LPR + QR payment as "a rental-based solution with no initial investment cost", pitched on the community earning visitor-parking revenue (example RM10 per overnight vehicle) **[snippet]** — [TimeTec brochure](https://www.timeteccloud.com/download/brochure/Bro_LPR_RVP.pdf)
- Per-household SaaS in the region: i-Neighbour "as low as RM2 per month, per household" (≈ Rp8,000, assumed rate) **[snippet; 2017 → STALE]** — [i-Neighbour newsletter, Dec 2017](https://www.i-neighbour.com/newsletter/Dec2017/fn-06.php)
- Per-camera SaaS abroad: Plate Recognizer USD 35–45 per camera per month plus USD 10 per gate **[opened]** — [platerecognizer.com/pricing](https://platerecognizer.com/pricing/); Rekor Scout USD 10 / USD 65 per camera per month **[snippet]** — [Rekor docs](https://docs.rekor.ai/scout/getting-started/subscriptions-and-licensing)
- Perpetual licence + 20% annual maintenance as the offline alternative **[opened]** — [platerecognizer.com/pricing](https://platerecognizer.com/pricing/)
- Maintenance contracts: Indonesia Rp25,000–50,000 per IP camera per month **[snippet]** — [toko.nale.co.id](https://toko.nale.co.id/?p=69281); UK £500–1,500 per year per site, cloud/updates/maintenance together £1,000–3,000 per year; "some dedicated camera systems have no recurring software costs" **[opened]** — [Nortech](https://blog.nortechcontrol.com/anpr-system-cost/)
- Integrator margins (US trade data, not Indonesia): gross margin on recurring business rose from 31.4% (2022) to 38.5%; nearly 40% of integrator revenue was recurring **[snippet; 2023 survey → STALE]** — [Security Sales & Integration](https://www.securitysales.com/news/recurring-revenue-deep-dive-2023/152812/); hardware gross margins are "permanently squeezed by the rise of on-line price competition" **[snippet; older → STALE]** — [IPVM](https://ipvm.com/reports/should-security-integrators-focus-on-recurring-revenues)
- Labour-outsourcing margin benchmark in the same buyer's budget: guard-service management fee 8–15% **[snippet]** — [Bin-Care](https://www.bin-care.com/outsourcing-security-untuk-perusahaan-jakarta/)
- Third-party cost split: visitor-management software from USD 199 per month, LPR camera hardware USD 800–3,500+ per lane **[snippet; non-Indonesian product]** — [Capterra: VisitForm](https://www.capterra.com/p/205201/VisitForm/reviews/)

### Inferences
- **Hardware-kit margin for a solo vendor is thin and exposed.** The kit's bill of materials is public on marketplaces (camera Rp8–17.5 million, barrier Rp6–28 million, UHF Rp1.4–2.9 million), so buyers can price-check, and the camera maker's firmware already does the job.
- **Indonesian parking integrators give software away to win the hardware and installation margin.** The implied software value inside a Rp90–110 million lane package is small; one MSM page even advertises "software & controller terintegrasi hanya 5 jutaan" (seen as a link title only, content not opened) — [palangparkirbandung.com](https://www.palangparkirbandung.com/2026/08/paket-harga-hardware-sistem-parkir.html)
- **Sub-segments ranked by unit economics for a solo developer (my judgement from the evidence):**
  1. *Software/SDK or white-label engine sold to existing integrators and camera installers* — they own survey, install and support; the developer sells a licence per lane. Ceiling is roughly the Rp6–15 million per-lane saving from using ordinary cameras, shared with the integrator.
  2. *Cluster/apartment management layer* (resident and visitor allowlist, guard app, log, dues-linked blocking as ZCluster does) that works with whatever reader the site has (ANPR camera, UHF, card). Recurring revenue is possible but local price points are low (Rp120,000–300,000 per site per month for dues apps).
  3. *Commercial parking* has the largest tickets (Rp90–180 million per site) but is occupied by bundled integrators and operators; revenue-share terms are not public.
  4. *Homeowner kit* has the worst economics: lowest willingness to pay, highest support per rupiah, cheapest substitutes.
- Per-site capex in Indonesia is paid once; converting buyers to subscriptions runs against local practice ("tanpa iuran bulanan" is used as a selling point).

### Gaps
- No Indonesian data on integrator or dealer gross margins for CCTV, barrier gates or parking systems.
- No published revenue-share or per-transaction terms for Indonesian parking operators (Secure Parking, Sky Parking, Parkee, Centrepark, ISS).
- No current (post-2024) per-house or per-gate SaaS price for a Southeast Asian residential LPR product.
- No information on what Indonesian integrators pay for third-party LPR engines or SDKs.

---

## Key question 6 — Legal and regulatory position in Indonesia

### Takeaway
UU 27/2022 now has its implementing regulation (PP 33/2026, signed 16 July 2026, fully applicable from 16 January 2027) with administrative fines of up to 2% of annual revenue, but the supervisory agency is not expected to function until about 2028, so enforcement in 2026 is weak. A licence plate is generally treated as indirectly identifying personal data, which would make a cluster manager a data controller and a software vendor a processor; I found no rule specific to private ANPR.

### Cited Findings
- PP 33/2026 implements UU 27/2022; 12 chapters, 225 articles covering data classification, legal bases, data-subject rights, controller and processor duties, transfers, data protection officers, impact assessments and administrative sanctions; signed by President Prabowo on 16 July 2026 **[snippet]** — [Veritask](https://veritask.ai/id/artikel/pengaturan-teknis-pelindungan-data-pribadi-dan-kewajiban-pengendali-serta-prosesor-akhirnya-terbit-lewat-pp-33-2026); [Meridian Hukum](https://meridianhukum.com/peraturan/pp-no-33-tahun-2026)
- It takes effect six months after promulgation, i.e. 16 January 2027 **[snippet]** — [Katadata, 3 Sep 2026](https://katadata.co.id/finansial/makro/6a9979b7c5745/pp-pelindungan-data-pribadi-berlaku-januari-2027-ini-aturan-baru-data-anak)
- Administrative fine up to 2% of annual revenue per violation variable, scaled by impact, duration, data type and number of data subjects; Articles 180–187 set the supervisor's powers from ordering processing to stop up to fines **[snippet]** — [Justisio](https://justisio.com/blog/pp-pdp-disahkan-jangan-sampai-kena-sanksi)
- The public can sue and receive compensation for personal-data violations **[snippet; headline]** — [Bisnis.com, 2 Sep 2026](https://teknologi.bisnis.com/read/20260902/84/2000857/masyarakat-dapat-gugat-dan-terima-ganti-rugi-atas-pelanggaran-data-pribadi)
- Enforcement status: formation of the PDP agency is being accelerated; implementation is judged not yet effective; the agency is expected to be effective only around 2028; Komdigi urges government bodies, businesses and the public to run internal audits now **[snippet — article returned 403 when opened]** — [Bisnis.com, 13 Sep 2026](https://teknologi.bisnis.com/read/20260913/84/2003698/pembentukan-badan-pdp-dipercepat-implementasi-uu-pdp-dinilai-belum-efektif); several technical provisions still need the independent authority **[snippet]** — [Bisnis.com, 1 Sep 2026](https://teknologi.bisnis.com/read/20260901/84/2000553/penerapan-aturan-pp-pelindungan-data-pribadi-butuh-dukungan-otoritas-independen)
- Is a plate personal data? Statutory definition: data about an individual who is identified or identifiable "secara tersendiri atau kombinasi dengan informasi lainnya"; a government training deck classes a vehicle plate as indirectly identifying personal data **[snippet; educational material, not a regulator ruling]** — [Pilar Statistik Kota Magelang](https://pilarstatistik.magelangkota.go.id/storage/uploads/coachingclinicfile/01K9V2BEFC1Z1EFKFHW47GFHFY.pdf); an academic thesis reaches the same view because a plate can be linked to the owner's identity **[snippet]** — [UMN thesis](https://kc.umn.ac.id/id/eprint/40144/2/BAB_I.pdf)
- Controller definition and duties: a controller is whoever determines the purpose and controls the processing; duties in Articles 20–50 include showing proof of consent, keeping data confidential and preventing unauthorised access; Article 47 makes the controller accountable **[snippet]** — [Hukumonline: controller versus processor](https://www.hukumonline.com/berita/a/bedah-uu-pdp--perbedaan-pengendali-vs-prosesor-data-pribadi-lt63460658550b0/); [Hukumonline klinik](https://www.hukumonline.com/klinik/a/uu-pdp--landasan-hukum-pelindungan-data-pribadi-lt5d588c1cc649e/)
- Visual data: unlawful processing of visual data carries sanctions **[snippet; title]** — [Hukumonline klinik](https://www.hukumonline.com/klinik/a/pemrosesan-data-visual-tidak-sah-ini-sanksinya-lt63368386819ef/); in August 2026 the Komdigi minister said a person's face and image are biometric personal data under UU PDP (statement in a viral case, not a CCTV-specific rule) **[snippet]** — [Suara Surabaya](https://www.suarasurabaya.net/kelanakota/2026/viral-kasus-kreator-konten-rekam-usher-giias-komdigi-sebut-langgar-uu-pdp-dan-etika/?page=all)
- Text of the law — [JDIH Komdigi: UU 27/2022](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/undangundang+nomor+27+tahun+2022)
- Plate regulation: Peraturan Kepolisian No. 7/2021 on vehicle registration and identification governs plate colour/format **[snippet]** — [detikOto](https://oto.detik.com/berita/d-5926057/pelat-putih-kendaraan-diterapkan-2022-ini-alasannya)
- ETLE context: police ANPR enforcement is active and escalating (Operasi Patuh 2026 targeted modified and covered plates; ETLE face recognition is linked to Dukcapil) **[snippet]** — [Kompas TV](https://www.kompas.tv/info-publik/673085/operasi-patuh-2026-mulai-8-juni-pelat-nomor-dimodifikasi-hingga-ditutup-jadi-target-etle); [detikOto](https://oto.detik.com/berita/d-8515543/3-kondisi-etle-pengenal-wajah-pengendara-bakal-berfungsi)
- Radio compliance note for the UHF alternative: Malaysian-market UHF readers carry SIRIM certification, so Indonesian deployments need the local equivalent **[snippet; the Indonesian requirement itself is my reading, not stated in the source]** — [TimeTec UHF](https://timeteccloud.com/parking/uhf)

### Inferences
- A cluster manager, RT/RW or building owner running an ANPR gate decides the purpose and means of processing, so it is the controller; a developer hosting plate logs or photos in a cloud service acts as a processor and would need a processing agreement, retention limits and access controls. An on-premise, on-camera allowlist keeps the developer out of the processor role entirely — a practical argument for an offline-first product.
- The gate camera inevitably captures faces of drivers and pedestrians, which the minister has characterised as biometric personal data; that raises the compliance bar above "plates only".
- Low enforcement risk through 2027 (no functioning supervisor) does not remove civil exposure: the right to sue for compensation exists now, and corporate buyers (developers, factories, operators) will ask vendors for compliance paperwork as the January 2027 date approaches.
- For residents, the lawful basis is likely contract/consent via estate rules; for visitors it is notice at the gate. This is my reading; no source addresses residential ANPR specifically.

### Gaps
- No official Komdigi or PDP-agency guidance on whether a vehicle plate is personal data, and no guidance specific to CCTV or ANPR operated by housing estates, offices or parking operators.
- No police/Korlantas regulation found on private use of ANPR, and no rule found on private access to the vehicle registration database (which a private product could not query anyway, as far as I could establish).
- The full text of PP 33/2026 was not read; article numbers and the 2% figure come from secondary summaries.
- Retention-period requirements for CCTV/plate logs under PP 33/2026 not found.
- The Bisnis.com article of 13 September 2026 (agency effective about 2028) could not be opened; the figure rests on a search summary.
