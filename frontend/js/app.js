const API_URL = "http://127.0.0.1:8000";

const input = document.getElementById("buscarServidor");
const infoDiv = document.getElementById("infoServidor");
const detallesServidor = document.getElementById("detallesServidor");
const detallesCosto = document.getElementById("detallesCosto");

input.addEventListener("change", async () => {
  const nombre = input.value.trim();
  if (!nombre) return;

  try {
    const serverResp = await fetch(`${API_URL}/servers/${nombre}`);
    if (!serverResp.ok) throw new Error("Servidor no encontrado");
    const servidor = await serverResp.json();

    detallesServidor.innerHTML = `
      <li class="list-group-item"><b>Nombre:</b> ${servidor.VM}</li>
      <li class="list-group-item"><b>OS:</b> ${servidor["OS according to the VMware Tools"] || servidor["OS according to the configuration file"]}</li>
      <li class="list-group-item"><b>CPUs:</b> ${servidor.CPUs}</li>
      <li class="list-group-item"><b>Memoria:</b> ${servidor.Memory} MiB</li>
      <li class="list-group-item"><b>Disco:</b> ${servidor["Provisioned MiB"]} MiB</li>
      <li class="list-group-item"><b>Datacenter:</b> ${servidor.Datacenter}</li>
    `;

    const quoteResp = await fetch(`${API_URL}/servers/${nombre}/quote`);
    const quote = await quoteResp.json();

    if(quote.detalles.error){
        detallesCosto.innerHTML = `<li class="list-group-item text-danger">${quote.detalles.error}</li>`;
    } else {
        const c = quote.detalles;
        detallesCosto.innerHTML = `
          <li class="list-group-item">CPU: $${c.cpu}</li>
          <li class="list-group-item">RAM: $${c.ram}</li>
          <li class="list-group-item">Almacenamiento: $${c.storage}</li>
          <li class="list-group-item">Licencia OS: $${c.os}</li>
          <li class="list-group-item fw-bold">Total: $${c.total}</li>
        `;
    }

    infoDiv.classList.remove("d-none");
  } catch (error) {
    alert("No se encontró el servidor o hubo un error.");
    infoDiv.classList.add("d-none");
  }
});
