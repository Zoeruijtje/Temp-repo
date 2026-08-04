#!/usr/bin/env bash
set -euo pipefail

mkdir -p audio assets
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36'
get() {
  echo "Downloading $2"
  curl -fL --retry 5 --retry-all-errors --connect-timeout 20 -A "$UA" "$1" -o "$2"
}

# Individually generated narration phrases. Each caption cue uses the duration
# of the matching file, eliminating proportional/estimated subtitle timing.
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/a0905e73-8abc-4c10-9629-bb3378db53ad.mp3' audio/01.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/dc49126c-a455-497b-a572-79d36ee14f53.mp3' audio/02.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/f87936f5-e26b-41f7-86ec-57984b92d425.mp3' audio/03.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/5f17720d-629f-417b-a9a4-3f38b53bd88f.mp3' audio/04.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/2bb55667-cc8b-4bfb-90de-287af8fd0b37.mp3' audio/05.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/0043dfb1-c60f-44c2-91ab-e135762dd5a4.mp3' audio/06.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/a779b225-64e2-49f4-8ef6-ce8e3e23efc9.mp3' audio/07.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/c9120067-be0a-48a0-94fa-fa25269f9ecf.mp3' audio/08.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/56d2da72-4dcc-4edb-803a-da61ec142787.mp3' audio/09.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/52011e84-411b-449f-8b86-966d5cf8a19a.mp3' audio/10.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/159050b4-eabb-45da-b4ca-042e9f5900c9.mp3' audio/11.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/27f7e984-df20-4106-ba0b-ec4e35e9be8f.mp3' audio/12.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/00c8fe74-4906-40d1-9a71-c3194e100fad.mp3' audio/13.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/dd02db65-5324-4e71-8881-04aade94f9f7.mp3' audio/14.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/385eae49-2e5b-4776-ae5e-973807b3a320.mp3' audio/15.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/806fe401-764c-4bad-837d-23b0994f0745.mp3' audio/16.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/88045d1a-9fe6-4707-b12a-c40154a5a93b.mp3' audio/17.mp3
get 'https://storage.googleapis.com/adm--audio-playback--7d--public/mcp-preview/4a5e17e4-90f1-485b-8c18-3f8758c19268.mp3' audio/18.mp3

# Official manufacturer/model cabin imagery. These are visibly labelled as
# representative model interiors, not owner-specific verified cabins.
get 'https://www.gulfstream.com/assets/images/aircraft/g800/d_g800_i_print_006_RT3.jpg' assets/g800_interior.jpg
get 'https://www.gulfstream.com/assets/images/aircraft/g700/d_g700_i_print_00051_PROD.jpg' assets/g700_interior.jpg
get 'https://businessjets.boeing.com/wp-content/uploads/2023/10/04-BBJ_Final_View2.jpg' assets/bbj737_interior.jpg
get 'https://businessjets.boeing.com/wp-content/uploads/2023/08/787-Lounge-comfort.jpg' assets/bbj787_interior.jpg

for f in audio/*.mp3 assets/*.jpg; do
  test -s "$f" || { echo "Missing or empty asset: $f" >&2; exit 1; }
done

file audio/*.mp3 assets/*.jpg
