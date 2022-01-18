'En este script están las operaciones necesarias que se deben hacer a los parámetros de input'

import numpy as np
from input import *


def to_min(hr):
    ''' Función básica que pasa horas a minutos '''
    return int(np.ceil(hr*60)) # mins

def min_to_str(min):
    ''' Función básica que pasa minutos a un string que reporesenta la hora en formato HH:MM '''
    min += INICIO_MIN
    if to_min(INICIO_BREAK_HR) < min:
        min += DURACION_BREAK_MIN
    # Habiendo hecho los cálculos, creamos el string
    strHR = f"{min//60}"
    strMIN = f"{min%60}"
    if len(strHR) == 1:
        strHR = '0' + strHR
    if len(strMIN) == 1:
        strMIN = '0' + strMIN
    return f"{strHR}:{strMIN}"


# Datos del almuerzo:
DURACION_BREAK_HR = FINAL_BREAK_HR - INICIO_BREAK_HR


# Pasamos todo a minutos:
INICIO_MIN = to_min(INICIO_HR)
FINAL_MIN = to_min(FINAL_HR)
DURACION_BREAK_MIN = to_min(DURACION_BREAK_HR)

# CÁLCULOS RELEVANTES: (trasladamos según INICIO_MIN -> minuto 0)
JORNADA_MIN = FINAL_MIN - INICIO_MIN - DURACION_BREAK_MIN # La jornada entera es desde que parte hasta que termina, menos el horario de almuerzo
                                                          # Esta última variable sirve para dar una cota superior de cuánto puede trabajar cada encuestador
AM_PM_MIN = to_min(AM_PM_HR) - INICIO_MIN
# Restamos la hora de almuerzo a AM_PM_MIN si AM_PM_HR ocurre después del almuerzo:
if AM_PM_HR >= FINAL_BREAK_HR:
    AM_PM_MIN -= DURACION_BREAK_MIN
# En el caso de que AM_PM_MIN esté dentro del período de almuerzo, le quitamos una parte
elif AM_PM_HR > INICIO_BREAK_HR and AM_PM_HR < FINAL_BREAK_HR:
    AM_PM_MIN -= to_min(AM_PM_HR - INICIO_BREAK_HR)

TIEMPO_ESPERA_MIN = JORNADA_MIN # Representa el tiempo de espera máximo para ir al siguiente lugar (quedarse esperando hasta que le toque)
