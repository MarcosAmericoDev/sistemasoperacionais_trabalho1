class Processo:
    def __init__(self, id, chegada, burst_time):
        self.id = id
        self.chegada = chegada
        self.burst_time = burst_time
        self.tempo_restante = burst_time
        self.tempo_espera = 0
        self.tempo_retorno = 0
        self.tempo_inicio = -1

def fcfs(processos):
    n = len(processos)
    fila_prontos = sorted(processos, key=lambda x: x.chegada)
    tempo_atual = 0
    sequencia_execucao = []
    tempos_espera = [0] * n
    tempos_retorno = [0] * n

    for i in range(n):
        processo = fila_prontos[i]
        if tempo_atual < processo.chegada:
            tempos_espera[i] = processo.chegada - tempo_atual
            tempo_atual = processo.chegada
        tempo_inicio = tempo_atual
        sequencia_execucao.append((processo.id, tempo_inicio, tempo_inicio + processo.burst_time))
        tempo_fim = processo.burst_time + tempo_inicio
        tempos_retorno[i] = tempo_fim - processo.chegada
        tempo_atual = tempo_fim
    
    return sequencia_execucao, tempos_espera, tempos_retorno

def sjf_nao_preemptivo(processos):
    n = len(processos)
    fila_prontos = []
    tempo_atual = 0
    sequencia_execucao = []
    tempos_espera = [0] * n
    tempos_retorno = [0] * n
    processos_restantes = sorted(processos, key=lambda x: x.chegada)
    indice_processo = 0
    processos_concluidos = 0

    while processos_concluidos < n:
        while indice_processo < n and processos_restantes[indice_processo].chegada <=tempo_atual:
            fila_prontos.append(processos_restantes[indice_processo])
            indice_processo += 1

        if not fila_prontos:
            tempo_atual += 1
            continue

        fila_prontos.sort(key=lambda x: x.burst_time)
        processo_atual = fila_prontos.pop(0)

        tempo_inicio = tempo_atual
        sequencia_execucao.append((processo_atual.id, tempo_inicio, tempo_inicio + processo_atual.burst_time))
        tempo_fim = tempo_inicio + processo_atual.burst_time
        tempos_espera[processos.index(processo_atual)] = tempo_inicio - processo_atual.chegada
        tempos_retorno[processos.index(processo_atual)] = tempo_fim - processo_atual.chegada
        tempo_atual = tempo_fim
        processos_concluidos += 1

    return sequencia_execucao, tempos_espera, tempos_retorno