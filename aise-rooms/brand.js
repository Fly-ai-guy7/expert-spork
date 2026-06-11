/* White-label override — GENERIC AISE deployment.
 *
 * The generic build uses the built-in AISE_CONFIG defaults in index.html, so
 * this is intentionally a no-op. Per-hotel deployments replace this file (see
 * demos/<hotel>/brand.js) with their own overrides, e.g.:
 *
 *   window.AISE_BRAND_OVERRIDE = {
 *     brandName:    'Arena Beach Interiors',
 *     brandLogo:    'https://…/logo.svg',
 *     primaryColor: '#0E7C86',
 *     accentColor:  '#F2A65A',
 *     currency:     'EGP',
 *     rooms:        ['living', 'lounge', 'bedroom'],
 *     footerText:   'Powered by AISE · Arena Beach Resort',
 *   };
 */
window.AISE_BRAND_OVERRIDE = window.AISE_BRAND_OVERRIDE || {};
