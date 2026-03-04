/* College ERP — main.js */

// ─── Sidebar toggle (mobile) ────────────────────────────
(function () {
  const toggle  = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");

  function openSidebar() {
    sidebar?.classList.add("open");
    overlay?.classList.add("show");
    document.body.style.overflow = "hidden";
  }
  function closeSidebar() {
    sidebar?.classList.remove("open");
    overlay?.classList.remove("show");
    document.body.style.overflow = "";
  }

  toggle?.addEventListener("click", openSidebar);
  overlay?.addEventListener("click", closeSidebar);
})();

// ─── Auto-dismiss alerts ──────────────────────────────
document.querySelectorAll(".alert[data-auto-dismiss]").forEach((el) => {
  setTimeout(() => {
    el.style.transition = "opacity .4s";
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 400);
  }, 4500);
});

// ─── Progress bars animate on load ────────────────────
window.addEventListener("load", () => {
  document.querySelectorAll(".progress-bar-fill[data-width]").forEach((el) => {
    requestAnimationFrame(() => {
      el.style.width = el.dataset.width + "%";
    });
  });
});

// ─── Student check cards ───────────────────────────────
document.querySelectorAll(".student-check-card").forEach((card) => {
  const cb = card.querySelector("input[type=checkbox]");
  if (!cb) return;
  const sync = () => card.classList.toggle("checked", cb.checked);
  sync();
  cb.addEventListener("change", sync);
  card.addEventListener("click", (e) => {
    if (e.target !== cb) { cb.checked = !cb.checked; sync(); }
  });
});

// ─── Select / Deselect All ─────────────────────────────
document.getElementById("selectAll")?.addEventListener("click", () => {
  document.querySelectorAll(".student-check-card input[type=checkbox]").forEach((cb) => {
    cb.checked = true;
    cb.closest(".student-check-card").classList.add("checked");
  });
});

document.getElementById("deselectAll")?.addEventListener("click", () => {
  document.querySelectorAll(".student-check-card input[type=checkbox]").forEach((cb) => {
    cb.checked = false;
    cb.closest(".student-check-card").classList.remove("checked");
  });
});

// ─── Cascading dropdowns for import form ──────────────
const deptSelect    = document.getElementById("id_department");
const programSelect = document.getElementById("id_program");
const courseSelect  = document.getElementById("id_course");
const classSelect   = document.getElementById("id_class");
const sectionSelect = document.getElementById("id_section");

async function fetchOptions(url, params) {
  const qs  = new URLSearchParams(params);
  const res = await fetch(`${url}?${qs}`);
  return res.json();
}

function fillSelect(sel, data, placeholder) {
  if (!sel) return;
  sel.innerHTML = `<option value="">— ${placeholder} —</option>`;
  data.forEach(({ id, name }) => {
    sel.innerHTML += `<option value="${id}">${name}</option>`;
  });
  sel.disabled = data.length === 0;
}

deptSelect?.addEventListener("change", async () => {
  const data = await fetchOptions("/academics/get-programs/", { department_id: deptSelect.value });
  fillSelect(programSelect, data, "Select Program");
  fillSelect(courseSelect,  [], "Select Course");
  fillSelect(classSelect,   [], "Select Class");
  fillSelect(sectionSelect, [], "Select Section");
});

programSelect?.addEventListener("change", async () => {
  const data = await fetchOptions("/academics/get-courses/", { program_id: programSelect.value });
  fillSelect(courseSelect, data, "Select Course");
  fillSelect(classSelect,  [], "Select Class");
  fillSelect(sectionSelect, [], "Select Section");
});

courseSelect?.addEventListener("change", async () => {
  const data = await fetchOptions("/academics/get-classes/", { course_id: courseSelect.value });
  fillSelect(classSelect, data, "Select Class");
  fillSelect(sectionSelect, [], "Select Section");
});

classSelect?.addEventListener("change", async () => {
  const data = await fetchOptions("/academics/get-sections/", { class_id: classSelect.value });
  fillSelect(sectionSelect, data, "Select Section");
});
