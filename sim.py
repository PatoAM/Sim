import csv  # Manejo de la archivo csv
import sys  


#Ordenamiento de lista

def srtf(columna):
    return lambda x: x[columna] 

def contar_procesos():
    return len(Listos) + len(ListSus) + len(Ejecucion) + len(Arribos)

def memlibre(mem):
    return 550 - mem

def expropiar(x=0):
    global Listos
    global Ejecucion
    Listos.append(Ejecucion.pop(0))
    Ejecucion.append(Listos.pop(x))
    Listos.sort(key=srtf(3), reverse=False) 


#Listas utilizadas: 
Arribos = []
Listos = []
ListSus = []
Ejecucion= []
Finalizados = []



# Tratar: el archivo tiene que existir, no puede tener mas de 10 elementos, el formato tiene que ser el correcto
# la extension tiene que ser csv
def controldeArchivo():
    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Ingrese: {sys.argv[0]} <archivo.csv>")
    try:
        with open(arg, "r") as f:
            pass
    except FileNotFoundError:
        raise SystemExit(f"Archivo < {sys.argv[1]} > no encontrado")




def csvtolist():
    global Arribos
    
    with open(sys.argv[1], newline='') as csvfile:
        procesos = csv.reader(csvfile, delimiter="'", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
        for row in procesos: 
            Arribos.append(row[0].split(","))


    Arribos.remove(Arribos[0])
    try: 
        Arribos = list(map(lambda x: list(map(lambda y: int(y), x)), Arribos))
    except ValueError:
        raise SystemExit(f"Formato incorrecto: se espera un archivo con campos numericos.")




#································
controldeArchivo()
csvtolist()

#-------------------------------------------------------------------------------------------------------

#aca podria hacer un control de C_ Arribos, aca es mas facil de manipular porque es una lista
#por ejemplo, si len(Arribos) > 10 lo boleteo a la conc
#por ejemploi si resulta que alguna de las sublistas es len(x) > a 4, osea tiene mas de 4 campos, tambien.
#por ejemplo, si alguna de los campos de la sublista x[i][1] es mayor a 450 (mem total disponible) tambien

#Lo unico que tengo que no puedo hacer aca, es el try: except de tipos que tiene que ser arriba 
##en la función de csvtolist. Ahi tengo que manejar la posibilidad de que el archivo tenga una palabra, un numero decimal
##en la parte donde iria un numero. Y manejar el error : "ValueError". Simple. (Ya esta hecho)

#-------------------------------------------------------------------------------------------------------


print("Cola de Arribos")
for row in Arribos:
    print(row)

Arribos.sort(key=srtf(2), reverse=False)

print("Ordenado (Para la cola de listos)")

for row in Arribos:
    print(row)
print("----------------------------------------------------------------------")


#for x in range(5):
#    listos.append(Arribos.pop(t))
#
#    print(Arribos)
#    print(listos)
#
#print("Arribos:",Arribos)
#print (listos)


t = 0 
procesos = contar_procesos()
mem = 100 ## No puede superar los 550, que seria el total de memoria fisica. Solo 450kb es del usuario.
dir_mem = [] 
while procesos > 0 :
    num_proc = procesos - len(Arribos)
    
    ### INCORPORACION DE PROCESOS NUEVOS A LISTOS O LISTSUS

    #print(num_proc," | " ,Arribos[0][1], "|", memlibre(mem), "|", Arribos[0][0])  borrame
    
    if len(Arribos) > 0:
        if (num_proc <= 5) and (Arribos[0][1] <= memlibre(mem)) and (Arribos[0][2] <= t):
            i=0

            while (Arribos[i][2] <= t) and (i <= len(Arribos)):
                if (num_proc <= 5) and (Arribos[0][1] <= memlibre(mem)) and (Arribos[0][2] <= t):
                    Listos.append(Arribos.pop(0))
                    print("Listos", Listos)
                    mem += Listos[0][1]
                    Listos.sort(key=srtf(3), reverse=False)

                elif (num_proc <= 5) and Arribos[0][2] <=t:
                    ListSus.append(Arribos.pop(0))
                    print("Listos suspendidos", ListSus)
                
                i+=1

        elif (num_proc <= 5) and (Arribos[0][0] <= t):
            ListSus.append(Arribos.pop(0))
            print("Directo a listos suspendidos", ListSus)
    
    ### BUCLE DE "EJECUCION"
    ## [La pregunta: ¿Puede entrar a listos, despues a ejecucion y descontar un t todo en el mismo loop?]
    ## A fines practicos, supongamos que si. Pero hay que revisar.

    ## Esta implementacion contempla a los procesos como si fueran liquidos y la memoria un "recipiente
    ## con capacidad máxima 550ml. Si la memoria de un proceso es menor o igual a la memoria libre, entra.
    ## Es decir, la logica de los huecos, best fit (mejor encaje) todavia no esta implementada.

    ## Pero con esto suficiente para ir implementando el resto del loop principal:
    ## Resumenes estadisticos, logica de colas, srtf, etc. 

    if len(Ejecucion) == 0:
        if len(Listos) > 0:
            Ejecucion.append(Listos.pop(0))

    elif (len(Listos) > 0) and (Ejecucion[0][3] > Listos[0][3]):
        if Listos[0][1] <= memlibre(mem):
            expropiar() 
        else:
            i=1
            while (Listos[i][2] <= t) and (i <= len(Listos)) and (Ejecucion[0][3] > Listos[i][3]):
                if Listos[i][1] <= memlibre(mem):
                    expropiar(i)
    
    if len(Ejecucion) == 1:
        Ejecucion[0][3]-=1

        if Ejecucion[0][3] == 0:
            mem -= Ejecucion[0][1]
            Finalizados.append(Ejecucion.pop(0))
            if len(ListSus) > 0:
                i=0
                while i < len(ListSus):  ##Puede salir mas de uno de Listsus en un mismo t?
                    if ListSus[i][1] <= memlibre(mem):
                        mem+=ListSus[i][1]
                        Listos.append(ListSus.pop(i))
                        Listos.sort(key=srtf(3), reverse=False)
                        i=0
                    i+=1

   
    print(f"""
    t = {t} \n
    Memoria Ocupada:{mem} \n
    Memoria libre: {memlibre(mem)} \n
    Listos: {Listos} \n
    ListSus: {ListSus} \n
    Ejecucion: {Ejecucion} \n
    Finalizados: {Finalizados}
    """)
 

    t = t + 1
    i = 1
    procesos = contar_procesos()
    for row in Listos:
        print(f"Fila{i}", row)
        i+=1

    input("Presione una tecla")

     

    


