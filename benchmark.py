import time
import statistics
from importlib import reload

# Importando os dois sistemas de arquivos
import sistemas_de_arquivos as inode_module
import sistemas_de_arquivos_lista_encadeada as encadeada_module

# Recarregar caso já tenham sido importados antes
reload(inode_module)
reload(encadeada_module)

# Parâmetros de teste
NUM_REPETICOES = 5
TAMANHOS_ARQUIVOS = [1000, 10000, 100000]  # caracteres


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
    tempos_inode_write = benchmark_write(inode_module.FileSystem, tamanho)
    tempos_encadeada_write = benchmark_write(encadeada_module.FileSystem, tamanho)
    resultados[f"escrita_{tamanho}"] = (tempos_inode_write, tempos_encadeada_write)

    tempos_inode_read = benchmark_read(inode_module.FileSystem, tamanho)
    tempos_encadeada_read = benchmark_read(encadeada_module.FileSystem, tamanho)
    resultados[f"leitura_{tamanho}"] = (tempos_inode_read, tempos_encadeada_read)

# Exibir resultados
for chave, (inode_times, encadeada_times) in resultados.items():
    tipo, tamanho = chave.split("_")
    label = f"{tipo.upper()} - {tamanho} caracteres"
    sumarizar_tempos(label, inode_times, encadeada_times)

import matplotlib.pyplot as plt

# Organizar os dados para os gráficos
tipos = ["escrita", "leitura"]
cores = {"inode": "#1f77b4", "encadeada": "#ff7f0e"}

for tipo in tipos:
    tamanhos = []
    medias_inode = []
    desvios_inode = []
    medias_encadeada = []
    desvios_encadeada = []

    for tamanho in TAMANHOS_ARQUIVOS:
        key = f"{tipo}_{tamanho}"
        inode_times, encadeada_times = resultados[key]

        tamanhos.append(tamanho)
        medias_inode.append(statistics.mean(inode_times))
        desvios_inode.append(statistics.stdev(inode_times))
        medias_encadeada.append(statistics.mean(encadeada_times))
        desvios_encadeada.append(statistics.stdev(encadeada_times))

    # Plotar gráfico
    plt.figure(figsize=(10, 6))
    plt.errorbar(tamanhos, medias_inode, yerr=desvios_inode, label="Inode", fmt='-o', capsize=5, color=cores["inode"])
    plt.errorbar(tamanhos, medias_encadeada, yerr=desvios_encadeada, label="Lista Encadeada", fmt='-o', capsize=5, color=cores["encadeada"])

    plt.title(f"Desempenho de {tipo.capitalize()} de Arquivos")
    plt.xlabel("Tamanho do Arquivo (caracteres)")
    plt.ylabel("Tempo (segundos)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
