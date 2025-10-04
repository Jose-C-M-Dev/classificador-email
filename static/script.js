document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("emailForm");
  const dropArea = document.getElementById("drop-area");
  const fileInput = document.getElementById("arquivo");
  const fileInfo = document.getElementById("file-info");

  const loader = document.getElementById("loader");
  const resultadoDiv = document.getElementById("resultado");
  const historicoDiv = document.getElementById("historico");

  const statAtualTotal = document.getElementById("stat-atual-total");
  const statAtualProd = document.getElementById("stat-atual-produtivo");
  const statAtualImprod = document.getElementById("stat-atual-improdutivo");

  const statHistTotal = document.getElementById("stat-hist-total");
  const statHistProd = document.getElementById("stat-hist-produtivo");
  const statHistImprod = document.getElementById("stat-hist-improdutivo");

  let historico = [];
  let ultimoResultados = [];
  let filtroAtual = "all";
  let paginaHistorico = 0;
  const HIST_PAGE_SIZE = 5;

  dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("dragover");
  });
  dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("dragover");
  });
  dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragover");
    const dtFiles = e.dataTransfer.files;
    if (!dtFiles) return;
    if (dtFiles.length > 10) {
      alert("Máximo 10 arquivos por envio.");
      return;
    }
    const dataTransfer = new DataTransfer();
    Array.from(dtFiles).forEach(f => dataTransfer.items.add(f));
    fileInput.files = dataTransfer.files;
    updateFileInfo();
  });

  dropArea.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 10) {
      alert("Máximo 10 arquivos por envio.");
      fileInput.value = "";
      fileInfo.innerText = "";
      return;
    }
    updateFileInfo();
  });

  function updateFileInfo() {
    const files = Array.from(fileInput.files || []);
    fileInfo.innerText = files.length ? `Selecionados: ${files.map(f => f.name).join(", ")}` : "";
  }

  function normalizeItem(raw) {
    const arquivo = raw.arquivo || raw.file || raw.name || "Sem nome";
    let categoria = "IMPRODUTIVO";
    let confianca = raw.confianca ?? raw.confidence ?? 0;
    let razao = raw.razao ?? raw.reason ?? "";

    if (raw.classificacao) {
      categoria = raw.classificacao.categoria ?? categoria;
      confianca = raw.classificacao.confianca ?? confianca;
      razao = raw.classificacao.razao ?? razao;
    } else {
      categoria = raw.categoria ?? raw.category ?? categoria;
    }

    const resposta = raw.resposta ?? raw.response ?? raw.answer ?? "";

    return {
      arquivo,
      classificacao: {
        categoria: String(categoria).toUpperCase(),
        confianca: Number(confianca) || 0,
        razao: String(razao || "")
      },
      resposta: String(resposta || "")
    };
  }

  function renderResultadoAtual(list) {
    ultimoResultados = list.map(normalizeItem);

    let exibidos = ultimoResultados;
    if (filtroAtual !== "all") {
      exibidos = ultimoResultados.filter(it => it.classificacao.categoria === filtroAtual);
    }

    const total = ultimoResultados.length;
    const prod = ultimoResultados.filter(i => i.classificacao.categoria === "PRODUTIVO").length;
    const impr = total - prod;

    statAtualTotal.innerText = total;
    statAtualProd.innerText = prod;
    statAtualImprod.innerText = impr;

    if (exibidos.length === 0) {
      resultadoDiv.innerHTML = "<p>Nenhum resultado para este filtro.</p>";
      return;
    }

    resultadoDiv.innerHTML = "";
    exibidos.forEach((it) => {
      const card = document.createElement("div");
      card.className = "resultado-item";
      card.innerHTML = `
        <h3>📄 ${escapeHtml(it.arquivo)} — <span class="tag ${it.classificacao.categoria.toLowerCase()}">${it.classificacao.categoria}</span></h3>
        <pre><code>${escapeHtml(JSON.stringify(it.classificacao, null, 2))}</code></pre>
        <p>Confiança: ${it.classificacao.confianca}%</p>
        <button class="toggle-response">▶ Resposta sugerida</button>
        <div class="resposta-box hidden">${escapeHtml(it.resposta)}</div>
      `;
      const btn = card.querySelector(".toggle-response");
      const box = card.querySelector(".resposta-box");
      btn.addEventListener("click", () => {
        box.classList.toggle("hidden");
        btn.textContent = box.classList.contains("hidden") ? "▶ Resposta sugerida" : "▼ Ocultar resposta";
      });

      resultadoDiv.appendChild(card);
    });
  }

  function renderHistorico() {
    if (historico.length === 0) {
      historicoDiv.innerHTML = "<p>Nenhuma execução ainda.</p>";
      statHistTotal.innerText = 0;
      statHistProd.innerText = 0;
      statHistImprod.innerText = 0;
      return;
    }

    const allItems = historico.flatMap(h => h.resultados.map(normalizeItem));
    statHistTotal.innerText = allItems.length;
    statHistProd.innerText = allItems.filter(i => i.classificacao.categoria === "PRODUTIVO").length;
    statHistImprod.innerText = allItems.filter(i => i.classificacao.categoria !== "PRODUTIVO").length;

    const inicio = paginaHistorico * HIST_PAGE_SIZE;
    const fim = inicio + HIST_PAGE_SIZE;
    const pageItems = historico.slice(inicio, fim);

    historicoDiv.innerHTML = "";

    pageItems.forEach((exec) => {
      const item = document.createElement("div");
      item.className = "historico-item";

      const total = exec.resultados.length;
      const prod = exec.resultados.filter(r => (r.categoria ?? r.classificacao?.categoria ?? "").toUpperCase() === "PRODUTIVO").length;
      const impr = total - prod;

      item.innerHTML = `
        <h4>🕒 ${escapeHtml(exec.timestamp)}</h4>
        <p>Total: ${total} • Produtivos: ${prod} • Improdutivos: ${impr}</p>
        <button class="toggle-details">▶ Ver detalhes</button>
        <div class="detalhes hidden"></div>
      `;
      const btn = item.querySelector(".toggle-details");
      const detalhes = item.querySelector(".detalhes");

      btn.addEventListener("click", () => {
        if (detalhes.classList.contains("hidden")) {
          detalhes.classList.remove("hidden");
          btn.textContent = "▼ Ocultar detalhes";
          if (detalhes.innerHTML.trim() === "") {
            detalhes.innerHTML = exec.resultados.map(r => {
              const n = normalizeItem(r);
              return `
                <div class="resultado-item mini">
                  <strong>📄 ${escapeHtml(n.arquivo)} — ${n.classificacao.categoria}</strong>
                  <pre><code>${escapeHtml(JSON.stringify(n.classificacao, null, 2))}</code></pre>
                  <details><summary>📩 Resposta sugerida</summary><div>${escapeHtml(n.resposta)}</div></details>
                </div>
              `;
            }).join("");
          }
        } else {
          detalhes.classList.add("hidden");
          btn.textContent = "▶ Ver detalhes";
        }
      });

      historicoDiv.appendChild(item);
    });

    const totalPages = Math.ceil(historico.length / HIST_PAGE_SIZE);
    if (totalPages > 1) {
      const nav = document.createElement("div");
      nav.className = "historico-nav";
      nav.innerHTML = `
        <button ${paginaHistorico <= 0 ? "disabled" : ""}>&laquo; Anterior</button>
        <span>Página ${paginaHistorico + 1} de ${totalPages}</span>
        <button ${paginaHistorico >= totalPages - 1 ? "disabled" : ""}>Próxima &raquo;</button>
      `;

      const buttons = nav.querySelectorAll("button");
      const btnPrev = buttons[0];
      const btnNext = buttons[1];

      if (btnPrev) {
        btnPrev.addEventListener("click", () => {
          if (paginaHistorico > 0) {
            paginaHistorico--;
            renderHistorico();
          }
        });
      }

      if (btnNext) {
        btnNext.addEventListener("click", () => {
          if (paginaHistorico < totalPages - 1) {
            paginaHistorico++;
            renderHistorico();
          }
        });
      }

      historicoDiv.appendChild(nav);
    }
  }

  function escapeHtml(s) {
    if (!s && s !== 0) return "";
    return String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData();
    const texto = document.getElementById("texto").value || "";
    if (texto.trim()) fd.append("texto", texto);
    const files = Array.from(fileInput.files || []);
    if (files.length > 10) { alert("Máximo 10 arquivos."); return; }
    files.forEach(f => fd.append("arquivo", f));

    loader.classList.remove("hidden");
    resultadoDiv.innerHTML = "";

    try {
      const resp = await fetch("/process", { method: "POST", body: fd });
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(txt || `Status ${resp.status}`);
      }

      const data = await resp.json();
      let resultadosRaw = [];
      if (Array.isArray(data)) resultadosRaw = data;
      else if (Array.isArray(data.resultados)) resultadosRaw = data.resultados;

      filtroAtual = "all"; // reset filtro
      renderResultadoAtual(resultadosRaw);

      historico.unshift({ timestamp: new Date().toLocaleString(), resultados: resultadosRaw });
      paginaHistorico = 0;
      renderHistorico();

      form.reset();
      fileInfo.innerText = "";
    } catch (err) {
      console.error("Erro no envio:", err);
      resultadoDiv.innerHTML = `<p style="color:red">Erro no processamento: ${escapeHtml(err.message || String(err))}</p>`;
    } finally {
      loader.classList.add("hidden");
    }
  });

  document.querySelectorAll("#stats-atual .circle").forEach(circle => {
    circle.addEventListener("click", () => {
      filtroAtual = circle.dataset.filter || "all";
      renderResultadoAtual(ultimoResultados);
    });
  });

  renderResultadoAtual([]);
  renderHistorico();
});