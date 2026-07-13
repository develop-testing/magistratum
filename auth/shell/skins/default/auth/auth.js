const form = document.getElementById("auth-form");
const errorEl = document.getElementById("auth-error");
const script = document.currentScript;
const action = script?.getAttribute("data-action") ?? "login";

form?.addEventListener("submit", async (e) => {
  e.preventDefault();

  errorEl?.classList.remove("-show");
  errorEl.textContent = "";

  const data = Object.fromEntries(new FormData(form));

  const res = await fetch(`http://127.0.0.1:8800/auth/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
    credentials: "include",
  });

  if (res.ok) {
    if (action === "register") {
      window.location = "/login";
    } else {
      window.location = "/dashboar/home";
    }
    return;
  }

  const text = await res.text();
  if (errorEl) {
    errorEl.textContent = text || "Ошибка";
    errorEl.classList.add("-show");
  }
});
