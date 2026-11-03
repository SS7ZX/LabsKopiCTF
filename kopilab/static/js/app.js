document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash").forEach((message) => {
    window.setTimeout(() => message.classList.add("flash-dismissed"), 6000);
  });

  const filter = document.querySelector("#lab-filter");
  if (filter) {
    filter.addEventListener("change", () => {
      document.querySelectorAll(".lab-card").forEach((card) => {
        card.hidden = filter.value !== "all" && card.dataset.category !== filter.value;
      });
    });
  }
});
