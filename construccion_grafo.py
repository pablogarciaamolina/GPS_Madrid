'''
Script para contrucción del grafo del callejero (de Madrid) a partir de los datasets:
- cruces.csv (“Callejero: informacion adicional asociada. Cruces de viales con coordenadas geograficas”)
- direcciones.csv (“Callejero: informacion adicional asociada. Direcciones postales vigentes con coordenadas geograficas” )

* web de datos del Gobierno
'''

import grafo as g
import pandas as pd
from support.cons import VELOCIDADES
from support.funcs import _distancia_euclidea_ as distancia
from typing import Tuple, Dict, List

class Datos_de_arista():
    '''
    Clase para almacenar os datos de cada arista del callejero en el grafo
    '''
    
    def __init__(self, codigo: int, v_in: Tuple, v_fin: Tuple, vel_max: float) -> None:
        '''
        Inicialización de los datos.
        
        -> codigo: código de la calle
        -> v_in: cruce inicial de la arista
        -> v_fin: cruce final de la vía
        -> vel_max: velocidad máxima permitida en la vía
        -------------------------------------------------------------
        - direcciones: direcciones asociadas a la arista (las direcciones de la calle que la involucran)
        - longitud: distancia entre los vértices de la arista definida para el plano del calleero
        - tiempo: tiempo minimo para recorrer la arista yendo a la velocidad máxima
        '''

        self.codigo = codigo
        # self.direcciones = _obtener_direcciones_(codigo, v_in, v_fin)
        self.velocidad_max = vel_max
        self.longitud = distancia(v_in,v_fin)
        self.tiempo = self.longitud/self.velocidad_max

def _cargar_datos_() -> List[pd.DataFrame]:

    cruces = pd.read_csv('cruces.csv', sep=';', encoding='latin_1')
    direcciones = pd.read_csv('direcciones.csv', sep=';', encoding='latin_1',low_memory=False)
    
    return [cruces, direcciones]

def _conseguir_tipos_calle_(cruces_df: pd.DataFrame):
    '''
    Obtiene todos los tipos de calles del callejero
    '''

    cruces_aux = cruces_df.drop_duplicates(subset=['Codigo de vía tratado'], inplace=False)
    tipos = {}
    for calle in cruces_aux.iloc():
        tipos[calle['Codigo de vía tratado']] = calle['Clase de la via tratado']
    
    return tipos

def _conseguir_vel_(calle: int, tipos: Dict[int, str]):
    '''
    Dada una calle, obtiene su velocidad máxima permitida
    '''
    try:
        return VELOCIDADES[tipos[calle]]
    except KeyError:
        return 5000000/3600

def cargar_y_unir_cruces_por_calle(cruces: pd.DataFrame) -> g.Grafo:
    '''
    A medida que carga los cruces del DataFrame, crea las aristas entre estos.Cada cruce es un vértice, 
    cuyo identificador son sus coordenadas (cm). Se van creando aristas entre los cruces de una misma calle (*). De esta forma,
    al terminar el proceso el resultado es el grafo completo (al unir los cruces por calles se crea el grafo, 
    pues en los datos los cruces están repetidos por calles).
 
    (*) El criterio para unir los cruces de una misma calle es la proximidad geográfica. El dataset trae las coordenadas
    de los cruces ordenadas por cercanía.
    '''

    cruces.drop_duplicates(subset=['Codigo de vía tratado', 'Coordenada X (Guia Urbana) cm (cruce)','Coordenada Y (Guia Urbana) cm (cruce)'], inplace=True)
    tipos_calle = _conseguir_tipos_calle_(cruces)

    G = g.Grafo(dirigido=False)
    code_ant = None
    cruce_ant = None
    for cruce in cruces.iloc():
        codigo = cruce['Codigo de vía tratado']
        v = (int(cruce['Coordenada X (Guia Urbana) cm (cruce)']), int(cruce['Coordenada Y (Guia Urbana) cm (cruce)']))
        if not v in G.vertices: G.agregar_vertice(v)
        if codigo == code_ant:
            if cruce_ant:
                G.agregar_arista(
                    cruce_ant,
                    v,
                    Datos_de_arista(codigo, cruce_ant, v, _conseguir_vel_(codigo, tipos_calle)),
                    1,
                )
        code_ant = codigo
        cruce_ant = v
    
    return G


if __name__ == '__main__':

    cruces, direcciones = _cargar_datos_()
    G = cargar_y_unir_cruces_por_calle(cruces)
    print('Graph DONE')