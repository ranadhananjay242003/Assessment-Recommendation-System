const API_URL = "http://localhost:8000";

const qEl = document.getElementById("query");
const btn = document.getElementById("go");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

async function recommend() {
  const q = qEl.value.trim();
  if (!q) {
    statusEl.textContent = "Enter a query.";
    return;
  }
  btn.disabled = true;
  statusEl.textContent = "Requesting recommendations...";
  resultsEl.innerHTML = "";
  try {
    const resp = await fetch(`${API_URL}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, top_k: 10 }),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }
    const data = await resp.json();
    const assessments = data.recommended_assessments || [];
    statusEl.textContent = `Got ${assessments.length} results.`;
    
    // Create table
    const table = document.createElement("table");
    table.className = "results-table";
    
    // Create header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const headers = ["#", "Assessment Name", "URL"];
    headers.forEach(h => {
      const th = document.createElement("th");
      th.textContent = h;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement("tbody");
    assessments.forEach((item, index) => {
      const tr = document.createElement("tr");
      
      // Index column
      const tdIndex = document.createElement("td");
      tdIndex.textContent = index + 1;
      tr.appendChild(tdIndex);
      
      // Assessment name column
      const tdName = document.createElement("td");
      tdName.textContent = item.name || "(No name)";
      tr.appendChild(tdName);
      
      // URL column
      const tdUrl = document.createElement("td");
      const a = document.createElement("a");
      a.href = item.url || "#";
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "View Assessment";
      tdUrl.appendChild(a);
      tr.appendChild(tdUrl);
      
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    resultsEl.appendChild(table);
  } catch (e) {
    statusEl.textContent = `Error: ${e.message}`;
  } finally {
    btn.disabled = false;
  }
}

btn.addEventListener("click", recommend);
qEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") recommend();
});

