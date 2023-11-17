
# * Pablo garcía Molina
# * Andrés Martínez Fuentes

import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy

INFTY = sys.float_info.max

@dataclass
class Arista:
    
    origen: object = field()
    destino: object = field()
    data: object = field()
    weight: float = field()

    def __contains__(self, n: object):
        return True if (self.origen == n or self.destino == n) else False

@dataclass()
class Vertice:
    data: object = field()
    adyacencia: Dict[object, Arista] = field(default_factory=dict) #Lista de adyacencia del vértice (solo salida) #!

    def __str__(self) -> str:

        word = ''
        word += f'{self.data} -> {self.adyacencia}'

        return word

class Grafo:
    #Diseñar y construir la clase grafo

    def __init__(self, dirigido=False):
        """ Crea un grafo dirigido o no dirigido.
        
        Args:
            dirigido: Flag que indica si el grafo es dirigido o no.
        Returns: Grafo o grafo dirigido (según lo indicado por el flag)
        inicializado sin vértices ni aristas.
        """

        self.vertices: Dict[object, Vertice] = {}
        self.aristas: List[Arista] = []
        self.dirigido: bool = dirigido

    def __str__(self):
        word = ''
        for v in self.vertices.values():
            word += f'\n\n{str(v)}'
        
        return word + '\n'
    
    #### Operaciones básicas del TAD ####
    def es_dirigido(self) -> bool:
        """ Indica si el grafo es dirigido o no
        
        Args: None
        Returns: True si el grafo es dirigido, False si no.
        """
        return self.dirigido
    
    def agregar_vertice(self, data: object) -> None:
        """ Agrega el vértice v al grafo.
        
        Args: v vértice que se quiere agregar
        Returns: None
        """
        self.vertices[data] = Vertice(data)

    def agregar_vertices_mult(self, mult_v: List[object]):
        '''
        Añade los elementos de la lista de objetos

        -> mult_v: List de objetos (iterable)
        '''

        for obj in mult_v: self.vertices[obj] = Vertice(obj)

    def agregar_arista(self, s: object, t: object, data: object=None, weight: float=1) -> None:
        """ Si los objetos s y t son vértices del grafo, agrega
        una arista al grafo que va desde el vértice s hasta el vértice t
        y le asocia los datos "data" y el peso weight.
        En caso contrario, no hace nada.
        
        Args:
            s: vértice de origen (source)
            t: vértice de destino (target)
            data: datos de la arista
            weight: peso de la arista
        Returns: None
        """

        if s and t in self.vertices:
            #Crear Arista y añadirla a la lista de aristas
            a = Arista(s, t, data, weight)
            if self.dirigido:
                #Si el grafo es dirigido sólo se añade la Arista a la lista de adyacencia del Vertice de origen
                self.aristas.append(a)
                self.vertices[s].adyacencia[t] = a
            else:
                if not s in self.vertices[t].adyacencia:
                    self.aristas.append(a)
                    #Si no es dirigido, añado la Arista a la lista de adyacincia de ambos Vertices
                    self.vertices[s].adyacencia[t] = a
                    self.vertices[t].adyacencia[s] = a
        
    def agregar_aristas_mult(self, mult_arist: List[Tuple]) -> None:
        '''
        Añade las tuplas de una lista al Grafo como elementos Arista

        -> mult_arist: lista de tuplas t.q. (origen, destino, data, weight),
        donde los parámetros data y weight son opcionales de Arista (ver Arista)
        '''

        for arist in mult_arist: self.agregar_arista(*arist)

    def eliminar_vertice(self, v: object) -> None:
        """ Si el objeto v es un vértice del grafo lo elimina.
        Si no, no hace nada.
        
        Args: v vértice que se quiere eliminar
        Returns: None
        """

        #Eliminar aristas de su adyacencia de la lista de aristas y de la adyacencia de otros |
        #                                                                                     | => Vertice eliminado
        #Eliminar vertice de los vertices y de la adyacencia de otros                         |
        
        v_obj = self.vertices.get(v, None)
        if v_obj:
            if self.dirigido:
                # * ¿Adyacencia de entrada para no tener que recorrer todas las aristas si es dirijido?
                for a in self.aristas:
                    if v in a:
                        self.aristas.remove(a)
                        w = a.origen if a.origen != v else a.destino
                        del self.vertices[w].adyacencia[v]
            else:
                for w in v_obj.adyacencia:
                    a = self.vertices[w].adyacencia.pop(v)
                    self.aristas.remove(a)
            #Eliminar de la lista de vértices
            del self.vertices[v]

    def eliminar_arista(self, s: object, t: object) -> None:
        """ Si los objetos s y t son vértices del grafo y existe
        una arista de u a v la elimina.
        Si no, no hace nada.
        
        Args:
            s: vértice de origen de la arista
            t: vértice de destino de la arista
        Returns: None
        """

        if s and t in self.vertices:
           
            if self.dirigido:
                #Comprobar que la Arista existe exactamente con ese origen y ese destino y la eliminarla
                for a in self.aristas:
                    if a.origen == s and a.destino == t:
                        self.aristas.remove(a)
                        del self.vertices[s].adyacencia[t]

            else:
                #Comprobar que la Arista exista con esos Vértices y eliminarla de las listas de adyacencia de ambos
                for a in self.aristas:
                    if s in a and t in a:
                        self.aristas.remove(a)
                        del self.vertices[s].adyacencia[t]
                        del self.vertices[t].adyacencia[s]

    def obtener_arista(self, s: object, t: object) -> Tuple[object, float] or None:
        """
        Si los objetos s y t son vértices del grafo y existe
        una arista de u a v, devuelve sus datos y su peso en una tupla.
        Si no, devuelve None
        
        Args:
            s: vértice de origen de la arista
            t: vértice de destino de la arista
        Returns: Una tupla (a,w) con los datos de la arista "a" y su peso
        "w" si la arista existe. None en caso contrario.
        """

        if s and t in self.vertices:
            if self.dirigido:
                for a in self.aristas:
                    if a.origen == s and a.destino == t: return (a.data, a.weight)
            else:
                for a in self.aristas:
                    if s in a and t in a: return (a.data, a.weight)

        return None

    def lista_adyacencia(self, u: object) -> List[object] or None:
        """
        Si el objeto u es un vértice del grafo, devuelve
        su Lista de adyacencia.
        Si no, devuelve None.
        
        Args: u vértice del grafo
        Returns: Una Lista [v1,v2,...,vn] de los vértices del grafo
        adyacentes a u si u es un vértice del grafo y None en caso
        contrario
        """

        u_obj = self.vertices.get(u, None)

        return u_obj.adyacencia.keys() if u_obj else None
        
    #### Grados de vértices ####
    def grado_saliente(self, v: object) -> int or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su grado saliente.
        Si no, devuelve None.
        
        Args: u vértice del grafo
        Returns: El grado saliente (int) si el vértice existe y
        None en caso contrario.
        """

        u_obj = self.vertices.get(v,None)
        return u_obj.adyacencia.__len__() if u_obj else None

    def grado_entrante(self, v: object) -> int or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su grado entrante.
        Si no, devuelve None.
        
        Args: u vértice del grafo
        Returns: El grado entrante (int) si el vértice existe y
        None en caso contrario.
        """

        c = 0
        if v in self.vertices:
            if self.dirigido:
                for a in self.aristas:
                    if a.destino == v: c += 1
            else: c = self.grado_saliente(v)
    
        return c if c else None

    def grado(self, v: object) -> int or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su grado si el grafo no es dirigido y su grado saliente si
        es dirigido.
        Si no pertenece al grafo, devuelve None.
        
        Args: u vértice del grafo
        Returns: El grado (int) o grado saliente (int) según corresponda
        si el vértice existe y None en caso contrario.
        """

        if v in self.vertices: return self.grado_saliente(v)

        return None

    #### Algoritmos #### ultimas
    def dijkstra(self, origen: object)-> Dict[object,object]:
        """
        Calcula un Árbol Abarcador Mínimo para el grafo partiendo
        del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
        el árbol de la componente conexa que contiene a "origen".
        
        Args: origen vértice del grafo de origen
        Returns: Devuelve un diccionario que indica, para cada vértice alcanzable
        desde "origen", qué vértice es su padre en el árbol abarcador mínimo.
        """
        
        padre =  {v: None for v in self.vertices}
        visitado = {v: False for v in self.vertices}
        d = {v: INFTY for v in self.vertices}
        
        d[origen] = 0
        q = [origen]

        while q:
            v = q.pop(0)
            if not visitado[v]:
                visitado[v] = True
                for w in self.vertices[v].adyacencia: # mirar si es mejor keys
                    if d[w] > (d[v] + self.vertices[v].adyacencia[w].weight):
                        d[w] = d[v] + self.vertices[v].adyacencia[w].weight
                        padre[w] = v
                        q.append(w)
                q.sort(key=lambda x: d[x])
        return padre

    def dijkstra_min(self, origen: object, destino: object) -> Dict[object, object]:
        '''
        Versión acotada del algoritmo de Dijkstra, que permite ejecutarlo hasta haber llegado a un vértice concreto,
        obteniedo la versión parcial del Árbol Abarcador Mínimo que lo contiene y parte del vértice origen.
        '''

        padre =  {v: None for v in self.vertices}
        visitado = {v: False for v in self.vertices}
        d = {v: INFTY for v in self.vertices}
        
        d[origen] = 0
        # Inicializar lista de prioridad Q = {origen} ordenada por d.
        q = [origen]

        while q and not visitado[destino]:
            v = q.pop(0)
            if not visitado[v]:
                visitado[v] = True
                for w in self.vertices[v].adyacencia: # mirar si es mejor keys
                    if d[w] > (d[v] + self.vertices[v].adyacencia[w].weight):
                        d[w] = d[v] + self.vertices[v].adyacencia[w].weight
                        padre[w] = v
                        q.append(w)
                q.sort(key=lambda x: d[x])
        return padre

    def camino_minimo(self,origen:object, destino:object) -> List[object]:
        '''
        Calcula el camino mínimo a partir de una versión acotada del algoritmo de Dijkstra
        '''
        
        d_padres = self.dijkstra_min(origen, destino)
        aux = destino
        camino = []
        while d_padres[aux]:
            camino.append(aux)
            aux = d_padres[aux]
        camino.append(origen)

        return camino[::-1]

    def prim(self)-> Dict[object,object]:
        """
        Calcula un Árbol Abarcador Mínimo para el grafo
        usando el algoritmo de Prim.
        
        Args: None
        Returns: Devuelve un diccionario que indica, para cada vértice del
        grafo, qué vértice es su padre en el árbol abarcador mínimo.
        """
        
        padre =  {v: None for v in self.vertices}
        coste_minimo = {v: INFTY for v in self.vertices}
        q = [v for v in self.vertices]

        while q:
            v = q.pop(0)
            vertice = self.vertices[v]
            for w in vertice.adyacencia:
                if w in q and (vertice.adyacencia[w].weight < coste_minimo[w]):
                    coste_minimo[w] = vertice.adyacencia[w].weight
                    padre[w] = v
            q.sort(key=lambda x: coste_minimo[x])
        
        return padre

    def kruskal(self)-> List[Tuple[object,object]]:
        """ Calcula un Árbol Abarcador Mínimo para el grafo
        usando el algoritmo de Prim.
        
        Args: None
        Returns: Devuelve una Lista [(s1,t1),(s2,t2),...,(sn,tn)]
        de los pares de vértices del grafo
        que forman las aristas del arbol abarcador mínimo.
        """
        l = deepcopy(self.aristas)
        l.sort(key=lambda x: x.weight)
        c = {} 
        for v in self.vertices:
            c[v] = [v]
        aristas_aam = []
        while l:
            a = l.pop(0)
            if c[a.origen] != c[a.destino]:
                aristas_aam.append((a.origen,a.destino))
                for el in c[a.destino]:
                    c[a.origen].append(el)
                    c[a.origen].sort()
                for w in c[a.destino]:
                    c[w] = c[a.origen]
        return aristas_aam


    #### NetworkX ####
    def convertir_a_NetworkX(self)-> nx.Graph or nx.DiGraph:
        """ Construye un grafo o digrafo de Networkx según corresponda
        a partir de los datos del grafo actual.
        
        Args: None
        Returns: Devuelve un objeto Graph de NetworkX si el grafo es
        no dirigido y un objeto DiGraph si es dirigido. En ambos casos,
        los vértices y las aristas son los contenidos en el grafo dado.
        """
        
        g = nx.DiGraph() if self.dirigido else nx.Graph()
        g.add_nodes_from(self.vertices.keys())
        g.add_edges_from([(a.origen, a.destino, {'weight': a.weight, 'data': a.data}) for a in self.aristas])

        return g

if __name__ == '__main__':

    G = Grafo(dirigido=False)
    G.agregar_vertices_mult(['a','b','c','d','e','f'])
    G.agregar_aristas_mult(
        [('f', 'a', None, 5),
        ('f', 'b', None, 5),
        ('f', 'c', None, 6),
        ('f', 'd', None, 3),
        ('f', 'e', None, 4),
        ('a', 'b', None, 5),
        ('a', 'e', None, 3),
        ('e', 'd', None, 2),
        ('c', 'b', None, 3),
        ('c', 'd', None, 4)]
        )
    
    G.eliminar_vertice('f')
    netxG = G.convertir_a_NetworkX()
    plot=plt.plot()
    nx.draw(netxG,with_labels=True)
    plt.show()

    