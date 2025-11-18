from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO import ConsumoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        if self._impianti is None:
            self.load_impianti()

        risultato = []

        for impianto in self._impianti:
            lista_consumi_impianto = impianto.get_consumi()

            if lista_consumi_impianto:
                consumi_del_mese = []
                for consumo_impianto in lista_consumi_impianto:
                    if consumo_impianto.data.month == mese:
                        consumi_del_mese.append(consumo_impianto.kwh)

                if consumi_del_mese:
                    media_kwh = sum(consumi_del_mese) / len(consumi_del_mese)
                    risultato.append((impianto.nome, media_kwh))
                else:
                    risultato.append((impianto.nome, 0))

            else:
                risultato.append((impianto.nome, 0))

        return risultato


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO

        if self.__costo_ottimo == -1:
            self.__costo_ottimo = float('inf')

        impianto_ids = [i.id for i in self._impianti]

        if giorno == 8:
            if costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale[:]
            return

        for impianto_scelto_id in impianto_ids:

            # 1. Calcola il costo totale per la scelta corrente
            kwh_consumo = consumi_settimana[impianto_scelto_id][giorno - 1]

            costo_spostamento = 0.0
            if ultimo_impianto is not None and impianto_scelto_id != ultimo_impianto:
                costo_spostamento = 5.0  # Costo fisso di 5€

            nuovo_costo = costo_corrente + kwh_consumo + costo_spostamento

            if nuovo_costo >= self.__costo_ottimo:
                continue

            self.__ricorsione(
                sequenza_parziale + [impianto_scelto_id],
                giorno + 1,
                impianto_scelto_id,
                nuovo_costo,
                consumi_settimana,
            )


    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        if self._impianti is None:
            self.load_impianti()

        consumi_settimana = {}

        for impianto in self._impianti:
            lista_giornaliera_inizializzata = [0]*7
            consumi_settimana[impianto.id] = lista_giornaliera_inizializzata

        for impianto in self._impianti:
            lista_consumi_impianto = ConsumoDAO.get_consumi(impianto.id)

            if lista_consumi_impianto:
                for consumo in lista_consumi_impianto:
                    giorno_del_mese = consumo.data.day

                    if consumo.data.month == mese and 1<=giorno_del_mese<=7:
                        giorno_indice = giorno_del_mese -1
                        consumi_settimana[impianto.id][giorno_indice] = consumo.kwh

        return consumi_settimana


