document.addEventListener("DOMContentLoaded", (e) => {
  const parent = document.querySelector("#manager-grid");
  const add_directory_modal = document.querySelector("#add-dir-modal");
  const add_directory_form = document.querySelector("#add-dir-form");
  const add_directory_button = document.querySelector("#add-directory");

  const manager_item = (item) => {
    const types = {
      dir: "Директория",
      text_file: "Файл",
      broken: "Ошибка доступа",
    };

    const type_classes = {
      dir: "type-dir",
      text_file: "type-file",
      broken: "type-broken",
    };

    const current_class = type_classes[item.type] || "type-unknown";
    const current_name = types[item.type] || "Неизвестно";

    return `<div data-id="${item.id}" class="file-item">
        <div class="file-item-img">
            <img src="${item.img}">
        </div>
        <div class="file-item-content">
            <div class="file-item-type ${current_class}">${current_name}</div>    
            <div class="file-item-title">${item.name}</div>
            <div class="file-item-owner">Владелец: ${item.owner}</div>
            <div class="file-item-group">Группа: ${item.group}</div>
        </div>
      </div>`;
  };

  fetch(
    "http://127.0.0.0:8800/directory/content?dir_id=dir%232443e7b0-41b5-49ab-bbca-f195dc2e958b",
  )
    .then((res) => res.json())
    .then((res) => {
      let data = "";
      res.map((item) => (data += manager_item(item)));
      parent.insertAdjacentHTML("beforeend", data);
    });

  add_directory_button.addEventListener("click", (e) => {
    add_directory_modal.classList.toggle("-show");
  });

  document.querySelectorAll(".modal").forEach((item) => {
    item.addEventListener("click", (e) => {
      if (e.target.classList.contains("modal")) {
        item.classList.remove("-show");
      }
    });
  });

  add_directory_form.addEventListener("submit", (e) => {
    e.preventDefault();

    const form_data = new FormData(e.target);
    const json_object = Object.fromEntries(form_data.entries());

    fetch("http://127.0.0.0:8800/directory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(json_object),
    })
      .then((response) => response.json())
      .then((data) => window.location.reload());
  });
});
