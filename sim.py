import csv  # Manejo de la archivo csv
import sys 
#Ordenamiento de lista

def srtf(columna):
    return lambda x: x[columna] 

C_Arribos=[]



# Tratar: el archivo tiene que existir, no puede tener mas de 10 elementos, el formato tiene que ser el correcto
# la extension tiene que ser csv
def controldeArchivo():
    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Ingrese: {sys.argv[0]} <archivo.csv>")





def csvtolist():
    global C_Arribos
    
    with open(sys.argv[1], newline='') as csvfile:
        procesos = csv.reader(csvfile, delimiter="'", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
        print(procesos)
        for row in procesos: 
            C_Arribos.append(row[0].split(","))


    C_Arribos.remove(C_Arribos[0])

    C_Arribos = list(map(lambda x: list(map(lambda y: int(y), x)), C_Arribos))





#································
controldeArchivo()
csvtolist()

print("Cola de Arribos")
for row in C_Arribos:
    print(row)

C_Arribos.sort(key=srtf(0), reverse=False)

print("Ordenado (Para la cola de listos)")

for row in C_Arribos:
    print(row)


t = 0
listos = []

for x in range(5):
    listos.append(C_Arribos.pop(t))

    print(C_Arribos)
    print(listos)

print("Arribos:",C_Arribos)
print (listos)

