import requests
import pandas as pd
from datetime import date
import os
from datas_inteligentes import gerar_datas_uteis

print("DEBUG: iniciar agente de viagens")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FEEDS = [
    "https://www.azair.eu/rss",
    "https://www.secretflying.com/feed",
    "https://www.traveldealz.com/feed",
    "https://www.holidaypirates.com/feed"
]

hoje = date.today().isoformat()
resultados = []

# ---------------------------
# LER RSS
# ---------------------------
for feed_url in FEEDS:
    try:
        r = requests.get(feed_url, timeout=15)
        r.raise_for_status()

        from xml.etree import ElementTree as ET
        tree = ET.fromstring(r.content)

        for item in tree.findall(".//item"):
            titulo = item.findtext("title", default="Sem título")
            link = item.findtext("link", default="")
            desc = item.findtext("description", default="")

            tipo = "Voo"
            if "hotel" in desc.lower():
                tipo = "Voo + Hotel"

            regime = "Tudo Incluído" if "all inclusive" in desc.lower() else ""

            resultados.append({
                "Data": hoje,
                "Título": titulo,
                "Tipo": tipo,
                "Regime": regime,
                "Link Oferta": link
            })

    except Exception as e:
        print(f"Erro no feed {feed_url}: {e}")

df = pd.DataFrame(resultados).drop_duplicates(subset=["Link Oferta"])

# ---------------------------
# LINKS GOOGLE / SKYSCANNER
# ---------------------------
df["Google Flights"] = "https://www.google.com/flights?hl=pt"
df["Skyscanner"] = "https://www.skyscanner.pt"

# ---------------------------
# GUARDAR FICHEIROS
# ---------------------------
csv_path = f"viagens_{hoje}.csv"
html_path = f"viagens_{hoje}.html"
status_path = "STATUS.txt"

df.to_csv(csv_path, index=False)
df.to_html(html_path, index=False)

status = f"{hoje} — {len(df)} oportunidades de viagem encontradas"
with open(status_path, "w", encoding="utf-8") as f:
    f.write(status)

print(status)

# ---------------------------
# TELEGRAM
# ---------------------------
def enviar_texto(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def enviar_ficheiro(path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": CHAT_ID})

if TOKEN and CHAT_ID:
    resumo = status + "\n\nTop 5:"
    for _, r in df.head(5).iterrows():
        resumo += f"\n- {r['Título']}\n{r['Link Oferta']}\n"

    if len(df) == 0:
        resumo += "\n⚠️ Nenhuma oportunidade hoje."

    enviar_texto(resumo)
    enviar_ficheiro(csv_path)
    enviar_ficheiro(html_path)

    print("Telegram enviado com sucesso")
else:
    print("Telegram secrets não disponíveis")
