#!usr/bin/env python
# coding: utf-8

"""
Controle de tráfego aéreo
Projeto da disciplina de Programação Paralela e Concorrente da Universidade Estadual do Ceará (UECE)
Semestre 2016.2
http://marcial.larces.uece.br/cursos/programacao-concorrente-e-paralela-2016-2/problema-controle-de-trafego-aereo
"""

import threading
from random import choice
from time import time, sleep
from operator import attrgetter


class MyThread(threading.Thread):
    def __init__(self, _func, _args):
        threading.Thread.__init__(self)
        self.func = _func
        self.args = _args

    def run(self):
        threading._start_new_thread(self.func, self.args)


class Aircraft:
    turn = threading.Event()

    def __init__(self, _time_created, _local):
        self.time_created = _time_created
        self.local = _local
        self.final_time = 0.0

    def __str__(self):
        return "Avião criado no {} aos {:.4f} segundos e removido aos {:.4f}. Tempo total: {:.4f}".format(self.local,
                                                                                                          self.time_created,
                                                                                                          self.final_time,
                                                                                                          (
                                                                                                          self.final_time - self.time_created))

    def verifica_proximo(self):
        if pista.mutex_pista._value > 0:
            # Verifica previamente o valor do mutex para evitar aleatoriedade na escolha
            if pista.lista_ar and pista.lista_ar[-1] == self:  # Verifica se é a sua vez
                tempo = time() - initial_time - self.time_created
                if tempo >= 20:
                    # Se avião tiver sido criado a 20 segundos ou mais
                    self.pouso()
                    return
                elif len(pista.lista_ar) >= len(pista.lista_aeroporto):
                    # Se o número de aviões no ar for maior ou igual aos do aeroporto
                    self.pouso()
                    return
            elif pista.lista_aeroporto and pista.lista_aeroporto[-1] == self:
                if len(pista.lista_ar) < len(pista.lista_aeroporto):
                    if not pista.lista_ar:
                        # Se não houver aviões no ar
                        self.voo()
                        return
                    elif pista.lista_ar and (time() - initial_time - pista.lista_ar[-1].time_created) < 20:
                        # Se houver mais aviões no aeroporto e nenhum criado a no mínimo 20 segundos no ar
                        self.voo()
                        return
            else:
                self.turn.clear()
                self.turn.wait()
        else:
            self.turn.clear()
            self.turn.wait()

    def pouso(self):
        pista.adquire_pista()
        print("-----------------------------------\n{:.4f} - PISTA DE POUSO OCUPADA\n-----------------------------------".format(time() - initial_time))
        pista.mutex_ar.acquire()
        self.final_time = (time() - initial_time)
        file.write('-' + self.__str__() + '\n')
        pista.lista_ar.pop()
        print("{:.4f} - Removido do Ar - Fila Ar/Aeroporto [{}]/[{}] - Total Ar/Aeroporto: {}/{}".format(time() - initial_time,
                                                                                                len(pista.lista_ar),
                                                                                                len(
                                                                                                    pista.lista_aeroporto),
                                                                                                pista.avioes_do_ar,
                                                                                                pista.avioes_do_aeroporto))
        pista.mutex_ar.release()
        sleep(10)
        print("-----------------------------------\n{:.4f} - PISTA DE POUSO LIBERADA\n-----------------------------------".format(time() - initial_time))
        pista.libera_pista()
        self.turn.set()

    def voo(self):
        pista.adquire_pista()
        print("-----------------------------------\n{:.4f} - PISTA DE VOO OCUPADA\n-----------------------------------".format(time() - initial_time))
        pista.mutex_aeroporto.acquire()
        self.final_time = (time() - initial_time)
        file.write('-' + self.__str__() + '\n')
        pista.lista_aeroporto.pop()
        print("{:.4f} - Removido do Aeroporto - Fila Ar/Aeroporto [{}]/[{}] - Total Ar/Aeroporto: {}/{}".format(
            time() - initial_time, len(pista.lista_ar),
            len(pista.lista_aeroporto), pista.avioes_do_ar,
            pista.avioes_do_aeroporto))
        pista.mutex_aeroporto.release()
        sleep(10)
        print("-----------------------------------\n{:.4f} - PISTA DE VOO LIBERADA\n-----------------------------------".format(time() - initial_time))
        pista.libera_pista()
        self.turn.set()


class Track:
    mutex_aeroporto = threading.Semaphore(1)
    mutex_ar = threading.Semaphore(1)
    mutex_pista = threading.Semaphore(1)

    def __init__(self):
        self.avioes_do_aeroporto = 0  # Número de aviões criados no aeroportp
        self.avioes_do_ar = 0  # Número de aviões criados no ar
        self.lista_aeroporto = []  # Fila de aviões no aeroporto
        self.lista_ar = []  # Fila de aviões no ar
        self.limite_lista = 4  # Limite de aviões na fila

    def adiciona_na_lista(self, aviao):
        if aviao.local == "Aeroporto":
            self.mutex_aeroporto.acquire()
            self.avioes_do_aeroporto += 1
            self.lista_aeroporto.append(aviao)
            print(
                "{:.4f} - Gerado no Aeroporto - Ar[{}] Aeroporto[{}] Total Ar/Aeroporto: {}/{}".format(
                    time() - initial_time, len(pista.lista_ar),
                    len(pista.lista_aeroporto),
                    pista.avioes_do_ar,
                    pista.avioes_do_aeroporto))
            self.lista_aeroporto.sort(key=attrgetter("time_created"), reverse=True)
            self.mutex_aeroporto.release()
        else:
            self.mutex_ar.acquire()
            self.avioes_do_ar += 1
            self.lista_ar.append(aviao)
            print(
                "{:.4f} - Gerado no Ar - Fila Ar/Aeroporto [{}]/[{}] - Total Ar/Aeroporto: {}/{}".format(time() - initial_time,
                                                                                                len(pista.lista_ar),
                                                                                                len(
                                                                                                    pista.lista_aeroporto),
                                                                                                pista.avioes_do_ar,
                                                                                                pista.avioes_do_aeroporto))

            self.lista_ar.sort(key=attrgetter("time_created"), reverse=True)
            self.mutex_ar.release()

    def adquire_pista(self):
        self.mutex_pista.acquire()

    def libera_pista(self):
        self.mutex_pista.release()


def geradora():
    while pista.avioes_do_aeroporto < 10 or pista.avioes_do_ar < 10:
        # Gera avião
        if pista.avioes_do_aeroporto < 10 and pista.avioes_do_ar < 10:
            local_do_aviao = choice(["Aeroporto", "Ar"])
        elif pista.avioes_do_aeroporto == 10:
            local_do_aviao = "Ar"
        else:
            local_do_aviao = "Aeroporto"

        if (local_do_aviao == "Aeroporto" and len(pista.lista_aeroporto) < pista.limite_lista) \
                or (local_do_aviao == "Ar" and len(pista.lista_ar) < pista.limite_lista):
            aviao = Aircraft((time() - initial_time), local_do_aviao)
            pista.adiciona_na_lista(aviao)
            nova_thread = MyThread(t_avioes, (aviao,))
            nova_thread.start()
        else:
            file.write("--ERRO-- Fila cheia\n")
            print("--ERRO-- Fila cheia")
        sleep(8)


def t_avioes(t_aviao):
    if t_aviao.local == "Aeroporto":
        while t_aviao in pista.lista_aeroporto:
            t_aviao.verifica_proximo()
    else:
        while t_aviao in pista.lista_ar:
            t_aviao.verifica_proximo()


initial_time = time()  # Momento em que o programa iniciou
pista = Track()  # Cria pista

file = open("LOG.txt", 'w')  # Cria arquivo de log
file.write("---------- LOG DE EXECUÇÃO ----------\n\n")

thread_geradora = MyThread(geradora, ())  # Instancia thread geradora
thread_geradora.start()  # Inicia thread geradora

while pista.avioes_do_aeroporto < 10 or pista.avioes_do_ar < 10 or pista.lista_aeroporto or pista.lista_ar:
    pass

print("{:.4f}: Fim da execução\n".format(time() - initial_time))
print("Nenhum avião foi derrubado durante o desenvolvimento desse programa")  # Mensagem importante

file.close()  # Fecha arquivo de log
