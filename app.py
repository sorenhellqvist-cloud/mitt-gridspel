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
    st.session_state.spelare_x = 1
    st.session_state.spelare_y = 1
    st.session_state.ryggsack = []
    st.session_state.rum_data = {}
    st.session_state.botar = [
        {
            "namn": BOT_NICKNAMES[i],
            "avatar": "🤖",
            "x": random.randint(1, STORLEK),
            "y": random.randint(1, STORLEK),
        }
        for i in range(4)
    ]


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
# 2. GRÄNSSNITT
# ==========================================
st.title("🏙️ Stadsäventyret")

col_titel, col_btn = st.columns([2, 1])
with col_btn:
    if st.button("▶️ Starta om spelet", type="primary"):
        nollstall_spel()
        st.rerun()

with st.sidebar:
    st.header("⚙️ Inställningar")
    vald_avatar = st.selectbox(
        "Välj din avatar:", list(AVATARER.keys()), index=0
    )
    st.session_state.avatar = AVATARER[vald_avatar]

    st.divider()
    st.subheader("🎒 Din Ryggsäck")
    if st.session_state.ryggsack:
        for item in st.session_state.ryggsack:
            st.write(f"- {item}")
    else:
        st.write("*Ryggsäcken är tom*")

current_nyckel = f"{st.session_state.spelare_x},{st.session_state.spelare_y}"
rum = hemta_rum_data(st.session_state.spelare_x, st.session_state.spelare_y)

# KAN KOLLA OM MAN ÄR I MÅL
if st.session_state.spelare_x == MAL_X and st.session_state.spelare_y == MAL_Y:
    st.balloons()
    st.success("🎉 MÅL! Du har hittat hela vägen till Målrummet! 🏆")

# --- RUMSFÖNSTER (DET SPELAREN SER) ---
st.subheader(
    f"📍 Rum ({st.session_state.spelare_x}, {st.session_state.spelare_y})"
)

# Finns det andra i rummet?
botar_i_rummet = [
    b
    for b in st.session_state.botar
    if b["x"] == st.session_state.spelare_x
    and b["y"] == st.session_state.spelare_y
]

figurer_html = f"<div style='background-color: #2b2b2b; padding: 20px; border-radius: 12px; text-align: center; font-size: 30px; margin-bottom: 15px; border: 2px solid #444;'>"
figurer_html += (
    f"<span title='Du'> {st.session_state.avatar} </span>"  # Din avatar
)

for b in botar_i_rummet:
    figurer_html += (
        f"<span title='{b['namn']}'> {b['avatar']} </span>"  # Andra avatarer
    )

if st.session_state.spelare_x == MAL_X and st.session_state.spelare_y == MAL_Y:
    figurer_html += " 🏆 "

figurer_html += "</div>"
st.markdown(figurer_html, unsafe_allow_html=True)

if botar_i_rummet:
    namn_lista = ", ".join([b["namn"] for b in botar_i_rummet])
    st.info(f"👥 Du är inte ensam! I detta rum står också: **{namn_lista}**")

st.divider()

# --- FRÅGEMOTOR & UTMANING ---
st.write(f"### 🏛️ Landmärke: {rum['fraga']['landmark']}")

if not rum.get("svarat", False):
    st.write(
        f"🎁 **Svara rätt inom 8 sekunder för att låsa upp:** {rum['beloning']}!"
    )

    if rum.get("start_tid") is None:
        rum["start_tid"] = time.time()

    tid_kvar_start = max(0.0, 8.0 - (time.time() - rum["start_tid"]))

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
                st.success(f"🎉 Rätt svar! Du vann **{rum['beloning']}**!")
                st.session_state.ryggsack.append(rum["beloning"])
                rum["klarad"] = True
            elif tid_anvand > 8.0:
                st.info("⏱️ Tiden gick ut! Ingen belöning i detta rum.")
            else:
                st.info("❌ Fel svar! Ingen belöning i detta rum.")
            st.rerun()
else:
    if rum.get("klarad", False):
        st.success(
            f"✅ Rummet är avklarat! Du plockade upp: {rum['beloning']}"
        )
    else:
        st.info("ℹ️ Du missade belöningen i detta rum.")

st.divider()

# --- FÖRFLYTTNING / DÖRRAR ---
st.subheader("🚪 Öppna dörrar i rummet")

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
