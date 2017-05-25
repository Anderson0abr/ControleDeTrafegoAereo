import threading
from operator import attrgetter

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
        '''Adiciona o avião gerado na respectiva lista'''
        if aviao.local == "Aeroporto":
            self.mutex_aeroporto.acquire()
            self.avioes_do_aeroporto += 1
            self.lista_aeroporto.append(aviao)
            aviao.status("gerar")
            self.lista_aeroporto.sort(key=attrgetter("time_created"), reverse=True)
            self.mutex_aeroporto.release()
        else:
            self.mutex_ar.acquire()
            self.avioes_do_ar += 1
            self.lista_ar.append(aviao)
            aviao.status("gerar")
            self.lista_ar.sort(key=attrgetter("time_created"), reverse=True)
            self.mutex_ar.release()

    def adquire_pista(self):
        '''Bloqueia o mutex da pista'''
        self.mutex_pista.acquire()

    def libera_pista(self):
        '''Libera o mutex da pista'''
        self.mutex_pista.release()