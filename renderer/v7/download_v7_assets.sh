#!/usr/bin/env bash
set -euo pipefail
mkdir -p private_jets_v7/assets
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/150 Safari/537.36'
fetch() {
  local url="$1" out="$2" referer="$3"
  echo "Downloading $out"
  curl -fL --retry 6 --retry-all-errors --connect-timeout 25 --max-time 180 \
    -A "$UA" -e "$referer" "$url" -o "$out"
  test -s "$out"
  file "$out"
}
fetch 'https://gulfstream.com/assets/images/aircraft/g800/d_g800_i_print_006_RT3.jpg' \
  private_jets_v7/assets/g800_interior.jpg 'https://gulfstream.com/en/aircraft/gulfstream-g800/'
fetch 'https://www.gulfstream.com/assets/images/aircraft/g700/d_g700_i_print_00051_PROD.jpg' \
  private_jets_v7/assets/g700_interior.jpg 'https://www.gulfstream.com/en/aircraft/gulfstream-g700/'
fetch 'https://businessjets.boeing.com/wp-content/uploads/2023/10/05-YG146-AMAC-1.jpg' \
  private_jets_v7/assets/bbj737_interior.jpg 'https://businessjets.boeing.com/737-max/'
fetch 'https://businessjets.boeing.com/wp-content/uploads/2023/10/787-9_ENTRANCE_LOBBY.jpg' \
  private_jets_v7/assets/bbj787_interior.jpg 'https://businessjets.boeing.com/787/'
python - <<'PY'
from PIL import Image, ImageStat
from pathlib import Path
for p in sorted(Path('private_jets_v7/assets').glob('*interior.jpg')):
    im=Image.open(p).convert('RGB')
    colors=im.resize((128,128)).getcolors(128*128)
    unique=16384 if colors is None else len(colors)
    variance=sum(ImageStat.Stat(im.resize((128,128))).var)/3
    print(p, im.size, 'unique=',unique,'variance=',round(variance,1))
    assert im.width >= 900 and im.height >= 500
    assert unique >= 500
    assert variance >= 400
PY
