# Client Configuration Schema Proposal

One `client.json` per client instance in `clients/<clientId>/`, validated by
`tooling/validate-config` against a JSON Schema in `packages/config`.
**No secrets ever appear in this file** — integrations reference environment
variable *names*; values live in host secret stores (the pattern RxEgypt's
`config.py` + Fly secrets already uses).

Companion files per client: `content/*.json` (ledger pattern from Luxor),
`brand/tokens.css` (AISE token contract values), `brand/assets/` (logo,
favicon, photos), `i18n/*.json` (string tables).

## Proposed schema (illustrated as an example instance)

```jsonc
{
  "schemaVersion": "1.0.0",

  "identity": {
    "clientId": "luxor-guest-house",          // permanent, kebab-case
    "productFamily": "travel",
    "template": { "id": "guesthouse", "version": "1.x" },
    "displayName": "Luxor Guest House",
    "legalName": "Luxor Guest House",
    "market": "egypt-luxor-west-bank",
    "country": "EG",
    "currency": "GBP",                         // pricing display currency
    "timezone": "Africa/Cairo",
    "status": "pilot"                          // draft|pilot|live|suspended|retired
  },

  "branding": {
    "logo": "brand/assets/logo.svg",
    "favicon": "brand/assets/favicon.svg",
    "tokens": {                                // maps onto the AISE contract
      "accent": "#c79a3a", "accentDark": "#a87f26",
      "ink": "#2b2620", "muted": "#6b6358", "line": "#e6ddcd",
      "surface": "#f1e7d2", "background": "#f3ebda", "text": "#2b2620",
      "radius": "14px", "spacingDensity": "comfortable"
    },
    "typography": { "heading": "Playfair Display", "body": "Inter" },
    "visualTheme": "warm-heritage",            // template-defined theme presets
    "photographyStyle": "golden-hour-editorial",
    "brandVoice": "warm, personal, host-led"
  },

  "languages": {
    "default": "en",
    "enabled": ["en"],                         // e.g. ["en","ar","de","nl"]
    "rtl": ["ar"],
    "formats": { "date": "DD/MM/YYYY", "number": "en-GB", "currencyDisplay": "symbol" }
  },

  "features": {                                // feature flags, template-scoped
    "booking": true, "reservations": false, "enquiries": true,
    "whatsapp": true, "login": false, "clientDashboard": false,
    "adminDashboard": true, "reviews": true, "offers": false,
    "events": false, "maps": true, "payments": false,
    "analytics": false, "notifications": false, "search": false,
    "aiConcierge": true                        // Luxor's deterministic concierge
  },

  "content": {
    "source": "files",                         // files|cms|database
    "collections": {                           // only what the template uses
      "rooms": "content/rooms.json",
      "tours": "content/tours.json",
      "faqs": "content/faq.json",
      "policies": "content/policies.json",
      "reviews": "content/reviews.json",
      "experiences": "content/experiences.json",
      "locations": "content/locations.json",
      "team": "content/team.json"
      // restaurant template: menus; hotel: rooms+rates; pharmacy: catalogue ref
    }
  },

  "integrations": {                            // adapter id + env-var NAMES only
    "whatsapp": { "adapter": "wa-deeplink", "number": "+201001842081" },
    "email":    { "adapter": "none" },
    "crm":      { "adapter": "none" },
    "analytics":{ "adapter": "none", "envKeys": ["ANALYTICS_ID"] },
    "maps":     { "adapter": "static-illustrated" },
    "payments": { "adapter": "none" },         // rxegypt: paymob + envKeys
    "bookingEngine": { "adapter": "none" },
    "database": { "adapter": "json-ledger" },  // or postgres w/ DATABASE_URL name
    "cms":      { "adapter": "none" },
    "storage":  { "adapter": "none" }
  },

  "deployment": {
    "provider": "render+vercel",               // or fly, docker, cloud-run
    "domain": "luxorguesthouse.example",
    "environments": ["preview", "production"],
    "region": "eu",
    "buildCommand": "npm run build",
    "healthEndpoint": "/healthz",
    "rollbackMethod": "platform-previous-deploy",
    "ports": { "api": 8001, "web": 5173 }      // must agree with registry/ports.json
  },

  "seo": {
    "titleTemplate": "%s · Luxor Guest House",
    "description": "Nile-side guest house on Luxor's West Bank…",
    "structuredDataProfile": "LodgingBusiness" // Restaurant | Pharmacy | …
  }
}
```

## Validation rules for `tooling/validate-config`

1. Schema-valid (required fields, enums, types); `clientId` unique in
   `registry/clients.json`.
2. **Secret scan:** reject values that look like keys/tokens/URLs-with-
   credentials anywhere in the file.
3. Every enabled feature is supported by the named template version.
4. Every enabled language has a string table; RTL languages require the
   template's RTL support flag.
5. Referenced content/brand files exist and parse.
6. Ports agree with `registry/ports.json`; WhatsApp number is E.164.
7. Token values satisfy contrast minimums (feeds the a11y QA gate).

## Evidence base

Every block generalises something already in the repo: `identity/content`
from Luxor's ledger + `contacts.json`; `branding.tokens` from the AISE
contract; `languages.rtl` from RxEgypt's AR/EN pages; `features` from both
apps' implicit toggles (demo mode, mock payments); `integrations` env-name
pattern from `config.py`/`.env.example`; `deployment` from
render.yaml/vercel.json/fly.toml.
