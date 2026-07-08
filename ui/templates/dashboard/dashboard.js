import {
  mk_manager_item,
  mk_file_manager,
  append_item,
  make_item_html,
} from "./file_manager.js";

document.addEventListener("DOMContentLoaded", (e) => {
  const add_directory_modal = document.querySelector("#add-dir-modal");
  const add_directory_form = document.querySelector("#add-dir-form");
  const add_directory_button = document.querySelector("#add-directory");
  const add_file_modal = document.querySelector("#add-file-modal");
  const add_file_form = document.querySelector("#add-file-form");
  const add_file_button = document.querySelector("#add-file");

  const show_file_manager = (html) => {
    const parent = document.querySelector("#manager-grid");
    parent.insertAdjacentHTML("beforeend", html);
  };

  const fetch_directory_content = () => {
    return fetch(
      "http://127.0.0.0:8800/directory/content?dir_id=dir%232443e7b0-41b5-49ab-bbca-f195dc2e958b",
    )
      .then((res) => res.json())
      .then((res) => {
        return mk_file_manager([
          ...res.map((item) =>
            mk_manager_item(
              item.item_id,
              item.type,
              item.img,
              item.name,
              item.owner,
              item.group,
            ),
          ),
        ]);
      });
  };

  let file_manager = fetch_directory_content().then((fm) => {
    show_file_manager(fm.items.map(make_item_html).join(""));
    return fm;
  });

  add_directory_button.addEventListener("click", (e) => {
    add_directory_modal.classList.toggle("-show");
  });

  add_file_button.addEventListener("click", (e) => {
    add_file_modal.classList.toggle("-show");
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
      .then((data) => {
        file_manager = fetch_directory_content().then((fm) => {
          show_file_manager(fm.items.map(make_item_html).join(""));
          return fm;
        });
        add_directory_modal.classList.toggle("-show");
      });
  });

  add_file_form.addEventListener("submit", (e) => {
    e.preventDefault();

    const form_data = new FormData(e.target);
    const json_object = Object.fromEntries(form_data.entries());

    fetch("http://127.0.0.0:8800/file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(json_object),
    })
      .then((response) => response.json())
      .then((data) => {
        file_manager = fetch_directory_content().then((fm) => {
          show_file_manager(fm.items.map(make_item_html).join(""));
          return fm;
        });
        add_file_modal.classList.toggle("-show");
      });
  });
});
