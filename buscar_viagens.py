import requests
import pandas as pd
from datetime import date
import os
from datas_inteligentes import gerar_datas_uteis

# -----------------------
# CONFIGURAÇÃO
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

ORIGENS = ["LIS", "OPO"]
FEEDS = [
    "https://www.azair.eu/rss",
    "https://www.secretflying.com/feed",
    "https://www.traveldealz.com/feed",
    "https://www.holidaypirates.com/feed"
]

hoje = date.today().isoformat()
resultados = []

# -----------------------
# PARSE RSS / OFERTAS
# -----------------------
for feed_url in FEEDS:
    try:
        r = requests.get(feed_url, timeout=10)
        r.raise_for_status()
        from xml.etree import ElementTree as ET
        tree = ET.fromstring(r.content)
        for item in tree.findall(".//item"):
            titulo = item.find("title").text if item.find("title") is not None else "Sem título"
            link = item.find("link").text if item.find("link") is not None else ""
            desc = item.find("description").text if item.find("description") is not None else ""
            origem = "LIS/OPO" if any(o in titulo for o in ORIGENS) else "Vários"
            tipo = "Voo+Hotel" if "hotel" in desc.lower() else "Voo"
            ti = "TI" if "all inclusive" in desc.lower() else ""
            resultados.append({
                "Origem": origem,
                "Título": titulo,
                "Tipo": tipo,
                "Regime": ti,
                "Link RSS": link
            })
    except Exception as e:
        print(f"Erro ao ler feed {feed_url}: {e}")

df = pd.DataFrame(resultados).drop_duplicates(subset=["Link RSS"])

# -----------------------
# LINKS GOOGLE FLIGHTS / SKYCANNER
# -----------------------
def gerar_link_google(origem, destino):
    return f"https://www.google.com/flights?hl=pt#flt={origem}.{destino}"

def gerar_link_skyscanner(origem, destino):
    return f"https://www.skyscanner.pt/transport/flights/{origem}/{destino}/"

df["Link Google Flights"] = df["Título"].apply(lambda t: gerar_link_google("LIS", "DESTINO"))
df["Link Skyscanner"] = df["Título"].apply(lambda t: gerar_link_skyscanner("LIS", "DESTINO"))

# -----------------------
# GUARDAR FICHEIROS
# -----------------------
csv_path = f"viagens_{hoje}.csv"
html_path = f"viagens_{hoje}.html"
status_path = "STATUS.txt"

df.to_csv(csv_path, index=False)
df.to_html(html_path, index=False)

status_text = f"{hoje} — {len(df)} oportunidades de viagem encontradas"
open(status_path, "w").write(status_text)
print(status_text)

# -----------------------
# TELEGRAM
# -----------------------
def enviar_texto(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def enviar_ficheiro(path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": CHAT_ID})

if TOKEN and CHAT_ID:
    try:
        # 1️⃣ Mensagem resumo
        resumo = status_text + "\n\nTop 5:"
        for _, row in df.head(5).iterrows():
            resumo += f"\n- {row['Título']}\n  {row['Link RSS']}"
        if len(df) == 0:
            resumo += "\n⚠️ Nenhuma oferta encontrada hoje."
        enviar_texto(resumo)

        # 2️⃣ Enviar CSV
        enviar_ficheiro(csv_path)

        # 3️⃣ Enviar HTML
        enviar_ficheiro(html_path)

        print("Telegram: mensagens e anexos enviados com sucesso")
    except Exception as e:
        print("Erro Telegram:", e)
else:
    print("Secrets do Telegram não disponíveis")
