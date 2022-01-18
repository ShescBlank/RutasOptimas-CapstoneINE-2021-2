## Documentación Proyecto Rutas Óptimas Capstone INE

Para resolver el problema de las rutas óptimas propuesto por el INE, utilizamos la librería OR TOOLS de Python ([OR TOOLS](https://developers.google.com/optimization/routing)),
cabe destacar que en la página se encuentra mucha información con respecto a distintas problemáticas y sus formas de resolverlas usando el software, y creemos que es una 
buena idea leer un poco sus guías para así entender las distintas aplicaciones que tiene y los ejemplos presentados.

El código creado para el proyecto de rutas óptimas cuenta con cuatro archivos principales:

- **MVRP.py**: es el código principal y es el que hay que correr para encontrar resultados.
- **input.py**: define los parámetros con los que se correrá el algoritmo, como el nombre del archivo excel a abrir, el número de encuestadores, el número de días, entre otros. 
Cabe destacar que, si se modifica este archivo, se pueden obtener distintas soluciones para los mismos puntos, por lo que recomendamos jugar con estos parámetros para encontrar
los más adecuados a la realidad.
- **parametros.py**: se encarga de aplicar operaciones sobre los parámetros de **input.py** y de definir funciones que los usan, con el objetivo de que el código principal reciba estos valores. Este archivo en principio no hay que modificarlo.
- Un archivo excel como el que nos entregaron. Su nombre debe ir en el archivo **input.py** y debe tener la siguiente información: LATITUD, LONGITUD y HORARIO_VISITA de cada punto.
Es importante mencionar que los primeros NUM_RECOLECTORES (parámetro del archivo **input.py**) del archivo excel serán utilizados como lugares de origen y término para los
encuestadores, y todo el resto serán lugares a visitar. Un ejemplo si tenemos 10 filas de datos en el excel y NUM_RECOLECTORES=2, entonces el primer encuestador partirá desde el
primer lugar del excel y el segundo encuestador del segundo lugar, mientras que los ocho lugares restantes serán los que tienen que visitar en sus jornadas laborales.

Si bien los códigos tienen comentarios para guiar la lectura, explicaremos detalladamente las distintas partes de cada archivo a continuación:

- **input.py**: el archivo tiene los siguientes parámetros:
  - INICIO_HR: Hora de inicio jornada laboral
  - FINAL_HR: Hora de término jornada laboral
  - INICIO_BREAK_HR: Hora de inicio del break (almuerzo)
  - FINAL_BREAK_HR: Hora de final del break (almuerzo)
  - AM_PM_HR: Hora de término AM e inicio PM
  - NUM_DIAS: Días de trabajo para visitar todos los lugares 
  - NUM_RECOLECTORES: Número de recolectores de información disponibles para visitar los lugares
  - DURACION_ENCUESTA_MIN: Duración de cada encuesta en minutos (este tiempo se sumará al tiempo de traslado entre lugares (matriz de tiempo))
  - PROM_VELOCIDAD: Promedio de velocidad caminando de una persona en m/min: 5 km/h => 83.3333 m/min
  - FILE_NAME: Nombre del archivo excel que contiene los datos .xlsx
  - TIEMPO_MAXIMO_DE_BUSQUEDA: Define el tiempo máximo que se le da al solver de encontrar una solución (en segundos)

- **parametros.py**: (recordar que este archivo opera sobre algunos parámetros del input para modelar el problema)
  - to_min(): función que recibe una hora y lo pasa a minutos (13 hrs = 780 mins). Si recibe alguna hora decimal, usará una función techo para aproximar los minutos.
  - min_to_str(): función que transforma una cantidad de minutos a la representación HH:MM (810 mins = 13:30).
  - DURACION_BREAK_HR: parámetro que representa la duración total del break en horas.
  - INICIO_MIN: parámetro que representa a INICIO_HR en minutos.
  - FINAL_MIN: lo mismo que INICIO_MIN pero con FINAL_HR.
  - DURACION_BREAK_MIN: pasa DURACION_BREAK_HR a minutos.
  - JORNADA_MIN: parámetro que representa la duración total de la jornada de trabajo cada día (sin considerar el tiempo de almuerzo). Además se trasladan las horas al 0, es decir, si la jornada parte a las 8 hrs y termina a las 18 hrs, entonces se considera que parte a las 0 hrs y termina a las 10 hrs (esto es solo para facilitar la programación). Nos gustaría mencionar que, si bien no consideramos el horario de almuerzo en la jornada laboral, los trabajadores siempre tendrán libre su duración del almuerzo, pero quizás no sea específicamente en el horario definido en el **input.py**, lo que significa que cada uno puede administrar su almuerzo y hacerlo un poco antes o después de lo definido originalmente. Esto lo hacemos ya que si definimos un horario fijo de almuerzo que tiene que calzar exacto, el tiempo de ejecución del código aumenta considerablemente.
  - AM_PM_MIN: representación en minutos de AM_PM_HR. También se traslada al 0 (ej: 12 hrs => 4 hrs si INICIO_HR=8 y 4 hrs = 240 mins).
  - TIEMPO_ESPERA_MIN: parámetro que representa el tiempo máximo (en minutos) de espera del encuestador para ir al siguiente lugar. Esto quiere decir que si el parámetro es igual a 60 minutos, el encuestador puede quedarse como máximo 1 hora en un lugar esperando a que abran el siguiente local (este tiempo de espera sería sin hacer nada en teoría). Por defecto lo tenemos definido como toda la jornada laboral en minutos, pero se pueden probar resultados con valores menores o incluso 0.

- **MVRP.py**:  
Comentario: esta es la parte central del código por lo que intentaremos explicar los puntos más importantes pero sin entrar en demasiado detalle con la notación de la librería. Si quedan dudas recomendamos revisar la página de OR TOOLS para ver los ejemplos y sus explicaciones.

   - CreateDataModel(): como su nombre lo indica, esta función se encarga de crear el modelo de los datos. Para esto lee las coordenadas y horarios del excel entregado, transforma las longitudes y latitudes a metros, calcula la matriz de tiempo asociada a todas las localizaciones, define el número de recolectores, gestiona los horarios de apertura/cierre y define los puntos de partida y término de cada encuestador. Es importante mencionar que la matriz de tiempo se calcula obteniendo la distancia manhattan entre todos los puntos (la cual es bastante cercana a la distancia real), luego se multiplica toda esa matriz por PROM_VELOCIDAD (velocidad promedio de caminata) y, finalmente, se le suma la DURACION_ENCUESTA_MIN (la duración general de las encuestas en minutos) para obtener la matriz de tiempo final. Otra anotación importante de hacer es que, como la matriz de tiempo considera el tiempo de encuesta, si un local abre a las 12:00, entonces el programa considera que abre a las 12:05 si el tiempo de encuesta es 5 minutos. Esto último lo hacemos porque podría llegar a producirse que, si el tiempo de encuesta es de 40 minutos por ejemplo, el programa considera que llega a las 12:00 (justo cuando abre) pero en realidad le está pidiendo que llegue a las 11:20 para que salga a las 12:00, lo que no estaría cumpliendo su horario de apertura.  
   **Nota**: si se quieren agregar tiempos de encuestas distintos, recomendamos agregar una columna en el excel inicial con estas duraciones, de manera que tengamos acceso a un vector de duraciones y, en vez de sumar la DURACION_ENCUESTA_MIN a la matriz de tiempo, se le sume la duración correspondiente al local.
   - PrintSolution(): función que encarga de imprimir texto plano en la consola (una vez solucionado el problema) las rutas de cada encuestador y guardar en una variable (diccionario) dichas rutas para luego utilizarla en otras funciones (graficar y crear archivo csv). En una última actualización del código quitamos la opción de imprimir en consola por un tema de limpieza en la visualización del progreso del programa. Además, agregamos la opción de mostrar
   - PlotSolutions(): función que se encarga de graficar las rutas de cada encuestador. Estas rutas son solo una representación visual del orden de puntos a visitar de cada encuestador, pero no representan directamente la ruta en la calle que debe tomar.
   - CsvSolution(): función que se encarga de crear el archivo csv en el mismo formato en que se nos fueron entregadas las rutas al iniciar el proyecto, con algunas columnas adicionales.
   - Rama principal del código: en esta sección del código se llama a todas las funciones anteriores y se modelo el problema usando las metodologías definidas por la librería. En particular se crea un administrador, un modelo de ruteo, se define la forma de evaluar los costos entre los puntos, se crea una dimensión de tiempo para agregar las restricciones de ventanas de tiempo, se definen los parámetros propios del solucionador asociado a OR Tools (tiempo de ejecución máximo, definir la metodología para encontrar la primera solución y se activan los logs para mostrar el avance de la búsqueda). Finalmente, se llama al método del modelo para resolver el problema y, en caso de que se encuentre una solución, se imprime el output que se describe a continuación.

### Output del programa

Una vez que se corre el código y se carge toda la información, la consola imprimirá "Calculando la solucion..." y, una vez encontrada una solución inicial, la consola comenzará a mostrar los logs del solucionador, es decir, cómo avanza el progreso de la búsqueda. Cabe destacar que si la consola se queda mucho tiempo sin mostrar nada más que el calculando... (10 minutos o más) es probable que no esté pudiendo encontrar una solución inicial al problema, la que es necesaria para comenzar a iterar. En estos casos recomendamos detener el programa y jugar con los parámetros **input.py** para darle más holgura al problema de optimización y que no esté tan apretado.

Una vez encontrada la solución, el programa abrirá ventanas para mostrar los gráficos de las rutas, imprimirá "Ejecución terminada" y el tiempo que se tardó. Además creará un archivo .csv con la información de dichas rutas, con el nombre **Ruta_optima.csv**. Dicho archivo tiene las columnas: 
- DIA: número del día
- RECOLECTOR: id del recolector
- LOCAL: id del local a visitar
- VAR_TIEMPO: indica los tiempos de holgura que tiene el encuestador para salir a la siguiente ubicación (generalmente hay holguras cuando debe esperar a que se abra un local en algún momento del día)
- LONGITUD y LATITUD: coordenadas de las ubicaciones
- HORARIO_VISITA: horario de funcionamiento del local (AM, PM, DIA)

### Instalación

Para correr el código se necesita instalar Python (sin olvidar aceptar la opción de añadir al PATH del sistema para facilitar la instalación de las librerías y la ejecución del código). Además, se necesitan instalar las siguientes librerías:
- numpy
- pandas
- geopandas
- matplotlib
- ortools

Todas estas librerías se deberían poder instalar haciendo uso del comando en la consola: pip install NOMBRE_LIBRERIA. La única que podría causar problemas es geopandas por algunas de sus dependencias.

Otra alternativa es usar el software Anaconda, el que se encarga de administrar los paquetes de las librerías y facilita la instalación de geopandas.

### Recomendaciones y observaciones

- Creemos importante dar un ejemplo de la administración del almuerzo: se puede ver en la solución final una ruta que visita y encuesta un lugar hasta las 12:56 y luego, el siguiente lugar, termina a las 14:05. Esto significa que desde que terminó el primer lugar hasta que terminó el segundo lugar se demoró 9 minutos (ya que no se considera el almuerzo) de los cuales 5 pertenecen al tiempo de la encuesta y 4 al desplazamiento (si se mantienen los parámetros originales del modelo). Luego, el encuestador puede decidir si parte su hora de almuerzo a las 12:56 o a las 13:05, es decir, almuerza una vez terminado el primer local mencionado (con un descanso de 12:56 a 13:56) o prefiere hacer el segundo directamente y tomarse su descanso de 13:05 a 14:05.

- Para evitar que los encuestadores visiten demasiados lugares el mismo día, recomendamos bajar la velocidad de movimiento, cambiar los depots (lugares de origen y término) a lugares más reales y que no estén al centro de Santiago y jugar con la duración de la encuesta. Cabe destacar que todo esto afecta la rapidez con la que se encuentra la solución final, por lo que se puede ir jugando con el límite de tiempo de ejecución para revisar si desean detenerlo antes de que termine completamente o basta con que corra una cantidad x de tiempo.

- Un caso que se podría presentar es que se tengan 10 encuestadores que deban partir del INE, en ese sentido bastaría con poner 10 veces la latitud y longitud de la ubicación del INE al inicio del archivo excel inicial, de esta manera todos los recolectores partirían y terminarían en el mismo lugar. Una observación interesante de este caso es que se pueden repartir las rutas de manera distinta a lo entregado por el programa, por ejemplo, al encuestador 1 le tocan las rutas 1, 2 y 3, mientras que al encuestador 2 le tocan las rutas 4 y 5, pero quizás el encuestador 1 no puede trabajar el tercer día y, entonces, la ruta 3 la debe hacer el encuestador 2, lo que no causaría ningún problema ya que parten de la misma ubicación.

- Si bien el código está pensado para que los encuestadores partan y terminen en el mismo lugar, esto se puede cambiar fácilmente y podemos conversarlo.

### Comentarios finales

Creemos que el software Open Source OR Tools que encontramos es una aplicación muy poderosa para resolver este tipo de problemas, además de otorgar muchas herramientas para modelar problemas complejos con muchos requerimientos. Si bien al inicio puede ser un poco difícil de manejar y entender solo leyendo el código, la documentación de la librería presenta variados ejemplos relacionados a problemas de ruteos, lo que facilita la comprensión de las distintas secciones del código y su funcionamiento. Asimismo, destacamos la posibilidad de utilizar más herramientas de la librería con el objetivo de mejorar el código actual o modificarlo para los distintos escenarios a los que se ve enfrentado el INE.

En caso de que surja alguna pregunta respecto a nuestra implementación o tienen algún problema, siempre estaremos disponibles y nos pueden escribir a nuestros a correos.

Para finalizar, queremos agradecer la oportunidad de haber podido trabajar en un proyecto así. Como grupo nos motivamos a investigar y conversar sobre las distintas formas de resolver este problema tan complejo y, si bien creemos que todavía se puede hacer y discutir más, estamos contentos con el resultado final y esperamos que les pueda servir.

Muchas gracias por todo y les deseamos un muy buen año 2022.
