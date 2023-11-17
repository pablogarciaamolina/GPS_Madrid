from typing import Dict, List, Tuple
import math
import os

BOLD = '\033[1m'
ALPHA = '\033[7m'
GREEN = '\033[38;2;85;206;88m'
UNDERLINE = '\033[4m'
END="\033[m"


def _distancia_euclidea_(v: Tuple, x: Tuple) -> float:
    '''
    Distancia euclídea para un plano de coordenadas (R2)
    '''
    
    return math.sqrt((v[0]-int(x[0]))**2+(v[1]-int(x[1]))**2)

def clear() -> None:
    '''
    Clears the screen
    '''

    os.system('cls')

def _pop_error_(error: str, error_code: str=None ) -> None:
    '''
    Displays an error on screen
    '''

    print(f'{UNDERLINE}ERROR{f"(Code {error_code})" if error_code else ""}{END}{BOLD}: {error}{END}')

def _leyenda_direcciones_(clases: List[str]):

    w = ' '
    for clase in clases:
        w += f'{BOLD}{clase}{END} | '

    print(f'\n{UNDERLINE}Clases de via:{END}{w}\n')

    print(f'{UNDERLINE}* A continuación, escribe con MAYUSCULAS y sin tildes en los distintos campos{END}\n')
    print(f'{UNDERLINE}*Las partícula de vía (como "de" o "del") se omitirán en el nombre{END}\n')
    print(f'{UNDERLINE}*Dejar los campos en blanco cerrará automáticamente el navegador\n')

