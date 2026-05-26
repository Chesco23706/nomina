from __future__ import annotations

from pathlib import Path

from payroll_system.models import Empleado, ResultadoNomina


class Nomina:
    def __init__(self, porcentaje_isr: float = 10.0, porcentaje_imss: float = 5.0) -> None:
        self.porcentaje_isr = porcentaje_isr
        self.porcentaje_imss = porcentaje_imss

    def calcular(self, empleado: Empleado) -> ResultadoNomina:
        salario_bruto = empleado.salario_base * empleado.horas_trabajadas
        descuento_isr = salario_bruto * (self.porcentaje_isr / 100)
        descuento_imss = salario_bruto * (self.porcentaje_imss / 100)
        salario_neto = salario_bruto - descuento_isr - descuento_imss
        return ResultadoNomina(
            empleado=empleado,
            salario_bruto=salario_bruto,
            descuento_isr=descuento_isr,
            descuento_imss=descuento_imss,
            salario_neto=salario_neto,
        )

    def exportar_txt(self, resultado: ResultadoNomina, ruta: str | Path) -> Path:
        ruta_archivo = Path(ruta)
        ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        contenido = resultado.como_texto(self.porcentaje_isr, self.porcentaje_imss)
        ruta_archivo.write_text(contenido, encoding="utf-8")
        return ruta_archivo

    def exportar_pdf(self, resultado: ResultadoNomina, ruta: str | Path) -> Path:
        ruta_archivo = Path(ruta)
        ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        contenido = resultado.como_texto(self.porcentaje_isr, self.porcentaje_imss).splitlines()
        pdf_bytes = self._crear_pdf_basico(contenido)
        ruta_archivo.write_bytes(pdf_bytes)
        return ruta_archivo

    def _crear_pdf_basico(self, lineas: list[str]) -> bytes:
        def escapar(texto: str) -> str:
            return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        instrucciones = ["BT", "/F1 12 Tf", "50 780 Td", "14 TL"]
        for indice, linea in enumerate(lineas):
            if indice == 0:
                instrucciones.append(f"({escapar(linea)}) Tj")
            else:
                instrucciones.append("T*")
                instrucciones.append(f"({escapar(linea)}) Tj")
        instrucciones.append("ET")
        stream = "\n".join(instrucciones).encode("latin-1", errors="replace")

        objetos = [
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
            (
                b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
            ),
            f"4 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream\nendobj\n",
            b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n",
        ]

        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for objeto in objetos:
            offsets.append(len(pdf))
            pdf.extend(objeto)

        xref_inicio = len(pdf)
        pdf.extend(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

        trailer = (
            f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_inicio}\n%%EOF"
        )
        pdf.extend(trailer.encode("latin-1"))
        return bytes(pdf)
