# Snooker Scorer

A single-file snooker scoring tracker for a real table. Open `index.html` in any browser, no build step or server needed.

## What it does

- Tap the balls potted in a turn, in order. Only the ball that is legally on can be tapped. Several reds potted on one shot are entered with a counter.
- Scores, break, frames won and best-of-N matches are kept for two players.
- Always shows the reds left on the table and the points left. When the player at the table has a free colour (after a red) or a free ball, both players' maximums are shown.
- Fouls: penalty is worked out from the ball on, the colour called, the ball hit first and any ball potted. Supports free ball, foul and a miss (replace the balls, three-miss rule with the clear-view condition), seven-point fouls, and the respotted black.
- Respot popup: names the spot, lets you mark a spot as taken and offers the next one, and says when several balls must be respotted.
- Undo, concede, re-rack, light/dark/auto theme.
- Players list and per-player stats (frames and matches won, points, highest break, 30+/50+/100+ breaks, pots by colour, fouls).

## Data

Everything is saved in the browser (`localStorage`). When the page is published as a Claude artifact with the `db` capability, it also syncs to the artifact's store; outside that environment it silently stays local.

## Rules

Written against the WPBSA Rules of Snooker (Section 3), May 2022 edition: <https://wpbsa.com/wp-content/uploads/Rulebook-Website-Updated-May-2022.pdf>. The rulebook is not included in this repo.

## Tests

The scoring engine is checked by 56 cases that cite the rule number each one comes from.

```
pip install -r tests/requirements.txt
python3 tests/rulebook_tests.py
```

The tests run the page's JavaScript in V8 (via `py-mini-racer`) with a minimal fake DOM.

## Not covered

Handicaps, four-handed play, six-reds snooker, stalemate timing, referee judgement calls (whether a foul happened, snookered or not), and two devices scoring the same frame at once (last write wins).
