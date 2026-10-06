import math
import random
import time
import streamlit as st

# Kräver Streamlit 1.37 eller senare (för st.fragment med run_every)

# ==========================================
# 1. KONFIGURATION OCH SPELINSTÄLLNINGAR
# ==========================================
st.set_page_config(
    page_title="Stadsäventyret 10x10", page_icon="🏙️", layout="centered"
)

STORLEK = 10
MAL_X, MAL_Y = 10, 10
TIDSGRANS = 8.0
EXTRA_DORR_ANDEL = 0.25  # andel extra dörrar utöver labyrintens grundgångar

FRAGE_BANK = [
    {"landmark": "Akropolis", "ratt_stad": "Aten",
     "falska_stader": ["Rom", "Istanbul", "Kairo", "Sofia", "Neapel", "Thessaloniki"]},
    {"landmark": "Brandenburger Tor", "ratt_stad": "Berlin",
     "falska_stader": ["München", "Hamburg", "Wien", "Prag", "Warszawa", "Köln"]},
    {"landmark": "Marienplatz", "ratt_stad": "München",
     "falska_stader": ["Berlin", "Stuttgart", "Wien", "Salzburg", "Zürich", "Nürnberg"]},
    {"landmark": "Elbphilharmonie", "ratt_stad": "Hamburg",
     "falska_stader": ["Berlin", "Bremen", "Köpenhamn", "Amsterdam", "Hannover", "Kiel"]},
    {"landmark": "Zwinger", "ratt_stad": "Dresden",
     "falska_stader": ["Leipzig", "Berlin", "Prag", "Wien", "Wrocław", "Kraków"]},
    {"landmark": "Atomium", "ratt_stad": "Bryssel",
     "falska_stader": ["Antwerpen", "Amsterdam", "Paris", "Luxemburg", "Gent", "Rotterdam"]},
    {"landmark": "Manneken Pis", "ratt_stad": "Bryssel",
     "falska_stader": ["Amsterdam", "Brygge", "Antwerpen", "Paris", "Köln", "Luxemburg"]},
    {"landmark": "Tower Bridge", "ratt_stad": "London",
     "falska_stader": ["Paris", "Dublin", "Edinburgh", "Amsterdam", "Manchester", "Liverpool"]},
    {"landmark": "Louvren", "ratt_stad": "Paris",
     "falska_stader": ["London", "Rom", "Madrid", "Wien", "Bryssel", "Berlin"]},
    {"landmark": "Vasamuseet", "ratt_stad": "Stockholm",
     "falska_stader": ["Göteborg", "Oslo", "Köpenhamn", "Helsingfors", "Malmö", "Karlskrona"]},
]

AVATARER = {
    "Riddare": "🧙",
    "Ninja": "🥷",
    "Robot": "🤖",
    "Katt": "🐱",
    "Utforskare": "🤠",
}
BOT_NICKNAMES = ["Bot_Alpha", "Bot_Beta", "Bot_Gamma", "Bot_Delta"]

# Riktningar: (dx, dy). Norr = uppåt = minskande y.
RIKTNINGAR = {"W": (0, -1), "S": (0, 1), "A": (-1, 0), "D": (1, 0)}
MOTSATS = {"W": "S", "S": "W", "A": "D", "D": "A"}
RIKTNINGSNAMN = {"A": "⬅️ Väster", "W": "⬆️ Norr", "S": "⬇️ Söder", "D": "➡️ Öster"}
KNAPPORDNING = ["A", "W", "S", "D"]

OBJEKT = {
    "🔦 Lampa": "Lyser upp frågan: ett felaktigt alternativ försvinner.",
    "⛏️ Hacka": "Hacka dig igenom en vägg (används en gång).",
    "🔑 Guldnyckel": "Hoppa över en fråga och få belöningen direkt (används en gång).",
    "📜 Karta": "Visar hela labyrinten på kartan.",
    "🧭 Kompass": "Visar åt vilket håll utgången ligger.",
}


# ==========================================
# 2. LABYRINT, FRÅGOR OCH SPELLOGIK
# ==========================================
def i_rutnat(x, y):
    return 1 <= x <= STORLEK and 1 <= y <= STORLEK


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
        st.session_state.fragelek = random.sample(FRAGE_BANK, len(FRAGE_BANK))
    return st.session_state.fragelek.pop()


def nollstall_spel():
    ss = st.session_state
    ss.spelare_x, ss.spelare_y = 1, 1
    ss.ryggsack = []
    ss.rum_data = {}
    ss.fragelek = []
    ss.labyrint = skapa_labyrint()
    ss.besokta = {(1, 1)}
    ss.mal_firat = False

    upptagna = {(1, 1), (MAL_X, MAL_Y)}
    ss.botar = []
    for namn in BOT_NICKNAMES:
        while True:
            pos = (random.randint(1, STORLEK), random.randint(1, STORLEK))
            if pos not in upptagna:
                break
        ss.botar.append({"namn": namn, "x": pos[0], "y": pos[1]})


if "labyrint" not in st.session_state:
    st.session_state.avatar = "🧙"
    nollstall_spel()


def hemta_rum_data(x, y):
    nyckel = f"{x},{y}"
    if nyckel not in st.session_state.rum_data:
        fraga = dra_fraga()
        falska = random.sample(fraga["falska_stader"], 4)
        val = falska + [fraga["ratt_stad"]]
        random.shuffle(val)

        exakt_avstand = abs(MAL_X - x) + abs(MAL_Y - y)
        cirka_avstand = max(1, exakt_avstand + random.choice([-1, 0, 1]))

        st.session_state.rum_data[nyckel] = {
            "fraga": fraga,
            "svars_val": val,
            "lampa_dold": random.choice(falska),  # alternativet lampan tar bort
            "objekt": random.choice(list(OBJEKT)),
            "cirka_avstand": cirka_avstand,
            "svarat": False,
            "ratt_svarat": False,
            "tiden_ute": False,
            "valj_beloning": False,
            "vald_beloning_typ": None,  # 'objekt' eller 'ledtrad'
            "start_tid": None,
        }
    return st.session_state.rum_data[nyckel]


def flytta_botar():
    # Botarna följer labyrintens dörrar och skapar inga rum i bakgrunden.
    for bot in st.session_state.botar:
        dorrar = st.session_state.labyrint[(bot["x"], bot["y"])]
        r = random.choice(sorted(dorrar))
        dx, dy = RIKTNINGAR[r]
        bot["x"] += dx
        bot["y"] += dy


def flytta(r):
    ss = st.session_state
    dx, dy = RIKTNINGAR[r]
    ss.spelare_x += dx
    ss.spelare_y += dy
    ss.besokta.add((ss.spelare_x, ss.spelare_y))
    flytta_botar()
    st.rerun()


def kompass_riktning(x, y):
    dx, dy = MAL_X - x, MAL_Y - y
    if dy > 0 and dx > 0:
        return "sydost"
    if dy > 0 and dx < 0:
        return "sydväst"
    if dy < 0 and dx > 0:
        return "nordost"
    if dy < 0 and dx < 0:
        return "nordväst"
    if dy > 0:
        return "söder"
    if dy < 0:
        return "norr"
    return "öster" if dx > 0 else "väster"


def rita_karta():
    ss = st.session_state
    har_karta = "📜 Karta" in ss.ryggsack
    vagg = "2px solid #3b4a5c"
    oppen = "2px solid transparent"

    celler = []
    for y in range(1, STORLEK + 1):
        for x in range(1, STORLEK + 1):
            pos = (x, y)
            dorrar = ss.labyrint[pos]
            if har_karta or pos in ss.besokta:
                stil = (
                    f"border-top:{oppen if 'W' in dorrar else vagg};"
                    f"border-bottom:{oppen if 'S' in dorrar else vagg};"
                    f"border-left:{oppen if 'A' in dorrar else vagg};"
                    f"border-right:{oppen if 'D' in dorrar else vagg};"
                    f"background:{'#dfe9f5' if pos in ss.besokta else '#b9c6d6'};"
                )
            else:
                stil = "border:2px solid #3b4a5c;background:#3b4a5c;"

            innehall = ""
            if pos == (ss.spelare_x, ss.spelare_y):
                innehall = ss.avatar
            elif any((b["x"], b["y"]) == pos for b in ss.botar):
                innehall = "🤖"
            elif pos == (MAL_X, MAL_Y):
                innehall = "🏆"

            celler.append(
                f'<div style="{stil}box-sizing:border-box;aspect-ratio:1;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:15px;">{innehall}</div>'
            )

    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(10,1fr);'
        'max-width:340px;margin:0 auto 8px;">' + "".join(celler) + "</div>",
        unsafe_allow_html=True,
    )


@st.fragment(run_every=0.25)
def fragedel(nyckel):
    """Körs om fyra gånger i sekunden så att tiden kan ta slut av sig själv."""
    ss = st.session_state
    rum = ss.rum_data[nyckel]
    if rum["svarat"]:
        return

    if rum["start_tid"] is None:
        rum["start_tid"] = time.time()

    kvar = TIDSGRANS - (time.time() - rum["start_tid"])
    if kvar <= 0:
        rum["svarat"] = True
        rum["tiden_ute"] = True
        st.rerun()

    st.progress(kvar / TIDSGRANS, text=f"⏱️ {math.ceil(kvar)} s kvar")

    if "🔑 Guldnyckel" in ss.ryggsack:
        if st.button("🔑 Använd guldnyckeln och hoppa över frågan", key=f"nyckel_{nyckel}"):
            ss.ryggsack.remove("🔑 Guldnyckel")
            rum["svarat"] = True
            rum["ratt_svarat"] = True
            rum["valj_beloning"] = True
            st.rerun()

    alternativ = rum["svars_val"]
    if "🔦 Lampa" in ss.ryggsack:
        alternativ = [a for a in alternativ if a != rum["lampa_dold"]]

    for alt in alternativ:
        if st.button(alt, key=f"btn_{nyckel}_{alt}", use_container_width=True):
            rum["svarat"] = True
            if alt == rum["fraga"]["ratt_stad"]:
                rum["ratt_svarat"] = True
                rum["valj_beloning"] = True
            st.rerun()


# ==========================================
# 3. GRÄNSSNITT
# ==========================================
ss = st.session_state
st.title("🏙️ Stadsäventyret")

if st.button("▶️ Starta om spelet", type="primary"):
    nollstall_spel()
    st.rerun()

with st.sidebar:
    st.header("⚙️ Inställningar")
    vald_avatar = st.selectbox("Välj din avatar:", list(AVATARER.keys()), index=0)
    ss.avatar = AVATARER[vald_avatar]

    st.divider()
    st.subheader("🎒 Din ryggsäck (max 3)")
    if ss.ryggsack:
        for idx, item in enumerate(ss.ryggsack):
            st.write(f"{idx+1}. {item}")
            st.caption(OBJEKT[item])
    else:
        st.write("*Ryggsäcken är tom*")

x, y = ss.spelare_x, ss.spelare_y
nyckel = f"{x},{y}"

# --- MÅL: spelet är slut ---
if (x, y) == (MAL_X, MAL_Y):
    if not ss.mal_firat:
        st.balloons()
        ss.mal_firat = True
    st.success("🎉 MÅL! Du har hittat hela vägen till målrummet! 🏆")
    st.write(f"Du besökte **{len(ss.besokta)}** av {STORLEK * STORLEK} rum.")
    rita_karta()
    st.info("Tryck på **Starta om spelet** för att spela igen.")
    st.stop()

rum = hemta_rum_data(x, y)

# --- BILDVISNING FRÅN BILDER-MAPPEN (oförändrad, punkt 1) ---
ratt_stad = rum["fraga"]["ratt_stad"]
bild_sokvag = f"bilder/{ratt_stad}.png"

try:
    st.image(bild_sokvag, caption=f"Landmärke i {ratt_stad}", width=350)
except Exception:
    st.info(f"🖼️ [Bild saknas i mappen: bilder/{ratt_stad}.png]")

st.subheader(f"📍 Rum ({x}, {y})")

with st.expander("🗺️ Karta", expanded=True):
    rita_karta()

if "🧭 Kompass" in ss.ryggsack:
    st.caption(f"🧭 Kompassen pekar åt **{kompass_riktning(x, y)}**.")

botar_har = [b["namn"] for b in ss.botar if (b["x"], b["y"]) == (x, y)]
if botar_har:
    st.caption(f"🤖 {', '.join(botar_har)} är också i det här rummet.")

st.divider()

# --- FRÅGE- OCH BELÖNINGSMOTOR ---
st.write(f"### 🏛️ Landmärke: {rum['fraga']['landmark']}")

if not rum["svarat"]:
    st.write(f"**Svara rätt inom {int(TIDSGRANS)} sekunder för att få välja en belöning!**")
    fragedel(nyckel)

elif rum["valj_beloning"]:
    st.success("🎉 RÄTT SVAR! Välj din belöning nedan:")
    col_obj, col_led = st.columns(2)

    with col_obj:
        if len(ss.ryggsack) < 3:
            if st.button(f"🎒 Ta objekt: {rum['objekt']}"):
                ss.ryggsack.append(rum["objekt"])
                rum["valj_beloning"] = False
                rum["vald_beloning_typ"] = "objekt"
                st.rerun()
        else:
            slapp = st.selectbox(
                "Ryggsäcken är full. Släpp:", ss.ryggsack, key=f"slapp_{nyckel}"
            )
            if st.button(f"🔄 Byt mot {rum['objekt']}"):
                ss.ryggsack.remove(slapp)
                ss.ryggsack.append(rum["objekt"])
                rum["valj_beloning"] = False
                rum["vald_beloning_typ"] = "objekt"
                st.rerun()
        st.caption(OBJEKT[rum["objekt"]])

    with col_led:
        if st.button("💡 Få en ledtråd"):
            rum["valj_beloning"] = False
            rum["vald_beloning_typ"] = "ledtrad"
            st.rerun()

else:
    if rum["ratt_svarat"]:
        if rum["vald_beloning_typ"] == "objekt":
            st.success(f"🎁 Du har valt objektet: **{rum['objekt']}**")
        elif rum["vald_beloning_typ"] == "ledtrad":
            st.info(f"💡 **LEDTRÅD:** Du är cirka **{rum['cirka_avstand']} rutor** från utgången!")
    elif rum["tiden_ute"]:
        st.info("⏰ Tiden gick ut. Ingen belöning!")
    else:
        st.info("❌ Fel svar. Ingen belöning!")

st.divider()

# --- FÖRFLYTTNING / DÖRRAR ---
st.subheader("🚪 Dörrar")
dorrar = ss.labyrint[(x, y)]

kolumner = st.columns(4)
for kol, r in zip(kolumner, KNAPPORDNING):
    with kol:
        if st.button(
            RIKTNINGSNAMN[r],
            key=f"dorr_{r}",
            disabled=r not in dorrar,
            use_container_width=True,
        ):
            flytta(r)

# --- HACKA: bryt igenom en vägg ---
if "⛏️ Hacka" in ss.ryggsack:
    vaggar = [
        r for r in KNAPPORDNING
        if r not in dorrar and i_rutnat(x + RIKTNINGAR[r][0], y + RIKTNINGAR[r][1])
    ]
    if vaggar:
        with st.expander("⛏️ Använd hackan"):
            vald = st.selectbox(
                "Hacka igenom väggen åt:",
                vaggar,
                format_func=lambda r: RIKTNINGSNAMN[r],
                key=f"hacka_{nyckel}",
            )
            if st.button("Hacka igenom", key=f"hacka_btn_{nyckel}"):
                oppna_dorr(ss.labyrint, x, y, vald)
                ss.ryggsack.remove("⛏️ Hacka")
                st.rerun()
