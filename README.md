# Sistema de Control de Nomina

Proyecto en Python para gestionar empleados, calcular nomina y generar recibos.

## Requisitos

- Python 3.10 o superior

## Ejecucion de consola

```bash
python main.py
```

## Aplicacion web recomendada para evaluacion

La carpeta `nomina-app` contiene una version web mas completa, pensada para cubrir la rubrica del programa contable:

- Login y cierre de sesion.
- Proteccion de informacion con endpoints autenticados.
- CRUD de empleados.
- Persistencia con SQLite.
- Calculo por salario por hora, dias trabajados y horas por jornada.
- Desglose de salario bruto, ISR, IMSS y salario neto.
- Recibos imprimibles.
- Dashboard de indicadores.
- Graficas contables con Chart.js.
- Exportacion de reporte CSV.
- Interfaz responsive con Bootstrap e iconos.

Para ejecutarla:

```bash
cd nomina-app/backend
py -3 app.py
```

Luego abre `http://localhost:5000`.

Credenciales de prueba:

```text
Usuario: admin
Contrasena: admin123
```

## Estructura

- `main.py`: punto de entrada de consola
- `payroll_system/models.py`: modelos de dominio
- `payroll_system/payroll.py`: logica de calculo y exportacion
- `payroll_system/storage.py`: persistencia en JSON
- `payroll_system/system.py`: interfaz de consola y flujo principal
- `nomina-app/`: aplicacion web completa
