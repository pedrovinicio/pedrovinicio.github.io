# Mangue Games — Instagram automation playbook

Instructions for the weekly scheduled run that plans, creates and schedules @manguegames posts (Instagram + Facebook Page "Mangue Games") with no human in the loop. Mangue Games is Pedro's indie studio from Recife; the account covers all of its games.

## Fixed settings
- Account: Metricool brand `blogId` **7239705** (Instagram `manguegames`, formerly `fast_eleven`, + Facebook Page "Mangue Games"), timezone `America/Recife`.
- **Every post goes to both Instagram and Facebook** (same image(s) and caption).
- Cadence: **4 posts/week, one per game — Saturday 13:00, Sunday 13:00, Wednesday 16:00, Thursday 16:00** (America/Recife). The weekly run (Fridays) fills every slot in the next 7 days. Never schedule in the past; skip a slot that already has a post (check `getScheduledPosts` and `log.md`).
- **Each game gets exactly one post per week.** Rotate which game gets which slot: no game keeps the same slot two weeks in a row (read last week's rows in `log.md`).
- Language: **Portuguese (Brazil) only**.
- Link in bio: `https://pedrovinicio.github.io/manguegames/` (lists every game with its store links).
- Drive backup folder id: **10kCrzRICnjlux0stSE653v-rRmlz8aoD** ("Mangue Games – Instagram Posts").
- Repos:
  - Image hosting + this playbook: `pedrovinicio/pedrovinicio.github.io` — push access, change **only `social/`** (never `manguegames/`, `app-ads.txt` or anything else).
  - Game code, read-only (never push): `pedrovinicio/fast-eleven`, `pedrovinicio/carom-legends`, `pedrovinicio/riot-racers`, `pedrovinicio/gold-rush-world-games`.
  - Fast Eleven's post history before 2026-11-13 is already copied into `log.md` and `insights.md` here; no need to clone `fast-eleven-website`.

## The games
Verify every fact in the game's repo (README, `docs/`, code; for Fast Eleven also `ROADMAP/*/_features_*.md`) before using it. Never invent features.

| Key (`"game"` in make_post.py) | Game | Repo | Stores (caption CTA) | Game tag | Content angle |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `fast-eleven` | Fast Eleven | fast-eleven | App Store + Google Play | #FastEleven | Football manager, Elifoot-style: 13 leagues, 32 clubs in 4 divisions, 14 rounds, promotion/relegation, 11 formations incl. BEST XI, dynamic ratings, manager morale, job offers, cup, cards/injuries, transfers. Vocabulary: escalação, acesso, rebaixamento, mercado, vestiário. |
| `carom-legends` | Carom Legends | carom-legends | App Store + Google Play | #CaromLegends | 3D pool (sinuca/bilhar) on a 9-ft tournament table: 8-ball and 9-ball, spin/english, ball in hand, fouls; online matches via Game Center with Elo per mode and leaderboards. |
| `riot-racers` | Riot Racers | riot-racers | App Store + Google Play | #RiotRacers | Punk combat racing in a desert galaxy, in the spirit of Rock n' Roll Racing: planets (Scrapia, Glowtown, Cryonix, Magmora), 4 tracks each, drivers, 10/6/3/1 points, upgrades (engine, tires, armor, missiles, mines, nitro), voxel/pixel art, synth punk soundtrack. Free planet + one-time Full Game purchase. |
| `gold-rush` | Gold Rush: World Games | gold-rush-world-games | App Store + Google Play | #GoldRushWorldGames | Multi-sport arcade in the spirit of 1992's Olympic Gold: 11 events (100m, hurdles, long jump, pole vault, hammer, javelin, archery, swimming, diving, kayak, track cycling), 24 nations, medal table, 3 difficulties, 25 achievements; free Mini Games + one-time full Games unlock. **Never** use "Olympic"/"Olimpíadas", the rings or other IOC marks — say "Jogos", "competição", "quadro de medalhas". |

All four games are on the App Store and Google Play (since 2026-11-11). Never claim a game is free, a price, a download count, a release date or a promotion.

## Goal
Maximise **reach** (people reached, new followers) for the studio and each game. Optimise for reach, shares and saves first, likes second.

## Each run
0. **Review performance first** — see "Learning loop". Its decisions (times, hashtags, topic mix, formats) override the defaults in this file for this run.
1. Attach (add_repo) and shallow-clone the hosting repo and the four game repos. Read `social/log.md`, `social/insights.md` and the library READMEs here.
2. Find news per game: in each game repo, look at commits since the last run (`git fetch --depth=200` then `git log --since=<last run date>`) and its docs/roadmap for features that are shipped and not yet posted (check `log.md`). Only announce shipped work — never specs, placeholders or plans.
3. Plan the week: one post per game, each with a content type:
   - **Novidade** — a shipped feature or update not yet posted (only if real news exists).
   - **Você sabia?** — a real, verified game fact.
   - **Engajamento** — a question/poll ("8-ball ou 9-ball?", "Qual planeta é o mais difícil?", "Qual prova você zera primeiro?", "4-3-3 ou BEST XI?").
   - **Dica** — a save-oriented tips post (Dica do técnico / Dica do mestre da sinuca / Dica do piloto / Dica do atleta), usually a carousel ending with "Salva esse post".
   Never repeat a game's topic from its last 6 weeks in `log.md`. Use at least 2 different content types per week.
4. **Visual variety (mandatory — the feed must never look repetitive).** Read the layout/theme/bg of the last 8 posts in `log.md`, then:
   - The 4 posts of a week use **4 different layouts**, and no post uses the same layout as the post right before it in the feed.
   - Rotate themes (`dark`, `color`, `light`): at most 2 `dark` per week, at least one `light` every week. Each game has its own palette, so the feed stays colourful.
   - Backgrounds: **prefer Pedro's library** (`social/library/<game>/`, see each README) when it has an image that fits; add the post slug to that README's usage log. Otherwise use the game's art (see make_post.py docstring). Never reuse the same bg **and** crop for a game within its last 3 posts: vary `bg_x`/`bg_y` (e.g. the 8-ball vs the 9-ball in the Carom icon, the runner vs the medal in the Gold Rush icon) and layouts so repeated art still looks different.
   - At least **one carousel per week** (2–5 slides via `"slides"`): slide 1 hook, middle slides one fact/tip each, last slide call to action.
   - Match layout to content: `stat` → a number fact; `versus` → A-vs-B polls; `list` → tips/steps; `quote` → tips/quotes; `card` → challenges/bold statements; `hero` → announcements with strong art.
   - Record `layout/theme/bg` for each post in the log's Type column (e.g. `Você sabia? · stat/color/icon.jpg@x0.2`).
   Render with `social/tools/make_post.py` (Pillow; for Fast Eleven set `FE_ASSETS=/home/claude/fast-eleven/assets/images/`):
   `python3 make_post.py '<json spec>' out.jpg` — keys: `game` (required), `layout`, `theme`, `bg`, `bg_x`, `bg_y`, `kicker` (NOVIDADE / VOCÊ SABIA? / SUA VEZ / DICA DO … / DESAFIO), `headline` (≤ 9 words), `highlight` (a word/phrase of the headline, drawn in the accent colour), `sub` (one short sentence); plus `number` (stat), `options` [A, B] (versus), `items` [3–5] (list), `footer` (quote). Carousel: `"slides": [...]` → out-1.jpg, out-2.jpg…
   **Open every rendered JPG and look at it**: text legible over the art, nothing cut off, no overlap, the art crop shows something recognisable. Re-render if not.
5. Save to `social/posts/<YYYY-MM-DD>-<game>-<slug>/image.jpg` (carousel: `image-1.jpg`, `image-2.jpg`…) + `caption.txt`, append rows to `log.md` (with the Game column), commit and push to `main` (only `social/`). Public URL: `https://raw.githubusercontent.com/pedrovinicio/pedrovinicio.github.io/main/social/posts/<dir>/image.jpg` — confirm it returns 200 before scheduling.
6. Schedule each with Metricool `createScheduledPost` (carousel = several URLs in `media`, in order, one alt text each): providers `[{"network":"instagram"},{"network":"facebook"}]`, `instagramData.type` POST, `facebookData` `{"type":"POST"}`, `draft` false, `autoPublish` true, `mediaAltText` in Portuguese, `isAiGenerated` false.
7. Backup: one Google Doc per post in the Drive folder, titled `<YYYY-MM-DD> — <Game> — <Tema> (Instagram)`, with publish time, image link(s), Metricool planner URL and the full caption.
8. Fill the Metricool uuid column in `log.md`, commit, push.
9. Finish with a short English summary of the 4 scheduled posts: date/time, game, topic, first caption line, planner link. Report problems plainly.

## Learning loop (every run, before planning)
1. Pull post data for the last 90 days with Metricool `getAnalyticsDataByMetrics` (brandId 7239705):
   - posts: `IGPO02` date+time, `IGPO03` content, `IGPO07` type, `IGPO14` reach, `IGPO28` views, `IGPO12` interactions, `IGPO27` shares, `IGPO15` saved, `IGPO08` comments, `IGPO29` follows.
   - hashtags: `IGHT01` hashtag, `IGHT03` posts, `IGHT06` views, `IGHT04` likes, `IGHT05` comments.
   Also `getBestTimeToPostByNetwork` (instagram, next 7 days, America/Recife).
2. Match each post to its `log.md` row and record results in `insights.md` → "Results" (with the Game column).
3. Decide, and write the reasoning (dated) to `insights.md` → "Current decisions":
   - **Times**: defaults Sat 13:00, Sun 13:00, Wed 16:00, Thu 16:00 (Pedro's choice). Only move a slot after ≥ 6 posts of data in the Mangue Games era, when best-time data or results clearly favour another hour **on the same day**; move ≤ 3 h per week, within 10:00–22:00. Don't change days — recommend it instead.
   - **Hashtags**: always `#MangueGames` + the game tag. Each game has its own set(s) (see insights). After a set has ≥ 2 posts, favour the best reach per post and replace weak tags.
   - **Games/topics/formats**: note which games and content types reach most; keep one post per game per week regardless, but give the best format more carousels.
   - Change **at most two variables per week** so results stay attributable. With too little data, say so and keep defaults.
4. Commit `insights.md` with the posts.
5. In the summary add 2–3 lines "What I learned / what I changed", and a recommendation if something needs Pedro (e.g. screenshots for a game's library, trying Reels).

## Caption style
- Portuguese, energetic but not cringe, using each game's vocabulary.
- Structure: hook line with 1–2 emojis → 2–3 short sentences → a question to drive comments 👇 → store line → hashtags (5–8).
- Store line (every game): "📲 <Game> na App Store e Google Play. Link na bio."
- Hashtags: the set chosen in `insights.md`; always `#MangueGames` and the game tag.
- Never mention real players, athletes, drivers, clubs, crests or brands (and no IOC marks for Gold Rush).

## Failure handling
- If Metricool rejects a post, retry once; otherwise skip it and report.
- At the start of each run, check last week's posts with `getScheduledPosts` (extendedRange): any with status ERROR → reschedule to a free slot in the coming week (or 5 min from now if still timely) and report it.
- If a game repo can't be reached, still post for that game using verified facts from this playbook, and report the access issue.
- Never delete or edit posts the run didn't create.
