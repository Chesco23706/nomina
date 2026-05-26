from __future__ import annotations

from pathlib import Path

from payroll_system.models import Empleado, ResultadoNomina
from payroll_system.payroll import Nomina
from payroll_system.storage import RepositorioEmpleados


class SistemaNomina:
    def __init__(self) -> None:
        self.repositorio = RepositorioEmpleados()
        self.empleados = self.repositorio.cargar()
        self.nomina = Nomina()

    def ejecutar(self) -> None:
        while True:
            self._mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()

            acciones = {
                "1": self.agregar_empleado,
                "2": self.mostrar_empleados,
                "3": self.calcular_nomina,
                "4": self.generar_recibo,
                "5": self.salir,
            }

            accion = acciones.get(opcion)
            if accion:
                accion()
            else:
                print("Opción no válida. Intente de nuevo.\n")

    def agregar_empleado(self) -> None:
        print("\n--- Agregar empleado ---")
        id_empleado = input("ID del empleado: ").strip()
        if self.buscar_empleado(id_empleado):
            print("Ya existe un empleado con ese ID.\n")
            return

        try:
            empleado = Empleado(
                id_empleado=id_empleado,
                nombre=self._leer_texto("Nombre: "),
                puesto=self._leer_texto("Puesto: "),
                salario_base=self._leer_numero("Salario base por hora: "),
                horas_trabajadas=self._leer_numero("Horas trabajadas: "),
            )
        except ValueError as error:
            print(f"Error: {error}\n")
            return

        self.empleados.append(empleado)
        self._guardar_datos()
        print("Empleado agregado correctamente.\n")

    def mostrar_empleados(self) -> None:
        print("\n--- Empleados registrados ---")
        if not self.empleados:
            print("No hay empleados registrados.\n")
            return

        for empleado in self.empleados:
            print(
                f"ID: {empleado.id_empleado} | Nombre: {empleado.nombre} | "
                f"Puesto: {empleado.puesto} | Salario/hora: ${empleado.salario_base:,.2f} | "
                f"Horas: {empleado.horas_trabajadas:,.2f}"
            )

        print("\nAcciones disponibles:")
        print("1. Editar empleado")
        print("2. Eliminar empleado")
        print("3. Volver al menú principal")

        opcion = input("Seleccione una acción: ").strip()
        if opcion == "1":
            self.editar_empleado()
        elif opcion == "2":
            self.eliminar_empleado()
        else:
            print()

    def editar_empleado(self) -> None:
        print("\n--- Editar empleado ---")
        empleado = self._seleccionar_empleado()
        if empleado is None:
            return

        print("Presione Enter para conservar el valor actual.")
        nombre = self._leer_texto_opcional(f"Nombre [{empleado.nombre}]: ")
        puesto = self._leer_texto_opcional(f"Puesto [{empleado.puesto}]: ")
        salario_base = self._leer_numero_opcional(
            f"Salario base por hora [{empleado.salario_base}]: "
        )
        horas_trabajadas = self._leer_numero_opcional(
            f"Horas trabajadas [{empleado.horas_trabajadas}]: "
        )

        empleado.actualizar(
            nombre=nombre,
            puesto=puesto,
            salario_base=salario_base,
            horas_trabajadas=horas_trabajadas,
        )
        self._guardar_datos()
        print("Empleado actualizado correctamente.\n")

    def eliminar_empleado(self) -> None:
        print("\n--- Eliminar empleado ---")
        empleado = self._seleccionar_empleado()
        if empleado is None:
            return

        confirmacion = input(
            f"Confirme eliminación de {empleado.nombre} (s/n): "
        ).strip().lower()
        if confirmacion != "s":
            print("Operación cancelada.\n")
            return

        self.empleados = [
            item for item in self.empleados if item.id_empleado != empleado.id_empleado
        ]
        self._guardar_datos()
        print("Empleado eliminado correctamente.\n")

    def calcular_nomina(self) -> None:
        print("\n--- Calcular nómina ---")
        empleado = self._seleccionar_empleado()
        if empleado is None:
            return

        resultado = self.nomina.calcular(empleado)
        self._mostrar_resultado(resultado)

    def generar_recibo(self) -> None:
        print("\n--- Generar recibo ---")
        empleado = self._seleccionar_empleado()
        if empleado is None:
            return

        resultado = self.nomina.calcular(empleado)
        self._mostrar_resultado(resultado)

        print("Formatos de exportación:")
        print("1. Texto (.txt)")
        print("2. PDF (.pdf)")
        opcion = input("Seleccione el formato: ").strip()

        carpeta = Path("recibos")
        nombre_archivo = f"recibo_{empleado.id_empleado}"

        if opcion == "1":
            ruta = self.nomina.exportar_txt(resultado, carpeta / f"{nombre_archivo}.txt")
        elif opcion == "2":
            ruta = self.nomina.exportar_pdf(resultado, carpeta / f"{nombre_archivo}.pdf")
        else:
            print("Formato no válido.\n")
            return

        print(f"Recibo generado en: {ruta.resolve()}\n")

    def salir(self) -> None:
        self._guardar_datos()
        print("Datos guardados. Hasta luego.")
        raise SystemExit

    def buscar_empleado(self, id_empleado: str) -> Empleado | None:
        return next(
            (empleado for empleado in self.empleados if empleado.id_empleado == id_empleado),
            None,
        )

    def _guardar_datos(self) -> None:
        self.repositorio.guardar(self.empleados)

    def _mostrar_menu(self) -> None:
        print("=== Sistema de Control de Nómina ===")
        print("1. Agregar empleado")
        print("2. Mostrar empleados")
        print("3. Calcular nómina")
        print("4. Generar recibo")
        print("5. Salir")

    def _seleccionar_empleado(self) -> Empleado | None:
        if not self.empleados:
            print("No hay empleados registrados.\n")
            return None

        id_empleado = input("Ingrese el ID del empleado: ").strip()
        empleado = self.buscar_empleado(id_empleado)
        if empleado is None:
            print("Empleado no encontrado.\n")
            return None
        return empleado

    def _mostrar_resultado(self, resultado: ResultadoNomina) -> None:
        print()
        print(resultado.como_texto(self.nomina.porcentaje_isr, self.nomina.porcentaje_imss))
        print()

    def _leer_texto(self, mensaje: str) -> str:
        valor = input(mensaje).strip()
        if not valor:
            raise ValueError("El valor no puede estar vacío.")
        return valor

    def _leer_texto_opcional(self, mensaje: str) -> str | None:
        valor = input(mensaje).strip()
        return valor or None

    def _leer_numero(self, mensaje: str) -> float:
        valor = input(mensaje).strip()
        try:
            numero = float(valor)
        except ValueError as error:
            raise ValueError("Debe ingresar un número válido.") from error

        if numero < 0:
            raise ValueError("El número no puede ser negativo.")
        return numero

    def _leer_numero_opcional(self, mensaje: str) -> float | None:
        valor = input(mensaje).strip()
        if not valor:
            return None

        try:
            numero = float(valor)
        except ValueError:
            print("Valor inválido. Se conservará el dato anterior.")
            return None

        if numero < 0:
            print("No se permiten valores negativos. Se conservará el dato anterior.")
            return None

        return numero
