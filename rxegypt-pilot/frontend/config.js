// RxEgypt frontend configuration — loaded BEFORE rxegypt-api.js on every page.
//
// Set RXEGYPT_API_URL to your backend base URL (including /api/v1) to enable
// LIVE mode. Leave it commented out to run in DEMO mode (no backend required).
//
//   window.RXEGYPT_API_URL = 'http://localhost:8000/api/v1';
//
// The frontend must be served from an origin allowed by the backend's
// CORS_ORIGINS (default http://localhost:3000).
//
// Pages that authenticate as a pharmacist (pharmacy-pos.html) set
// window.RXEGYPT_TOKEN_KEY = 'rxegypt_token_pharmacist' before this file, so
// patient and pharmacist sessions don't collide in localStorage.
