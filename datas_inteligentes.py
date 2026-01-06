from datetime import date, timedelta
from feriados_pt import FERIADOS_NACIONAIS, FERIADOS_REGIONAIS, FERIAS_ESCOLARES

def gerar_datas_uteis(base=date.today()):
    datas = []

    # fins-de-semana longos: quinta à noite → terça
    for i in range(90):
        d = base + timedelta(days=i)
        if d.weekday() == 3:  # quinta
            datas.append((d, d + timedelta(days=4)))
        elif d.weekday() == 4:  # sexta
            datas.append((d, d + timedelta(days=3)))

    # acrescentar feriados e férias escolares
    # (simplificação: acrescenta datas manualmente, podemos expandir)
    return datas
