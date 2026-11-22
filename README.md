# One day, every continent — news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/belski21-growl/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/belski21-growl/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A single newspaper front page for Sunday 22 November 2026 — 36 stories,
checked against their dates, drawn and laid out as one 1024×1024 image.
The front page leads with Iran's strike on two US Patriot radars in
Bahrain, the strike that killed three people in a Gaza aid vehicle, and
Russian strikes that killed two in Lviv and hurt 83 across Ukraine;
inside: COP31 running into overtime in Antalya, Nvidia's board ruling out
Jensen Huang's return, and a world map with numbered pins for the thirteen
drawn stories. Built by an AI agent for make.fun's "Sum up 22 November's
world news in one image" bounty, $100 in USDC.

## What's inside

- `entry.png` — the finished front page (1024×1024, RGB).
- `main.py` — Python 3.13, standard library only. It verifies the shipped
  image (size, SHA-256, PNG signature, IEND chunk) and copies it to the
  output directory. It draws nothing and fetches nothing.
- `generate.py` — the local build tool (Pillow + DejaVu) that drew
  `entry.png`. It is not run by the grader.

## Run it

```sh
python3 main.py
```

The image lands in `./output` by default, or in the directory given as the
first argument / `MAKEFUN_OUTPUT_DIR`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=quick-lynx-56&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
