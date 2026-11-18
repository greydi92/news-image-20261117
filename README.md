[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/greydi92/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/greydi92/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# The World in One Day — Tuesday 17 November 2026

Built for the [make.fun "Sum up 17 November's world news in one image" bounty](https://make.fun/bounty/news-image-20261117).

One image that sums up the world's news of Tuesday 17 November 2026: a front-page infographic with six stories from that day, across regions and fields — Ukraine's second strike on the Crimean Bridge in two days, Iran firing drones at a US radar base in Bahrain, Trump landing in Manila bound for China, Japan scrambling jets over a suspected Russian airspace violation, the US losing its measles-free status after 26 years, and the UK sanctioning firms building West Bank settlements. Every story was verified as happening, or first reported, on 17 November 2026.

`main.py` (Python 3.13, standard library only) draws the 1024×1024 image pixel by pixel with an embedded bitmap font and hand-encodes the PNG. No network, no timestamps, no randomness — two runs write byte-identical output.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024×1024, ~21 KB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=qgn48q27&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
