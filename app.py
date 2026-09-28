import random
import time
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. KONFIGURATION OCH SPELINSTÄLLNINGAR
# ==========================================
st.set_page_config(
    page_title="Stadsäventyret 10x10", page_icon="🏙️", layout="centered"
)

STORLEK = 10
MAL_X, MAL_Y = 10, 10

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
BOT_NICKNAMES = ["Bot_Alpha", "Bot_Beta", "Bot_Gamma", "Bot_Delta"]


def nollstall_spel():
    """Nollställer hela spelarens framsteg, position och rum."""
    st.session_state.spelare_x = 1
    st.session_state.spelare_y = 1
    st.session_state.ryggsack = []
    st.session_state.rum_data = {}
    st.session_state.botar = [
        {
            "namn": BOT_NICKNAMES[i],
            "x": random.randint(1, STORLEK),
            "y": random.randint(1, STORLEK),
        }
        for i in range(4)
    ]


# ==========================================
# 2. INITIELISERING AV SESSION STATE
# ==========================================
if "spelare_x" not in st.session_state:
    st.session_state.avatar = "🧙"
    st.session_state.antal_dorrar = 3
    nollstall_spel()


def hemta_rum_data(x, y):
    nyckel = f"{x},{y}"
    if nyckel not in st.session_state.rum_data:
        alla_dir = ["W", "S", "A", "D"]
        oppna = random.sample(
            alla_dir, min(st.session_state.antal_dorrar, len(alla_dir))
        )
        fraga = random.choice(FRAGE_BANK)
        falska = random.sample(fraga["falska_stader"], 4)
        val = falska + [fraga["ratt_stad"]]
        random.shuffle(val)

        beloningar = [
            "💎 Ädelsten",
            "🔑 Guldnyckel",
            "📜 Gammal karta",
            "🏆 Stadsmedalj",
            "⭐ Stjärna",
        ]

        st.session_state.rum_data[nyckel] = {
            "oppna_dorrar": oppna,
            "fraga": fraga,
            "svars_val": val,
            "beloning": random.choice(beloningar),
            "svarat": False,
            "klarad": False,
            "start_tid": None,
        }
    return st.session_state.rum_data[nyckel]


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
# 3. GRÄNSSNITT
# ==========================================
st.title("🏙️ Stadsäventyret 10x10")

# HUVUDBUTTON FÖR ATT STARTA/RESETTA SPELET LÄNGST UPP
col_top1, col_top2 = st.columns([3, 1])
with col_top2:
    if st.button("▶️ Starta om spelet", use_container_width=True):
        nollstall_spel()
        st.rerun()

with st.sidebar:
    st.header("⚙️ Spelinställningar")
    vald_avatar = st.selectbox(
        "Välj din avatar:", list(AVATARER.keys()), index=0
    )
    st.session_state.avatar = AVATARER[vald_avatar]

    if st.button("🔄 Nollställ spelet", key="side_reset"):
        nollstall_spel()
        st.rerun()

    st.divider()
    st.subheader("🎒 Din Ryggsäck")
    if st.session_state.ryggsack:
        for item in st.session_state.ryggsack:
            st.write(f"- {item}")
    else:
        st.write("*Ryggsäcken är tom*")

current_nyckel = f"{st.session_state.spelare_x},{st.session_state.spelare_y}"
rum = hemta_rum_data(st.session_state.spelare_x, st.session_state.spelare_y)

# RITA KARTAN
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
            bot_har = any(
                b["x"] == x and b["y"] == y for b in st.session_state.botar
            )
            rad += " 🤖 " if bot_har else " ⬜ "
    kart_html += rad + "<br>"
kart_html += "</div>"
st.markdown(kart_html, unsafe_allow_html=True)

st.write(
    f"📍 **Position:** X={st.session_state.spelare_x}, Y={st.session_state.spelare_y}"
)

st.divider()

# FRÅGEMOTOR
st.subheader(f"🏛️ Utmaning: {rum['fraga']['landmark']}")

if not rum.get("svarat", False):
    st.write(
        f"🎁 **Svara rätt inom 8 sekunder för att vinna:** {rum['beloning']}!"
    )

    if rum.get("start_tid") is None:
        rum["start_tid"] = time.time()

    tid_kvar_start = max(0.0, 8.0 - (time.time() - rum["start_tid"]))

    # Live time bar
    timer_code = f"""
    <div style="width: 100%; background-color: #ddd; border-radius: 10px; height: 16px; overflow: hidden; margin-bottom: 12px;">
      <div id="bar" style="width: {(tid_kvar_start/8.0)*100}%; height: 100%; background-color: #ff4b4b; transition: width 0.1s linear;"></div>
    </div>
    <script>
      var timeLeft = {tid_kvar_start};
      var bar = document.getElementById('bar');
      var interval = setInterval(function() {{
        timeLeft -= 0.1;
        if (timeLeft <= 0) {{
          timeLeft = 0;
          clearInterval(interval);
        }}
        bar.style.width = (timeLeft / 8.0 * 100) + '%';
      }}, 100);
    </script>
    """
    components.html(timer_code, height=30)

    for alt in rum["svars_val"]:
        if st.button(alt, key=f"btn_{current_nyckel}_{alt}"):
            tid_anvand = time.time() - rum["start_tid"]
            rum["svarat"] = True

            if tid_anvand <= 8.0 and alt == rum["fraga"]["ratt_stad"]:
                st.success(
                    f"🎉 Rätt svar på {tid_anvand:.1f} s! Du vann **{rum['beloning']}** till ryggsäcken."
                )
                st.session_state.ryggsack.append(rum["beloning"])
                rum["klarad"] = True
            elif tid_anvand > 8.0:
                st.info(
                    f"⏱️ Tiden gick ut ({tid_anvand:.1f} s). Du fick ingen belöning denna gång, men kan gå vidare!"
                )
            else:
                st.info(
                    "❌ Fel svar! Ingen belöning i detta rum, men du kan gå vidare."
                )
            st.rerun()
else:
    if rum.get("klarad", False):
        st.success(
            f"✅ Du har redan klarat detta rum och hämtat din belöning: {rum['beloning']}"
        )
    else:
        st.info(
            "ℹ️ Du har redan testat frågan i detta rum utan att nå belöningen. Välj en dörr nedan för att gå vidare!"
        )

st.divider()

# DÖRRAR / FÖRFLYTTNING
st.subheader("🚪 Öppna dörrar")

col_w, col_a, col_s, col_d = st.columns(4)


def flytta(riktning):
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
            flytta("W")
with col_s:
    if "S" in rum["oppna_dorrar"]:
        if st.button("⬇️ Söder (S)"):
            flytta("S")
with col_a:
    if "A" in rum["oppna_dorrar"]:
        if st.button("⬅️ Väster (A)"):
            flytta("A")
with col_d:
    if "D" in rum["oppna_dorrar"]:
        if st.button("➡️ Öster (D)"):
            flytta("D")
