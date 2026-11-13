# Image lab tambahan untuk melatih ulang fast-plate-ocr (K26). Dibangun HANYA lewat tools\image-lab-fpo.ps1, di atas image
# lab vision-seed yang ID-nya dikunci (tools/vendor.lock.json, image_lab). Jaringan dipakai hanya saat membangun, untuk
# mengunduh wheel yang SHA-256-nya terkunci di requirements.txt (--require-hashes --no-deps --no-build). Saat jalan selalu
# lewat tools\lab.ps1 -Fpo: tanpa jaringan, repo read-only. Keras memakai torch yang sudah ada; TensorFlow tidak dipasang.
FROM vision-seed-lab:v1
USER root
COPY requirements.txt /bangun-fpo/requirements.txt
RUN uv pip install --python /opt/venv/bin/python --require-hashes --no-deps --no-build -r /bangun-fpo/requirements.txt \
    && rm -rf /root/.cache/uv /bangun-fpo
# NO_ALBUMENTATIONS_UPDATE: albumentations memeriksa versi terbaru ke pypi.org setiap kali dimuat (Rencana 10). Dimatikan,
# supaya kode pihak ketiga tidak mencoba ke internet, juga kelak di server (K25).
ENV KERAS_BACKEND=torch \
    NO_ALBUMENTATIONS_UPDATE=1
USER lab
ARG KUNCI_LAB_FPO=tak-diketahui
LABEL id.megatron.cctvgerbang.kunci-fpo=$KUNCI_LAB_FPO
