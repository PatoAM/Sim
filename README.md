# simuladorSO

## Instrucciones de uso

Binarios del simulador para Linux y Windows (x86-64). Hay archivos de ejemplo de csvprocesos/.


Para usarse debe pasar el archivo `.csv` de los modelos de lote como argumento. 

- **Linux:**  
    `chmod +x ./sim-so-linux-v101-x64`  
    `./sim-so-linux-v101-x64 <ruta a lote.csv>`

<img width="873" height="395" alt="Pasted image 20261117164308" src="https://github.com/user-attachments/assets/28445405-c885-4a99-a3ec-03302bc52963" />

- **Windows:**
    - cmd  
        `sim-so-windows-v101-64.exe <ruta a lote.csv>`
    - Powershell  
        `.\sim-so-windows-v101-64.exe <ruta a lote.csv>`

--- 

En caso de que se desee correr el simulador desde el código fuente se deben instalar las dependencias desde `requirements.txt` de la siguiente manera:

**Linux**
```zsh 
cd Sim-main\ 
python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
``` 
**Windows cmd**
```zsh 
cd Sim-main\ 
python -m venv .venv
.venv\Scripts\activate  
pip install -r requirements.txt
``` 

Finalmente, ejecutar: 
```zsh 
python sim.py <ruta a lote.csv>
``` 


