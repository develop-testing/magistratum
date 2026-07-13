export class ManagerItem {
  constructor(id, type, img, name, owner, group) {
    this.id = id;
    this.type = type;
    this.img = img;
    this.name = name;
    this.owner = owner;
    this.group = group;
  }
}

export class FileManager {
  constructor(items) {
    this.items = items;
  }
}

export const mk_manager_item = (id, type, img, name, owner, group) => {
  return new ManagerItem(id, type, img, name, owner, group);
};

export const mk_file_manager = (items) => {
  return new FileManager(items);
};

export const append_item = (m_items, item) => {
  return mk_file_manager([...m_items.items, item]);
};

export const make_item_html = (item) => {
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

  const type_links = {
    dir: "/dashboar/directory/",
    text_file: "/text_file/",
    broken: "type-broken",
  };

  const current_class = type_classes[item.type] || "type-unknown";
  const current_name = types[item.type] || "Неизвестно";
  const link = type_links[item.type] + encodeURIComponent(item.id);

  return `<div data-type="${item.type}" data-id="${item.id}" class="file-item">
		<div class="file-item-img">
				<img src="${item.img}">
		</div>
		<div class="file-item-content">
        <div data-node-remove class="file-item-close">&#128473;</div>
				<div class="file-item-type ${current_class}">${current_name}</div>    
				<a href="${link}" class="file-item-title">${item.name}</a>
				<div class="file-item-owner">Владелец: ${item.owner}</div>
				<div class="file-item-group">Группа: ${item.group}</div>
		</div>
	</div>`;
};
