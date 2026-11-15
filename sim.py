# Simulador de memoria (MVT con Best-Fit) y planificación SRTF.
# El CSV tiene que tener:  id,tam,arribo,irrupcion  (el encabezado es opcional)
import csv
import sys
from rich.console import Console
from rich.table import Table
from rich import print
from rich.panel import Panel
from rich.rule import Rule

MEM_SO = 100          
MEM_USER = 450       
MAX_EN_SISTEMA = 5    # tope entre Ejecución + Listos + Listos/Suspendidos
MAX_PROCESOS = 10   

Arribos = []       
Listos = []
ListSus = []      
Ejecucion = []     
Finalizados = []

# Tabla de particiones de la memoria de usuario. Si pid es None, es un hueco libre
particiones = [{"id": 1, "inicio": MEM_SO, "tam": MEM_USER, "pid": None}]
_sig_id_particion = 2

# Archivo de entrada
def controldeArchivo():
    if len(sys.argv) < 2:
        raise SystemExit(f"Ingrese: {sys.argv[0]} <archivo.csv>")
    ruta = sys.argv[1]
    if not ruta.lower().endswith(".csv"):
        raise SystemExit(f"El archivo < {ruta} > debe tener extensión .csv")
    try:
        with open(ruta, "r"):
            pass
    except FileNotFoundError:
        raise SystemExit(f"Archivo < {ruta} > no encontrado")
    return ruta


def csvtolist(ruta):
    with open(ruta, newline="") as f:
        filas = [r for r in csv.reader(f) if any(c.strip() for c in r)]

    # si la primera fila no es numérica, la tomamos como encabezado y la tiramos
    if filas and not all(c.strip().lstrip("-").isdigit() for c in filas[0]):
        filas.pop(0)

    if not filas:
        raise SystemExit("El archivo no contiene procesos.")
    if len(filas) > MAX_PROCESOS:
        raise SystemExit(f"El archivo tiene {len(filas)} procesos; el máximo es {MAX_PROCESOS}.")

    ids = set()
    for n, fila in enumerate(filas, start=1):
        
        if len(fila) != 4:
            raise SystemExit(f"Proceso {n}: se esperan 4 campos (id,tam,arribo,irrupcion).")
        try:
            pid, tam, arribo, irrupcion = (int(c.strip()) for c in fila)
        except ValueError:
            raise SystemExit(f"Proceso {n}: formato incorrecto, se esperan campos numéricos enteros.")

        if pid in ids:
            raise SystemExit(f"Proceso {n}: el Id {pid} está repetido.")
        if tam <= 0 or irrupcion <= 0 or arribo < 0:
            raise SystemExit(f"Proceso {n}: tamaño e irrupción deben ser > 0 y el arribo >= 0.")
        if tam > MEM_USER:
            raise SystemExit(f"Proceso {n}: pide {tam}K y la memoria de usuario es de {MEM_USER}K.")
        ids.add(pid)
        Arribos.append({"id": pid, "tam": tam, "arribo": arribo,
                        "irrupcion": irrupcion, "TI": irrupcion})

    Arribos.sort(key=lambda p: (p["arribo"], p["id"]))


# MEMORIA: Best-Fit con particiones variables

def best_fit(p):
    # Busca el hueco más chico donde entre p y se lo asigna.
    # Devuelve la partición, o None si no hay ningún hueco que sirva.
    global _sig_id_particion
    huecos = [x for x in particiones if x["pid"] is None and x["tam"] >= p["tam"]]
    if not huecos:
        return None
    h = min(huecos, key=lambda x: x["tam"])
    if h["tam"] > p["tam"]:  # si sobra lugar, partimos el hueco y lo que sobra queda libre al lado
        particiones.insert(particiones.index(h) + 1, {
            "id": _sig_id_particion,
            "inicio": h["inicio"] + p["tam"],
            "tam": h["tam"] - p["tam"],
            "pid": None,
        })
        _sig_id_particion += 1
        h["tam"] = p["tam"]
    h["pid"] = p["id"]
    return h


def liberar(p):
    for x in particiones:
        if x["pid"] == p["id"]:
            x["pid"] = None
    i = 0
    while i < len(particiones) - 1:  # juntamos los huecos libres que quedaron pegados
        a, b = particiones[i], particiones[i + 1]
        if a["pid"] is None and b["pid"] is None:
            a["tam"] += b["tam"]
            particiones.pop(i + 1)
        else:
            i += 1


def en_sistema():
    return len(Listos) + len(ListSus) + len(Ejecucion)



# Planificacion SRTF
def planificar():
    Listos.sort(key=lambda p: (p["TI"], p["arribo"]))
    if not Listos:
        return
    if not Ejecucion:
        Ejecucion.append(Listos.pop(0))
    elif Listos[0]["TI"] < Ejecucion[0]["TI"]:  # llegó uno con menos tiempo TI: sale el actual y entra ese
        Listos.append(Ejecucion.pop())
        Ejecucion.append(Listos.pop(0))
        Listos.sort(key=lambda p: (p["TI"], p["arribo"]))


# Salida

def fmt(lista):
    if not lista:
        return "(vacía)"
    return ", ".join(f"P{p['id']}(TI={p['TI']}, tam={p['tam']}K)" for p in lista)


def mostrar(t, eventos):
    console = Console()
    console.rule(f"[bold cyan]Tick {t} - Estado de Memoria[/]")
    for e in eventos:
        print(f"* {e}")

    if Ejecucion:
        p = Ejecucion[0]
        print(Panel.fit(f"\nProcesador: P{p['id']} (TI {p['TI']} de {p['irrupcion']}) \n"))
    else:
        print(Panel.fit("\nProcesador: ocioso\n"))

    tabla = Table(title="Tabla de particiones", show_lines=True, style='blue')
    tabla.add_column("id. Part")
    tabla.add_column("Inicio")
    tabla.add_column("Tamaño")
    tabla.add_column("Proceso")
    tabla.add_column("Frag. interna")
    for x in particiones:
        if x["pid"] is None:
            tabla.add_row(str(x['id']),str(x['inicio']), str(x['tam']),'libre', '-', style="yellow")
        else:
            tabla.add_row(str(x['id']),str(x['inicio']),str(x['tam']),'P'+str(x['pid']),'0')
    console.print(tabla)

    print(f"\nListos:                 {fmt(Listos)}")
    print(f"Listos y suspendidos:   {fmt(ListSus)}")
    print(f"Nuevos (sin admitir):   {fmt(Arribos)}")
    input("\nPresione Enter para continuar...")


def informe(t_total):
    console = Console()    
    console.rule("Fin de ejecución", style="dim green", characters="=")
    tabla2 = Table(title="INFORME ESTADÍSTICO", show_edge=False , row_styles=["dim", ""])

    tabla2.add_column('Proceso')
    tabla2.add_column('Arribo')
    tabla2.add_column('Irrupción')
    tabla2.add_column('Fin')
    tabla2.add_column('Retorno')
    tabla2.add_column('Espera')
    
    for p in sorted(Finalizados, key=lambda p: p["id"]):
        p["retorno"] = p["fin"] - p["arribo"]
        p["espera"] = p["retorno"] - p["irrupcion"]
        tabla2.add_row('P'+str(p['id']), str(p['arribo']),str(p['irrupcion']),str(p['fin']),str(p['retorno']),str(p['espera']))
    console.print(tabla2)

    n = len(Finalizados)
    print(f"\nTiempo de retorno promedio: {sum(p['retorno'] for p in Finalizados) / n:.2f}")
    print(f"Tiempo de espera promedio:  {sum(p['espera'] for p in Finalizados) / n:.2f}")
    print(f"Rendimiento: {n} trabajos / {t_total} unidades = {n / t_total:.4f} trabajos por unidad de tiempo")


def main():
    ruta = controldeArchivo()
    csvtolist(ruta)

    t = 0
    while Arribos or en_sistema() > 0:
        # si no hay nadie en el sistema, saltamos directo al próximo arribo (así no mostramos ticks vacíos)
        if en_sistema() == 0 and Arribos[0]["arribo"] > t:
            t = Arribos[0]["arribo"]

        eventos = []

        # a) Entran los procesos nuevos (siempre que no pasemos los 5 en el sistema)
        while Arribos and Arribos[0]["arribo"] <= t and en_sistema() < MAX_EN_SISTEMA:
            p = Arribos.pop(0)
            part = best_fit(p)
            if part:
                Listos.append(p)
                eventos.append(f"Arribó P{p['id']} -> Listos (partición {part['id']})")
            else:
                ListSus.append(p)
                eventos.append(f"Arribó P{p['id']} -> Listos y suspendidos (no hay hueco)")

        # b) SRTF: vemos quién tiene que estar en la CPU
        planificar()
        if eventos:
            mostrar(t, eventos)

        # c) La CPU trabaja una unidad de tiempo
        if Ejecucion:
            p = Ejecucion[0]
            p["TI"] -= 1
            t += 1

            # d) Si terminó: liberamos la memoria y vemos si algún suspendido ya entra
            if p["TI"] == 0:
                p["fin"] = t
                liberar(p)
                Finalizados.append(Ejecucion.pop())
                eventos = [f"Terminó P{p['id']}"]
                for q in ListSus[:]:
                    part = best_fit(q)
                    if part:
                        ListSus.remove(q)
                        Listos.append(q)
                        eventos.append(f"P{q['id']} pasa de Listos y suspendidos a Listos (partición {part['id']})")
                planificar()
                mostrar(t, eventos)
        else:
            t += 1

    informe(t)


if __name__ == "__main__":
    main()
