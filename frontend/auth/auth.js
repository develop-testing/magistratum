const form = document.getElementById("auth-form")
const errorEl = document.getElementById("auth-error")
const script = document.currentScript
const action = script?.getAttribute("data-action") ?? "login"

form?.addEventListener("submit", e => {
  e.preventDefault()

  errorEl?.classList.remove("-show")
  errorEl.textContent = ""

  const data = Object.fromEntries(new FormData(form))

  send_post(`/auth/${action}`, data)
    .then(() => (window.location = "/dashboard/root"))
    .catch(err => {
      if (errorEl) {
        errorEl.textContent = err.message || "Ошибка"
        errorEl.classList.add("-show")
      }
    })
})
