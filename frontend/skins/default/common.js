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
