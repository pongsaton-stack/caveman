(function () {
  const CATEGORY_LABELS = {
    image: "ภาพ",
    video: "วิดีโอ",
    writing: "งานเขียน",
    code: "โค้ด",
    music: "เพลง",
    other: "อื่น ๆ"
  };

  const grid = document.getElementById("worksGrid");
  const emptyState = document.getElementById("emptyState");
  const resultsCount = document.getElementById("resultsCount");
  const searchInput = document.getElementById("searchInput");
  const filterButtons = document.querySelectorAll(".filter-btn");

  const modalOverlay = document.getElementById("modalOverlay");
  const modalClose = document.getElementById("modalClose");
  const modalThumb = document.getElementById("modalThumb");
  const modalCategory = document.getElementById("modalCategory");
  const modalTitle = document.getElementById("modalTitle");
  const modalTool = document.getElementById("modalTool");
  const modalDescription = document.getElementById("modalDescription");
  const modalDate = document.getElementById("modalDate");
  const modalLink = document.getElementById("modalLink");

  let activeCategory = "all";
  let searchTerm = "";

  function formatDate(isoDate) {
    const d = new Date(isoDate);
    if (Number.isNaN(d.getTime())) return isoDate;
    return d.toLocaleDateString("th-TH", { year: "numeric", month: "short", day: "numeric" });
  }

  function matchesFilters(work) {
    const categoryOk = activeCategory === "all" || work.category === activeCategory;
    if (!categoryOk) return false;
    if (!searchTerm) return true;
    const haystack = `${work.title} ${work.tool} ${work.description}`.toLowerCase();
    return haystack.includes(searchTerm);
  }

  function render() {
    const works = (window.AI_WORKS || []).filter(matchesFilters);

    grid.innerHTML = "";
    works.forEach((work) => {
      const card = document.createElement("button");
      card.className = "card";
      card.type = "button";
      card.setAttribute("aria-haspopup", "dialog");
      card.innerHTML = `
        <div class="card-thumb">${work.thumbnail || "✨"}</div>
        <span class="tag">${CATEGORY_LABELS[work.category] || work.category}</span>
        <h3>${work.title}</h3>
        <p>${work.description}</p>
        <div class="card-meta">
          <span>${work.tool}</span>
          <span>${formatDate(work.date)}</span>
        </div>
      `;
      card.addEventListener("click", () => openModal(work));
      grid.appendChild(card);
    });

    emptyState.hidden = works.length !== 0;
    resultsCount.textContent = `พบ ${works.length} ผลงาน`;
  }

  function openModal(work) {
    modalThumb.textContent = work.thumbnail || "✨";
    modalCategory.textContent = CATEGORY_LABELS[work.category] || work.category;
    modalTitle.textContent = work.title;
    modalTool.textContent = `สร้างด้วย ${work.tool}`;
    modalDescription.textContent = work.description;
    modalDate.textContent = formatDate(work.date);
    modalLink.href = work.link || "#";
    modalOverlay.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modalOverlay.hidden = true;
    document.body.style.overflow = "";
  }

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterButtons.forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-selected", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-selected", "true");
      activeCategory = btn.dataset.category;
      render();
    });
  });

  searchInput.addEventListener("input", (e) => {
    searchTerm = e.target.value.trim().toLowerCase();
    render();
  });

  modalClose.addEventListener("click", closeModal);
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modalOverlay.hidden) closeModal();
  });

  render();
})();
