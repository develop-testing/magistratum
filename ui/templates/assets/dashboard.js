document.addEventListener("DOMContentLoaded", (e) => {
  const file_manager = (node_id) => {
    const parent = document.querySelector(node_id);

    const file_item = (id, img, title) => {
      return `<div data-id="${id}" class="file-item">
        <div class="file-item-img">
            <img src="${img}">
        </div>
        <div class="file-item-content">
            <div class="file-item-title">${title}</div>
        </div>
    </div>`;
    };

    fetch(
      "http://127.0.0.0:8800/directories?parent_id=dir%232443e7b0-41b5-49ab-bbca-f195dc2e958b",
    )
      .then((res) => res.json())
      .then((res) => {
        let data = "";

        res.map((item) => {
          console.log(item);
          data += file_item(
            item.dir_id,
            "https://warhammergames.ru/_pu/3/s42932075.jpg",
            item.name,
          );
        });

        parent.insertAdjacentHTML("beforeend", data);
      })
      .then((_) => {
        fetch(
          "http://127.0.0.0:8800/files?by_directory=dir%232443e7b0-41b5-49ab-bbca-f195dc2e958b&limit=10&offset=0",
        )
          .then((res) => res.json())
          .then((res) => {
            let data = "";

            res.map((item) => {
              data += file_item(
                item.file_id,
                "https://warhammergames.ru/_pu/3/35037612.jpg",
                item.name,
              );
            });

            parent.insertAdjacentHTML("beforeend", data);
          });
      });
  };

  file_manager("#manager-grid");
});
