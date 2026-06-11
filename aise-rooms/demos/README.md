# AISE Rooms — Demo Instances

Three live demo targets for the sales pipeline. All three run the **same**
`../index.html`; only `brand.js` differs (the white-label override).

| Instance | App / subdomain | Brand | Currency | Rooms |
|---|---|---|---|---|
| **AISE generic** | `aise-rooms` · rooms.aise.app | AISE Rooms (blue/yellow) | EGP | living, kitchen, lounge, bedroom |
| **Arena Beach** | `arena-beach-rooms` | Arena Beach Interiors (teal/sand) | EGP | living, lounge, bedroom |
| **Coral Crest** | `coral-crest-rooms` | Coral Crest Residences (blue/gold) | USD | lounge, living, bedroom, kitchen |

## How white-label works

`index.html` loads `brand.js` before the app boots. If that file sets
`window.AISE_BRAND_OVERRIDE`, those fields are merged over the built-in
`AISE_CONFIG` (brand name, logo, colours, currency, room subset, footer,
pricing on/off). One shared app, infinite skins — no app code is copied.

## Add a new hotel (≈ the doc's "2 hours per hotel")

```bash
cp -r demos/arena-beach demos/<hotel>
# edit demos/<hotel>/brand.js   (name, logo, colours, currency, rooms, footer)
# edit demos/<hotel>/fly.toml   (set app = "<hotel>-rooms")
```

## Preview locally

```bash
./deploy-demo.sh arena-beach --preview   # → http://localhost:8080
./deploy-demo.sh coral-crest --preview
```

## Deploy to Fly.io

```bash
./deploy-demo.sh arena-beach   # assembles index.html + brand.js, runs `fly deploy`
./deploy-demo.sh coral-crest
# generic:
fly deploy                     # from aise-rooms/ (uses ./fly.toml + ./brand.js)
```

`deploy-demo.sh` assembles the shared `index.html`, the shared `Dockerfile`,
and the demo's `brand.js` + `fly.toml` into a temp dir, so the Docker build
context is self-contained.
