#!usr/bin/env python
# coding: utf-8

"""
Controle de tráfego aéreo
Projeto da disciplina de Programação Paralela e Concorrente da Universidade Estadual do Ceará (UECE)
Semestre 2016.2
http://marcial.larces.uece.br/cursos/programacao-concorrente-e-paralela-2016-2/problema-controle-de-trafego-aereo
"""

import threading
from decorators.sync import synchronized
from classes.myThread import MyThread
from classes.track import Track
from random import choice
from time import time, sleep


class Aircraft:
    def __init__(self, _id, _time_created, _local):
        self.id = _id
        self.time_created = _time_created
        self.local = _local
        self.final_time = 0.0

    def __str__(self):
        '''Sobrecarrega print para imprimir os dados do avião'''
        return "<Avião {}> criado no {} aos {:.4f} segundos e removido aos {:.4f}. Tempo total: {:.4f}" \
            .format(self.id,
                    self.local,
                    self.time_created,
                    self.final_time,
                    (self.final_time - self.time_created))

    def status(self, type):
        '''Imprime status da fila'''
        if type == "gerar":
            print("{:.4f}s - <Avião {}> gerado no {} - Fila Ar/Aeroporto [{}]/[{}] - Total Ar/Aeroporto: {}/{}"
                  .format(time() - initial_time,
                          self.id,
                          self.local,
                          len(pista.lista_ar),
                          len(pista.lista_aeroporto),
                          pista.avioes_do_ar,
                          pista.avioes_do_aeroporto))
        elif type == "remover":
            print("{:.4f}s - <Avião {}> removido do {} - Fila Ar/Aeroporto [{}]/[{}] - Total Ar/Aeroporto: {}/{}"
                  .format(time() - initial_time,
                          self.id,
                          self.local,
                          len(pista.lista_ar),
                          len(pista.lista_aeroporto),
                          pista.avioes_do_ar,
                          pista.avioes_do_aeroporto))

    @synchronized
    def verifica_proximo(self):
        '''Verifica se o avião é o próximo a usar a pista. Se não for, entra em espera'''
        if pista.mutex_pista._value > 0:
            # Verifica previamente o valor do mutex para evitar aleatoriedade na escolha
            if pista.lista_ar and pista.lista_ar[-1] == self:  # Verifica se é a sua vez
                tempo = time() - initial_time - self.time_created
                if tempo > 20:
                    # Se avião tiver sido criado a mais de 20 segundos
                    pista.turn.clear()
                    self.pouso()
                    return
                elif len(pista.lista_ar) > len(pista.lista_aeroporto):
                    # Se o número de aviões no ar for maior ou igual aos do aeroporto
                    pista.turn.clear()
                    self.pouso()
                    return
            elif pista.lista_aeroporto and pista.lista_aeroporto[-1] == self:
                if len(pista.lista_ar) <= len(pista.lista_aeroporto):
                    if not pista.lista_ar:
                        # Se não houver aviões no ar
                        pista.turn.clear()
                        self.voo()
                        return
                    elif pista.lista_ar and (time() - initial_time - pista.lista_ar[-1].time_created) < 20:
                        # Se houver mais aviões no aeroporto e nenhum criado a no mínimo 20 segundos no ar
                        pista.turn.clear()
                        self.voo()
                        return

    def pouso(self):
        '''Bloqueia a pista, realiza o pouso e libera a pista'''
        print("-" * 50 + "\n{:.4f}s - <AVIÃO {}> OCUPANDO A PISTA PARA POUSO\n".format(time() - initial_time, self.id) + "-" * 50)

        pista.adquire_pista()
        pista.mutex_ar.acquire()
        self.final_time = (time() - initial_time)
        pista.lista_ar.pop()
        self.status("remover")
        pista.mutex_ar.release()
        sleep(10)
        pista.libera_pista()

        file.write('-' + self.__str__() + '\n')
        print("-" * 50 + "\n{:.4f}s - <AVIÃO {}> LIBEROU A PISTA\n".format(time() - initial_time, self.id) + "-" * 50)

        pista.turn.set()


    def voo(self):
        '''Bloqueia a pista, realiza o voo e libera a pista'''
        print("-" * 50 + "\n{:.4f}s - <AVIÃO {}> OCUPANDO A PISTA PARA VOO\n".format(time() - initial_time, self.id) + "-" * 50)

        pista.adquire_pista()
        pista.mutex_aeroporto.acquire()
        self.final_time = (time() - initial_time)
        pista.lista_aeroporto.pop()
        self.status("remover")
        pista.mutex_aeroporto.release()
        sleep(10)
        pista.libera_pista()

        file.write('-' + self.__str__() + '\n')
        print("-" * 50 + "\n{:.4f}s - <AVIÃO {}> LIBEROU A PISTA\n".format(time() - initial_time, self.id) + "-" * 50)

        pista.turn.set()


def geradora():
    '''Função base da thread de geração de aviões'''
    i = 1
    while pista.avioes_do_aeroporto < 10 or pista.avioes_do_ar < 10:
        if pista.avioes_do_aeroporto < 10 and pista.avioes_do_ar < 10:
            local_do_aviao = choice(["Aeroporto", "Ar"])
        elif pista.avioes_do_aeroporto == 10:
            local_do_aviao = "Ar"
        else:
            local_do_aviao = "Aeroporto"

        if (local_do_aviao == "Aeroporto" and len(pista.lista_aeroporto) < pista.limite_lista) \
                or (local_do_aviao == "Ar"):
            aviao = Aircraft(i, (time() - initial_time), local_do_aviao)
            pista.adiciona_na_lista(aviao)
            nova_thread = MyThread(t_avioes, (aviao,))
            nova_thread.start()
            i += 1
        else:
            file.write("--ERRO-- Fila cheia")
            print("--ERRO-- Fila cheia")
        sleep(8)


def t_avioes(t_aviao):
    '''Função base da thread do avião que o coloca em loop até que seja sua vez'''
    if t_aviao.local == "Aeroporto":
        while t_aviao in pista.lista_aeroporto:
            if not pista.turn.is_set():
                pista.turn.wait()
            t_aviao.verifica_proximo()
    else:
        while t_aviao in pista.lista_ar:
            if not pista.turn.is_set():
                pista.turn.wait()
            t_aviao.verifica_proximo()


initial_time = time()  # Momento em que o programa iniciou
pista = Track()  # Cria pista
pista.turn.set()

file = open("LOG.txt", 'w')  # Cria arquivo de log
file.write("---------- LOG DE EXECUÇÃO ----------\n\n")

thread_geradora = MyThread(geradora, ())  # Instancia thread geradora
thread_geradora.start()  # Inicia thread geradora

while pista.avioes_do_ar < 10 or pista.avioes_do_aeroporto < 10 or len(pista.lista_ar) > 0 or len(pista.lista_aeroporto) > 0:
    pass

print("\n{:.4f}: Fim da execução\n".format(time() - initial_time))
print("Nenhum avião foi derrubado durante o desenvolvimento desse programa")  # Mensagem importante

file.close()  # Fecha arquivo de log
