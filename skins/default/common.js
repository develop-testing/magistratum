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
