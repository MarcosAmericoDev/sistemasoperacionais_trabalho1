import numpy as np
import matplotlib.pyplot as plt

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
            tempo_atual = processo.chegada
        tempos_espera[i] = tempo_atual - processo.chegada
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

def calcular_metricas(sequencia, espera, retorno, numero_de_processos):

    media_espera = np.mean(espera)
    soma_espera = np.sum(espera)
    media_retorno = np.mean(retorno)
    soma_retorno = np.sum(retorno) 
    vazao = numero_de_processos/np.sum(retorno)

    return {
        'media_espera' : media_espera,
        'soma_espera' : soma_espera,
        'media_retorno' : media_retorno,
        'soma_retorno' : soma_retorno,
        'sequencia_processos': sequencia,
        'vazao': round(vazao, 6)
    }

def generate_process(N, max_chegada=100,max_burst=300):
    processos=[]
    for id in range(1,N+1):
        tempo_chegada = np.random.randint(0,max_chegada)
        tempo_burst = np.random.randint(1,max_burst)
        processos.append(Processo(id,tempo_chegada,tempo_burst))

    return processos

N = 25
processos = generate_process(N)
quantums = [50,100,400]

print("Processos gerados:")
print("ID | Chegada | Burst")
for p in processos:
    print(f"{p.id:3} | {p.chegada:7} | {p.burst_time:5}")


#simular FCFS
fcfs_resultado = fcfs(processos)
fcfs_metricas = calcular_metricas(fcfs_resultado[0], fcfs_resultado[1], fcfs_resultado[2], N)

#simular sjf
sjf_resultado = sjf_nao_preemptivo(processos)
sjf_metricas = calcular_metricas(sjf_resultado[0], sjf_resultado[1], sjf_resultado[2], N)

#simular rr por quantum
rr_metricas = {}
for q in quantums:
    rr_resultado = round_robin(processos,q)
    rr_metricas[q] = calcular_metricas(rr_resultado[0], rr_resultado[1], rr_resultado[2], N)

    
# Exibir resultados
print("\nMétricas:")
print("Algoritmo \t| Avg Waiting (std)\t| Avg Turnaround (std) \t| Throughput \t| Order of Execution")
print(f"FCFS      \t| {fcfs_metricas['media_espera']:.2f}\t (±{fcfs_metricas['soma_espera']:.2f})\t | {fcfs_metricas['media_retorno']:.2f} (±{fcfs_metricas['soma_retorno']:.2f})\t | {fcfs_metricas['vazao']:.4f}\t | {fcfs_metricas['sequencia_processos']}")
print(f"SJF       \t| {sjf_metricas['media_espera']:.2f} \t (±{sjf_metricas['soma_espera']:.2f})\t | {sjf_metricas['media_retorno']:.2f} (±{sjf_metricas['soma_retorno']:.2f})\t | {sjf_metricas['vazao']:2.4f}\t | {sjf_metricas['sequencia_processos']}")
for q in quantums:
    print(f"RR (q={q}) \t| {rr_metricas[q]['media_espera']:.2f}\t (±{rr_metricas[q]['soma_espera']:.2f})\t | {rr_metricas[q]['media_retorno']:.2f} (±{rr_metricas[q]['soma_retorno']:.2f})\t | {rr_metricas[q]['vazao']:2.4f}\t | {rr_metricas[q]['sequencia_processos']}")

metodos = ['FCFS', 'SJF', f'RR(q={quantums[0]})', f'RR(q={quantums[1]})', f'RR(q={quantums[2]})']
tempos = [fcfs_metricas['media_espera'], sjf_metricas['media_espera'], rr_metricas[50]['media_espera'], rr_metricas[100]['media_espera'], rr_metricas[400]['media_espera']]
plt.bar(metodos, tempos, color='skyblue')
plt.xlabel('métodos escolhidos')
plt.ylabel('media tempo de espera')
plt.title('media tempo de espera de cada algoritmo')
for i, value in enumerate(tempos):
    plt.text(i, value, str(value), ha='center')
plt.show()

tempos = [fcfs_metricas['media_retorno'], sjf_metricas['media_retorno'], rr_metricas[50]['media_retorno'], rr_metricas[100]['media_retorno'], rr_metricas[400]['media_retorno']]
plt.bar(metodos, tempos, color='tomato')
plt.xlabel('métodos escolhidos')
plt.ylabel('media tempo de retorno')
plt.title('media tempo de retorno de cada algoritmo')
for i, value in enumerate(tempos):
    plt.text(i, value, str(value), ha='center')
plt.show()

tempos = [fcfs_metricas['vazao'], sjf_metricas['vazao'], rr_metricas[50]['vazao'], rr_metricas[100]['vazao'], rr_metricas[400]['vazao']]
plt.bar(metodos, tempos, color='cyan')
plt.xlabel('métodos escolhidos')
plt.ylabel('vazão')
plt.title('vazão de cada algoritmo')
for i, value in enumerate(tempos):
    plt.text(i, value, str(value), ha='center')
plt.show()