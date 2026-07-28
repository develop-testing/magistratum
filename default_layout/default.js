const tabs = (btns_tags, tabs_tags) => {
  const tabs_buttons = document.querySelectorAll(btns_tags)
  const tabs = document.querySelectorAll(tabs_tags)

  tabs_buttons.forEach(button => {
    button.addEventListener("click", e => {
      const tab_name = e.target.getAttribute("data-tab")
      tabs.forEach(tab => {
        if (tab_name !== tab.getAttribute("data-tab-content")) {
          tab.classList.remove("active")
        } else {
          tab.classList.add("active")
        }
      })
    })
  })
}

const modals = () => {
  const modals = document.querySelectorAll("[data-modal]")
  const buttons = document.querySelectorAll("[data-modal-open]")

  buttons.forEach(button => {
    button.addEventListener("click", e => {
      const target_modal_name = e.target.getAttribute("data-modal-open")

      modals.forEach(modal => {
        const modal_name = modal.getAttribute("data-modal")
        if (target_modal_name === modal_name) modal.classList.toggle("-show")
      })
    })
  })

  document.querySelectorAll(".modal").forEach(item => {
    item.addEventListener("click", e => {
      if (e.target.classList.contains("modal")) {
        item.classList.remove("-show")
      }
    })
  })
}

const send_get = (url, params) => {
  const full_url = new URL(`http://127.0.0.1:8800${url}`)

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        full_url.searchParams.append(key, value)
      }
    })
  }

  return fetch(full_url, { credentials: "include" }).then(res => {
    if (!res.ok)
      return res.text().then(text => {
        throw { status: res.status, message: text }
      })
    return res.json()
  })
}

const send_post = (url, data) => {
  return fetch(`http://127.0.0.1:8800${url}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(res => {
    if (!res.ok)
      return res.text().then(text => {
        throw { status: res.status, message: text }
      })
    return res.json()
  })
}

const send_patch = (url, data) => {
  return fetch(`http://127.0.0.1:8800${url}`, {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(res => {
    if (!res.ok)
      return res.text().then(text => {
        throw { status: res.status, message: text }
      })
    return res.json()
  })
}

const send_delete = (url, data) => {
  return fetch(`http://127.0.0.1:8800${url}`, {
    method: "DELETE",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(res => {
    if (!res.ok)
      return res.text().then(text => {
        throw { status: res.status, message: text }
      })
    return res.json()
  })
}

document.querySelector("[data-logout]").addEventListener("click", e => {
  send_post("/auth/logout")
    .then(e => window.location.reload())
    .catch(e => alert("Произошла ошибка"))
})
