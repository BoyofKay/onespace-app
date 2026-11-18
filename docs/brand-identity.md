# OneSpace — Brand identity specification

Status: **Working specification for layout and messaging only. Original logo is unchanged.**, November 18, 2026.

## Official lockup

- **Do not redesign, redraw, modify or recolor the existing OneSpace logo.** Use the original `assets/mark.svg` on the website and `assets/branding/mark.png` in Flutter.
- Product name: **OneSpace** (never "One Space" in the wordmark).
- Signature tagline: **Two of Us. One Space.** Exact capitalization and punctuation.
- The English wordmark and official tagline remain consistent in every locale.
- Optional explanatory Arabic translation, separate from the official tagline: **نحن الاثنان. مساحة واحدة.**
- Adjust only spacing, scale and surrounding layout. When the surface is extremely small, show the original symbol alone and supply accessible brand text.

## Type

- Primary Latin/web: **Inter**. Name bold (800); tagline medium/semibold (600); body regular (400–500).
- Arabic: **IBM Plex Sans Arabic** for website UI, with Arabic-appropriate line height; avoid letter spacing in Arabic.
- Mobile: use matching brand weights and hierarchy. Bundle a licensed Inter font before claiming pixel-identical typography on Flutter/Android/iOS; current brand widget uses safe platform fallback.
- Never display a tagline in tiny illegible text just to force it into a narrow space.

## Official colors

| Use | Color |
|---|---|
| Display name / midnight navy | `#14213D` |
| Surrounding interface accent / ocean teal | `#1F6E78` |
| Tagline / slate | `#51657A` |
| Secondary expressive coral | `#E8745A` |
| Dark surface main text | `#F5F7FB` |
| Dark surface accent | `#8AD9D3` |
| Dark surface tagline | `#CCD5E3` |

The original brand asset and its existing artwork are the source of truth. These palette values are for adjacent UI typography and accents, **not instructions to modify the logo**.

## Layout

- Website pinned header: symbol 48px desktop / 38–42px compact, wordmark ~26px desktop / 19–23px compact, tagline 9–11px only if legible.
- Large marketing applications: use clear space of at least one quarter of the symbol's width around the lockup.
- Email signatures: symbol 40px, name 18–20px, tagline 11–12px, with text fallback (no dependence on remote fonts). Avoid large banner images.
- App loading and sign-in: prominent mark above wordmark, tagline centered below; honor light and dark theme contrast.
- Social graphics: use the same navy, teal and coral accents; avoid novel versions of the logo. Provide the full lockup on primary announcement imagery.

## Copy examples

English signature:

**OneSpace**  
Two of Us. One Space.  
onespace.live

Arabic supporting copy for posts:

**OneSpace**  
نحن الاثنان. مساحة واحدة.  
onespace.live

## Rules

- Keep product name in Latin characters, including Arabic/French/Spanish/German UI.
- Avoid replacing the symbol with generic heart, infinity, or couple emoji in product headers.
- Keep brand colors stable across user-selected themes. Theme colors apply to the surrounding UI, not the identity.
- Maintain accessibility: descriptive alt/semantic label for standalone marks; empty alt when adjacent visible name conveys identity.
- Legal-document dates are not marketing copy: each localized legal page must be versioned and dated only after a real publication or revision.
