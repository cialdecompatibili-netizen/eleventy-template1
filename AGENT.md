# Eleventy Template — AGENT.md

Progetto: sito Fernfolio (Eleventy) reso base clonabile per futuri siti.
Repo GitHub: https://github.com/cialdecompatibili-netizen/eleventy-template1
Sito live: https://cialdecompatibili-netizen.github.io/eleventy-template1/
Editor contenuti: https://cialdecompatibili-netizen.github.io/eleventy-template1/admin/
Cartella locale: C:\Users\mirco\Desktop\Eleventy

## Stack
- Eleventy v2 (Nunjucks templates)
- Sass compilato separatamente (build:sass)
- esbuild per il JS
- Sveltia CMS come editor browser (fork di Decap/Netlify CMS)
- GitHub Actions per build + deploy automatico su GitHub Pages
- pathPrefix: /eleventy-template1/ (impostato via env PATH_PREFIX nel workflow)

## Come funziona il flusso (100% automatico, zero build locale)

1. Modifichi contenuti dal browser su /admin (login con token GitHub, vedi sotto)
2. Sveltia CMS fa commit diretto sul repo GitHub (branch main)
3. GitHub Actions parte da solo, builda con Eleventy+Sass+esbuild
4. Il sito si ripubblica da solo su GitHub Pages in 1-2 minuti

Non serve mai lavorare in locale. La cartella locale serve solo da
riferimento/appunti per le sessioni future con Claude.

## Autenticazione editor /admin

Sveltia CMS usa un GitHub Personal Access Token (NON OAuth, niente proxy
esterno da hostare). Il token:
- si genera su github.com/settings/tokens (classic) con scope "repo"
- va generato DA LOGGATO come utente cialdecompatibili-netizen
  (proprietario della repo — attenzione se si hanno più account GitHub,
  è il bug che ci ha fatto perdere tempo la prima volta: il token deve
  appartenere al proprietario/collaboratore del repo, non basta lo scope)
- dura secondo la scadenza scelta in creazione (consigliato 90gg)
- si incolla una volta nel browser su /admin, resta salvato in
  localStorage di quel browser
- su un altro PC/browser va incollato di nuovo (stesso token o uno nuovo)
- NON esiste modo di "recuperare" un token già generato: se perso, se
  ne genera uno nuovo

## Problemi già risolti (non ripetere questi errori)

1. **CSS mancante al primo deploy**: npm-run-all lanciava build:sass PRIMA
   di eleventy, ma eleventy pulisce _site all'avvio e cancellava il CSS
   appena scritto. Fix: nel workflow, ordine forzato:
   build:eleventy -> build:sass -> build:scripts -> postcss

2. **Tutti i link rotti (mancava /eleventy-template1/ nel path)**: il sito
   vive in una sottocartella di github.io, non alla root. Serve pathPrefix
   in .eleventy.js + filtro `| url` su OGNI href/src assoluto nei template
   njk (head.njk, drawer.njk, index.njk, tags/*.njk, image-shortcode.js).
   NON usare HtmlBasePlugin: non esiste in Eleventy v2, rompe la build.

3. **Netlify CMS -> Sveltia CMS**: Decap/Netlify CMS richiede OAuth con
   proxy esterno da hostare. Sveltia CMS (fork moderno, stesso config.yml)
   supporta login diretto con Personal Access Token, zero servizi esterni.

4. **Token con push:false**: se un fine-grained o classic token risulta
   senza permessi di scrittura sul repo, il sospetto n.1 è account GitHub
   sbagliato (utente diverso dal proprietario/collaboratore del repo),
   non i permessi scelti in fase di creazione.

5. **Menu duplicato "Home"**: home.json/index.njk ha eleventyNavigation
   proprio (key: Home, order: 0) per comparire nel menu principale — ma
   drawer.njk (menu mobile) aveva ANCHE una voce "Home" scritta a mano.
   Rimossa quella statica, ora usa solo il loop dinamico su navPages.

## Struttura contenuti (dove editare cosa)

- src/_data/home.json — testo hero homepage
- src/_data/global.json — impostazioni tema (dark/light, logo, icone)
- src/_data/metadata.json — title/description SEO globali
- src/posts/*.md — articoli blog (collection "post" / "article")
- src/projects/*.md — progetti portfolio (collection "project")
- src/pages/*.md — pagine statiche (about, blog, projects, contact) —
  ognuna ha eleventyNavigation nel front matter per comparire nel menu
- src/admin/config.yml — schema del CMS Sveltia (collections, campi)

## Come clonare questo template per un nuovo sito

1. Su GitHub, crea nuovo repo (o usa "Use this template" se abilitato)
2. Copia tutti i file da questo repo
3. Modifica .github/workflows/deploy.yml: cambia PATH_PREFIX al nuovo
   nome repo (es. /nuovo-sito-nome/)
4. Modifica src/admin/config.yml: cambia "repo:" col nuovo nome repo
5. Attiva GitHub Pages nelle Settings del nuovo repo (Source: GitHub
   Actions) — oppure via API come fatto qui (vedi sessione precedente
   per il comando PowerShell/API REST usato)
6. Personalizza src/_data/*.json con contenuti del nuovo sito
7. Genera un nuovo Personal Access Token per l'editor (o riusa quello
   esistente se ha accesso a tutti i repo dell'account)

## Limiti noti / cose da migliorare in futuro

- Eleventy v2, non l'ultima v3 (funziona bene, ma se si vuole aggiornare
  serve testare bene HtmlBasePlugin che in v3 potrebbe funzionare ed
  evitare tutti i filtri | url manuali)
- pathPrefix hardcoded nel workflow, va cambiato a mano ad ogni clone
- Questo è un template PORTFOLIO, non e-commerce: nessun carrello,
  checkout, categorie prodotto. Per un e-commerce vero, discussione
  precedente ha valutato: estendere CartaCMS (soluzione preferita da
  Mirco, riusa stack PHP esistente) vs Eleventy+Snipcart vs backend
  headless (Medusa/Saleor) — decisione non ancora presa
