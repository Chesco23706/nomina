# nomina-app

Aplicacion web de control de nomina con Flask, SQLite, SQLAlchemy y frontend en HTML, Bootstrap, Bootstrap Icons, Chart.js y JavaScript.

## Funcionalidades principales

- Acceso seguro con inicio y cierre de sesion.
- Proteccion de endpoints mediante sesion de usuario.
- Alta, consulta, edicion y eliminacion de empleados.
- Validacion de datos en frontend y backend.
- Calculo automatico por salario por hora, dias trabajados y horas por jornada.
- Desglose de salario bruto, ISR, IMSS y salario neto.
- Generacion e impresion de recibos de nomina.
- Panel de indicadores con totales de empleados, salario bruto, deducciones y salario neto.
- Graficas para visualizar salario neto por empleado y distribucion de deducciones.
- Exportacion de reporte contable en CSV.
- Persistencia de informacion en SQLite.

## Credenciales de prueba

```text
Usuario: admin
Contrasena: admin123
```

Para cambiar las credenciales sin modificar codigo:

```powershell
$env:NOMINA_ADMIN_USER="tu_usuario"
$env:NOMINA_ADMIN_PASSWORD="tu_contrasena"
$env:NOMINA_SECRET_KEY="una_clave_larga_y_segura"
```

## Estructura

```text
nomina-app/
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── empleados.py
│   │   ├── nomina.py
│   │   └── __init__.py
│   └── database/
│       └── nomina.db
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── requirements.txt
```

## Instalacion

```bash
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion

```bash
cd backend
py -3 app.py
```

Luego abre [http://localhost:5000](http://localhost:5000).

## Endpoints principales

- `POST /auth/login`
- `GET /auth/status`
- `POST /auth/logout`
- `POST /empleados`
- `GET /empleados`
- `GET /empleados/<id>`
- `PUT /empleados/<id>`
- `DELETE /empleados/<id>`
- `POST /nomina/calcular/<id>`
- `GET /nomina/recibo/<id>`
- `GET /nomina/resumen`
- `GET /nomina/reporte.csv`
