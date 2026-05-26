const API_BASE_URL = window.location.origin;

const loginView = document.getElementById("login-view");
const appView = document.getElementById("app-view");
const loginForm = document.getElementById("login-form");
const loginAlert = document.getElementById("login-alert");
const logoutButton = document.getElementById("logout-btn");
const sessionLabel = document.getElementById("session-label");
const form = document.getElementById("empleado-form");
const tbody = document.getElementById("empleados-tbody");
const alertContainer = document.getElementById("alert-container");
const formTitle = document.getElementById("form-title");
const submitButton = document.getElementById("submit-btn");
const resetFormButton = document.getElementById("reset-form-btn");
const reloadButton = document.getElementById("reload-btn");
const downloadReportButton = document.getElementById("download-report-btn");
const modalElement = document.getElementById("resultadoModal");
const modalBody = document.getElementById("resultado-modal-body");
const modalTitle = document.getElementById("resultadoModalLabel");
const printReceiptButton = document.getElementById("print-receipt-btn");
const lastUpdateLabel = document.getElementById("last-update-label");
const resultadoModal = new bootstrap.Modal(modalElement);

let ultimoResultado = null;
let ultimoTituloModal = "Recibo de nomina";
let payrollChart = null;
let deductionChart = null;

document.addEventListener("DOMContentLoaded", inicializar);
window.editarEmpleado = editarEmpleado;
window.eliminarEmpleado = eliminarEmpleado;
window.calcularNomina = calcularNomina;
window.verRecibo = verRecibo;

async function inicializar() {
    loginForm.addEventListener("submit", iniciarSesion);
    logoutButton.addEventListener("click", cerrarSesion);
    form.addEventListener("submit", guardarEmpleado);
    resetFormButton.addEventListener("click", resetFormulario);
    reloadButton.addEventListener("click", cargarPanel);
    downloadReportButton.addEventListener("click", descargarReporte);
    printReceiptButton.addEventListener("click", imprimirReciboActual);

    try {
        const estado = await request("/auth/status");
        if (estado.autenticado) {
            mostrarApp(estado.usuario);
            await cargarPanel();
        } else {
            mostrarLogin();
        }
    } catch (error) {
        mostrarLogin();
        mostrarLoginAlerta(error.message, "danger");
    }
}

async function iniciarSesion(event) {
    event.preventDefault();
    if (!loginForm.checkValidity()) {
        loginForm.classList.add("was-validated");
        return;
    }

    try {
        const respuesta = await request("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                usuario: document.getElementById("usuario").value.trim(),
                password: document.getElementById("password").value,
            }),
        });
        mostrarApp({ usuario: respuesta.usuario, rol: "Administrador" });
        await cargarPanel();
    } catch (error) {
        mostrarLoginAlerta(error.message, "danger");
    }
}

async function cerrarSesion() {
    await request("/auth/logout", { method: "POST" }).catch(() => null);
    resetFormulario();
    tbody.innerHTML = "";
    mostrarLogin();
}

function mostrarLogin() {
    loginView.classList.remove("d-none");
    appView.classList.add("d-none");
}

function mostrarApp(usuario) {
    loginView.classList.add("d-none");
    appView.classList.remove("d-none");
    sessionLabel.textContent = usuario ? `${usuario.rol}: ${usuario.usuario}` : "";
}

async function cargarPanel() {
    tbody.innerHTML = `
        <tr>
                <td colspan="7" class="text-center text-muted py-4">Cargando empleados...</td>
        </tr>
    `;

    try {
        const [empleados, resumen] = await Promise.all([
            request("/empleados"),
            request("/nomina/resumen"),
        ]);
        renderTabla(empleados);
        renderResumen(resumen);
        lastUpdateLabel.textContent = `Actualizado ${new Date().toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" })}`;
    } catch (error) {
        renderTabla([]);
        mostrarAlerta(error.message, "danger");
        if (error.status === 401) {
            mostrarLogin();
        }
    }
}

function renderTabla(empleados) {
    if (!empleados.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">No hay empleados registrados.</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = empleados.map((empleado) => `
        <tr>
            <td>${empleado.id}</td>
            <td>${escapeHtml(empleado.nombre)}</td>
            <td>${escapeHtml(empleado.puesto)}</td>
            <td>${formatoMoneda(empleado.salario_base)}</td>
            <td>${Number(empleado.dias_trabajados ?? empleado.horas_trabajadas).toFixed(2)}</td>
            <td>${Number(obtenerHorasJornada(empleado)).toFixed(2)}</td>
            <td class="text-end">
                <div class="actions-group">
                    <button class="btn btn-outline-primary btn-sm" onclick="editarEmpleado(${empleado.id})">
                        <i class="bi bi-pencil-square"></i> Editar
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="eliminarEmpleado(${empleado.id})">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button class="btn btn-outline-success btn-sm" onclick="calcularNomina(${empleado.id})">
                        <i class="bi bi-calculator"></i> Calcular
                    </button>
                    <button class="btn btn-outline-dark btn-sm" onclick="verRecibo(${empleado.id})">
                        <i class="bi bi-receipt"></i> Recibo
                    </button>
                </div>
            </td>
        </tr>
    `).join("");
}

function renderResumen(resumen) {
    const totales = resumen.totales || {};
    const detalle = resumen.detalle || [];
    const deducciones = Number(totales.isr || 0) + Number(totales.imss || 0);

    document.getElementById("metric-empleados").textContent = totales.empleados || 0;
    document.getElementById("metric-bruto").textContent = formatoMoneda(totales.salario_bruto || 0);
    document.getElementById("metric-deducciones").textContent = formatoMoneda(deducciones);
    document.getElementById("metric-neto").textContent = formatoMoneda(totales.salario_neto || 0);

    renderGraficas(detalle, totales);
}

function renderGraficas(detalle, totales) {
    const nombres = detalle.map((item) => item.empleado.nombre);
    const netos = detalle.map((item) => item.salario_neto);
    const ctxPayroll = document.getElementById("payroll-chart");
    const ctxDeductions = document.getElementById("deduction-chart");

    if (payrollChart) {
        payrollChart.destroy();
    }
    if (deductionChart) {
        deductionChart.destroy();
    }

    payrollChart = new Chart(ctxPayroll, {
        type: "bar",
        data: {
            labels: nombres.length ? nombres : ["Sin datos"],
            datasets: [{
                label: "Salario neto",
                data: netos.length ? netos : [0],
                backgroundColor: "#0d6efd",
                borderRadius: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } },
        },
    });

    deductionChart = new Chart(ctxDeductions, {
        type: "doughnut",
        data: {
            labels: ["Neto", "ISR", "IMSS"],
            datasets: [{
                data: [totales.salario_neto || 0, totales.isr || 0, totales.imss || 0],
                backgroundColor: ["#198754", "#ffc107", "#0dcaf0"],
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } },
        },
    });
}

async function guardarEmpleado(event) {
    event.preventDefault();

    const empleadoId = document.getElementById("empleado-id").value;
    const payload = obtenerPayloadEmpleado();

    if (!payload) {
        form.classList.add("was-validated");
        mostrarAlerta("Revisa que nombre, puesto, salario por hora, dias y horas por jornada tengan valores validos.", "warning");
        return;
    }

    try {
        if (empleadoId) {
            await request(`/empleados/${empleadoId}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            });
            mostrarAlerta("Empleado actualizado correctamente.", "success");
        } else {
            await request("/empleados", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            mostrarAlerta("Empleado agregado correctamente.", "success");
        }

        resetFormulario();
        cargarPanel();
    } catch (error) {
        mostrarAlerta(error.message, "danger");
    }
}

function obtenerPayloadEmpleado() {
    const nombre = document.getElementById("nombre").value.trim();
    const puesto = document.getElementById("puesto").value.trim();
    const salarioBase = Number(document.getElementById("salario_base").value);
    const diasTrabajados = Number(document.getElementById("dias_trabajados").value);
    const horasJornada = Number(document.getElementById("horas_jornada").value);

    if (
        !nombre
        || !puesto
        || !Number.isFinite(salarioBase)
        || !Number.isFinite(diasTrabajados)
        || !Number.isFinite(horasJornada)
    ) {
        return null;
    }

    if (salarioBase < 0 || diasTrabajados < 0 || horasJornada < 0) {
        return null;
    }

    return {
        nombre,
        puesto,
        salario_base: salarioBase,
        dias_trabajados: diasTrabajados,
        horas_jornada: horasJornada,
    };
}

async function editarEmpleado(id) {
    try {
        const empleado = await request(`/empleados/${id}`);
        document.getElementById("empleado-id").value = empleado.id;
        document.getElementById("nombre").value = empleado.nombre;
        document.getElementById("puesto").value = empleado.puesto;
        document.getElementById("salario_base").value = empleado.salario_base;
        document.getElementById("dias_trabajados").value = empleado.dias_trabajados ?? empleado.horas_trabajadas;
        document.getElementById("horas_jornada").value = obtenerHorasJornada(empleado);
        form.classList.remove("was-validated");
        formTitle.textContent = "Editar empleado";
        submitButton.innerHTML = '<i class="bi bi-save me-1"></i> Actualizar empleado';
        resetFormButton.classList.remove("d-none");
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
        mostrarAlerta(error.message, "danger");
    }
}

async function eliminarEmpleado(id) {
    const confirmado = window.confirm("Deseas eliminar este empleado?");
    if (!confirmado) {
        return;
    }

    try {
        await request(`/empleados/${id}`, { method: "DELETE" });
        mostrarAlerta("Empleado eliminado correctamente.", "success");
        if (document.getElementById("empleado-id").value === String(id)) {
            resetFormulario();
        }
        cargarPanel();
    } catch (error) {
        mostrarAlerta(error.message, "danger");
    }
}

async function calcularNomina(id) {
    try {
        const resultado = await request(`/nomina/calcular/${id}`, { method: "POST" });
        modalTitle.textContent = `Nomina de ${resultado.empleado.nombre}`;
        modalBody.innerHTML = crearHtmlResultado(resultado, false);
        ultimoResultado = resultado;
        ultimoTituloModal = modalTitle.textContent;
        resultadoModal.show();
    } catch (error) {
        mostrarAlerta(error.message, "danger");
    }
}

async function verRecibo(id) {
    try {
        const resultado = await request(`/nomina/recibo/${id}`);
        modalTitle.textContent = `Recibo de ${resultado.empleado.nombre}`;
        modalBody.innerHTML = crearHtmlResultado(resultado, true);
        ultimoResultado = resultado;
        ultimoTituloModal = modalTitle.textContent;
        resultadoModal.show();
    } catch (error) {
        mostrarAlerta(error.message, "danger");
    }
}

function crearHtmlResultado(resultado, incluirCabecera) {
    return `
        ${incluirCabecera ? `
            <div class="receipt-summary mb-3">
                <div><strong>Empleado:</strong> ${escapeHtml(resultado.empleado.nombre)}</div>
                <div><strong>Puesto:</strong> ${escapeHtml(resultado.empleado.puesto)}</div>
                <div><strong>Salario por hora:</strong> ${formatoMoneda(resultado.empleado.salario_base)}</div>
                <div><strong>Dias trabajados:</strong> ${Number(resultado.empleado.dias_trabajados ?? resultado.empleado.horas_trabajadas).toFixed(2)}</div>
                <div><strong>Horas por jornada:</strong> ${Number(obtenerHorasJornada(resultado.empleado)).toFixed(2)}</div>
            </div>
        ` : ""}
        <div class="receipt-line">
            <span>Salario bruto</span>
            <span class="payroll-value">${formatoMoneda(resultado.salario_bruto)}</span>
        </div>
        <div class="receipt-line">
            <span>ISR (${resultado.porcentajes.isr}%)</span>
            <span>-${formatoMoneda(resultado.isr)}</span>
        </div>
        <div class="receipt-line">
            <span>IMSS (${resultado.porcentajes.imss}%)</span>
            <span>-${formatoMoneda(resultado.imss)}</span>
        </div>
        <div class="receipt-line">
            <span><strong>Salario neto</strong></span>
            <span class="payroll-value text-success">${formatoMoneda(resultado.salario_neto)}</span>
        </div>
    `;
}

function resetFormulario() {
    form.reset();
    form.classList.remove("was-validated");
    document.getElementById("empleado-id").value = "";
    formTitle.textContent = "Agregar empleado";
    submitButton.innerHTML = '<i class="bi bi-save me-1"></i> Guardar empleado';
    resetFormButton.classList.add("d-none");
}

function descargarReporte() {
    window.location.href = `${API_BASE_URL}/nomina/reporte.csv`;
}

function imprimirReciboActual() {
    if (!ultimoResultado) {
        mostrarAlerta("Primero abre un recibo o calculo de nomina.", "warning");
        return;
    }

    const ventana = window.open("", "_blank", "width=900,height=700");
    if (!ventana) {
        mostrarAlerta("El navegador bloqueo la ventana de impresion.", "warning");
        return;
    }

    ventana.document.open();
    ventana.document.write(crearPlantillaImpresion(ultimoResultado, ultimoTituloModal));
    ventana.document.close();
}

function crearPlantillaImpresion(resultado, titulo) {
    const fecha = new Date().toLocaleString("es-MX");
    return `
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>${escapeHtml(titulo)}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 32px; color: #212529; }
                .header { border-bottom: 3px solid #0d6efd; margin-bottom: 24px; padding-bottom: 12px; }
                .header h1 { margin: 0 0 8px; font-size: 28px; }
                .line { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #dcdfe3; }
                .summary { margin: 20px 0; padding: 16px; background: #f8f9fa; border: 1px solid #dcdfe3; border-radius: 10px; }
                .net { font-weight: 700; font-size: 18px; color: #198754; }
                @media print { body { margin: 16px; } }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>${escapeHtml(titulo)}</h1>
                <div>Fecha de impresion: ${escapeHtml(fecha)}</div>
            </div>
            <div class="summary">
                <div><strong>Empleado:</strong> ${escapeHtml(resultado.empleado.nombre)}</div>
                <div><strong>ID:</strong> ${resultado.empleado.id}</div>
                <div><strong>Puesto:</strong> ${escapeHtml(resultado.empleado.puesto)}</div>
                <div><strong>Salario por hora:</strong> ${formatoMoneda(resultado.empleado.salario_base)}</div>
                <div><strong>Dias trabajados:</strong> ${Number(resultado.empleado.dias_trabajados ?? resultado.empleado.horas_trabajadas).toFixed(2)}</div>
                <div><strong>Horas por jornada:</strong> ${Number(obtenerHorasJornada(resultado.empleado)).toFixed(2)}</div>
            </div>
            <div class="line"><span>Salario bruto</span><span>${formatoMoneda(resultado.salario_bruto)}</span></div>
            <div class="line"><span>ISR (${resultado.porcentajes.isr}%)</span><span>-${formatoMoneda(resultado.isr)}</span></div>
            <div class="line"><span>IMSS (${resultado.porcentajes.imss}%)</span><span>-${formatoMoneda(resultado.imss)}</span></div>
            <div class="line net"><span>Salario neto</span><span>${formatoMoneda(resultado.salario_neto)}</span></div>
            <script>window.addEventListener("load", () => window.print());</script>
        </body>
        </html>
    `;
}

async function request(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const detalle = Array.isArray(data.detalles) ? data.detalles.join(" ") : "";
        const error = new Error(data.mensaje || data.error || detalle || "Ocurrio un error en la solicitud.");
        error.status = response.status;
        throw error;
    }

    return data;
}

function mostrarAlerta(mensaje, tipo = "success") {
    alertContainer.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            ${escapeHtml(mensaje)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        </div>
    `;
}

function mostrarLoginAlerta(mensaje, tipo = "danger") {
    loginAlert.innerHTML = `
        <div class="alert alert-${tipo}" role="alert">
            ${escapeHtml(mensaje)}
        </div>
    `;
}

function obtenerHorasJornada(empleado) {
    return empleado.horas_jornada ?? empleado.horas_trabajadas ?? 0;
}

function formatoMoneda(valor) {
    return Number(valor || 0).toLocaleString("es-MX", {
        style: "currency",
        currency: "MXN",
    });
}

function escapeHtml(texto) {
    return String(texto)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
