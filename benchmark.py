import time
import statistics
import random
from importlib import reload

# Importar os dois sistemas de arquivos
import sistemas_de_arquivos as inode_module
import sistemas_de_arquivos_lista_encadeada as encadeada_module

NUM_REPETICOES = 20
TAMANHOS_ARQUIVOS = [1000, 5000, 10000, 15000, 20000, 25000, 30000]

def benchmark_write(fs_class, tamanho):
    tempos = []
    for _ in range(NUM_REPETICOES):
        fs = fs_class()
        fs.touch("arquivo.txt")
        data = "a" * tamanho
        inicio = time.time()
        fs.write("arquivo.txt", data)
        fim = time.time()
        tempos.append(fim - inicio)
    return tempos

def benchmark_read(fs_class, tamanho):
    tempos = []
    for _ in range(NUM_REPETICOES):
        fs = fs_class()
        fs.touch("arquivo.txt")
        data = "a" * tamanho
        fs.write("arquivo.txt", data)
        inicio = time.time()
        fs.read("arquivo.txt")
        fim = time.time()
        tempos.append(fim - inicio)
    return tempos

def benchmark_random_access(fs_class, tamanho):
    tempos = []
    for _ in range(NUM_REPETICOES):
        fs = fs_class()
        fs.touch("arquivo.txt")
        data = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=tamanho))
        fs.write("arquivo.txt", data)

        start = time.time()
        if hasattr(fs, 'current'):
            inode = fs.current.children["arquivo.txt"]
            if hasattr(inode, 'content'):
                _ = inode.content[random.randint(0, tamanho - 1)]
            elif hasattr(inode, 'first_block'):
                idx = inode.first_block
                pos = random.randint(0, tamanho - 1)
                count = 0
                while idx is not None:
                    bloco = fs.disk[idx]
                    if count + len(bloco.data) > pos:
                        _ = bloco.data[pos - count]
                        break
                    count += len(bloco.data)
                    idx = bloco.next
        end = time.time()
        tempos.append(end - start)
    return tempos

def benchmark_mv(fs_class):
    tempos = []
    for _ in range(NUM_REPETICOES):
        fs = fs_class()
        fs.mkdir("dir1")
        fs.touch("arquivo.txt")
        inicio = time.time()
        fs.mv("arquivo.txt", "dir1")
        fim = time.time()
        tempos.append(fim - inicio)
    return tempos

def sumarizar_tempos(label, tempos_inode, tempos_encadeada):
    def resumo(nome, tempos):
        media = statistics.mean(tempos)
        desvio = statistics.stdev(tempos)
        return f"{nome}: Média = {media:.6f}s | Desvio = {desvio:.6f}s"

    print(f"\n🔧 {label}")
    print(resumo("Inode     ", tempos_inode))
    print(resumo("Encadeada ", tempos_encadeada))


# Executar benchmarks
resultados = {}

for tamanho in TAMANHOS_ARQUIVOS:
    resultados[f"escrita_{tamanho}"] = (
        benchmark_write(inode_module.FileSystem, tamanho),
        benchmark_write(encadeada_module.FileSystem, tamanho)
    )
    resultados[f"leitura_{tamanho}"] = (
        benchmark_read(inode_module.FileSystem, tamanho),
        benchmark_read(encadeada_module.FileSystem, tamanho)
    )
    resultados[f"aleatorio_{tamanho}"] = (
        benchmark_random_access(inode_module.FileSystem, tamanho),
        benchmark_random_access(encadeada_module.FileSystem, tamanho)
    )

# Movimentação de arquivos
resultados["mv"] = (
    benchmark_mv(inode_module.FileSystem),
    benchmark_mv(encadeada_module.FileSystem)
)

# Exibir resultados
for chave, (inode_times, encadeada_times) in resultados.items():
    tipo, *resto = chave.split("_")
    label = f"{tipo.upper()} - {resto[0]} caracteres" if resto else f"{tipo.upper()}"
    sumarizar_tempos(label, inode_times, encadeada_times)

# Gráficos
import matplotlib.pyplot as plt

def plot_resultados(tipos):
    for tipo in tipos:
        tamanhos = []
        medias_inode = []
        desvios_inode = []
        medias_encadeada = []
        desvios_encadeada = []

        for tamanho in TAMANHOS_ARQUIVOS:
            key = f"{tipo}_{tamanho}"
            if key not in resultados:
                continue
            inode_times, encadeada_times = resultados[key]

            tamanhos.append(tamanho)
            medias_inode.append(statistics.mean(inode_times))
            desvios_inode.append(statistics.stdev(inode_times))
            medias_encadeada.append(statistics.mean(encadeada_times))
            desvios_encadeada.append(statistics.stdev(encadeada_times))

        plt.figure(figsize=(10, 6))
        plt.errorbar(tamanhos, medias_inode, yerr=desvios_inode, label="Inode", fmt='-o', capsize=5)
        plt.errorbar(tamanhos, medias_encadeada, yerr=desvios_encadeada, label="Lista Encadeada", fmt='-o', capsize=5)
        plt.title(f"Desempenho de {tipo.capitalize()} de Arquivos")
        plt.xlabel("Tamanho do Arquivo (caracteres)")
        plt.ylabel("Tempo (segundos)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

plot_resultados(["escrita", "leitura", "aleatorio"])
