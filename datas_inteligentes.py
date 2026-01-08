from datetime import date, timedelta

def gerar_datas_uteis(base=date.today()):
    datas = []

    for i in range(120):
        d = base + timedelta(days=i)

        # Quinta → Terça
        if d.weekday() == 3:
            datas.append((d, d + timedelta(days=4)))

        # Sexta → Segunda
        if d.weekday() == 4:
            datas.append((d, d + timedelta(days=3)))

    return datas
