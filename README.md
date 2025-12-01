# Simulación SIR Paralela

Este proyecto simula un modelo **SIR** (Susceptible, Infectado, Recuperado) en una grilla 2D. Cada celda representa a una persona y puede estar Susceptible (0), Infectada (1) o Recuperada (2). La simulación corre día a día y cambia los estados según probabilidades de contagio, recuperación y muerte.  

Se hizo una versión **paralela**, que divide la grilla en bloques y usa varios procesos para que corra más rápido. También guarda estadísticas diarias (S, I, R, nuevas infecciones y R0) y snapshots diarios para poder hacer animaciones.  
Además, existe una versión **secuencial** que corre todo en un solo proceso.

## Requisitos

Python 3 y estas librerías:

```bash
pip install numpy matplotlib imageio
```
## ejecucion secuencial
```bash
python sequential.py --size 1000 --days 365 --out results/seq_1000.npz
```

## ejecucion paralela
para la paralela corra una a la vez, la carpeta results se crea de manera automatica, si su sistema no la detecta creela, luego ejecute uno a la vez. importante, puede correr varios juntos, pero por terminos de rendimiento se sugiere uno por vez
```bash
# 1 worker
python parallel.py --size 1000 --days 365 --workers 1 --out results/par_1.npz

# 2 workers
python parallel.py --size 1000 --days 365 --workers 2 --out results/par_2.npz

# 4 workers
python parallel.py --size 1000 --days 365 --workers 4 --out results/par_4.npz

# 8 workers
python parallel.py --size 1000 --days 365 --workers 8 --out results/par_8.npz
``` 

## grafica y csv
para esto corra
```bash
run_scaling.py 
``` 
en caso de arrojar unrecognized arguments: --snap_interval 0, corra de nuevo los workers