/**
 * Tangga sumbu yang selalu bilangan bulat dan enak dibaca: 1, 2, 5, 10, 20, 50, …
 *
 * Dipakai grafik jam di beranda, yang menghitung KENDARAAN — pecahan di sumbunya tidak punya arti, dan
 * "3,75 kendaraan" membuat orang berhenti mempercayai grafiknya. Sempat terjadi saat beranda pertama dibuka
 * di peramban (26 Okt), jadi ia dipisah ke berkas sendiri supaya bisa diuji.
 */
export function tanggaBulat(kasar) {
  const perlu = Math.max(1, kasar);
  const pangkat = 10 ** Math.floor(Math.log10(perlu));
  for (const kelipatan of [1, 2, 5, 10]) {
    const calon = kelipatan * pangkat;
    if (calon >= perlu) return Math.max(1, Math.round(calon));
  }
  return Math.max(1, Math.round(10 * pangkat));
}
