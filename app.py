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
        "landmark": "Akropolis",
        "ratt_stad": "Aten",
        "falska_stader": [
            "Rom",
            "Istanbul",
            "Kairo",
            "Sofia",
            "Neapel",
            "Thessaloniki",
        ],
    },
    {
        "landmark": "Brandenburger Tor",
        "ratt_stad": "Berlin",
        "falska_stader": [
            "München",
            "Hamburg",
            "Wien",
            "Prag",
            "Warszawa",
            "Köln",
        ],
    },
    {
        "landmark": "Marienplatz",
        "ratt_stad": "München",
        "falska_stader": [
            "Berlin",
            "Stuttgart",
            "Wien",
            "Salzburg",
            "Zürich",
            "Nürnberg",
        ],
    },
    {
        "landmark": "Elbphilharmonie",
        "ratt_stad": "Hamburg",
        "falska_stader": [
            "Berlin",
            "Bremen",
            "Köpenhamn",
            "Amsterdam",
            "Hannover",
            "Kiel",
        ],
    },
    {
        "landmark": "Zwinger",
        "ratt_stad": "Dresden",
        "falska_stader": [
            "Leipzig",
            "Berlin",
            "Prag",
            "Wien",
            "Wrocław",
            "Kraków",
        ],
    },
    {
        "landmark": "Atomium",
        "ratt_stad": "Bryssel",
        "falska_stader": [
            "Antwerpen",
            "Amsterdam",
            "Paris",
            "Luxemburg",
            "Gent",
            "Rotterdam",
        ],
    },
    {
        "landmark": "Manneken Pis",
        "ratt_stad": "Bryssel",
        "falska_stader": [
            "Amsterdam",
            "Brygge",
            "Antwerpen",
            "Paris",
            "Köln",
            "Luxemburg",
        ],
    },
    {
        "landmark": "Tower Bridge",
        "ratt_stad": "London",
        "falska_stader": [
            "Paris",
            "Dublin",
            "Edinburgh",
            "Amsterdam",
            "Manchester",
            "Liverpool",
        ],
    },
    {
        "landmark": "Louvren",
        "ratt_stad": "Paris",
        "falska_stader": [
            "London",
            "Rom",
            "Madrid",
            "Wien",
            "Bryssel",
            "Berlin",
        ],
    },
    {
        "landmark": "Vasamuseet",
        "ratt_stad": "Stockholm",
        "falska_stader": [
            "Göteborg",
            "Oslo",
            "Köpenhamn",
            "Helsingfors",
            "Malmö",
            "Karlskrona",
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

        objekt_lista = [
            "🔦 Lampa",
            "⛏️ Hacka",
            "🔑 Guldnyckel",
            "📜 Karta",
            "🧭 Kompass",
        ]

        # Räkna ut faktiskt avstånd (antal rutor) till målet (10,10)
        exakt_avstand = abs(MAL_X - x) + abs(MAL_Y - y)
        # Lägg till en liten slumpmässig avvikelse (-1, 0, eller +1) för "cirka"
        variation = random.choice([-1, 0, 1])
        cirka_avstand = max(1, exakt_avstand + variation)

        st.session_state.rum_data[nyckel] = {
            "oppna_dorrar": oppna,
            "fraga": fraga,
            "svars_val": val,
            "objekt": random.choice(objekt_lista),
            "cirka_avstand": cirka_avstand,
            "svarat": False,
            "ratt_svarat": False,
            "valj_beloning": False,
            "vald_beloning_typ": None,  # 'objekt' eller 'ledtrad'
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
    st.subheader("🎒 Din Ryggsäck (Max 3)")
    if st.session_state.ryggsack:
        for idx, item in enumerate(st.session_state.ryggsack):
            st.write(f"{idx+1}. {item}")
    else:
        st.write("*Ryggsäcken är tom*")

current_nyckel = f"{st.session_state.spelare_x},{st.session_state.spelare_y}"
rum = hemta_rum_data(st.session_state.spelare_x, st.session_state.spelare_y)

if st.session_state.spelare_x == MAL_X and st.session_state.spelare_y == MAL_Y:
    st.balloons()
    st.success("🎉 MÅL! Du har hittat hela vägen till Målrummet! 🏆")

# --- BILDVISNING FRÅN BILDER-MAPPEN ---
ratt_stad = rum["fraga"]["ratt_stad"]
bild_sokvag = f"bilder/{ratt_stad}.png"

try:
    st.image(
        bild_sokvag, caption=f"Landmärke i {ratt_stad}", width=350
    )
except Exception:
    st.info(f"🖼️ [Bild saknas i mappen: bilder/{ratt_stad}.png]")

st.subheader(
    f"📍 Rum ({st.session_state.spelare_x}, {st.session_state.spelare_y})"
)

st.divider()

# --- FRÅGE- OCH BELÖNINGSMOTOR ---
st.write(f"### 🏛️ Landmärke: {rum['fraga']['landmark']}")

if not rum["svarat"]:
    st.write(
        "⏱️ **Svara rätt inom 8 sekunder för att få välja en belöning!**"
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
                rum["ratt_svarat"] = True
                rum["valj_beloning"] = True
            st.rerun()

# Om spelaren svarat rätt – Ge valet mellan Objekt eller Ledtråd
elif rum["valj_beloning"]:
    st.success("🎉 RÄTT SVAR! Välj din belöning nedan:")

    col_obj, col_led = st.columns(2)

    with col_obj:
        if st.button(f"🎒 Ta objekt: {rum['objekt']}"):
            if len(st.session_state.ryggsack) < 3:
                st.session_state.ryggsack.append(rum["objekt"])
                rum["valj_beloning"] = False
                rum["vald_beloning_typ"] = "objekt"
                st.rerun()
            else:
                st.warning(
                    "⚠️ Din ryggsäck är full (max 3 objekt)! Du måste byta eller välja ledtråd."
                )

    with col_led:
        if st.button("💡 Få en Ledtråd"):
            rum["valj_beloning"] = False
            rum["vald_beloning_typ"] = "ledtrad"
            st.rerun()

else:
    if rum["ratt_svarat"]:
        if rum["vald_beloning_typ"] == "objekt":
            st.success(f"🎁 Du har valt objektet: **{rum['objekt']}**")
        elif rum["vald_beloning_typ"] == "ledtrad":
            st.info(
                f"💡 **LEDTRÅD:** Du är cirka **{rum['cirka_avstand']} rutor** från utgången!"
            )
    else:
        st.info("ℹ️ Tiden gick ut eller fel svar angavs. Ingen belöning!")

st.divider()

# --- FÖRFLYTTNING / DÖRRAR ---
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
