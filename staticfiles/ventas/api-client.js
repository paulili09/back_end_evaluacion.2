const statusMessage = document.querySelector("#status");
const loader = document.querySelector("#loader");
let accessToken = "";
const state = { productos: [], clientes: [], ventas: [], "detalles-venta": [] };

function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    if (loader) statusMessage.prepend(loader);
    statusMessage.dataset.error = isError ? "true" : "false";
}

function setLoading(loading) {
    if (loader) loader.hidden = !loading;
}

function showSkeleton(resource) {
    const bodyId = resource === "productos" ? "products" : resource === "clientes" ? "clients" : resource === "ventas" ? "sales" : "details";
    const body = document.querySelector(`#${bodyId}`);
    const columns = body.closest("table").querySelectorAll("thead th").length;
    body.replaceChildren(...Array.from({length: 3}, () => {
        const row = document.createElement("tr");
        row.className = "skeleton-row";
        for (let index = 0; index < columns; index += 1) {
            const cell = document.createElement("td");
            const placeholder = document.createElement("span");
            placeholder.className = "skeleton";
            cell.appendChild(placeholder);
            row.appendChild(cell);
        }
        return row;
    }));
}

async function apiRequest(path, options = {}) {
    setLoading(true);
    try {
        const response = await fetch(`/api/${path}`, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
                ...(options.headers || {}),
            },
        });
        if (!response.ok) {
            const detail = await response.json().catch(() => ({}));
            throw new Error(`${response.status}: ${JSON.stringify(detail)}`);
        }
        return response.status === 204 ? null : response.json();
    } finally {
        setLoading(false);
    }
}

function actionCell(id) {
    const cell = document.createElement("td");
    cell.className = "row-actions";
    const edit = document.createElement("button");
    edit.className = "btn btn-light btn-small";
    edit.type = "button";
    edit.textContent = "Editar";
    edit.dataset.edit = id;
    const remove = document.createElement("button");
    remove.className = "btn btn-danger btn-small";
    remove.type = "button";
    remove.textContent = "Eliminar";
    remove.dataset.delete = id;
    cell.append(edit, remove);
    return cell;
}

function textCell(value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";
    return cell;
}

function renderProducts() {
    const body = document.querySelector("#products");
    body.replaceChildren(...state.productos.map((item) => {
        const row = document.createElement("tr");
        row.append(textCell(item.nombre), textCell(item.sku), textCell(`$${Number(item.precio).toLocaleString("es-CL")}`), textCell(item.stock), textCell(item.activo ? "Activo" : "Inactivo"), actionCell(item.id));
        return row;
    }));
}

function renderClients() {
    const body = document.querySelector("#clients");
    body.replaceChildren(...state.clientes.map((item) => {
        const row = document.createElement("tr");
        row.append(textCell(item.nombre), textCell(item.email || "Sin correo"), actionCell(item.id));
        return row;
    }));
    const select = document.querySelector("#sale-client");
    const selected = select.value;
    select.replaceChildren(new Option("Cliente general", ""));
    state.clientes.forEach((item) => select.add(new Option(item.nombre, item.id)));
    select.value = selected;
}

function renderSales() {
    const body = document.querySelector("#sales");
    body.replaceChildren(...state.ventas.map((item) => {
        const row = document.createElement("tr");
        row.className = "expandable";
        row.dataset.saleId = item.id;
        const client = state.clientes.find((value) => value.id === item.cliente);
        row.append(textCell(item.id), textCell(client ? client.nombre : "Cliente general"), textCell(item.fecha ? new Date(item.fecha).toLocaleString("es-CL") : ""), textCell(`$${Number(item.total || 0).toLocaleString("es-CL")}`), actionCell(item.id));
        return row;
    }));
}

function renderDetails() {
    const body = document.querySelector("#details");
    const productName = (id) => state.productos.find((item) => item.id === id)?.nombre || id;
    body.replaceChildren(...state["detalles-venta"].map((item) => {
        const row = document.createElement("tr");
        row.append(textCell(item.id), textCell(item.venta), textCell(productName(item.producto)), textCell(item.cantidad), textCell(`$${Number(item.subtotal || 0).toLocaleString("es-CL")}`), actionCell(item.id));
        return row;
    }));
    const saleSelect = document.querySelector("#detail-sale");
    const productSelect = document.querySelector("#detail-product");
    const selectedSale = saleSelect.value;
    const selectedProduct = productSelect.value;
    saleSelect.replaceChildren();
    productSelect.replaceChildren();
    state.ventas.forEach((item) => saleSelect.add(new Option(`Venta #${item.id}`, item.id)));
    state.productos.forEach((item) => productSelect.add(new Option(`${item.nombre} (${item.stock} disponibles)`, item.id)));
    saleSelect.value = selectedSale;
    productSelect.value = selectedProduct;
}

async function loadResource(resource) {
    try {
        showSkeleton(resource);
        state[resource] = await apiRequest(`${resource}/`);
        if (resource === "productos") renderProducts();
        if (resource === "clientes") renderClients();
        if (resource === "ventas") renderSales();
        if (resource === "detalles-venta") renderDetails();
        showStatus(`${state[resource].length} registro(s) de ${resource} cargado(s).`);
    } catch (error) {
        showStatus(`No se pudo cargar ${resource}: ${error.message}`, true);
    }
}

document.querySelector("#login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        const response = await fetch("/api/token/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username: document.querySelector("#username").value, password: document.querySelector("#password").value}),
        });
        if (!response.ok) throw new Error("Credenciales inválidas.");
        accessToken = (await response.json()).access;
        document.querySelectorAll("button:disabled").forEach((button) => { button.disabled = false; });
        showStatus("Autenticación correcta.");
        await Promise.all(["productos", "clientes", "ventas"].map(loadResource));
        renderDetails();
    } catch (error) {
        showStatus(error.message, true);
    }
});

document.querySelectorAll(".load-resource").forEach((button) => button.addEventListener("click", () => loadResource(button.dataset.resource)));

document.querySelector("#sales").addEventListener("click", (event) => {
    if (event.target.closest("button")) return;
    const row = event.target.closest("[data-sale-id]");
    if (!row) return;
    const existing = row.nextElementSibling;
    if (existing?.classList.contains("expanded-row")) {
        existing.remove();
        return;
    }
    const sale = state.ventas.find((item) => String(item.id) === row.dataset.saleId);
    const details = sale?.detalles || [];
    const expanded = document.createElement("tr");
    expanded.className = "expanded-row";
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = details.length
        ? details.map((detail) => `Producto #${detail.producto}: ${detail.cantidad} unidad(es)`).join(" | ")
        : "Esta venta todavía no tiene detalles.";
    expanded.appendChild(cell);
    row.after(expanded);
});

function bindForm(formId, resource, readPayload, fillForm, resetForm) {
    const form = document.querySelector(formId);
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const id = form.querySelector("input[type=hidden]").value;
        try {
            await apiRequest(`${resource}/${id ? `${id}/` : ""}`, {method: id ? "PUT" : "POST", body: JSON.stringify(readPayload())});
            resetForm();
            await loadResource(resource);
            showStatus(id ? `${resource} actualizado.` : `${resource} creado.`);
        } catch (error) {
            showStatus(`No se pudo guardar: ${error.message}`, true);
        }
    });
    form.querySelector("[data-cancel]")?.addEventListener("click", resetForm);
    form._fill = fillForm;
}

function resetProduct() {
    document.querySelector("#product-form").reset();
    document.querySelector("#product-id").value = "";
    document.querySelector("#product-active").checked = true;
    document.querySelector("#product-form-title").textContent = "Crear producto";
    document.querySelector("#cancel-product").hidden = true;
}

function resetClient() {
    document.querySelector("#client-form").reset();
    document.querySelector("#client-id").value = "";
    document.querySelector("#client-form-title").textContent = "Crear cliente";
    document.querySelector("#cancel-client").hidden = true;
}

function resetSale() {
    document.querySelector("#sale-form").reset();
    document.querySelector("#sale-id").value = "";
    document.querySelector("#sale-form-title").textContent = "Crear venta";
    document.querySelector("#cancel-sale").hidden = true;
}

bindForm("#product-form", "productos", () => ({
    nombre: document.querySelector("#product-name").value.trim(),
    sku: document.querySelector("#product-sku").value.trim(),
    precio: document.querySelector("#product-price").value,
    stock: Number(document.querySelector("#product-stock").value),
    activo: document.querySelector("#product-active").checked,
}), null, resetProduct);
bindForm("#client-form", "clientes", () => ({
    nombre: document.querySelector("#client-name").value.trim(),
    email: document.querySelector("#client-email").value.trim() || null,
}), null, resetClient);
bindForm("#sale-form", "ventas", () => ({
    cliente: document.querySelector("#sale-client").value || null,
}), null, resetSale);
bindForm("#detail-form", "detalles-venta", () => ({
    venta: Number(document.querySelector("#detail-sale").value),
    producto: Number(document.querySelector("#detail-product").value),
    cantidad: Number(document.querySelector("#detail-quantity").value),
    precio_unitario: document.querySelector("#detail-price").value || null,
}), null, () => {
    document.querySelector("#detail-form").reset();
    document.querySelector("#detail-id").value = "";
    document.querySelector("#detail-form-title").textContent = "Crear detalle de venta";
    document.querySelector("#cancel-detail").hidden = true;
});

document.querySelector("#cancel-product").addEventListener("click", resetProduct);
document.querySelector("#cancel-client").addEventListener("click", resetClient);
document.querySelector("#cancel-sale").addEventListener("click", resetSale);
document.querySelector("#cancel-detail").addEventListener("click", () => {
    document.querySelector("#detail-form").reset();
    document.querySelector("#detail-id").value = "";
    document.querySelector("#detail-form-title").textContent = "Crear detalle de venta";
    document.querySelector("#cancel-detail").hidden = true;
});

document.querySelector("main").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-edit], [data-delete]");
    if (!button) return;
    const tableId = button.closest("tbody").id;
    const resource = tableId === "products" ? "productos" : tableId === "clients" ? "clientes" : tableId === "sales" ? "ventas" : "detalles-venta";
    const id = button.dataset.edit || button.dataset.delete;
    if (button.dataset.delete) {
        if (!window.confirm(`¿Eliminar este registro de ${resource}?`)) return;
        try {
            await apiRequest(`${resource}/${id}/`, {method: "DELETE"});
            await loadResource(resource);
            showStatus(`${resource} eliminado.`);
        } catch (error) {
            showStatus(`No se pudo eliminar: ${error.message}`, true);
        }
        return;
    }
    try {
        const item = await apiRequest(`${resource}/${id}/`);
        if (resource === "productos") {
            document.querySelector("#product-id").value = item.id;
            document.querySelector("#product-name").value = item.nombre;
            document.querySelector("#product-sku").value = item.sku;
            document.querySelector("#product-price").value = item.precio;
            document.querySelector("#product-stock").value = item.stock;
            document.querySelector("#product-active").checked = item.activo;
            document.querySelector("#product-form-title").textContent = "Editar producto";
            document.querySelector("#cancel-product").hidden = false;
        } else if (resource === "clientes") {
            document.querySelector("#client-id").value = item.id;
            document.querySelector("#client-name").value = item.nombre;
            document.querySelector("#client-email").value = item.email || "";
            document.querySelector("#client-form-title").textContent = "Editar cliente";
            document.querySelector("#cancel-client").hidden = false;
        } else if (resource === "ventas") {
            document.querySelector("#sale-id").value = item.id;
            document.querySelector("#sale-client").value = item.cliente || "";
            document.querySelector("#sale-form-title").textContent = "Editar venta";
            document.querySelector("#cancel-sale").hidden = false;
        } else {
            document.querySelector("#detail-id").value = item.id;
            document.querySelector("#detail-sale").value = item.venta;
            document.querySelector("#detail-product").value = item.producto;
            document.querySelector("#detail-quantity").value = item.cantidad;
            document.querySelector("#detail-price").value = item.precio_unitario || "";
            document.querySelector("#detail-form-title").textContent = "Editar detalle de venta";
            document.querySelector("#cancel-detail").hidden = false;
        }
    } catch (error) {
        showStatus(`No se pudo cargar: ${error.message}`, true);
    }
});
