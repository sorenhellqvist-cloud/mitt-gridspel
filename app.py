import random
import time
from datetime import datetime
import streamlit as st

# ==========================================
# 1. KONFIGURATION OCH SPELINSTÄLLNINGAR
# ==========================================
st.set_page_config(
    page_title="Stadsäventyret 10x10", page_icon="🏙️", layout="centered"
)

STORLEK = 10
MAL_X, MAL_Y = 10, 10

# Frågedatabas för städer
FRAGE_BANK = [
    {
        "landmark": "Colosseum",
        "ratt_stad": "Rom",
        "falska_stader": [
            "Paris",
            "Madrid",
            "Aten",
            "Berlin",
            "Lissabon",
            "Prag",
        ],
    },
    {
        "landmark": "Eiffeltornet",
        "ratt_stad": "Paris",
        "falska_stader": [
            "London",
            "Bryssel",
            "Rom",
            "Wien",
            "Amsterdam",
            "Madrid",
        ],
    },
    {
        "landmark": "Big Ben",
        "ratt_stad": "London",
        "falska_stader": [
            "Dublin",
            "Edinburgh",
            "Paris",
            "Berlin",
            "Oslo",
            "Köpenhamn",
        ],
    },
    {
        "landmark": "Frihetsgudinnan",
        "ratt_stad": "New York",
        "falska_stader": [
            "Washington",
            "Los Angeles",
            "Chicago",
            "Toronto",
            "Miami",
            "Boston",
        ],
    },
    {
        "landmark": "Sagrada Família",
        "ratt_stad": "Barcelona",
        "falska_stader": [
            "Madrid",
            "Sevilla",
            "Valencia",
            "Lissabon",
            "Porto",
            "Rom",
        ],
    },
]

AVATARER = {
    "Riddare": "🧙",
    "Ninja": "🥷",
    "Robot": "🤖",
    "Katt": "🐱",
    "Utforskare": "🤠",
}

BOT_NICKNAMES = ["Bot_Alpha", "Bot_Beta", "Bot_Gamma", "Bot_Delta", "Bot_Epsilon"]
BOT_SVAR = [
    "Jag har bråttom!",
    "Letar efter målrummet, hinner inte prata.",
    "Har inte tid nu!",
    "Pip popp... jag måste vidare!",
    "Nej, jag behåller mina grejer.",
]

# ==========================================
# 2. INITIELISERING AV SESSION STATE (MINNE)
# ==========================================
if "spelare_x" not in st.session_state:
    st.session_state.spelare_x = 1
    st.session_state.spelare_y = 1
    st.session_state.forra_x = 1
    st.session_state.forra_y = 1
    st.session_state.avatar = "🧙"
    st.session_state.ryggsack = []
    st.session_state.antal_dorrar = 3
    st.session_state.senaste_midnatt_koll = datetime.now().day

    # Rumstillstånd (Slumpade dörrar, hinder, rummets belöning)
    st.session_state.rum_data = {}
    # Chattmeddelanden för rummen
    st.session_state.chatt_logg = {}
    # Hemliga botar
    st.session_state.botar = [
        {
            "namn": BOT_NICKNAMES[i],
            "x": random.randint(1, STORLEK),
            "y": random.randint(1, STORLEK),
        }
        for i in range(4)
    ]


# Midnattsåterställning (Kollar om ny dag inträtt)
def kolla_midnatt():
    idag = datetime.now().day
    if idag != st.session_state.senaste_midnatt_koll:
        st.session_state.senaste_midnatt_koll = idag
        st.session_state.spelare_x = 1
        st.session_state.spelare_y = 1
        st.session_state.ryggsack = []
        st.session_state.rum_data = {}
        st.warning(
            "🌕 MIDNATT! Klockan har slagit 00:00. Labyrinten har nollställts och du skickas tillbaka till start!"
        )


kolla_midnatt()


# Generera unikt data för ett rum vid första besöket
def hemta_rum_data(x, y):
    nyckel = f"{x},{y}"
    if nyckel not in st.session_state.rum_data:
        # Slumpa 1-4 öppna dörrar
        alla_dir = ["W", "S", "A", "D"]
        oppna = random.sample(
            alla_dir, min(st.session_state.antal_dorrar, len(alla_dir))
        )

        # Slumpa eventuellt hinder
        hinder = random.choice([None, "morkt", "stenmur", None])

        # Slumpa tillgängligt objekt
        objekt = random.choice(["Lampa", "Hacka", None])

        # Slumpa fråga
        fraga = random.choice(FRAGE_BANK)
        falska = random.sample(fraga["falska_stader"], 4)
        val = falska + [fraga["ratt_stad"]]
        random.shuffle(val)

        st.session_state.rum_data[nyckel] = {
            "oppna_dorrar": oppna,
            "hinder": hinder,
            "objekt": objekt,
            "fraga": fraga,
            "svars_val": val,
            "besokt": False,
            "svarat_ratt": False,
            "valdt_ledtrad": False,
        }
    return st.session_state.rum_data[nyckel]


# Flytta botar planlöst
def flytta_botar():
    for bot in st.session_state.botar:
        omrade = hemta_rum_data(bot["x"], bot["y"])
        if omrade["oppna_dorrar"]:
            val = random.choice(omrade["oppna_dorrar"])
            if val == "W" and bot["y"] > 1:
                bot["y"] -= 1
            elif val == "S" and bot["y"] < STORLEK:
                bot["y"] += 1
            elif val == "A" and bot["x"] > 1:
                bot["x"] -= 1
            elif val == "D" and bot["x"] < STORLEK:
                bot["x"] += 1


# ==========================================
# 3. GRÄNSSNITT OCH SPELSKÄRM
# ==========================================
st.title("🏙️ Stadsäventyret 10x10")

# Sidopanel för inställningar
with st.sidebar:
    st.header("⚙️ Spelinställningar")
    vald_avatar = st.selectbox(
        "Välj din avatar:", list(AVATARER.keys()), index=0
    )
    st.session_state.avatar = AVATARER[vald_avatar]

    st.session_state.antal_dorrar = st.slider(
        "Max öppna dörrar per rum:", 1, 4, 3
    )

    st.divider()
    st.subheader("🎒 Din Ryggsäck (Max 3)")
    if st.session_state.ryggsack:
        for item in st.session_state.ryggsack:
            st.write(f"- {item}")
    else:
        st.write("*Ryggsäcken är tom*")

current_nyckel = f"{st.session_state.spelare_x},{st.session_state.spelare_y}"
rum = hemta_rum_data(st.session_state.spelare_x, st.session_state.spelare_y)

# Kontrollera hinder vid entré
if (
    rum["hinder"] == "morkt"
    and "Lampa" not in st.session_state.ryggsack
    and not rum["besokt"]
):
    st.error(
        "🌑 Rummet är kolmörkt! Du behöver en Lampa i ryggsäcken för att gå in. Du tvingas backa!"
    )
    st.session_state.spelare_x = st.session_state.forra_x
    st.session_state.spelare_y = st.session_state.forra_y
    st.rerun()
elif (
    rum["hinder"] == "stenmur"
    and "Hacka" not in st.session_state.ryggsack
    and not rum["besokt"]
):
    st.error(
        "🧱 En stenmur blockerar vägen! Du behöver en Hacka i ryggsäcken för att ta dig igenom. Du tvingas backa!"
    )
    st.session_state.spelare_x = st.session_state.forra_x
    st.session_state.spelare_y = st.session_state.forra_y
    st.rerun()

rum["besokt"] = True

# --- RITA KARTAN ---
st.subheader("🗺️ Kartvy")
kart_html = "<div style='font-family: monospace; line-height: 1.2; font-size: 18px; text-align: center; background: #1e1e1e; padding: 10px; border-radius: 8px; color: white;'>"
for y in range(1, STORLEK + 1):
    rad = ""
    for x in range(1, STORLEK + 1):
        if x == st.session_state.spelare_x and y == st.session_state.spelare_y:
            rad += f" {st.session_state.avatar} "
        elif x == MAL_X and y == MAL_Y:
            rad += " 🏆 "
        else:
            # Kolla om bot står här
            bot_har = any(b["x"] == x and b["y"] == y for b in st.session_state.botar)
            if bot_har:
                rad += " 🤖 "
            else:
                rad += " ⬜ "
    kart_html += rad + "<br>"
kart_html += "</div>"
st.markdown(kart_html, unsafe_allow_html=True)

st.write(
    f"📍 **Position:** X={st.session_state.spelare_x}, Y={st.session_state.spelare_y}"
)

# Vinst-kontroll
if st.session_state.spelare_x == MAL_X and st.session_state.spelare_y == MAL_Y:
    st.balloons()
    st.success(
        f"🎉 GRATTIS! Du hittade hela vägen till målet på ({MAL_X},{MAL_Y})!"
    )

st.divider()

# --- FRÅGEMOTOR OCH BELÖNING ---
st.subheader(f"🏛️ Utmaning: {rum['fraga']['landmark']}")

if not rum["svarat_ratt"]:
    st.write(f"**Vilken stad finns detta landmärke i?** *(8 sekunders timer)*")

    if "start_tid" not in st.session_state:
        st.session_state.start_tid = time.time()

    svar = st.radio(
        "Välj alternativ:",
        rum["svars_val"],
        key=f"q_{current_nyckel}",
        index=None,
    )

    if st.button("Skicka svar"):
        tid_anvand = time.time() - st.session_state.start_tid
        if tid_anvand > 8.0:
            st.error(
                f"⏳ Tiden tog slut! Det tog {tid_anvand:.1f} sekunder. Försök igen nästa gång du kliver in."
            )
        elif svar == rum["fraga"]["ratt_stad"]:
            st.success(f"🎉 Rätt svar på {tid_anvand:.1f} sekunder!")
            rum["svarat_ratt"] = True
            st.rerun()
        else:
            st.error("❌ Fel stad! Försök igen.")
else:
    st.success("✅ Du har klarat frågan i detta rum!")

    col_bel1, col_bel2 = st.columns(2)
    with col_bel1:
        if st.button("💡 Få ledtråd om bästa väg"):
            rum["valdt_ledtrad"] = True
            st.info("💡 LEDTRÅD: Rör dig mot Söder eller Öster för att nå målet!")

    with col_bel2:
        if rum["objekt"]:
            if st.button(f"🎒 Plocka upp {rum['objekt']}"):
                if len(st.session_state.ryggsack) < 3:
                    st.session_state.ryggsack.append(rum["objekt"])
                    st.success(f"Plockade upp {rum['objekt']}!")
                    rum["objekt"] = None
                    st.rerun()
                else:
                    st.warning("Din ryggsäck är full (max 3 objekt)!")

st.divider()

# --- RUMSCHATT & BOT-INTERAKTION ---
botar_i_rummet = [
    b
    for b in st.session_state.botar
    if b["x"] == st.session_state.spelare_x
    and b["y"] == st.session_state.spelare_y
]
figurer_i_rummet = 1 + len(botar_i_rummet)  # Spelare + botar

st.subheader(f"💬 Rumschatt ({figurer_i_rummet}/3 figurer i rummet)")

if botar_i_rummet:
    st.write(
        f"I detta rum står också: {', '.join([b['namn'] for b in botar_i_rummet])}"
    )

if current_nyckel not in st.session_state.chatt_logg:
    st.session_state.chatt_logg[current_nyckel] = []

for msg in st.session_state.chatt_logg[current_nyckel]:
    st.text(msg)

chatt_input = st.text_input(
    "Skriv ett meddelande i rummet:", key=f"chat_{current_nyckel}"
)
if st.button("Skicka meddelande"):
    if chatt_input:
        st.session_state.chatt_logg[current_nyckel].append(
            f"Du: {chatt_input}"
        )
        # Låt en bot svara om någon finns i rummet
        if botar_i_rummet:
            svarande_bot = random.choice(botar_i_rummet)
            st.session_state.chatt_logg[current_nyckel].append(
                f"{svarande_bot['namn']}: {random.choice(BOT_SVAR)}"
            )
        st.rerun()

st.divider()

# --- FÖRFLYTTNING/DÖRRAR ---
st.subheader("🚪 Öppna dörrar")

if figurer_i_rummet > 3:
    st.warning("🔒 Rummet är överfullt! Du måste välja en dörr och gå vidare.")

col_w, col_a, col_s, col_d = st.columns(4)


def flytta_spelare(riktning):
    st.session_state.forra_x = st.session_state.spelare_x
    st.session_state.forra_y = st.session_state.spelare_y

    if riktning == "W" and st.session_state.spelare_y > 1:
        st.session_state.spelare_y -= 1
    elif riktning == "S" and st.session_state.spelare_y < STORLEK:
        st.session_state.spelare_y += 1
    elif riktning == "A" and st.session_state.spelare_x > 1:
        st.session_state.spelare_x -= 1
    elif riktning == "D" and st.session_state.spelare_x < STORLEK:
        st.session_state.spelare_x += 1

    flytta_botar()
    st.rerun()


with col_w:
    if "W" in rum["oppna_dorrar"]:
        if st.button("⬆️ Norr (W)"):
            flytta_spelare("W")

with col_s:
    if "S" in rum["oppna_dorrar"]:
        if st.button("⬇️ Söder (S)"):
            flytta_spelare("S")

with col_a:
    if "A" in rum["oppna_dorrar"]:
        if st.button("⬅️ Väster (A)"):
            flytta_spelare("A")

with col_d:
    if "D" in rum["oppna_dorrar"]:
        if st.button("➡️ Öster (D)"):
            flytta_spelare("D")