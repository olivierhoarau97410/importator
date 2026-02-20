"""
IMPORTATOR — Version Streamlit
Réseau sismique PF / Piton de la Fournaise — La Réunion
Données FDSN : http://ws.ipgp.fr
"""
import streamlit as st
from datetime import date, datetime
import requests
import zipfile
import io

import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION PAGE
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IMPORTATOR",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Fond général */
    [data-testid="stAppViewContainer"] { background: #1a1a2e; }
    [data-testid="stSidebar"]          { background: #16213e; }
    /* Titres */
    h1, h2, h3 { color: #4ecdc4; }
    /* Texte général */
    p, label, .stMarkdown { color: #cccccc; }
    /* Bouton principal */
    .stButton > button {
        background: #ff6b6b; color: #000; font-weight: bold;
        border: none; border-radius: 6px; padding: 0.6em 1.4em;
    }
    .stButton > button:hover { background: #ff8e8e; }
    /* Selectbox / number_input */
    .stSelectbox > div, .stNumberInput > div { color: #fff; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  DONNÉES GÉOGRAPHIQUES — CONTOUR GADM 4.1
# ─────────────────────────────────────────────────────────────
REUNION_CONTOUR = [
    (55.5876,-21.3735),(55.5854,-21.3721),(55.5762,-21.376),(55.5696,-21.3762),(55.5635,-21.3729),(55.5546,-21.3721),(55.5504,-21.3751),(55.549,-21.3738),(55.5496,-21.3713),(55.5457,-21.3679),(55.5426,-21.3688),(55.5371,-21.3638),(55.5246,-21.3624),(55.5024,-21.3515),(55.4885,-21.351),(55.4863,-21.3515),(55.4863,-21.3529),(55.4835,-21.3529),(55.4832,-21.3501),(55.4785,-21.3482),(55.4793,-21.3449),(55.4782,-21.3465),(55.4751,-21.3468),(55.474,-21.3446),(55.4696,-21.3449),(55.4599,-21.3418),(55.4538,-21.3354),(55.454,-21.3312),(55.4499,-21.3288),(55.4296,-21.3268),(55.4249,-21.3249),(55.414,-21.3182),(55.4085,-21.3082),(55.3993,-21.2999),(55.3971,-21.296),(55.3921,-21.2932),(55.3812,-21.2888),(55.361,-21.2835),(55.3385,-21.281),(55.331,-21.2732),(55.3343,-21.2693),(55.3315,-21.2651),(55.3324,-21.2624),(55.3299,-21.2571),(55.3235,-21.2529),(55.3199,-21.2524),(55.321,-21.251),(55.3199,-21.2479),(55.3132,-21.2451),(55.3071,-21.2371),(55.3021,-21.2371),(55.2929,-21.2307),(55.2918,-21.2235),(55.2885,-21.2199),(55.2849,-21.2074),(55.2804,-21.2049),(55.2801,-21.2032),(55.2829,-21.1996),(55.2826,-21.1965),(55.2843,-21.196),(55.2871,-21.184),(55.2865,-21.1724),(55.2849,-21.1688),(55.2865,-21.1607),(55.2807,-21.1532),(55.2713,-21.1499),(55.2704,-21.1318),(55.2671,-21.1307),(55.2663,-21.1274),(55.2624,-21.1265),(55.259,-21.1196),(55.2524,-21.114),(55.254,-21.1101),(55.2479,-21.1065),(55.2457,-21.1024),(55.2313,-21.0924),(55.2265,-21.0843),(55.2212,-21.079),(55.2215,-21.0543),(55.224,-21.0535),(55.2185,-21.0462),(55.2163,-21.0401),(55.2165,-21.0354),(55.2188,-21.0354),(55.221,-21.0315),(55.2251,-21.0293),(55.2249,-21.0263),(55.2274,-21.0265),(55.2329,-21.0185),(55.2376,-21.0168),(55.2399,-21.019),(55.251,-21.0185),(55.2701,-21.0076),(55.2782,-20.9985),(55.2826,-20.9754),(55.2765,-20.9574),(55.2804,-20.9504),(55.2821,-20.939),(55.2851,-20.9376),(55.2863,-20.939),(55.2849,-20.9396),(55.2868,-20.9401),(55.2879,-20.9376),(55.2868,-20.9357),(55.2837,-20.936),(55.2835,-20.9263),(55.2885,-20.9249),(55.2901,-20.9271),(55.2971,-20.9271),(55.3013,-20.9301),(55.3093,-20.931),(55.3121,-20.929),(55.319,-20.9279),(55.3199,-20.9307),(55.3151,-20.9326),(55.3224,-20.9321),(55.3243,-20.9335),(55.3218,-20.9263),(55.3237,-20.9282),(55.331,-20.9279),(55.3429,-20.9232),(55.3482,-20.9185),(55.3512,-20.9124),(55.3615,-20.9076),(55.3676,-20.8993),(55.3749,-20.8968),(55.3799,-20.8915),(55.3871,-20.8896),(55.3937,-20.8824),(55.4226,-20.8743),(55.4399,-20.8765),(55.4482,-20.8718),(55.4532,-20.8724),(55.4574,-20.8768),(55.4693,-20.884),(55.4865,-20.886),(55.5035,-20.8818),(55.5479,-20.8951),(55.5601,-20.8907),(55.5743,-20.8929),(55.5804,-20.8971),(55.5938,-20.8957),(55.6215,-20.911),(55.6299,-20.9096),(55.6318,-20.9115),(55.6371,-20.9112),(55.6457,-20.9137),(55.666,-20.9254),(55.6718,-20.9343),(55.6838,-20.9449),(55.6918,-20.9587),(55.6965,-20.964),(55.7015,-20.9801),(55.7001,-20.9865),(55.7032,-21.0174),(55.7062,-21.0187),(55.7062,-21.0249),(55.7085,-21.0279),(55.7185,-21.0307),(55.7235,-21.036),(55.7274,-21.046),(55.7321,-21.0471),(55.7315,-21.0485),(55.7326,-21.0471),(55.7343,-21.0479),(55.7343,-21.0513),(55.7313,-21.054),(55.7313,-21.0588),(55.7365,-21.0682),(55.7474,-21.081),(55.7515,-21.0829),(55.7543,-21.0871),(55.7565,-21.0874),(55.7615,-21.0987),(55.7721,-21.1065),(55.7799,-21.1213),(55.7832,-21.1243),(55.7874,-21.1254),(55.7918,-21.1232),(55.7976,-21.1254),(55.8065,-21.1318),(55.8101,-21.1374),(55.8149,-21.139),(55.8179,-21.1382),(55.8276,-21.1437),(55.8279,-21.1518),(55.8304,-21.1535),(55.8321,-21.1582),(55.8351,-21.159),(55.836,-21.161),(55.8338,-21.1663),(55.8338,-21.1724),(55.8374,-21.1838),(55.8324,-21.1868),(55.8251,-21.186),(55.8249,-21.1935),(55.8271,-21.1957),(55.8249,-21.2051),(55.8221,-21.2082),(55.8182,-21.2096),(55.8143,-21.2143),(55.8138,-21.2199),(55.8085,-21.2288),(55.8088,-21.2351),(55.8074,-21.2412),(55.8054,-21.2429),(55.8054,-21.2504),(55.8021,-21.261),(55.8046,-21.2721),(55.8029,-21.2826),(55.8068,-21.2921),(55.8043,-21.3088),(55.8049,-21.3165),(55.8093,-21.3335),(55.8082,-21.3374),(55.8013,-21.3449),(55.7979,-21.351),(55.7896,-21.3546),(55.7815,-21.3621),(55.7713,-21.366),(55.7554,-21.3638),(55.7518,-21.3682),(55.741,-21.3699),(55.7335,-21.3693),(55.7179,-21.3757),(55.7107,-21.3768),(55.6815,-21.3754),(55.679,-21.376),(55.6782,-21.3796),(55.676,-21.3799),(55.6724,-21.3838),(55.659,-21.3829),(55.6479,-21.3899),(55.6435,-21.3885),(55.6418,-21.3843),(55.6368,-21.3829),(55.6235,-21.3832),(55.6193,-21.3865),(55.6087,-21.3876),(55.6026,-21.3846),(55.5985,-21.3793),(55.589,-21.376),(55.5876,-21.3735),
]

# ─────────────────────────────────────────────────────────────
#  STATIONS — réseau PF, coordonnées GPS
# ─────────────────────────────────────────────────────────────
STATIONS_COORDS = {
    "ADV": (-21.06, 55.47), "BLE": (-21.16, 55.56), "BOB": (-21.18, 55.71),
    "BON": (-21.24, 55.71), "BOR": (-21.25, 55.71), "C98": (-21.20, 55.74),
    "CAM": (-20.93, 55.65), "CAS": (-21.18, 55.83), "CIL": (-21.13, 55.47),
    "CPR": (-21.05, 55.47), "CRA": (-21.22, 55.76), "CSS": (-21.25, 55.68),
    "DOD": (-20.98, 55.39), "DSM": (-21.20, 55.73), "DSO": (-21.25, 55.71),
    "ENO": (-21.24, 55.70), "EOL": (-21.27, 55.67), "FEU": (-21.33, 55.80),
    "FJS": (-21.23, 55.72), "FLR": (-21.19, 55.74), "FOR": (-21.26, 55.72),
    "FRE": (-21.20, 55.70), "GBS": (-21.27, 55.78), "GPN": (-21.24, 55.75),
    "GPS": (-21.27, 55.76), "HDL": (-21.25, 55.79), "HIM": (-21.21, 55.72),
    "LAC": (-21.04, 55.53), "LCR": (-21.34, 55.67), "MAID":(-21.08, 55.38),
    "MAT": (-21.30, 55.45), "MVL": (-21.06, 55.26), "NSR": (-21.21, 55.72),
    "NTR": (-21.28, 55.74), "OBS": (-21.21, 55.57), "PBR": (-21.22, 55.65),
    "PCR": (-21.21, 55.57), "PER": (-21.19, 55.69), "PHR": (-21.25, 55.67),
    "PJR": (-21.23, 55.40), "PRA": (-21.29, 55.71), "PRO": (-20.90, 55.45),
    "PVD": (-21.26, 55.74), "RER": (-21.18, 55.72), "RMR": (-21.26, 55.73),
    "RVA": (-21.25, 55.70), "RVL": (-21.24, 55.71), "RVP": (-20.97, 55.49),
    "SFR": (-21.28, 55.77), "SNE": (-21.24, 55.72), "TEO": (-21.35, 55.71),
    "TKR": (-21.31, 55.76), "TTR": (-21.19, 55.78), "TXR": (-21.19, 55.64),
    "VIL": (-21.04, 55.72),
}
ALL_STATIONS = sorted(STATIONS_COORDS.keys())

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
if "selected_stations" not in st.session_state:
    st.session_state.selected_stations = set()
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────────────────────
#  CARTE PLOTLY (mise en cache pour ne pas la reconstruire à chaque rerun)
# ─────────────────────────────────────────────────────────────
@st.cache_data
def build_island_trace():
    """Trace du contour de l'île — ne change jamais."""
    lons = [pt[0] for pt in REUNION_CONTOUR]
    lats = [pt[1] for pt in REUNION_CONTOUR]
    return go.Scattermap(
        lon=lons, lat=lats,
        mode="lines",
        line=dict(color="#c8e6c9", width=1.5),
        fill="toself",
        fillcolor="rgba(74,124,89,0.55)",
        name="La Réunion",
        hoverinfo="skip",
    )


def build_station_trace(selected: set):
    """Trace des marqueurs stations — recontruit à chaque rerun (couleur dépend sélection)."""
    lats, lons, codes, colors, sizes = [], [], [], [], []
    for code, (lat, lon) in STATIONS_COORDS.items():
        lats.append(lat)
        lons.append(lon)
        codes.append(code)
        if code in selected:
            colors.append("#00e676")
            sizes.append(14)
        else:
            colors.append("#ffffff")
            sizes.append(10)
    return go.Scattermap(
        lon=lons, lat=lats,
        mode="markers+text",
        marker=dict(size=sizes, color=colors, opacity=0.92,
                    sizemode="diameter"),
        text=codes,
        textposition="top right",
        textfont=dict(size=9, color="#ffffff"),
        customdata=codes,
        name="Stations",
        hovertemplate="<b>%{customdata}</b><br>lat %{lat:.4f} lon %{lon:.4f}<extra></extra>",
        selected=dict(marker=dict(color="#ffeb3b", size=16)),
    )


def make_figure(selected: set) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(build_island_trace())
    fig.add_trace(build_station_trace(selected))
    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(lat=-21.13, lon=55.52),
            zoom=9.5,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=540,
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        showlegend=False,
        dragmode="pan",
    )
    return fig

# ─────────────────────────────────────────────────────────────
#  BARRE LATÉRALE — traitée EN PREMIER pour que session_state
#  soit à jour avant le rendu des colonnes et du bouton
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Sélection des stations")
    st.caption("Cochez les stations à télécharger · Les stations sélectionnées s'affichent en vert sur la carte")

    search = st.text_input("Filtrer", placeholder="ex: FJS, BLE…").upper().strip()
    filtered = [s for s in ALL_STATIONS if not search or search in s]

    for sta in filtered:
        checked = sta in st.session_state.selected_stations
        if st.checkbox(sta, value=checked, key=f"cb_{sta}"):
            st.session_state.selected_stations.add(sta)
        else:
            st.session_state.selected_stations.discard(sta)

# ─────────────────────────────────────────────────────────────
#  EN-TÊTE
# ─────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;color:#4ecdc4;margin-bottom:0'>🌋 IMPORTATOR</h1>"
    "<p style='text-align:center;color:#888;margin-top:0'>Réseau sismique PF · Piton de la Fournaise · La Réunion</p>",
    unsafe_allow_html=True,
)
st.divider()

# ─────────────────────────────────────────────────────────────
#  MISE EN PAGE — 2 colonnes : carte | paramètres
# ─────────────────────────────────────────────────────────────
col_map, col_par = st.columns([3, 2], gap="large")

# ══════════════════════════════════════════════════════════════
#  COLONNE CARTE
# ══════════════════════════════════════════════════════════════
with col_map:
    st.markdown("#### Carte des stations — réseau PF, La Réunion")
    st.caption("🗺 Visualisation des stations · Les stations sélectionnées apparaissent en vert · Sélection via le panneau gauche ☰")

    fig = make_figure(st.session_state.selected_stations)
    st.plotly_chart(
        fig,
        key="station_map",
        use_container_width=True,
    )

    # Résumé sélection
    n = len(st.session_state.selected_stations)
    if n == 0:
        st.info("Aucune station sélectionnée — cochez les stations dans le panneau ☰ à gauche.")
    else:
        sel_sorted = sorted(st.session_state.selected_stations)
        st.success(f"**{n} station(s) sélectionnée(s) :** {', '.join(sel_sorted)}")

    st.warning(
        "⚠️ Plus le nombre de stations et la durée sont élevés, "
        "plus les fichiers seront volumineux et le téléchargement long.",
        icon=None,
    )

# ══════════════════════════════════════════════════════════════
#  COLONNE PARAMÈTRES
# ══════════════════════════════════════════════════════════════
with col_par:
    st.markdown("#### Paramètres de téléchargement")

    # ── Date
    st.markdown("**Date de début (UTC)**")
    chosen_date = st.date_input(
        "Date",
        value=date.today(),
        min_value=date(2010, 1, 1),
        max_value=date(2030, 12, 31),
        label_visibility="collapsed",
    )

    # ── Heure
    st.markdown("**Heure de début (UTC)**")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        hh = st.number_input("Heure",   min_value=0, max_value=23, value=0, step=1, label_visibility="visible")
    with tc2:
        mm = st.number_input("Minutes", min_value=0, max_value=59, value=0, step=1, label_visibility="visible")
    with tc3:
        ss = st.number_input("Secondes",min_value=0, max_value=59, value=0, step=1, label_visibility="visible")

    # ── Durée
    st.markdown("**Durée (secondes)**")
    st.caption("ex : 300 = 5 min · 3600 = 1 h · 86400 = 24 h")
    duree = st.number_input(
        "Durée en secondes",
        min_value=1,
        max_value=604800,
        value=300,
        step=1,
        label_visibility="collapsed",
    )

    # ── Composante
    st.markdown("**Composante**")
    comp_label = st.selectbox(
        "Composante",
        options=["3 composantes ZNE", "1 seule, la Z", "1 seule, la N", "1 seule, la E"],
        label_visibility="collapsed",
    )
    comp_map = {
        "3 composantes ZNE": "HH?",
        "1 seule, la Z":     "HHZ",
        "1 seule, la N":     "HHN",
        "1 seule, la E":     "HHE",
    }
    compo = comp_map[comp_label]

    st.divider()

    # ── Récapitulatif
    dt_str = (f"{chosen_date.year}-{chosen_date.month:02d}-{chosen_date.day:02d}"
              f"T{hh:02d}:{mm:02d}:{ss:02d}")
    st.markdown(
        f"**Début :** `{dt_str}`  \n"
        f"**Durée :** `{duree} s`  \n"
        f"**Composante :** `{compo}`  \n"
        f"**Stations :** `{len(st.session_state.selected_stations)}`"
    )

    st.divider()

    # ── Bouton téléchargement
    download_clicked = st.button(
        "🔽 TÉLÉCHARGER",
        type="primary",
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────
#  TÉLÉCHARGEMENT — appels HTTP directs au serveur FDSN IPGP
#  URL : http://ws.ipgp.fr/fdsnws/dataselect/1/query
#  Paramètres : network, station, location, channel, starttime, endtime
#  Le fichier MiniSEED brut est proposé en téléchargement dans le navigateur.
# ─────────────────────────────────────────────────────────────
FDSN_URL = "https://ws.ipgp.fr/fdsnws/dataselect/1/query"

if download_clicked:
    selected_list = sorted(st.session_state.selected_stations)
    if not selected_list:
        st.error("Aucune station sélectionnée !")
    else:
        st.divider()
        st.markdown("### Téléchargement en cours…")

        dt_start  = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        t_start   = dt_start.strftime("%Y-%m-%dT%H:%M:%S")
        dt_end    = datetime.fromtimestamp(dt_start.timestamp() + int(duree))
        t_end     = dt_end.strftime("%Y-%m-%dT%H:%M:%S")
        zip_label = f"PF_{dt_start.strftime('%Y%m%d_%H%M%S')}_{int(duree)}s.zip"

        total        = len(selected_list)
        messages     = []
        ok_stations  = []
        zip_buffer   = io.BytesIO()

        progress_bar = st.progress(0, text="Initialisation…")
        log_area     = st.empty()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, station in enumerate(selected_list, 1):
                progress_bar.progress(i / total, text=f"[{i}/{total}] {station}…")
                try:
                    params = {
                        "network":   "PF",
                        "station":   station,
                        "location":  "00",
                        "channel":   compo,
                        "starttime": t_start,
                        "endtime":   t_end,
                        "format":    "miniseed",
                    }
                    resp = requests.get(FDSN_URL, params=params, timeout=60)

                    if resp.status_code == 204 or len(resp.content) == 0:
                        messages.append(f"⚠️ **{station}** — Aucune donnée disponible")
                    elif resp.status_code == 200:
                        fname = f"{station}_{dt_start.strftime('%Y%m%d_%H%M%S')}.mseed"
                        zf.writestr(fname, resp.content)
                        ok_stations.append(station)
                        messages.append(f"✅ **{station}** — {len(resp.content)//1024} Ko")
                    else:
                        messages.append(f"❌ **{station}** — Erreur HTTP {resp.status_code}")

                except requests.exceptions.Timeout:
                    messages.append(f"❌ **{station}** — Délai dépassé (timeout 60s)")
                except Exception as e:
                    messages.append(f"❌ **{station}** — Erreur : {e}")

                log_area.markdown("\n\n".join(messages))

        progress_bar.progress(1.0, text="Terminé !")

        # ── Fenêtre de confirmation style pop-up ──────────────────────
        if ok_stations:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #0d4f3c, #0d6e4f);
                    border: 2px solid #4ecdc4;
                    border-radius: 14px;
                    padding: 28px 32px;
                    margin: 20px auto;
                    max-width: 680px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
                ">
                    <div style="font-size:2.4em; margin-bottom:8px">✅</div>
                    <div style="font-size:1.3em; font-weight:bold; color:#4ecdc4; margin-bottom:12px">
                        Traces sismiques prêtes
                    </div>
                    <div style="color:#ccc; font-size:0.95em; margin-bottom:6px">
                        <b>{len(ok_stations)}</b> station(s) récupérée(s) :
                        <span style="color:#fff">{', '.join(ok_stations)}</span>
                    </div>
                    <div style="color:#aaa; font-size:0.85em; margin-bottom:16px">
                        Début : <b>{dt_str}</b> &nbsp;·&nbsp; Durée : <b>{duree} s</b>
                        &nbsp;·&nbsp; Composante : <b>{compo}</b>
                    </div>
                    <div style="color:#ffcc66; font-size:0.85em">
                        📦 Cliquez sur le bouton ci-dessous pour télécharger l'archive ZIP
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            zip_buffer.seek(0)
            st.download_button(
                label=f"📦 Télécharger {zip_label}  ({len(ok_stations)} fichier(s) .mseed)",
                data=zip_buffer.getvalue(),
                file_name=zip_label,
                mime="application/zip",
                use_container_width=True,
            )
        else:
            st.warning("Aucune donnée récupérée pour les stations sélectionnées.")

        st.session_state.messages = messages
