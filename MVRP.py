import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import time as tm
import csv

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from scipy.spatial.distance import cdist
from parametros import NUM_DIAS, NUM_RECOLECTORES, DURACION_ENCUESTA_MIN, PROM_VELOCIDAD, INICIO_MIN, JORNADA_MIN, AM_PM_MIN, TIEMPO_ESPERA_MIN, FILE_NAME, TIEMPO_MAXIMO_DE_BUSQUEDA, min_to_str



def CreateDataModel(xy, horarios):

    '''Guarda la data del problema'''

    data = {}
    data['locations'] = xy

    duracion_encuesta = (np.ones((NUM_RECOLECTORES + NUM_VISITAR, NUM_RECOLECTORES + NUM_VISITAR)) - 
                         np.identity(NUM_RECOLECTORES + NUM_VISITAR)) * DURACION_ENCUESTA_MIN
    data['time_matrix'] = np.ceil(cdist(xy,xy, metric='cityblock')/PROM_VELOCIDAD + duracion_encuesta)

    lista = []
    for horario in horarios:
        if horario == 'AM':
            lista.append((0, AM_PM_MIN))
        elif horario == 'PM':
            lista.append((AM_PM_MIN + DURACION_ENCUESTA_MIN, JORNADA_MIN))
        elif horario == 'DIA':
            lista.append((0, JORNADA_MIN))
        else:
            print('Formato inválido de horario (AM, PM o DIA)')

    data['time_windows'] = lista
    data['horarios'] = horarios
    data['num_recolectores'] = NUM_RECOLECTORES * NUM_DIAS
    data['NUM_RECOLECTORES'] = NUM_RECOLECTORES
    data['num_dias'] = NUM_DIAS 

    # Se sacan solo los depots
    lista = [[i]*NUM_DIAS for i in range(NUM_RECOLECTORES)] 
    start_end = [j for i in lista for j in i] # no funciona con funciones de numpy

    # Definimos los puntos de inicio y término de cada encuestador (salen y vuelven al mismo depot)
    data['starts'] = start_end
    data['ends'] = start_end
    return data

def PrintSolution(data, manager, routing, solution):
    """Imprime solución en la consola """
    #print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    rutas = {} # Variable que contendrá toda la información de las rutas
    var_time = {}
    rec_id = {}
    for i in range(data['NUM_RECOLECTORES']):
        rec_id[i] = []
    
    for recolector_id in range(data['num_recolectores']):
        index = routing.Start(recolector_id)
        rutas[recolector_id] = [] # Creamos la lista que guardará las rutas para graficar
        var_time[recolector_id] = []
        plan_output = 'Route for recolector {}:\n'.format(recolector_id)
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            var_time[recolector_id].append('({0},{1})'.format(min_to_str(solution.Min(time_var)),
                                                          min_to_str(solution.Max(time_var))))
            plan_output += '{0} Time({1},{2}) -> '.format(manager.IndexToNode(index), 
                                                          min_to_str(solution.Min(time_var)),
                                                          min_to_str(solution.Max(time_var)))
            rutas[recolector_id].append(manager.IndexToNode(index)) # Vamos agregando sus paradas para graficar después
            index = solution.Value(routing.NextVar(index))
        rutas[recolector_id].append(manager.IndexToNode(index)) # Agregamos la última parada de la ruta
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                    min_to_str(solution.Min(time_var)),
                                                    min_to_str(solution.Max(time_var)))
        var_time[recolector_id].append('({0},{1})'.format(min_to_str(solution.Min(time_var)),
                                                          min_to_str(solution.Max(time_var))))
        plan_output += 'Time of the route: {}min\n'.format(
            solution.Min(time_var))
        #print(plan_output)
        total_time += solution.Min(time_var)


        if len(rutas[recolector_id]) <= 2:
            rec_id[np.floor(recolector_id / data['num_dias'])] = rec_id[np.floor(recolector_id / data['num_dias'])] + [recolector_id]
        
        else:
            rec_id[np.floor(recolector_id / data['num_dias'])] =  [recolector_id] + rec_id[np.floor(recolector_id / data['num_dias'])]
    

    #print('Total time of all routes: {}min'.format(total_time))

    return rutas, var_time, rec_id

def PlotSolutions(rutas, data, rec_id):
    '''Entrega un gráfica de las soluciones'''
    plt.figure(figsize=(10,10))
    plt.scatter(data['locations'][NUM_RECOLECTORES:,0], data['locations'][NUM_RECOLECTORES:,1], color = '#85E1FF') # Graficamos los lugares a visitar
    plt.scatter(data['locations'][:NUM_RECOLECTORES,0], data['locations'][:NUM_RECOLECTORES,1], marker='*', color = '#EB3FBC') # Graficamos los depots
    for recolector_id in rutas:
        x = []
        y = []
        for ruta in rutas[recolector_id]:
            x.append(data['locations'][ruta][0])
            y.append(data['locations'][ruta][1])
        plt.plot(x,y) # Graficamos las rutas de cada encuestador
    plt.rcParams["image.cmap"] = "Set1"
    plt.show(block=False)

    fig, axes = plt.subplots(nrows=int(np.ceil(data['num_dias']/4)), ncols=4, figsize=(10,10))

    if data['num_dias' ]<= 4:

        for i in range(data['num_dias']):
        
            axes[i].scatter(data['locations'][NUM_RECOLECTORES:,0], data['locations'][NUM_RECOLECTORES:,1], color = '#85E1FF') # Graficamos los lugares a visitar
            axes[i].scatter(data['locations'][:NUM_RECOLECTORES,0], data['locations'][:NUM_RECOLECTORES,1], marker='*', color = '#EB3FBC') # Graficamos los depots

            for j in range(data['NUM_RECOLECTORES']):

                x = []
                y = []
                recolector_id = rec_id[j][i]
                # recolector_id = i  + j * data['num_dias']
                for ruta in rutas[recolector_id]:
                    x.append(data['locations'][ruta][0])
                    y.append(data['locations'][ruta][1])
             
                axes[i].plot(x,y) # Graficamos las rutas de cada encuestador
            
            axes[i].set_title(f'Dia {1+i}')
            axes[i].axes.get_xaxis().set_ticks([])
            axes[i].axes.get_yaxis().set_ticks([])


        plt.show()
        
    else: 

        for i in range(data['num_dias']):
            
            axes[int(np.floor(i/4)) , int(i%4)].scatter(data['locations'][NUM_RECOLECTORES:,0], data['locations'][NUM_RECOLECTORES:,1], color = '#85E1FF') # Graficamos los lugares a visitar
            axes[int(np.floor(i/4)) , int(i%4)].scatter(data['locations'][:NUM_RECOLECTORES,0], data['locations'][:NUM_RECOLECTORES,1], marker='*', color = '#EB3FBC') # Graficamos los depots

            for j in range(data['NUM_RECOLECTORES']):

                x = []
                y = []
                recolector_id = rec_id[j][i]
                # recolector_id = i  + j * data['num_dias']
                for ruta in rutas[recolector_id]:
                    x.append(data['locations'][ruta][0])
                    y.append(data['locations'][ruta][1])             
                    
                axes[int(np.floor(i/4)) , int(i%4)].plot(x,y) # Graficamos las rutas de cada encuestador
            
            axes[int(np.floor(i/4)) , int(i%4)].set_title(f'Dia {1+i}')
            axes[int(np.floor(i/4)) , int(i%4)].axes.get_xaxis().set_ticks([])
            axes[int(np.floor(i/4)) , int(i%4)].axes.get_yaxis().set_ticks([])
        plt.show()
    
def CsvSolution(rutas, var_time, data, longitud, latitud, rec_id):
    '''Entrega la solución en formato .cvs'''

    filename = "Ruta_optima.csv"
    
    # writing to csv file 
    with open(filename, 'w', encoding='UTF8', newline='') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(['DIA', 'RECOLECTOR', 'LOCAL', 'VAR_TIEMPO','LONGITUD', 'LATITUD', 'HORARIO_VISITA']) 
        
        info =[]

        for i in range(data['num_dias']):
            for j in range(data['NUM_RECOLECTORES']):

                # recolector_id = i  + j * data['num_dias']
                recolector_id = rec_id[j][i]

                for k in range(len(rutas[recolector_id])):

                    info.append([i+1,j+1, rutas[recolector_id][k], var_time[recolector_id][k] ,longitud[rutas[recolector_id][k]],
                                latitud[rutas[recolector_id][k]], data['horarios'][rutas[recolector_id][k]]])
        
        
        csvwriter.writerows(info)



if __name__ == '__main__':
    '''Resuelve el problema MVRP con ventanas de tiempo'''

    # Leemos el documento y extraemos latitud, longitud y horario de visita
    df = pd.read_excel(FILE_NAME)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUD, df.LATITUD), crs='EPSG:4326').to_crs(epsg='5358')
    longitud = gdf.LONGITUD 
    latitud = gdf.LATITUD
    horarios = np.array(gdf['HORARIO_VISITA'])

    # Definimos numero de visita
    NUM_VISITAR = len(longitud) - NUM_RECOLECTORES

    # Pasamos latitud a metros
    xy = np.column_stack((gdf.geometry.x, gdf.geometry.y))

    # Se generan el diccionario con los datos
    data = CreateDataModel(xy, horarios)

    # Crea el administrador de índice de enrutamiento.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_recolectores'], data['starts'],
                                           data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define el costo de cada arco.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    #==============================================================

    # Agregar restricción de ventanas de tiempo.
    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        TIEMPO_ESPERA_MIN,  # permite tiempo de espera (An upper bound for slack)
        JORNADA_MIN,  # tiempo máximo por recolector
        False,  # No fuerce el inicio de la jornada a la primera hora.
        time)
    time_dimension = routing.GetDimensionOrDie(time)

    # Agrega restricciones de ventana de tiempo para cada ubicación, excepto los depósitos.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx in data['starts'] or location_idx in data['ends']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Agrega restricciones de ventana de tiempo para cada nodo de inicio de recolector.
    for recolector_id in range(data['num_recolectores']):
        index = routing.Start(recolector_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][recolector_id // NUM_DIAS][0],
            data['time_windows'][recolector_id // NUM_DIAS][1]) # División entera porque sale un vehículo por día en cada depot

    # Cree instancias de las horas de inicio y finalización de la ruta para producir tiempos factibles
    for i in range(data['num_recolectores']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    #==============================================================

    # Definimos parámetros de búsqueda
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    # Establece la primera solución heurística
    #search_parameters.first_solution_strategy = (
    #    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)

    # Definimos un tiempo máximo de búsqueda
    search_parameters.time_limit.seconds = TIEMPO_MAXIMO_DE_BUSQUEDA

    # Muestra registros de avance a medida que va encontrando soluciones
    search_parameters.log_search = True

    print("Calculando la solucion...")
    t1  = tm.time()
    # Resuelve el problema.
    solution = routing.SolveWithParameters(search_parameters)
    t2  = tm.time()
    print("Ejecución terminada")
    print('Tiempo: ',t2-t1)

    # Print solution on console.
    if solution:
        rutas, var_time, rec_id = PrintSolution(data, manager, routing, solution)
        CsvSolution(rutas, var_time, data, longitud, latitud, rec_id)
        PlotSolutions(rutas, data, rec_id)

    else:
        print('Solución no encontrada')




