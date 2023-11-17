'''
GPS
'''

from construccion_grafo import _cargar_datos_, cargar_y_unir_cruces_por_calle, Datos_de_arista
import grafo as g
import support.funcs as f
from support.cons import ALPHA, BOLD, END, CLASES_VIA, UNDERLINE
import pandas as pd
import time
import networkx as nx
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

class Navegador():

    def __init__(self, grafo: g.Grafo, direcciones: pd.DataFrame, codigos_validos: List[int]) -> None:
        '''
        Inicilización del navegador.

        -> grafo: Grafo del callejero
        -> direcciones: DataFrame con direcciones
        -> tipo_ruta: 'corta' o 'rapida'
        '''
        
        self.grafo = grafo
        self.direcciones = direcciones
        self.codigos_validos = codigos_validos
        self.tipo_ruta = None
        
        #Datos del navegador para mayor rendimiento con NetworkX
        self.xgrafo: nx.Graph = None
        self.pos: Dict[Tuple] = {v: v for v in grafo.vertices}

    def _seleccionar_direccion_(self, tipo: str) -> List[int or Tuple]:
        '''
        Seleccion de la dirección de origen o destino en función de los siguientas campos:
        - Clase de via
        - Nombre de la via
        - Número de la direccion
        
        Devuleve el código de la vía y una tupla con las coordenadas exactas de la dirección

        -> tipo: 'origen' o 'destino'
        '''
        

        def seleccionar_campo(campo: str, clase: str = 'str'):
            
            try:
                r = input(campo).strip().upper()
                if not r: return r
                if clase == 'int': r = int(r)
            except Exception as e:
                return e
            
            return r
        
        direccion = False

        while not direccion:

            print(f'{BOLD}SELECCION DE {ALPHA}{tipo.upper()}{END}')

            campos = ['· Seleccione una clase de vía : ', '· Escriba el nombre de la vía: ','· Escriba el número de la dirección: ']
            i = 0
            ins = []
            while i < len(campos):
                r = seleccionar_campo(campos[i]) if i != 2 else seleccionar_campo(campos[i], clase='int')
                if type(r) != str and type(r) != int:
                    f._pop_error_('entrada inválida')
                else:
                    ins.append(r)
                    i += 1
            clase, nombre, numero = ins

            if not clase and not nombre and not numero: return []
            
            d = self.direcciones.loc[self.direcciones['Clase de la via'] == clase + (24-len(clase))*' ']
            
            d = d.loc[d['Nombre de la vía'] == nombre+(48-len(nombre))*' ']

            direccion = []
            
            for c in d.iloc():
                if int(c['Direccion completa para el numero'].split(',')[1].split(' ')[1]) == numero:
                    direccion.append(c)

            if len(direccion) > 1:
                txt = '| '
                for d in direccion:
                    l = d['Direccion completa para el numero'].split(',')[1].split(' ')[2]
                    if l == '':
                        l = d['Direccion completa para el numero'].split(',')[1].split(' ')[3]
                    txt += BOLD + l + END + ' | ' 
                print(txt)
                letra = input('· Selecione una letra: ').strip()
                for d in direccion:
                    l = d['Direccion completa para el numero'].split(',')[1].split(' ')[2]
                    if l == '':
                        l = d['Direccion completa para el numero'].split(',')[1].split(' ')[3]
                    if letra == l:
                        direccion = [d['Codigo de via'],(int(d['Coordenada X (Guia Urbana) cm']),int(d['Coordenada Y (Guia Urbana) cm']))]
            elif len(direccion) == 1:
                d = direccion[0]
                direccion = [d['Codigo de via'],(int(d['Coordenada X (Guia Urbana) cm']),int(d['Coordenada Y (Guia Urbana) cm']))]
            else:
                f._pop_error_('Dirección inexistente')
                direccion = []

            if direccion and not d['Codigo de via'] in self.codigos_validos:
                direccion = []
                f._pop_error_('No existen cruces para esta direccion')

            

        return direccion

    def _seleccionar_tipo_ruta_(self) -> str:

        r = None
        print(f'¿DESEA BUSCAR LA RUTA MAS {BOLD}CORTA{END} O LA MAS {BOLD}RAPIDA{END}?')
        r = input('-> ')
        
        while r.strip().upper() != 'CORTA' and r.strip().upper() != 'RAPIDA':
            f._pop_error_('seleccione uno de los dos campos')
            r = input('-> ')
        
        return r
    
    def cambiar_ruta(self, ruta):
        '''
        Cambia el tipo de ruta que busca el navegador.

        -> ruta: 'corta' o 'rapida'
        '''

        if ruta != self.tipo_ruta:

            self.tipo_ruta = ruta
            
            for arista in self.grafo.aristas:
                
                if ruta == 'corta':
                    arista.weight = arista.data.longitud
                
                elif ruta == 'rapida':
                    arista.weight = arista.data.tiempo

    def _añadir_direccion_grafo_(self, codigo: int, coord: Tuple[int]) -> None:
        '''
        Añade al grafo del navegador un vértice representando la direccion, dadas sus coordenadas y su código de calle.
        Lo conecta con los cruces más cercanos.
        '''

        if not coord in self.grafo.vertices.keys():
            #Buscar los dos cruces, de la calle en la que esta la direccion, que contienen a la dirección
            vertices_calle = []
            for arista in self.grafo.aristas:
                if arista.data.codigo == codigo:
                    if not arista.origen in vertices_calle: vertices_calle.append(arista.origen)
                    if not arista.destino in vertices_calle: vertices_calle.append(arista.destino)
            dists = [f._distancia_euclidea_(coord, v) for v in vertices_calle]

            i = dists.index(min(dists))
            v1_coord = vertices_calle.pop(i)
            j = dists.index(min(dists))
            v2_coord = vertices_calle.pop(j)

            v1 = self.grafo.vertices[v1_coord]
            v2 = self.grafo.vertices[v2_coord]
            #Conectar los vértices más cercanos a la dirección
            if not v2_coord in v1.adyacencia:
                for v in v1.adyacencia:
                    vs = []
                    if v1.adyacencia[v].data.codigo == codigo:
                        vs.append(v)
                vs_dists = [f._distancia_euclidea_(coord, w) for w in vs]
                v2_coord = vs[vs_dists.index(min(vs))]
            
            vel = v1.adyacencia[v2_coord].data.velocidad_max

            self.grafo.agregar_vertice(coord)
            self.grafo.agregar_aristas_mult(
                [(coord, v1_coord, Datos_de_arista(codigo, coord, v1_coord, vel), 1),
                (coord, v2_coord, Datos_de_arista(codigo, coord, v1_coord, vel), 1)]
                )

    def get_instrucciones(self, camino: List[Tuple]):
        """
        Obtiene las instrucciones del camino entre origen y destino con todos los detalles pertinentes
        
        """
        aristas = []
        giros = {'direccion': [], 'longitud': [],'calle': []}

        for i in range(len(camino)-1):
            v = self.grafo.vertices[camino[i]]
            ar = v.adyacencia[camino[i+1]]
            aristas.append(ar)

        i = 1
        lon = aristas[0].data.longitud//100
        while i < len(aristas):
            if aristas[i].data.codigo == aristas[i-1].data.codigo:
                lon += aristas[i].data.longitud//100
            else:
                giros['longitud'].append(lon)
                codigo = aristas[i].data.codigo
                direc = self.direcciones.loc[self.direcciones['Codigo de via'] == codigo].iloc()[0]
                calle = direc['Clase de la via'].strip().lower()+' '+direc['Partícula de la vía'].strip().lower()+' '+direc['Nombre de la vía'].strip().lower()
                giros['calle'].append(calle)
                lon = aristas[i].data.longitud//100
                if aristas[i-1].origen[1] < aristas[i-1].destino[1]:
                    if aristas[i].origen[0] < aristas[i].destino[0]:
                        giros['direccion'].append('derecha')
                    else:
                        giros['direccion'].append('izquierda')
                else:
                    if aristas[i].origen[0] < aristas[i].destino[0]:
                        giros['direccion'].append('izquierda')
                    else:
                        giros['direccion'].append('derecha')
            i += 1
        
        text = ''
        
        for i in range(len(giros['longitud'])):
            text += f"·Avance {giros['longitud'][i]} metros por {BOLD}{giros['calle'][i]}{END}, a continuacion gire a la {BOLD}{giros['direccion'][i]}{END}\n"

        return text

    def mostrar_ruta(self, inicio: Tuple[int], final: Tuple[int], camino: List[Tuple]) -> None:
        '''
        Transforma el grafo a NetworkX y muestra por pantalla en una ventana el mapa con la 
        ruta seleccionada.

        -> inicion: vertice inicial
        -> final: vertice final
        -> camino: Lista de vértices de la ruta
        '''
        
        if not self.xgrafo:

            self.xgrafo = self.grafo.convertir_a_NetworkX()
        

        ruta_grafo = g.Grafo(False)
        ruta_grafo.agregar_vertices_mult(camino)
        aux = None
        for v in camino:
            if aux:
                ruta_grafo.agregar_arista(aux,v)
            aux=v
        rutx = ruta_grafo.convertir_a_NetworkX()

        color_map = []
        for v in rutx:        
            if v == inicio:
                color_map.append('green')
            elif v == final:
                color_map.append('blue')
            else:
                color_map.append('red')


        if not inicio in self.pos: self.pos[inicio] = inicio
        if not final in self.pos: self.pos[final] = final

        plot = plt.plot()
        nx.draw(self.xgrafo,with_labels=False,pos=self.pos, node_size=10, node_color='grey', edge_color='grey')
        nx.draw(rutx, pos=self.pos, node_size=12,node_color=color_map, width=3, edge_color='red')
        plt.show()
                      
    def run(self):
        '''
        Inicia el navegador. Pedirá intrucciones de origen y destino y mostrá a ruta en función
        de los parámetros introducidos por el usuario. De no introducir origen o destino se cerrará 
        automáticamente
        '''

        f.clear()

        origen = '.'
        destino = '.'

        while origen and destino:
            
            print(f'{BOLD}{UNDERLINE}NUEVA RUTA{END}\n\n')
            f._leyenda_direcciones_(CLASES_VIA)
            origen = self._seleccionar_direccion_('origen')
            if origen: destino = self._seleccionar_direccion_('destino')

            if origen and destino:
                ruta = self._seleccionar_tipo_ruta_()
                f.clear()

                self._añadir_direccion_grafo_(origen[0], origen[1])
                self._añadir_direccion_grafo_(destino[0], destino[1])
                self.cambiar_ruta(ruta.lower())

                camino = self.grafo.camino_minimo(origen[1], destino[1])

                instrucciones = self.get_instrucciones(camino)
                print(f'{ALPHA}DIRECCIONES{END}\n')
                print(instrucciones)
                self.mostrar_ruta(origen[1], destino[1], camino)
            
            f.clear()

        print('CERRANDO NAVEGADOR...', end='')
        print('DONE')

def arrancar_navegador() -> Navegador:
    '''
    Arranca el navegador del GPS
    '''
    
    f.clear()
    s = time.perf_counter()
    print('ARRANCANDO NAVEGADOR....')
    cruces, direcciones = _cargar_datos_()
    G = cargar_y_unir_cruces_por_calle(cruces)
    codigos_validos = []
    for a in G.aristas:
        if not a.data.codigo in codigos_validos: codigos_validos.append(a.data.codigo)
    e = time.perf_counter()
    f.clear()
    print(f'NAVEGADOR LISTO ({e-s} segundos)')

    return Navegador(G, direcciones, codigos_validos)

if __name__ == '__main__':

    navegador = arrancar_navegador()
    navegador.run()
    