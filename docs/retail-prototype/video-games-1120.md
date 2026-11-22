# Video games and consoles, with title collisions (gen#1120)

The retail build had game controllers and gaming headsets (gen#956) but no game and no console:
0 of each on the served index `catalog_combined_2026-11-20-1837`. Two template-only specs now sit
under `Electronics > Gaming`, beside the controllers and headsets.

| Type | Spec | Path | Styles | SKUs | SKU axis |
|---|---|---|---:|---:|---|
| Video Game | `type_specs/video_game.py` | Electronics > Gaming > Video Games | 206 | 618 | platform |
| Game Console | `type_specs/game_console.py` | Electronics > Gaming > Consoles | 7 | 32 | color |

- **Titles.** There are 188 titles. 162 are an invented world and a genre word (`Quarrow Rally`,
  `Velden Tactics`): 18 worlds take nine genres each. 26 are collision titles (below). Every
  tenth title also has a `Deluxe Edition` style, which makes 18 more styles.
- **Platforms.** Each style is sold on three of four platforms: `PC` and the invented console
  families `Kestara`, `Lumivo` and `Drovik`. Each is one SKU. The platform a title skips cycles.
- **Attributes.** Each game has `genre` (12 genres), `age_rating` (3+, 7+, 12+, 16+ or 18+),
  `number_of_players`, `edition` (Standard or Deluxe) and `format` (Disc, or Download Code on
  every fourth title).
- **Consoles.** There are five consoles, one maker per family: two Kestara, two Lumivo
  (one handheld) and one Drovik. Each comes in the six main colors. Each states its `platform`
  and `console_form`. There are two decoys: a class 4 red trim and a class 6 `Green Hollow`
  bundle.
- **Drawings.** `kit_gaming.video_game` draws a case with its disc, or a download code card,
  and adds a slipcover and a gold band for a deluxe edition. `kit_gaming.game_console` draws a
  home box, a slim box or a handheld.
- **Invented.** Every title, publisher (the brand), platform and console is invented. The test
  checks every title, brand, platform, attribute and description against a list of real
  consoles, stores and publishers.
- **Templates only.** A derived style would invent titles from the values a title shows, and
  a game's name shows none.

## Collision titles

Each title holds a word of another department's product type or category. The test measures
each word on the build's own vocabulary (every word of a product type or category label outside
Electronics). Any title not in this list must hold no such word. The counts are the styles
outside Electronics whose title holds the word, at the ceiling build (seed 0).

**Without a policy**, a lexical search for the title matches the game, which holds every word of
it. It also matches every product whose title holds one of the words. A semantic leg reads the
family word ("kitchen", "garden") and pulls that family up.

**With a policy**, one policy covers every title rather than one trigger per query (the 2026-10-10
ruling). Its vocabulary is the game titles, and it reads a query that is a whole title as the
Video Games category. The game comes first and the family leaves the first row. The family's
own query (`kitchen knife`, `garden chair`) does not match a title and is unchanged.

| Query | Collides with | Styles whose title holds the word, without a policy | Expected with the policy |
|---|---|---|---|
| `garden party` | Garden Chair; party goods (Party Cup, Party Plate) | garden 549 (Garden Chair 130, Garden Table 80); party 260 (Board Game 101, Card Game 87, Party Cup 21) | the game first, then party goods |
| `kitchen rush` | Kitchen Utensil, Kitchen Knife | kitchen 467 | the game first |
| `pet rescue` | Pet Bed, Pet Toy | pet 43 | the game first |
| `tool time` | Hand Tool, Tool Kit | tool 33 (Grill Accessory 15, Tool Kit 6) | the game first |
| `dinosaur dig` | Toy Figure | dinosaur 109 (Soft Toy 28, Building Set 18) | the game first |
| `pillow fight` | Pillow | pillow 166 (Pillow 153) | the game first |
| `cake quest` | Cake | cake 125 (Cake 100) | the game first |
| `sofa surfers` | Sofa, Corner Sofa | sofa 73 | the game first |
| `tent troopers` | Tent | tent 6 | the game first |
| `golf club legends` | Golf Club, Golf Ball | golf 95; club 65; both words 42 | the game first |
| `robot mower mayhem` | Robot Mower, Lawn Mower | robot 118; mower 35; both words 17 | the game first |
| `jigsaw island` | Jigsaw Puzzle | jigsaw 67 | the game first |
| `toaster tactics` | Toaster | toaster 5 | the game first |
| `kettle kingdom` | Kettle | kettle 32 | the game first |
| `blender brawl` | Blender | blender 170 | the game first |
| `shampoo showdown` | Shampoo | shampoo 190 | the game first |
| `dog park dash` | Dog Food, Dog Treats | dog 669 | the game first |
| `cat burglar` | Cat Food, Cat Litter | cat 600 | the game first |
| `umbrella storm` | Umbrella | umbrella 10 | the game first |
| `saucepan samurai` | Saucepan | saucepan 6 | the game first |
| `lantern light` | Camping Lantern, Night Light | lantern 77; light 756; both words 36 | the game first |
| `picnic blanket panic` | Picnic Blanket | picnic 25; blanket 13; both words 5 | the game first |
| `coffee table tycoon` | Coffee Table, Coffee | coffee 1,027; table 881; both words 110 | the game first |
| `candle keeper` | Scented Candle | candle 173 | the game first |
| `light bulb labs` | Light Bulb | light 756; bulb 64 | the game first |
| `ladder climb` | Step Ladder | ladder 10 | the game first |

### `garden party game` vs `garden party chairs`

| Query | Without a policy | Expected with the policy |
|---|---|---|
| `garden party game` | `game` also matches the party board and card games (101 and 87 styles hold "party"), so they sit around the video game | the title and `game` name the Video Games category: the video game first |
| `garden party chairs` | no style holds all three words; `garden chair` is in 133 titles (Garden Chair 130), and the video game holds two of the three words | `chairs` names Garden Chair, so the query is not a whole title: Garden Chairs first and the game off the first row |
