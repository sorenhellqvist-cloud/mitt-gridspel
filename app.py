import base64
import math
import random
import re
import time
from pathlib import Path
import streamlit as st

# Kräver Streamlit 1.42 eller senare (st.fragment med run_every och st.container med key)

# ==========================================
# 1. KONFIGURATION OCH SPELINSTÄLLNINGAR
# ==========================================
st.set_page_config(page_title="Stadsäventyret", page_icon="✈️", layout="centered")

STORLEK = 10
RADER = "ABCDEFGHIJ"  # rader A–J uppifrån och ned, kolumner 1–10 från vänster
MIN_AVSTAND = 8       # minsta antal steg mellan start och mål (0 = ingen gräns)
TIDSGRANS = 8.0       # sekunder att svara på
LANDNINGSTID = 1.8    # sekunder innan frågan dyker upp (planet landar)
AVGANGSTID = 1.5      # sekunder som planet lyfter innan det flyger till nästa ruta
BONUS_POANG = 100     # poäng för att välja flygbonus
KOP_PRIS = 300        # vad det kostar att köpa rätt svar
BILDMAPP = Path(__file__).parent / "bilder"
EXTRA_DORR_ANDEL = 0.25  # andel extra dörrar utöver labyrintens grundgångar

FRAGE_BANK = [
    # --- Europa ---
    {"landmark": "Akropolis", "ratt_stad": "Aten", "bild": "aten_akropolis.png",
     "falska_stader": ["Rom", "Istanbul", "Kairo", "Sofia", "Neapel", "Thessaloniki"],
     "fakta": "Klippan mitt i staden där templet Parthenon byggdes på 400-talet före Kristus, till gudinnan Athenas ära."},
    {"landmark": "Brandenburger Tor", "ratt_stad": "Berlin", "bild": "berlin_brandenburger-tor.png",
     "falska_stader": ["München", "Hamburg", "Wien", "Prag", "Warszawa", "Köln"],
     "fakta": "En stadsport från 1791. Under kalla kriget stod den precis vid Berlinmuren, och i dag är den en symbol för Tysklands återförening 1990."},
    {"landmark": "Marienplatz", "ratt_stad": "München", "bild": "munchen_marienplatz.png",
     "falska_stader": ["Berlin", "Stuttgart", "Wien", "Salzburg", "Zürich", "Nürnberg"],
     "fakta": "Stadens stora torg. I tornet på Nya rådhuset finns ett klockspel där figurer dansar och rider tornerspel varje dag."},
    {"landmark": "Elbphilharmonie", "ratt_stad": "Hamburg", "bild": "hamburg_elbphilharmonie.png",
     "falska_stader": ["Berlin", "Bremen", "Köpenhamn", "Amsterdam", "Hannover", "Kiel"],
     "fakta": "Ett konserthus som invigdes 2017. Det är byggt ovanpå ett gammalt lagerhus i hamnen, och taket ser ut som vågor."},
    {"landmark": "Zwinger", "ratt_stad": "Dresden", "bild": "dresden_zwinger.png",
     "falska_stader": ["Leipzig", "Berlin", "Prag", "Wien", "Wrocław", "Kraków"],
     "fakta": "Ett barockpalats från början av 1700-talet, byggt åt kung August den starke. Det förstördes nästan helt i bombningarna 1945 men har byggts upp igen."},
    {"landmark": "Atomium", "ratt_stad": "Bryssel", "bild": "bryssel_atomium.png",
     "falska_stader": ["Antwerpen", "Amsterdam", "Paris", "Luxemburg", "Gent", "Rotterdam"],
     "fakta": "Byggdes till världsutställningen 1958. Det föreställer en järnkristall som har förstorats 165 miljarder gånger."},
    {"landmark": "Manneken Pis", "ratt_stad": "Bryssel", "bild": "bryssel_manneken-pis.png",
     "falska_stader": ["Amsterdam", "Brygge", "Antwerpen", "Paris", "Köln", "Luxemburg"],
     "fakta": "En liten bronsstaty av en kissande pojke, bara drygt en halvmeter hög. Han har över tusen dräkter som han klär ut sig i vid olika tillfällen."},
    {"landmark": "Hôtel van Eetvelde", "ratt_stad": "Bryssel", "bild": "bryssel_van-eetvelde.png",
     "falska_stader": ["Wien", "Barcelona", "Riga", "Antwerpen", "Paris", "Prag"],
     "fakta": "Ett hus i jugendstil som arkitekten Victor Horta ritade på 1890-talet. Det finns med på Unescos världsarvslista."},
    {"landmark": "Tower Bridge", "ratt_stad": "London", "bild": "london_tower-bridge.png",
     "falska_stader": ["Paris", "Dublin", "Edinburgh", "Amsterdam", "Manchester", "Liverpool"],
     "fakta": "En bro över Themsen som invigdes 1894. Mittendelarna kan fällas upp så att höga fartyg kan passera."},
    {"landmark": "Abbey Road Studios", "ratt_stad": "London", "bild": "london_abbey-road.png",
     "falska_stader": ["Liverpool", "Manchester", "Dublin", "Birmingham", "Edinburgh", "New York"],
     "fakta": "Inspelningsstudion där Beatles spelade in de flesta av sina låtar. Övergångsstället utanför blev världskänt genom omslaget till skivan Abbey Road 1969."},
    {"landmark": "Radcliffe Camera", "ratt_stad": "Oxford", "bild": "oxford_radcliffe-camera.png",
     "falska_stader": ["Cambridge", "London", "Edinburgh", "Bath", "York", "Dublin"],
     "fakta": "En rund biblioteksbyggnad från 1749 som tillhör Oxfords universitet. Camera betyder rum på latin."},
    {"landmark": "Louvren", "ratt_stad": "Paris", "bild": "paris_louvren.png",
     "falska_stader": ["London", "Rom", "Madrid", "Wien", "Bryssel", "Berlin"],
     "fakta": "Ett av världens största konstmuseer, där bland annat Mona Lisa hänger. Glaspyramiden vid entrén byggdes 1989."},
    {"landmark": "Vasamuseet", "ratt_stad": "Stockholm", "bild": "stockholm_vasamuseet.png",
     "falska_stader": ["Göteborg", "Oslo", "Köpenhamn", "Helsingfors", "Malmö", "Karlskrona"],
     "fakta": "Här står regalskeppet Vasa, som sjönk på sin första resa 1628 bara en dryg kilometer från kajen. Skeppet bärgades 1961 och är nästan helt bevarat."},
    {"landmark": "Stadshuset", "ratt_stad": "Stockholm", "bild": "stockholm_stadshuset.png",
     "falska_stader": ["Göteborg", "Oslo", "Köpenhamn", "Helsingfors", "Malmö", "Uppsala"],
     "fakta": "Invigdes 1923 och har tre kronor i guld på tornet. Här hålls Nobelfesten varje år i december."},
    {"landmark": "Operahuset", "ratt_stad": "Oslo", "bild": "oslo_operahuset.png",
     "falska_stader": ["Bergen", "Köpenhamn", "Stockholm", "Helsingfors", "Reykjavik", "Göteborg"],
     "fakta": "Invigdes 2008 och ligger vid vattnet i Bjørvika. Man kan promenera på det sluttande vita taket ända upp till toppen."},
    {"landmark": "Nyhavn", "ratt_stad": "Köpenhamn", "bild": "kopenhamn_nyhavn.png",
     "falska_stader": ["Stockholm", "Oslo", "Amsterdam", "Hamburg", "Bergen", "Malmö"],
     "fakta": "En kanal från 1670-talet med färgglada hus längs kajerna. Sagoförfattaren H.C. Andersen bodde här under flera perioder av sitt liv."},
    {"landmark": "Erasmusbron", "ratt_stad": "Rotterdam", "bild": "rotterdam_Erasmus-bron.png",
     "falska_stader": ["Amsterdam", "Antwerpen", "Haag", "Utrecht", "Hamburg", "Bryssel"],
     "fakta": "En vit bro över floden Maas som invigdes 1996. På grund av formen kallas den för Svanen."},
    {"landmark": "Karlsbron", "ratt_stad": "Prag", "bild": "prag_karlsbron.png",
     "falska_stader": ["Wien", "Budapest", "Bratislava", "Kraków", "Brno", "Ljubljana"],
     "fakta": "En stenbro över floden Moldau som började byggas 1357. Längs räckena står 30 statyer av helgon."},
    {"landmark": "Kedjebron", "ratt_stad": "Budapest", "bild": "budapest_kedjebron.png",
     "falska_stader": ["Wien", "Prag", "Bratislava", "Belgrad", "Zagreb", "Ljubljana"],
     "fakta": "Den första fasta bron över Donau mellan stadsdelarna Buda och Pest, invigd 1849. Vid brofästena vaktar stora lejon av sten."},
    {"landmark": "Parlamentspalatset", "ratt_stad": "Bukarest", "bild": "bucharest_palace-of-parliamen.png",
     "falska_stader": ["Sofia", "Belgrad", "Budapest", "Chișinău", "Minsk", "Warszawa"],
     "fakta": "En av världens största byggnader, med över tusen rum. Den byggdes på 1980-talet på order av diktatorn Nicolae Ceaușescu."},
    {"landmark": "Grundarnas monument", "ratt_stad": "Kiev", "bild": "kiev_grundarnas-monument.png",
     "falska_stader": ["Moskva", "Minsk", "Odessa", "Lviv", "Warszawa", "Charkiv"],
     "fakta": "En skulptur av en båt med bröderna Kyj, Sjtjek och Choryv och deras syster Lybid, som enligt legenden grundade staden. Den restes 1982 när staden firade 1500 år."},
    {"landmark": "Vasilijkatedralen", "ratt_stad": "Moskva", "bild": "moskva_vasilijkatedralen.png",
     "falska_stader": ["Sankt Petersburg", "Kiev", "Minsk", "Kazan", "Novgorod", "Warszawa"],
     "fakta": "Kyrkan vid Röda torget med färgglada lökkupoler. Den byggdes på 1550-talet på order av tsar Ivan den förskräcklige."},
    {"landmark": "Colosseum", "ratt_stad": "Rom", "bild": "rom_colosseum.png",
     "falska_stader": ["Verona", "Aten", "Neapel", "Nîmes", "Pula", "Milano"],
     "fakta": "En amfiteater som invigdes år 80 efter Kristus. Här kunde minst 50 000 åskådare se gladiatorer slåss."},
    {"landmark": "Ponte Vecchio", "ratt_stad": "Florens", "bild": "florens_ponte-vecchio.png",
     "falska_stader": ["Venedig", "Pisa", "Bologna", "Siena", "Verona", "Rom"],
     "fakta": "En medeltida bro över floden Arno med butiker byggda direkt på bron. I dag säljs mest guld och smycken där."},
    {"landmark": "Domkyrkan Santa Maria del Fiore", "ratt_stad": "Florens", "bild": "florens_santa-maria-de-flori.png",
     "falska_stader": ["Siena", "Pisa", "Milano", "Bologna", "Venedig", "Rom"],
     "fakta": "Stadens domkyrka. Den enorma kupolen ritades av Filippo Brunelleschi och blev klar 1436."},
    {"landmark": "Formel 1-banan", "ratt_stad": "Monaco", "bild": "monaco_race.png",
     "falska_stader": ["Nice", "Cannes", "Marseille", "Genua", "Sanremo", "Barcelona"],
     "fakta": "Monacos Grand Prix har körts på stadens gator sedan 1929. Bilarna kör bland annat genom en tunnel och längs hamnen."},
    {"landmark": "Plaza Mayor", "ratt_stad": "Madrid", "bild": "madrid_plaza-mayor.png",
     "falska_stader": ["Salamanca", "Barcelona", "Sevilla", "Valladolid", "Lissabon", "Mexico City"],
     "fakta": "Ett stort torg från 1600-talet, omgivet av hus med över 200 balkonger. Här har det hållits marknader, fester och tjurfäktningar."},
    {"landmark": "Alcázar", "ratt_stad": "Segovia", "bild": "segovia_alczar.png",
     "falska_stader": ["Toledo", "Salamanca", "Madrid", "Sevilla", "Granada", "Ávila"],
     "fakta": "En medeltida borg högt uppe på en klippa. Den sägs ha inspirerat Walt Disneys sagoslott."},

    # --- Nordamerika ---
    {"landmark": "Frihetsgudinnan", "ratt_stad": "New York", "bild": "new-york_frihetsgudinnan.png",
     "falska_stader": ["Boston", "Philadelphia", "Washington", "Chicago", "Paris", "Toronto"],
     "fakta": "En gåva till USA från det franska folket, som en symbol för att fira hundraårsminnet av USA:s självständighet. Invigd 1886."},
    {"landmark": "Vita huset", "ratt_stad": "Washington", "bild": "washington_white-house.png",
     "falska_stader": ["New York", "Philadelphia", "Boston", "Baltimore", "Richmond", "Ottawa"],
     "fakta": "USA:s presidents bostad och arbetsplats sedan år 1800. Brittiska soldater satte eld på huset 1814, men det byggdes upp igen."},
    {"landmark": "Golden Gate-bron", "ratt_stad": "San Francisco", "bild": "san-francisco_golden-gate.png",
     "falska_stader": ["Los Angeles", "Seattle", "Lissabon", "Vancouver", "San Diego", "Oakland"],
     "fakta": "En hängbro som öppnade 1937. Den orangeröda färgen valdes bland annat för att bron ska synas bra i stadens täta dimma."},
    {"landmark": "CN Tower", "ratt_stad": "Toronto", "bild": "toronto_cn-tower.png",
     "falska_stader": ["Montréal", "Vancouver", "Ottawa", "Chicago", "Calgary", "Seattle"],
     "fakta": "Ett 553 meter högt torn som invigdes 1976. I över 30 år var det världens högsta fristående byggnadsverk."},
    {"landmark": "Palacio de Bellas Artes", "ratt_stad": "Mexico City", "bild": "mexico-city_palacio-de-bellas-artes.png",
     "falska_stader": ["Madrid", "Havanna", "Buenos Aires", "Bogotá", "Lima", "Guadalajara"],
     "fakta": "Ett konsthus och en teater med en kupol täckt av gult och orange kakel. Bygget började 1904 men blev inte klart förrän 1934."},

    # --- Asien ---
    {"landmark": "Burj al Arab", "ratt_stad": "Dubai", "bild": "dubai_burj-al-arab.png",
     "falska_stader": ["Abu Dhabi", "Doha", "Riyadh", "Muscat", "Bahrain", "Kuwait City"],
     "fakta": "Ett lyxhotell från 1999 som ligger på en konstgjord ö. Formen ska likna ett segel."},
    {"landmark": "Boudhanath-stupan", "ratt_stad": "Kathmandu", "bild": "kathmandu_boudhanath.png",
     "falska_stader": ["Lhasa", "Thimphu", "Delhi", "Varanasi", "Pokhara", "Dhaka"],
     "fakta": "En av världens största stupor, ett slags buddhistiskt helgedomsmonument. Från tornet blickar Buddhas ögon ut åt alla fyra väderstreck."},
    {"landmark": "Petronas Towers", "ratt_stad": "Kuala Lumpur", "bild": "kuala-lumpur_petronas-towers.png",
     "falska_stader": ["Singapore", "Jakarta", "Bangkok", "Shanghai", "Hongkong", "Manila"],
     "fakta": "Två 452 meter höga skyskrapor som stod klara 1998 och var världens högsta byggnader fram till 2004. En gångbro förbinder tornen högt upp."},
    {"landmark": "Raffles Hotel", "ratt_stad": "Singapore", "bild": "singapore_raffles-hotel.png",
     "falska_stader": ["Kuala Lumpur", "Hongkong", "Bangkok", "Jakarta", "Manila", "Penang"],
     "fakta": "Ett hotell från 1887, uppkallat efter stadens grundare Stamford Raffles. Drinken Singapore Sling uppfanns i hotellets bar."},
    {"landmark": "Singapore Flyer", "ratt_stad": "Singapore", "bild": "singapore_singapore-flyer.png",
     "falska_stader": ["London", "Kuala Lumpur", "Hongkong", "Dubai", "Shanghai", "Bangkok"],
     "fakta": "Ett 165 meter högt pariserhjul som öppnade 2008. Ett varv tar ungefär en halvtimme."},

    # --- Afrika ---
    {"landmark": "Union Buildings", "ratt_stad": "Pretoria", "bild": "pretoria_union-buildings.png",
     "falska_stader": ["Johannesburg", "Kapstaden", "Durban", "Nairobi", "Harare", "Windhoek"],
     "fakta": "Sydafrikas regeringsbyggnad, klar 1913. Här svors Nelson Mandela in som landets första demokratiskt valda president 1994."},

    # --- Oceanien ---
    {"landmark": "Operahuset", "ratt_stad": "Sydney", "bild": "sydney_operahuset.png",
     "falska_stader": ["Melbourne", "Brisbane", "Auckland", "Perth", "Adelaide", "Wellington"],
     "fakta": "Invigdes 1973. Taket med sina vita skal ritades av den danske arkitekten Jørn Utzon."},
    {"landmark": "Flinders Street Station", "ratt_stad": "Melbourne", "bild": "melburn_flinders-street-station.png",
     "falska_stader": ["Sydney", "Brisbane", "Adelaide", "Perth", "Auckland", "Wellington"],
     "fakta": "Stadens stora järnvägsstation, med en byggnad från början av 1900-talet. Att mötas under klockorna vid entrén är ett klassiskt sätt att bestämma träff."},
]


def filnyckel(namn):
    """Jämför filnamn utan hänsyn till stora/små bokstäver, mellanslag, _ - och punkt."""
    return re.sub(r"[^a-z0-9]", "", namn.lower())


def las_bildmapp():
    if not BILDMAPP.is_dir():
        return {}
    return {filnyckel(p.name): p for p in BILDMAPP.iterdir() if p.is_file()}


BILDFILER = las_bildmapp()


def hitta_bild(fil):
    return BILDFILER.get(filnyckel(fil))


# Bara frågor vars bild finns i bilder-mappen används i spelet.
AKTIVA_FRAGOR = [f for f in FRAGE_BANK if hitta_bild(f["bild"])] or FRAGE_BANK


FLYGPLAN = {
    "Blå": "#2F6FDB",
    "Röd": "#D93A40",
    "Grön": "#1F8A3E",
    "Lila": "#7B4FD1",
    "Orange": "#F28C28",
}

# Riktningar: (dx, dy). Norr = uppåt = minskande y.
RIKTNINGAR = {"W": (0, -1), "S": (0, 1), "A": (-1, 0), "D": (1, 0)}
MOTSATS = {"W": "S", "S": "W", "A": "D", "D": "A"}
ETIKETTER = {"W": "↑ Norr", "A": "← Väster", "D": "Öster →", "S": "↓ Söder"}
VADERSTRECK = {"W": "norr", "A": "väster", "D": "öster", "S": "söder"}

REGLER = [
    "Spelet går ut på att flyga från startrutan till målet.",
    f"Spelplanen är hundra rutor ordnade i {STORLEK} rader med {STORLEK} rutor i varje rad. "
    "Startrutan ligger vid en kant av spelplanen och målet vid en annan kant.",
    f"I varje ny ruta ser du en bild som ska ge dig en ledtråd om var du har landat, "
    f"och du har {int(TIDSGRANS)} sekunder på dig att svara i vilken stad du landat.",
    f"Rätt svar ger dig en ledtråd eller {BONUS_POANG} bonuspoäng. "
    f"Har du {KOP_PRIS} bonuspoäng kan du köpa rätt svar när du svarat fel.",
    "Du kan landa i en ruta som redan är avklarad, men då är det bara att flyga vidare.",
]


# ==========================================
# 2. LABYRINT, FRÅGOR OCH SPELLOGIK
# ==========================================
def i_rutnat(x, y):
    return 1 <= x <= STORLEK and 1 <= y <= STORLEK


def rutnamn(x, y):
    """Ruta (3, 5) heter 3E: kolumnens nummer följt av radens bokstav."""
    return f"{x}{RADER[y - 1]}"


def kanter(x, y):
    """Vilka kanter av kartan en ruta ligger vid. Hörnrutor ligger vid två."""
    k = set()
    if y == 1:
        k.add("N")
    if y == STORLEK:
        k.add("S")
    if x == 1:
        k.add("V")
    if x == STORLEK:
        k.add("O")
    return k


def slumpa_start_och_mal():
    """Start och mål ligger vid kanten, men aldrig vid samma kant."""
    kantrutor = [
        (x, y)
        for x in range(1, STORLEK + 1)
        for y in range(1, STORLEK + 1)
        if kanter(x, y)
    ]
    while True:
        start = random.choice(kantrutor)
        mojliga = [
            p for p in kantrutor
            if not (kanter(*p) & kanter(*start))
            and abs(p[0] - start[0]) + abs(p[1] - start[1]) >= MIN_AVSTAND
        ]
        if mojliga:
            return start, random.choice(mojliga)


def oppna_dorr(dorrar, x, y, r):
    """Öppnar en dörr åt båda hållen, så att den alltid går att gå tillbaka genom."""
    dx, dy = RIKTNINGAR[r]
    dorrar[(x, y)].add(r)
    dorrar[(x + dx, y + dy)].add(MOTSATS[r])


def skapa_labyrint():
    dorrar = {
        (x, y): set()
        for x in range(1, STORLEK + 1)
        for y in range(1, STORLEK + 1)
    }

    # Steg 1: slumpad djupet-först-sökning. Garanterar att alla rum,
    # inklusive målet, går att nå från start.
    besokta = {(1, 1)}
    stack = [(1, 1)]
    while stack:
        x, y = stack[-1]
        grannar = [
            r for r, (dx, dy) in RIKTNINGAR.items()
            if i_rutnat(x + dx, y + dy) and (x + dx, y + dy) not in besokta
        ]
        if grannar:
            r = random.choice(grannar)
            dx, dy = RIKTNINGAR[r]
            oppna_dorr(dorrar, x, y, r)
            besokta.add((x + dx, y + dy))
            stack.append((x + dx, y + dy))
        else:
            stack.pop()

    # Steg 2: några extra dörrar så att det finns flera vägar att välja.
    for (x, y) in list(dorrar):
        for r in ("S", "D"):
            dx, dy = RIKTNINGAR[r]
            if (
                i_rutnat(x + dx, y + dy)
                and r not in dorrar[(x, y)]
                and random.random() < EXTRA_DORR_ANDEL
            ):
                oppna_dorr(dorrar, x, y, r)

    return dorrar


def dra_fraga():
    """Drar frågor ur en blandad lek, så att alla används innan någon upprepas."""
    if not st.session_state.fragelek:
        st.session_state.fragelek = random.sample(AKTIVA_FRAGOR, len(AKTIVA_FRAGOR))
    return st.session_state.fragelek.pop()


def nollstall_spel():
    ss = st.session_state
    ss.start, ss.mal = slumpa_start_och_mal()
    ss.spelare_x, ss.spelare_y = ss.start
    ss.rum_data = {}
    ss.fragelek = []
    ss.labyrint = skapa_labyrint()
    ss.besokta = {ss.start}
    ss.poang = 0
    ss.mal_firat = False
    ss.landning_nyckel = None  # rummet där planet senast landade
    ss.redan_klarad = False    # om rummet var klarat redan när planet landade
    ss.avgang = None           # vald riktning och starttid medan planet lyfter


def hemta_rum_data(x, y):
    nyckel = f"{x},{y}"
    if nyckel not in st.session_state.rum_data:
        fraga = dra_fraga()
        falska = random.sample(fraga["falska_stader"], 4)
        val = falska + [fraga["ratt_stad"]]
        random.shuffle(val)

        mal_x, mal_y = st.session_state.mal
        exakt_avstand = abs(mal_x - x) + abs(mal_y - y)
        cirka_avstand = max(1, exakt_avstand + random.choice([-1, 0, 1]))

        st.session_state.rum_data[nyckel] = {
            "fraga": fraga,
            "svars_val": val,
            "cirka_avstand": cirka_avstand,
            "klarad": False,        # rätt svar eller köpt svar
            # Det aktuella försöket:
            "svarat": False,
            "ratt_svarat": False,
            "tiden_ute": False,
            "valj_beloning": False,
            "beloning": None,       # 'bonus', 'ledtrad' eller 'kopt'
            "start_tid": None,
        }
    return st.session_state.rum_data[nyckel]


def nytt_forsok(rum):
    """Nollställer frågan när spelaren landar i ett rum som inte är klarat."""
    rum["svarat"] = False
    rum["ratt_svarat"] = False
    rum["tiden_ute"] = False
    rum["valj_beloning"] = False
    rum["beloning"] = None
    rum["start_tid"] = time.time() + LANDNINGSTID
    random.shuffle(rum["svars_val"])


def flytta(r):
    """Planet lyfter först. Själva förflyttningen sker när avgången är klar."""
    st.session_state.avgang = {"r": r, "tid": time.time()}
    st.rerun()


def genomfor_flytt(r):
    ss = st.session_state
    dx, dy = RIKTNINGAR[r]
    ss.spelare_x += dx
    ss.spelare_y += dy
    ss.besokta.add((ss.spelare_x, ss.spelare_y))
    ss.avgang = None


@st.cache_data(ttl=300)
def bild_data_uri(fil):
    """Läser bilden som data, så att planet kan landa ovanpå den."""
    sokvag = hitta_bild(fil)
    if sokvag is None:
        return None
    data = sokvag.read_bytes()
    # Bildtypen avgörs av innehållet, så filer med fel eller saknad filändelse fungerar ändå.
    if data[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        mime = "image/webp"
    elif data[:3] == b"GIF":
        mime = "image/gif"
    else:
        mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()


# ==========================================
# 3. UTSEENDE
# ==========================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
:root {
--ink: #14213D;
--ink-ljus: #24365E;
--gul: #FFC93C;
--himmel: #EEF2F7;
--vit: #FFFFFF;
--dimma: #C9D3E1;
--gra: #55627A;
--gron: #1F8A3E;
--rod: #D93A40;
}
.stApp { background: var(--himmel); color: var(--ink); }
.stApp, .stApp p, .stApp label, .stApp button, .stApp li,
.stApp h1, .stApp h2, .stApp h3, .stApp input {
font-family: 'Atkinson Hyperlegible', system-ui, -apple-system, sans-serif;
}
.block-container { max-width: 720px; padding-top: 2rem; padding-bottom: 4rem; }

.tavla { background: var(--ink); color: var(--vit); border-radius: 18px; padding: 1rem 1.25rem 1.1rem; margin-bottom: 0.9rem; }
.tavla-titel { font-size: 0.95rem; opacity: 0.75; margin-bottom: 0.35rem; }
.tavla-rad { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; }
.tavla-liten { font-size: 0.85rem; opacity: 0.75; }
.tavla-stor { font-size: 2.4rem; font-weight: 700; color: var(--gul); line-height: 1.05; }
.tavla-hoger { text-align: right; }

.hangar { display: flex; justify-content: center; padding: 1.5rem 0 1rem; }
.hangar svg { filter: drop-shadow(0 8px 6px rgba(20,33,61,0.25)); }
.regler { color: var(--gra); font-size: 1rem; line-height: 1.5; margin: 0 0 0.7rem; }

.st-key-fragekort { background: var(--vit); border-radius: 18px; padding: 1rem 1rem 1.2rem; }

.scen { position: relative; border-radius: 14px; overflow: hidden; background: var(--dimma); }
.scen-bild { display: block; width: 100%; height: 260px; object-fit: cover; }
.scen-himmel { height: 260px; background: linear-gradient(180deg, #9CC3EB 0%, #DCEBF8 100%); }
.scen-saknas { height: 260px; display: flex; align-items: center; justify-content: center; color: var(--gra); text-align: center; padding: 1rem; }
.bana { position: absolute; left: 0; right: 0; bottom: 0; height: 30px; background: rgba(20,33,61,0.85); }
.bana::after {
content: ""; position: absolute; left: 6%; right: 6%; top: 50%; height: 3px; transform: translateY(-50%);
background: repeating-linear-gradient(90deg, var(--gul) 0 18px, transparent 18px 34px);
}
.plan { position: absolute; left: 50%; bottom: 12px; width: 110px; line-height: 0; transform: translateX(-50%); filter: drop-shadow(0 4px 3px rgba(0,0,0,0.35)); }
.plan.landar { animation: landa 1.6s cubic-bezier(0.25, 0.7, 0.35, 1) both; }
.plan.lyfter { animation: lyft 1.4s cubic-bezier(0.55, 0, 0.75, 0.6) both; }
.plan.lyfter.vanster { animation-name: lyft-vanster; }
.plan.vanster svg { transform: scaleX(-1); }
@keyframes lyft {
0%   { transform: translate(-50%, 0) rotate(0deg); opacity: 1; }
40%  { transform: translate(-15%, 0) rotate(0deg); }
55%  { transform: translate(10%, -6px) rotate(-6deg); }
90%  { opacity: 1; }
100% { transform: translate(320%, -420%) rotate(-14deg); opacity: 0; }
}
@keyframes lyft-vanster {
0%   { transform: translate(-50%, 0) rotate(0deg); opacity: 1; }
40%  { transform: translate(-85%, 0) rotate(0deg); }
55%  { transform: translate(-110%, -6px) rotate(6deg); }
90%  { opacity: 1; }
100% { transform: translate(-420%, -420%) rotate(14deg); opacity: 0; }
}
@keyframes landa {
0%   { transform: translate(-330%, -420%) rotate(14deg); opacity: 0; }
12%  { opacity: 1; }
75%  { transform: translate(-58%, -10%) rotate(5deg); }
88%  { transform: translate(-51%, 1px) rotate(-1deg); }
100% { transform: translate(-50%, 0) rotate(0deg); }
}
.landmark { font-size: 1.9rem; font-weight: 700; margin: 0.9rem 0 0.6rem; line-height: 1.15; color: var(--ink); }
.fakta { background: #E3F4E8; border-radius: 12px; padding: 0.85rem 1rem; margin: 0.8rem 0; }
.fakta-rubrik { color: var(--gron); font-weight: 700; font-size: 1.1rem; margin: 0 0 0.3rem; }
.fakta-text { color: var(--ink); line-height: 1.5; margin: 0; }
.avgang-text { text-align: center; font-weight: 700; color: var(--ink); margin: 0.8rem 0 0.2rem; }

.st-key-svar button, .st-key-val button {
background: var(--vit); color: var(--ink); border: 2px solid var(--ink); border-radius: 12px;
min-height: 3rem; transition: background 0.12s ease;
}
.st-key-svar button p, .st-key-val button p { font-size: 1.05rem; font-weight: 700; color: inherit; }
.st-key-svar button:hover, .st-key-svar button:focus, .st-key-svar button:active,
.st-key-val button:hover, .st-key-val button:focus, .st-key-val button:active {
background: var(--gul); color: var(--ink); border-color: var(--ink);
}

.resultat { border-radius: 12px; padding: 0.8rem 1rem; font-weight: 700; margin: 0.8rem 0; }
.resultat.ratt { background: #E3F4E8; color: var(--gron); }
.resultat.fel { background: #FBE6E7; color: var(--rod); }
.resultat.info { background: #FFF4D6; color: var(--ink); }
.resultat span { font-weight: 400; color: var(--ink); }

.rubrik { font-size: 1.15rem; font-weight: 700; margin: 1.4rem 0 0.6rem; color: var(--ink); }
.st-key-dpad { max-width: 380px; margin: 0 auto; }
.st-key-dpad [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.5rem; }
.st-key-dpad [data-testid="stColumn"] { flex: 1 1 0 !important; min-width: 0 !important; width: auto !important; }
.st-key-dpad button { width: 100%; min-height: 3.2rem; border-radius: 14px; background: var(--ink); color: var(--gul); border: none; }
.st-key-dpad button p { font-weight: 700; color: inherit; }
.st-key-dpad button:hover, .st-key-dpad button:focus, .st-key-dpad button:active { background: var(--ink-ljus); color: var(--gul); border: none; }
.st-key-dpad button:disabled { background: var(--dimma); color: #7A879B; }
.dpad-mitt { display: flex; justify-content: center; align-items: center; height: 3.2rem; }

.stApp button[kind="primary"], .stApp [data-testid="stBaseButton-primary"] { background: var(--gul); color: var(--ink); border: none; font-weight: 700; }
.stApp button[kind="primary"] p, .stApp [data-testid="stBaseButton-primary"] p { color: var(--ink); }
[data-testid="stSidebar"] { background: var(--vit); }

@media (prefers-reduced-motion: reduce) {
.plan.landar, .plan.lyfter { animation: none; }
.st-key-svar button, .st-key-val button { transition: none; }
}
</style>
"""


def visa_html(html):
    # Tar bort indrag och tomma rader, annars kan Markdown tolka HTML som kod.
    rader = [rad.strip() for rad in html.splitlines() if rad.strip()]
    st.markdown("\n".join(rader), unsafe_allow_html=True)


def plan_svg(farg, bredd=110):
    """Ett flygplan från sidan, med nosen åt höger."""
    fonster = "".join(
        f'<circle cx="{x}" cy="25" r="2.4" fill="#fff"/>' for x in range(40, 92, 8)
    )
    return (
        f'<svg viewBox="0 0 120 48" width="{bredd}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<path d="M12 21 L5 4 L19 4 L34 21 Z" fill="{farg}"/>'
        f'<path d="M12 21 L5 4 L19 4 L34 21 Z" fill="#000" opacity="0.15"/>'
        f'<path d="M8 27 Q8 20 18 20 L92 20 Q111 20 116 27 Q111 34 92 34 L18 34 Q8 34 8 27 Z" fill="{farg}"/>'
        f'<path d="M46 29 L70 29 L57 45 L49 45 Z" fill="{farg}"/>'
        f'<path d="M46 29 L70 29 L57 45 L49 45 Z" fill="#000" opacity="0.25"/>'
        f'<path d="M99 22 Q108 22 112 26 L99 26 Z" fill="#fff"/>'
        f"{fonster}</svg>"
    )


def mitt_plan(bredd=110):
    return plan_svg(FLYGPLAN[st.session_state.plan_farg], bredd)


def rita_tavla():
    ss = st.session_state
    visa_html(
        f"""
        <div class="tavla">
        <div class="tavla-titel">✈️ Stadsäventyret</div>
        <div class="tavla-rad">
        <div><div class="tavla-liten">Du är i ruta</div>
        <div class="tavla-stor">{rutnamn(ss.spelare_x, ss.spelare_y)}</div></div>
        <div class="tavla-hoger"><div class="tavla-liten">Bonuspoäng</div>
        <div class="tavla-stor">{ss.poang}</div></div>
        </div>
        </div>
        """
    )


def rita_scen(rum, planklass):
    fil = rum["fraga"]["bild"]
    uri = bild_data_uri(fil)
    if uri:
        bild = f'<img class="scen-bild" src="{uri}" alt="">'
    else:
        bild = '<div class="scen-saknas">Bilden saknas</div>'
    visa_html(
        f'<div class="scen">{bild}<div class="bana"></div>'
        f'<div class="{planklass}">{mitt_plan()}</div></div>'
    )


def rita_himmel(planklass):
    visa_html(
        f'<div class="scen"><div class="scen-himmel"></div><div class="bana"></div>'
        f'<div class="{planklass}">{mitt_plan()}</div></div>'
    )


def visa_fraga(rum):
    visa_html('<p class="landmark">Var har vi landat?</p>')


def visa_fakta(rum, rubrik):
    fraga = rum["fraga"]
    fakta = fraga.get("fakta", "")
    visa_html(
        f'<div class="fakta"><p class="fakta-rubrik">{rubrik} Du såg '
        f'{fraga["landmark"]} i {fraga["ratt_stad"]}.</p>'
        + (f'<p class="fakta-text">{fakta}</p>' if fakta else "")
        + "</div>"
    )


@st.fragment(run_every=0.25)
def avgangs_klocka():
    """Väntar tills planet har lyft och flyttar sedan spelaren."""
    avgang = st.session_state.avgang
    if avgang and time.time() - avgang["tid"] >= AVGANGSTID:
        genomfor_flytt(avgang["r"])
        st.rerun()


@st.fragment(run_every=0.25)
def fragedel(nyckel):
    """Körs om fyra gånger i sekunden så att tiden kan ta slut av sig själv."""
    rum = st.session_state.rum_data[nyckel]
    if rum["svarat"]:
        return

    nu = time.time()
    if nu < rum["start_tid"]:
        st.progress(1.0, text="✈️ Planet landar …")
        return

    kvar = TIDSGRANS - (nu - rum["start_tid"])
    if kvar <= 0:
        rum["svarat"] = True
        rum["tiden_ute"] = True
        st.rerun()

    visa_fraga(rum)
    st.progress(kvar / TIDSGRANS, text=f"{math.ceil(kvar)} sekunder kvar")

    with st.container(key="svar"):
        for alt in rum["svars_val"]:
            if st.button(alt, key=f"btn_{nyckel}_{alt}", use_container_width=True):
                rum["svarat"] = True
                if alt == rum["fraga"]["ratt_stad"]:
                    rum["ratt_svarat"] = True
                    rum["klarad"] = True
                    rum["valj_beloning"] = True
                st.rerun()


def rita_styrkors(x, y):
    dorrar = st.session_state.labyrint[(x, y)]
    visa_html('<div class="rubrik">Flyg vidare</div>')
    with st.container(key="dpad"):
        rader = [[None, "W", None], ["A", "mitt", "D"], [None, "S", None]]
        for rad in rader:
            kolumner = st.columns(3)
            for kol, r in zip(kolumner, rad):
                with kol:
                    if r == "mitt":
                        visa_html(f'<div class="dpad-mitt">{mitt_plan(64)}</div>')
                    elif r is not None:
                        if st.button(
                            ETIKETTER[r],
                            key=f"dorr_{r}",
                            disabled=r not in dorrar,
                            use_container_width=True,
                        ):
                            flytta(r)


def startskarm():
    ss = st.session_state
    visa_html(
        '<div class="tavla"><div class="tavla-titel">✈️ Stadsäventyret</div>'
        '<div class="tavla-stor">Välj ditt flygplan</div></div>'
    )
    farger = list(FLYGPLAN)
    ss.plan_farg = st.radio(
        "Färg på flygplanet",
        farger,
        index=farger.index(ss.plan_farg),
        horizontal=True,
        label_visibility="collapsed",
    )
    visa_html(f'<div class="hangar">{mitt_plan(240)}</div>')
    visa_html("".join(f'<p class="regler">{stycke}</p>' for stycke in REGLER))
    if st.button("Starta resan", type="primary", use_container_width=True):
        ss.spel_startat = True
        st.rerun()


# ==========================================
# 4. GRÄNSSNITT
# ==========================================
ss = st.session_state
visa_html(CSS)

if "spel_startat" not in ss or "mal" not in ss:
    ss.plan_farg = "Blå"
    ss.spel_startat = False
    nollstall_spel()

with st.sidebar:
    st.header("Så spelar du")
    for stycke in REGLER:
        st.write(stycke)
    if ss.spel_startat:
        st.divider()
        if st.button("Börja om och byt flygplan", type="primary", use_container_width=True):
            nollstall_spel()
            ss.spel_startat = False
            st.rerun()

if not ss.spel_startat:
    startskarm()
    st.stop()

x, y = ss.spelare_x, ss.spelare_y
nyckel = f"{x},{y}"

rita_tavla()

# --- AVGÅNG: planet lyfter från rutan innan det flyger vidare ---
if ss.avgang:
    r = ss.avgang["r"]
    planklass = "plan lyfter vanster" if r == "A" else "plan lyfter"
    with st.container(key="fragekort"):
        if (x, y) == ss.start:
            rita_himmel(planklass)
        else:
            rita_scen(hemta_rum_data(x, y), planklass)
        visa_html(f'<p class="avgang-text">✈️ Vi lyfter mot {VADERSTRECK[r]} …</p>')
    avgangs_klocka()
    st.stop()

# --- MÅL: spelet är slut ---
if (x, y) == ss.mal:
    if not ss.mal_firat:
        st.balloons()
        ss.mal_firat = True
    visa_html(f'<div class="hangar">{mitt_plan(240)}</div>')
    visa_html(
        f'<div class="resultat ratt">🏆 Du hittade ut! '
        f'<span>Du flög från {rutnamn(*ss.start)} till {rutnamn(*ss.mal)} genom '
        f'{len(ss.besokta)} rutor och har {ss.poang} bonuspoäng.</span></div>'
    )
    if st.button("Spela igen", type="primary", use_container_width=True):
        nollstall_spel()
        ss.spel_startat = False
        st.rerun()
    st.stop()

# --- STARTRUTAN: ingen bild och ingen fråga ---
if (x, y) == ss.start:
    animera = ss.landning_nyckel not in (None, nyckel)
    forsta_gangen = ss.landning_nyckel is None
    ss.landning_nyckel = nyckel
    with st.container(key="fragekort"):
        rita_himmel("plan landar" if animera else "plan")
        if forsta_gangen:
            visa_html('<div class="resultat info">Här startar resan. <span>Välj åt vilket håll du vill flyga.</span></div>')
        else:
            visa_html('<div class="resultat info">Här startade du. <span>Flyg vidare!</span></div>')
    rita_styrkors(x, y)
    st.stop()

rum = hemta_rum_data(x, y)

# --- LANDNING: körs bara första gången spelaren kommer in i rummet ---
animera = False
if ss.landning_nyckel != nyckel:
    ss.landning_nyckel = nyckel
    animera = True
    ss.redan_klarad = rum["klarad"]
    if not rum["klarad"]:
        nytt_forsok(rum)

kan_flyga = False
ratt_stad = rum["fraga"]["ratt_stad"]

with st.container(key="fragekort"):
    rita_scen(rum, "plan landar" if animera else "plan")

    if ss.redan_klarad:
        visa_html('<div class="resultat info">Här har du varit. <span>Flyg vidare!</span></div>')
        kan_flyga = True

    elif not rum["svarat"]:
        fragedel(nyckel)

    elif rum["valj_beloning"]:
        visa_fakta(rum, "Rätt!")
        visa_html('<p class="avgang-text">Välj din belöning</p>')
        with st.container(key="val"):
            col_bonus, col_led = st.columns(2)
            with col_bonus:
                if st.button(f"✈️ Flygbonus +{BONUS_POANG}", use_container_width=True):
                    ss.poang += BONUS_POANG
                    rum["valj_beloning"] = False
                    rum["beloning"] = "bonus"
                    st.rerun()
            with col_led:
                if st.button("💡 Ledtråd", use_container_width=True):
                    rum["valj_beloning"] = False
                    rum["beloning"] = "ledtrad"
                    st.rerun()

    else:
        kan_flyga = True
        if rum["ratt_svarat"]:
            visa_fakta(rum, "Rätt!" if rum["beloning"] != "kopt" else "Rätt svar:")
        else:
            visa_fraga(rum)
        if rum["beloning"] == "bonus":
            visa_html(
                f'<div class="resultat ratt">✈️ <span>Du fick {BONUS_POANG} bonuspoäng.</span></div>'
            )
        elif rum["beloning"] == "ledtrad":
            visa_html(
                f'<div class="resultat info">💡 Ledtråd: '
                f'<span>du är cirka {rum["cirka_avstand"]} rutor från utgången.</span></div>'
            )
        elif rum["beloning"] == "kopt":
            visa_html(
                f'<div class="resultat info">💡 Ledtråd: '
                f'<span>du är cirka {rum["cirka_avstand"]} rutor från utgången.</span></div>'
            )
        else:
            fel_text = "Tiden tog slut." if rum["tiden_ute"] else "Fel svar."
            visa_html(f'<div class="resultat fel">{fel_text}</div>')
            if ss.poang >= KOP_PRIS:
                if st.button(
                    f"Köp rätt svar för {KOP_PRIS} poäng",
                    type="primary",
                    use_container_width=True,
                ):
                    ss.poang -= KOP_PRIS
                    rum["ratt_svarat"] = True
                    rum["klarad"] = True
                    rum["beloning"] = "kopt"
                    st.rerun()
            else:
                st.caption(f"Med {KOP_PRIS} bonuspoäng kan du köpa rätt svar nästa gång.")

# --- FLYG VIDARE: visas först när frågan är avklarad ---
if kan_flyga:
    rita_styrkors(x, y)
