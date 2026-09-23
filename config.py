"""Shop registry and global pipeline settings.

Every shop in SHOPS has passed the permission check recorded in SOURCES.md.
Do not add a shop here without completing that check first: see README.md,
section "Adding a new shop".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
HISTORY_DIR = DATA_DIR / "history"
LAST_GOOD_DIR = DATA_DIR / "last_good"
SITE_DIR = REPO_ROOT / "site"
TEMPLATE_DIR = REPO_ROOT / "templates"
STATIC_DIR = REPO_ROOT / "static"

# Identify the crawler honestly. Override the contact URL via the
# POKEARB_CONTACT_URL environment variable when deploying your own fork.
USER_AGENT_TEMPLATE = (
    "PokeArbBot/1.0 (prissammenligning for forseglede Pokemon TCG-produkter; "
    "+{contact})"
)
DEFAULT_CONTACT_URL = "https://github.com/pokearb/pokearb"

# Politeness floor. Applied per host, never per request thread.
MIN_DELAY_SECONDS = 2.0
REQUEST_TIMEOUT = 30
# On HTTP 429 without Retry-After, back off from here and give up after
# MAX_RATE_LIMIT_RETRIES attempts, leaving the shop on its last good data.
RATE_LIMIT_BASE_BACKOFF = 60
MAX_RATE_LIMIT_RETRIES = 3

# TCGdex set lists are fetched live on every run, in these languages, so that
# localised set names on shop titles resolve to the same canonical set as the
# English ones. English carries the Latin-script names of the Japanese,
# Korean and Chinese exclusive sets, which is what European shops print.
TCGDEX_BASE = "https://api.tcgdex.net/v2"
TCGDEX_LANGUAGES = ("en", "de", "fr", "nl", "es", "it", "pt")

# ECB daily reference rates. Rates are quoted as units of CUR per 1 EUR.
ECB_BASE = "https://data-api.ecb.europa.eu/service/data/EXR"
ECB_CURRENCIES = ("DKK", "SEK", "NOK", "PLN", "CZK", "HUF", "RON", "BGN", "GBP", "CHF")


# --------------------------------------------------------------------------
# Shipping
# --------------------------------------------------------------------------
#
# Most shops publish no per-country price list at all: the figure only appears
# at checkout. Rather than invent numbers, PokeArb records the rate only where
# the shop states it, and falls back to a clearly labelled assumption
# everywhere else. The assumption is adjustable on the site, so a user who
# knows the real figure can put it in and the ranking updates.
#
# These defaults are PokeArb's own placeholders. They are NOT quoted rates and
# they are never presented as such.

ASSUMED_SHIPPING_DKK: dict[str, float] = {
    "DK": 45.0,
    "SE": 85.0,
    "DE": 95.0,
    "NL": 95.0,
    "BE": 95.0,
    "AT": 110.0,
    "PL": 110.0,
    "FI": 110.0,
    "ES": 120.0,
    "IT": 120.0,
    "FR": 110.0,
    "PT": 120.0,
}
ASSUMED_SHIPPING_FALLBACK_DKK = 120.0


@dataclass(frozen=True)
class Shipping:
    """What the shop says it charges, or nothing at all.

    `amount` and `free_over` are in the shop's own currency. `verified` is
    False when the shop publishes no figure, in which case the site uses the
    assumption above and says so on the page.
    """

    amount: float | None = None
    free_over: float | None = None
    source_url: str = ""
    checked: str = ""
    verified: bool = False
    note: str = ""


@dataclass(frozen=True)
class Shop:
    key: str
    name: str
    country: str
    currency: str
    adapter: str
    base_url: str
    ships_to_dk: bool
    # False when the shop does not publish a country list we could read.
    # Surfaced on the site so a user is never told delivery is certain.
    shipping_confirmed: bool = True
    shipping: Shipping = field(default_factory=Shipping)
    min_delay: float = MIN_DELAY_SECONDS
    # Shopify collection handles or Woo category slugs to narrow the crawl.
    # Empty means walk the whole catalogue.
    collections: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""
    # False keeps the shop documented but out of the daily run, for shops
    # that refuse us (403) or whose adapter is broken. Never used to hide a
    # shop that simply failed once: that is what last_good is for.
    enabled: bool = True

    @property
    def flag(self) -> str:
        return {
            "DK": "Danmark",
            "DE": "Tyskland",
            "NL": "Holland",
            "SE": "Sverige",
            "BE": "Belgien",
            "AT": "Østrig",
            "PL": "Polen",
            "FI": "Finland",
            "ES": "Spanien",
            "IT": "Italien",
            "FR": "Frankrig",
            "PT": "Portugal",
        }.get(self.country, self.country)


SHOPS: tuple[Shop, ...] = (
    # --- Denmark -----------------------------------------------------------
    Shop(
        key="matraws",
        name="Matraws",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://matraws.dk",
        # Sendte HTTP 429 23-09-2026. Laengere pause end standard.
        min_delay=4.0,
        ships_to_dk=True,
        # 25.001 produkter i alt, men kun ca. 1.700 er Pokemon. At hente hele
        # kataloget tog over 20 minutter og var unoedigt tungt for butikken.
        collections=("alt-pokemon", "pokemon-collection-boxes"),
        shipping=Shipping(
            amount=39.0,
            source_url="https://matraws.dk/policies/shipping-policy",
            checked="2026-09-22",
            verified=True,
            note="GLS, 'Fragtpriser fra 39 kr'. Ingen fri-fragt-graense oplyst.",
        ),
        notes="25.000+ produkter. Stort katalog, saa crawlet tager laengst tid.",
    ),
    Shop(
        key="musenogslottet",
        name="Musen og Slottet",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://www.musenogslottet.dk",
        # Sendte HTTP 429 23-09-2026. Laengere pause end standard.
        min_delay=4.0,
        ships_to_dk=True,
        shipping=Shipping(
            amount=49.0,
            free_over=699.0,
            source_url="https://www.musenogslottet.dk/policies/shipping-policy",
            checked="2026-09-22",
            verified=True,
            note="GLS Pakkeshop 49 kr, privatadresse 69 kr. Gratis over 699 kr.",
        ),
        notes="Generel legetoejsbutik. Kun en lille del af kataloget er Pokemon.",
    ),
    Shop(
        key="pocketmonster",
        name="Pocket Monster",
        country="DK",
        currency="DKK",
        adapter="woocommerce",
        base_url="https://pocketmonster.dk",
        ships_to_dk=True,
        shipping=Shipping(
            amount=36.0,
            free_over=1000.0,
            source_url="https://pocketmonster.dk/handelsbetingelser/",
            checked="2026-09-22",
            verified=True,
            note="PostNord pakkeboks 36 kr, doeren 48 kr. Gratis over 1000 kr.",
        ),
        notes="WooCommerce Store API giver valuta og lagerstatus direkte.",
    ),
    Shop(
        key="kelz0r",
        name="Kelz0r",
        country="DK",
        currency="DKK",
        adapter="kelz0r",
        base_url="https://www.kelz0r.dk",
        ships_to_dk=True,
        min_delay=5.0,
        notes=(
            "Ingen maskinlaesbart katalog, saa HTML-parsing. robots.txt tillader "
            "produktsiderne for User-agent: * men blokerer ClaudeBot og AhrefsBot "
            "helt, og saetter Crawl-delay op til 10s for navngivne bots. Vi koerer "
            "derfor 5s her, ikke 2s."
        ),
        enabled=False,  # HTML-adapteren fandt 0 produkter 23-09-2026. Slaaet fra indtil selektorerne er rettet.
    ),
    # --- Germany -----------------------------------------------------------
    Shop(
        key="godofcards",
        name="God of Cards",
        country="DE",
        currency="EUR",
        adapter="shopify",
        base_url="https://godofcards.com",
        ships_to_dk=True,
        shipping=Shipping(
            note="Oplyser kun fri fragt til Tyskland fra 150 EUR. Ingen sats til DK.",
        ),
    ),
    Shop(
        key="tcgviert",
        name="TCGViert",
        country="DE",
        currency="EUR",
        adapter="shopify",
        base_url="https://tcgviert.com",
        # Sendte HTTP 429 23-09-2026. Laengere pause end standard.
        min_delay=4.0,
        ships_to_dk=True,
        shipping=Shipping(
            note="Oplyser fri fragt DE fra 150 EUR og AT fra 200 EUR. Intet om DK.",
        ),
    ),
    Shop(
        key="bulkparadise",
        name="Bulk Paradise TCG",
        country="DE",
        currency="EUR",
        adapter="woocommerce",
        base_url="https://bulkparadise-tcg.de",
        ships_to_dk=True,
        shipping_confirmed=False,
        shipping=Shipping(note="Oplyser kun 'Gratis Versand ab 150 EUR' uden landeliste."),
        notes="Butikken offentliggoer ingen landeliste. Levering til DK er ikke bekraeftet.",
    ),
    # --- Netherlands -------------------------------------------------------
    Shop(
        key="tcgshoppers",
        name="TCGshoppers",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.tcgshoppers.nl",
        ships_to_dk=True,
        shipping=Shipping(
            amount=14.95,
            source_url="https://www.tcgshoppers.nl/policies/shipping-policy",
            checked="2026-09-22",
            verified=True,
            note="'For bestellingen naar andere EU-landen bedragen de verzendkosten 14,95 EUR'.",
        ),
    ),
    Shop(
        key="tcgreus",
        name="TcgReus",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.tcgreus.nl",
        ships_to_dk=True,
        shipping_confirmed=False,
        shipping=Shipping(note="Forsendelsessiden oplyser ingen satser."),
        notes=(
            "ships_to_countries er ['*','BE','NL']. Jokertegnet daekker sandsynligvis "
            "DK, men det er ikke bekraeftet."
        ),
    ),
    Shop(
        key="tcgcompany",
        name="TCG Company",
        country="NL",
        currency="EUR",
        adapter="woocommerce",
        base_url="https://tcgcompany.nl",
        ships_to_dk=True,
        shipping_confirmed=False,
        notes=(
            "Forsendelsessiden gav HTTP 404, saa levering til DK er ikke bekraeftet. "
            "Butikkens TLS-certifikat blev afvist under testkoerslen 22-09-2026 "
            "(self-signed i kaeden), saa butikken faldt tilbage paa sidste gode "
            "data. Tjek om det ogsaa sker i GitHub Actions."
        ),
        enabled=False,  # Svarede HTTP 403 til GitHubs servere ved foerste koersel 23-09-2026. Butikken afviser os, saa vi spoerger ikke dagligt. Koer 'build --only tcgcompany' for at teste igen.
    ),
    Shop(
        key="thetcgplug",
        name="The TCG Plug",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.thetcgplug.nl",
        ships_to_dk=True,
        shipping=Shipping(
            source_url="https://www.thetcgplug.nl/policies/shipping-policy",
            checked="2026-09-22",
            note="Satsen beregnes foerst ved checkout og staar ikke paa siden.",
        ),
    ),
    # --- Sweden ------------------------------------------------------------
    Shop(
        key="poketalk",
        name="PokeTalk",
        country="SE",
        currency="SEK",
        adapter="shopify",
        base_url="https://www.poketalk.se",
        ships_to_dk=True,
        shipping=Shipping(note="Oplyser kun svenske leveringstider, ingen sats til DK."),
    ),
    # --- Belgium -----------------------------------------------------------
    Shop(
        key="energyvault",
        name="Energy Vault",
        country="BE",
        currency="EUR",
        adapter="shopify",
        base_url="https://energy-vault.be",
        ships_to_dk=True,
        shipping=Shipping(
            source_url="https://energy-vault.be/policies/shipping-policy",
            checked="2026-09-22",
            note="Vaelges mellem standard og forsikret ved checkout. Ingen satser paa siden.",
        ),
    ),

    # --- Added 2026-09-23 after the second permission sweep ----------------
    Shop(
        key="mtgwebshop",
        name="MtgwebshopDK",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://mtgwebshop.dk",
        ships_to_dk=True,
        shipping=Shipping(note="Forsendelsessiden oplyser leveringstid, ikke pris."),
    ),
    Shop(
        key="rogerz",
        name="Rogerz",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://rogerz.dk",
        ships_to_dk=True,
        shipping=Shipping(note="Forsendelsessiden viser ingen satser."),
    ),
    Shop(
        key="sealedcardzz",
        name="SealedCardzz",
        country="DE",
        currency="EUR",
        adapter="shopify",
        base_url="https://sealedcardzz.com",
        ships_to_dk=True,
    ),
    Shop(
        key="yonko",
        name="Yonko TCG",
        country="DE",
        currency="EUR",
        adapter="shopify",
        base_url="https://yonko-tcg.de",
        ships_to_dk=True,
    ),
    Shop(
        key="cardify",
        name="Cardify",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://cardifytcg.nl",
        ships_to_dk=True,
    ),
    Shop(
        key="lichcards",
        name="Lichcards",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://lichcards.nl",
        ships_to_dk=True,
        # 25.001 produkter i alt. "alle-tcg-producten" er de 453 forseglede.
        collections=("alle-tcg-producten",),
        shipping=Shipping(
            amount=9.95,
            free_over=75.0,
            source_url="https://lichcards.nl/policies/shipping-policy",
            checked="2026-09-23",
            verified=True,
            note="Oevrige EU-lande: standard 9,95 EUR, gratis fra 75 EUR.",
        ),
    ),
    Shop(
        key="bescards",
        name="Bescards",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.bescards.com",
        ships_to_dk=True,
        shipping=Shipping(note="FedEx International, pris beregnes ved checkout."),
    ),
    Shop(
        key="davidptcg",
        name="DavidPTCG",
        country="NL",
        currency="EUR",
        adapter="woocommerce",
        base_url="https://davidptcg.nl",
        ships_to_dk=True,
        shipping_confirmed=False,
        notes="Betingelserne naevner kun fri fragt i Holland. Levering til DK er ikke bekraeftet.",
    ),
    Shop(
        key="spelparken",
        name="Spelparken",
        country="SE",
        currency="SEK",
        adapter="shopify",
        base_url="https://spelparken.se",
        ships_to_dk=True,
    ),
    Shop(
        key="tigercards",
        name="Tiger Cards",
        country="ES",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.tigercards.es",
        ships_to_dk=True,
    ),
    Shop(
        key="pokemillon",
        name="Pokemillon",
        country="ES",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.pokemillon.com",
        ships_to_dk=True,
        # Kun Pokemon-kollektionen: 4 sider i stedet for 17. Tjekket 23-09-2026:
        # alle 39 accepterede produkter fra den fulde koersel ligger i den.
        collections=("pokemon",),
    ),
    Shop(
        key="baruzcard",
        name="BaruZcard",
        country="IT",
        currency="EUR",
        adapter="shopify",
        base_url="https://baruzcard.it",
        ships_to_dk=True,
        notes=(
            "Betingelsernes art. 1.10 forbyder gengivelse af sidens indhold uden "
            "tilladelse. PokeArb viser kun pris, lagerstatus og et link, ikke "
            "butikkens tekst eller billeder. Vurderingssag, ikke et forbud mod "
            "automatiseret adgang."
        ),
    ),

    # --- Third sweep, 2026-09-23 (SOURCES.md section F) --------------------
    Shop(
        key="symbizon",
        name="Symbizon",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://symbizon.dk",
        ships_to_dk=True,
        collections=("pokemon-kort",),
        shipping=Shipping(
            amount=49.0,
            free_over=599.0,
            source_url="https://symbizon.dk/policies/terms-of-service",
            checked="2026-09-23",
            verified=True,
            note="GLS og DAO pakkeshop 49 kr., gratis over 599 kr. (afsnit 4).",
        ),
    ),
    Shop(
        key="vaulted",
        name="Vaulted",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://www.vaulted.dk",
        ships_to_dk=True,
        collections=("alt-i-pokemon",),
        shipping=Shipping(note="Pris vises ved checkout. Gratis fragt fra 1.000 kr."),
    ),
    Shop(
        key="familyevolution",
        name="Family-Evolution",
        country="DK",
        currency="DKK",
        adapter="shopify",
        base_url="https://family-evolution.dk",
        ships_to_dk=True,
        collections=("pokemon-kort",),
        notes=(
            "Betingelsernes afsnit 16 forbyder kopiering af tekst og billeder. "
            "PokeArb viser kun pris, lager og link."
        ),
    ),
    Shop(
        key="andcards",
        name="&Cards",
        country="DK",
        currency="DKK",
        adapter="woocommerce",
        base_url="https://www.andcards.dk",
        ships_to_dk=True,
        # Kategori-id'er: booster-boxe, elite-trainer-box, booster-bundles,
        # collections-pokemon. Resten af de ca. 1.900 varer er mest gradede kort.
        collections=("640", "652", "661", "677"),
        shipping=Shipping(
            amount=49.0,
            source_url="https://www.andcards.dk/handelsbetingelser/",
            checked="2026-09-23",
            verified=True,
            note="Butikken skriver 'Fragtpriser fra 49 kr.', saa 49 kr. er laveste sats.",
        ),
    ),
    Shop(
        key="aquitaz",
        name="Aquitaz",
        country="SE",
        currency="SEK",
        adapter="shopify",
        base_url="https://aquitaz.se",
        ships_to_dk=True,
        collections=("pokemon-kort-boxes-display-boxes-booster-packs", "pokemon-elite-trainer-boxes-etbs"),
    ),
    Shop(
        key="samlarhobby",
        name="Samlarhobby",
        country="SE",
        currency="SEK",
        adapter="shopify",
        base_url="https://www.samlarhobby.se",
        ships_to_dk=True,
        collections=("elite-trainer-boxar", "booster-boxar", "booster-boxar-displayer"),
    ),
    Shop(
        key="sgames",
        name="S-Games",
        country="AT",
        currency="EUR",
        adapter="shopify",
        base_url="https://s-games.at",
        ships_to_dk=True,
        collections=("pokemon",),
        shipping=Shipping(
            amount=13.90,
            source_url="https://s-games.at/policies/shipping-policy",
            checked="2026-09-23",
            verified=True,
            note="Danmark 13,90 EUR, 2-6 dage. Fri fragt gaelder kun AT og DE.",
        ),
    ),
    Shop(
        key="primeprotector",
        name="Prime Protector",
        country="AT",
        currency="EUR",
        adapter="shopify",
        base_url="https://primeprotector.at",
        ships_to_dk=True,
        collections=("pokemon-tcg",),
        shipping=Shipping(
            amount=9.90,
            source_url="https://primeprotector.at/policies/shipping-policy",
            checked="2026-09-23",
            verified=True,
            note="Danmark 7,90 EUR til 1 kg, 9,90 til 2 kg, 15,90 til 5 kg. PokeArb bruger 2 kg-satsen.",
        ),
    ),
    Shop(
        key="merchfox",
        name="Merchfox",
        country="AT",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.merchfox.at",
        ships_to_dk=True,
        collections=("pokemon-sammelkartenspiel",),
        shipping=Shipping(note="Pris efter land og vaegt, vises ved checkout."),
    ),
    Shop(
        key="feenturm",
        name="Feenturm",
        country="DE",
        currency="EUR",
        adapter="shopify",
        base_url="https://feenturm.de",
        ships_to_dk=True,
        collections=("pokemon-gesamtes-sortiment",),
        shipping=Shipping(
            amount=16.99,
            source_url="https://feenturm.de/policies/shipping-policy",
            checked="2026-09-23",
            verified=True,
            note="Hele EU 16,99 EUR. Fri fragt over 49 EUR gaelder kun Tyskland.",
        ),
    ),
    Shop(
        key="starz",
        name="Starz Collectibles",
        country="DE",
        currency="EUR",
        adapter="shopify",
        base_url="https://starzcollectibles.de",
        ships_to_dk=True,
        collections=("pokemon",),
        shipping=Shipping(
            amount=14.49,
            source_url="https://starzcollectibles.de/policies/shipping-policy",
            checked="2026-09-23",
            verified=True,
            note="EU-lande 14,49 EUR.",
        ),
    ),
    Shop(
        key="pokefamily",
        name="PokeFamily",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://pokefamily.nl",
        ships_to_dk=True,
        collections=("pokemon",),
    ),
    Shop(
        key="cardnation",
        name="CardNation",
        country="NL",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.cardnation.nl",
        ships_to_dk=True,
        collections=("pokemon-kaarten",),
    ),
    Shop(
        key="hikaru",
        name="Hikaru Distribution",
        country="FR",
        currency="EUR",
        adapter="shopify",
        base_url="https://hikarudistribution.com",
        ships_to_dk=True,
        collections=("display-pokemon", "etb-coffret-dresseur-delite", "coffret-pokemon", "bundles"),
    ),
    Shop(
        key="metamorph",
        name="Metamorph Center",
        country="ES",
        currency="EUR",
        adapter="shopify",
        base_url="https://metamorphcenter.com",
        ships_to_dk=True,
        collections=("pokemon-tcg",),
    ),
    Shop(
        key="gsgameon",
        name="GS-Gameon",
        country="IT",
        currency="EUR",
        adapter="shopify",
        base_url="https://www.gs-gameon.com",
        ships_to_dk=True,
        collections=("sigillati-pokemon",),
    ),
    Shop(
        key="psydeck",
        name="Psydeck",
        country="PT",
        currency="EUR",
        adapter="shopify",
        base_url="https://psydeck.com",
        ships_to_dk=True,
        collections=("pokemon",),
        notes="Betingelsernes afsnit 2 forbyder kopiering af materialer. PokeArb viser kun pris, lager og link.",
    ),
    Shop(
        key="versus",
        name="Versus Gamecenter",
        country="PT",
        currency="EUR",
        adapter="shopify",
        base_url="https://versusgamecenter.pt",
        ships_to_dk=True,
        collections=("pokemon-tcg-1",),
    ),

)

SHOPS_BY_KEY = {s.key: s for s in SHOPS}

# What the daily run fetches. Disabled shops stay in SHOPS so their permission
# record and last known prices are not lost.
ACTIVE_SHOPS: tuple[Shop, ...] = tuple(s for s in SHOPS if s.enabled)
