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

  const remove_directory = (id) => {
    return fetch(`http://127.0.0.1:8800/directory`, {
      credentials: "include",
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dir_id: id }),
    })
      .then((res) => res.json())
      .then((res) => {
        return res;
      });
  };

  const remove_text_file = (id) => {
    return fetch(`http://127.0.0.1:8800/file`, {
      credentials: "include",
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id: id }),
    })
      .then((res) => res.json())
      .then((res) => {
        return res;
      });
  };

  const fetch_directory_content = () => {
    return fetch(`http://127.0.0.1:8800/directory/content?dir_id=${dir_id}`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((res) => {
        return mk_file_manager([
          ...res.map((item) =>
            mk_manager_item(
              item.node.node_id,
              item.node.type,
              item.meta.img,
              item.meta.name,
              item.perms.owner_name,
              item.perms.group_name,
            ),
          ),
        ]);
      });
  };

  const show_file_manager = (html) => {
    const parent = document.querySelector("#manager-grid");
    parent.innerHTML = "";
    parent.insertAdjacentHTML("beforeend", html);

    let remove_node_buttons = document.querySelectorAll("[data-node-remove]");

    remove_node_buttons.forEach((node) => {
      node.addEventListener("click", (e) => {
        const type = e.target.closest(".file-item").getAttribute("data-type");
        const id = e.target.closest(".file-item").getAttribute("data-id");

        let result =
          type === "dir" ? remove_directory(id) : remove_text_file(id);

        result.then((res) => {
          file_manager = fetch_directory_content().then((fm) => {
            show_file_manager(fm.items.map(make_item_html).join(""));
            return fm;
          });
        });
      });
    });
  };

  const create_directory = (data) => {
    return fetch("http://127.0.0.1:8800/directory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      credentials: "include",
    }).then((response) => response.json());
  };

  const create_file = (data) => {
    return fetch("http://127.0.0.1:8800/file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      credentials: "include",
    }).then((response) => response.json());
  };

  const dir_id = document.body.dataset.dirId;

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

    create_directory(json_object).then((_) => {
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
    json_object.content = "";

    create_file(json_object).then((_) => {
      file_manager = fetch_directory_content().then((fm) => {
        show_file_manager(fm.items.map(make_item_html).join(""));
        return fm;
      });
      add_file_modal.classList.toggle("-show");
    });
  });
});
