document.addEventListener("DOMContentLoaded", (e) => {
  const parent = document.querySelector("#manager-grid");
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
    console.log(e);
  });
});
