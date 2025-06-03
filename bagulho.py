import threading
import time
import random

# Variáveis globais
dogs = 0  # Número de cães na sala
cats = 0  # Número de gatos na sala
state = "vazia"  # Estado da sala (sinal móvel)
mutex = threading.Semaphore(1)  # Para proteger variáveis compartilhadas
room_empty = threading.Semaphore(1)  # Para garantir exclusão mútua entre tipos de animais

# Rotina para um cão querer entrar
def dogWantsToEnter():
    global dogs, cats, state
    with mutex:  # Seção crítica
        if state == "vazia" or state == "cães":  # Se a sala está vazia ou já tem cães
            if state == "vazia":
                room_empty.acquire()  # Bloqueia a sala para outros tipos
                state = "cães"
                print("Sinal móvel: CÃES")
            dogs += 1
            print(f"Cão entrou. Cães: {dogs}, Gatos: {cats}")
        else:  # Se há gatos, espera até que a sala esteja vazia
            print("Cão esperando: sala ocupada por gatos")
    if state == "gatos":
        room_empty.acquire()  # Espera até a sala estar vazia
        with mutex:
            state = "cães"
            print("Sinal móvel: CÃES")
            dogs += 1
            print(f"Cão entrou. Cães: {dogs}, Gatos: {cats}")

# Rotina para um gato querer entrar
def catWantsToEnter():
    global dogs, cats, state
    with mutex:  # Seção crítica
        if state == "vazia" or state == "gatos":  # Se a sala está vazia ou já tem gatos
            if state == "vazia":
                room_empty.acquire()  # Bloqueia a sala para outros tipos
                state = "gatos"
                print("Sinal móvel: GATOS")
            cats += 1
            print(f"Gato entrou. Cães: {dogs}, Gatos: {cats}")
        else:  # Se há cães, espera até que a sala esteja vazia
            print("Gato esperando: sala ocupada por cães")
    if state == "cães":
        room_empty.acquire()  # Espera até a sala estar vazia
        with mutex:
            state = "gatos"
            print("Sinal móvel: GATOS")
            cats += 1
            print(f"Gato entrou. Cães: {dogs}, Gatos: {cats}")

# Rotina para um cão sair
def dogLeaves():
    global dogs, cats, state
    with mutex:  # Seção crítica
        dogs -= 1
        print(f"Cão saiu. Cães: {dogs}, Gatos: {cats}")
        if dogs == 0 and cats == 0:  # Se a sala ficou vazia
            state = "vazia"
            print("Sinal móvel: VAZIA")
            room_empty.release()  # Libera a sala para outros tipos

# Rotina para um gato sair
def catLeaves():
    global dogs, cats, state
    with mutex:  # Seção crítica
        cats -= 1
        print(f"Gato saiu. Cães: {dogs}, Gatos: {cats}")
        if dogs == 0 and cats == 0:  # Se a sala ficou vazia
            state = "vazia"
            print("Sinal móvel: VAZIA")
            room_empty.release()  # Libera a sala para outros tipos

# Função para simular um cão
def dog():
    for _ in range(3):  # Cada cão tenta entrar 3 vezes
        time.sleep(random.uniform(0.1, 1))  # Atraso aleatório
        dogWantsToEnter()
        time.sleep(random.uniform(0.1, 1))  # Fica na sala por um tempo
        dogLeaves()

# Função para simular um gato
def cat():
    for _ in range(3):  # Cada gato tenta entrar 3 vezes
        time.sleep(random.uniform(0.1, 1))  # Atraso aleatório
        catWantsToEnter()
        time.sleep(random.uniform(0.1, 1))  # Fica na sala por um tempo
        catLeaves()

# Criação das threads para simulação
def main():
    dog_threads = [threading.Thread(target=dog) for _ in range(5)]  # 5 cães
    cat_threads = [threading.Thread(target=cat) for _ in range(5)]  # 5 gatos

    # Inicia todas as threads
    for t in dog_threads + cat_threads:
        t.start()

    # Espera todas as threads terminarem
    for t in dog_threads + cat_threads:
        t.join()

if __name__ == "__main__":
    main()