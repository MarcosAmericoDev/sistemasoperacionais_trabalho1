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

def round_robin(processos, quantum):
    n = len(processos)
    fila_prontos = []
    tempo_atual = 0
    sequencia_execucao = []
    tempo_restante = [proc.burst_time for proc in processos]
    tempos_espera = [0] * n
    tempos_retorno = [0] * n
    tempo_inicio = [-1] * n

    #coloca na fila os processos que "já chegaram"
    for i, proc in enumerate(processos):
        if proc.chegada == 0:
            fila_prontos.append(i)

    #caso ainda tenha processos na fila de outros ou, se não tiver processos prontos, mas ainda tiver
    #processos para chegarem, dá seguimento ao loop
    while fila_prontos or any(t > 0 for t in tempo_restante):

        if not fila_prontos:
            tempo_atual += 1
            for i, proc in enumerate(processos):
                if proc.chegada <= tempo_atual and tempo_inicio[i] == -1 and i not in fila_prontos:
                    fila_prontos.append(i)
            continue

        processo_atual_index = fila_prontos.pop(0)
        processo_atual = processos[processo_atual_index]

        if tempo_inicio[processo_atual_index] == -1:
            tempo_inicio[processo_atual_index] = tempo_atual

        #compara qual é o menor valor entre o quantum e o burst_time atual do processo e atualiza o tempo atual
        tempo_executar = min(quantum, tempo_restante[processo_atual_index])
        tempo_atual += tempo_executar

        sequencia_execucao.append((processo_atual.id, tempo_atual - tempo_executar, tempo_atual))
        tempo_restante[processo_atual_index] -= tempo_executar

        tempo_atual += 1 #para fazer a mudança de contexto

        #coloca na fila os processos que chegaram enquanto outro estava executando
        for i, proc in enumerate(processos):
            if proc.chegada <= tempo_atual and tempo_inicio[i] == -1 and i not in fila_prontos and i != processo_atual_index:
                fila_prontos.append(i)

        if tempo_restante[processo_atual_index] > 0:
            fila_prontos.append(processo_atual_index)

        else:
            tempos_retorno[processo_atual_index] = tempo_atual - processo_atual.chegada
            tempos_espera[processo_atual_index] = tempos_retorno[processo_atual_index] - processo_atual.burst_time

    return sequencia_execucao, tempos_espera, tempos_retorno