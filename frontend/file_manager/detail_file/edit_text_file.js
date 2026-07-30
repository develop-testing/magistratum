const mapPerms = (permString, type = "group") => {
  if (!permString) return ""
  if (permString.length === 4) {
    const offset = type === "other" ? 2 : 0
    const g =
      (permString[offset] === "r" ? "r" : "") +
      (permString[offset + 1] === "w" ? "w" : "")
    return g || ""
  }
  const lower = permString.toLowerCase()
  if (lower.includes("read") && lower.includes("write")) return "rw"
  if (lower.includes("read")) return "r"
  if (lower.includes("write")) return "w"
  return ""
}

const combinePerms = (g, o) => {
  return (g.includes("r") ? "r" : "-") + (g.includes("w") ? "w" : "-") +
         (o.includes("r") ? "r" : "-") + (o.includes("w") ? "w" : "-")
}

const _file_name = c => (c?.file?.name || c?.name || "")
const _file_content = c => (c?.file?.content || c?.content || "")
const _file_img = c => (c?.decor?.cover || "")
const _dir_name = c => (c?.directory?.name || c?.name || "")

const mk_file_edit_form = data => {
  const file = data.file || {}
  const dirsList = data.dirs || []
  const usersList = data.users || []
  const groupsList = data.groups || []
  const c = file.value?.content

  return {
    file_id: file.id || "",
    title: _file_name(c),
    content: _file_content(c),
    image: {
      url: file.image || "",
      file: null,
    },
    dirs: {
      active: file.parent_id || "",
      list: dirsList
        .filter(d => d.id !== file.id)
        .map(d => ({ value: d.id, label: _dir_name(d.value?.content) })),
    },
    owner: {
      active: file.owner || "",
      list: usersList.map(u => ({ value: u.username, label: u.username })),
    },
    group: {
      active: file.group || "",
      list: groupsList.map(g => ({ value: g.name, label: g.name })),
    },
    group_perms: {
      active: mapPerms(file.permitions, "group"),
      list: [
        { value: "r", label: "Чтение" },
        { value: "w", label: "Запись" },
        { value: "rw", label: "Чтение и запись" },
      ],
    },
    other_perms: {
      active: mapPerms(file.permitions, "other"),
      list: [
        { value: "r", label: "Чтение" },
        { value: "w", label: "Запись" },
        { value: "rw", label: "Чтение и запись" },
      ],
    },
  }
}

const change_file_edit_form = (form, field, value) => {
  if (field === "title") return { ...form, title: value }

  if (field === "content") return { ...form, content: value }

  if (field === "parent")
    return { ...form, dirs: { ...form.dirs, active: value } }

  if (field === "owner")
    return { ...form, owner: { ...form.owner, active: value } }

  if (field === "group")
    return { ...form, group: { ...form.group, active: value } }

  if (field === "group-perms")
    return { ...form, group_perms: { ...form.group_perms, active: value } }

  if (field === "other-perms")
    return { ...form, other_perms: { ...form.other_perms, active: value } }

  if (field === "image") {
    return {
      ...form,
      image: {
        url: value[0] ? URL.createObjectURL(value[0]) : form.image.url,
        file: value[0],
      },
    }
  }

  return form
}

const fetch_file_edit_form = (file_id, username) => {
  return Promise.all([
    send_get("/node/" + file_id, { data_type: "rich" }).then(node => ({
      ...node,
      ...node.permitions,
      image: _file_img(node.value?.content),
    })),
    send_get("/groups", { member: username, only_can_write: true }),
    send_get("/nodes", { type_filter: "directory" }),
    send_get("/members"),
  ])
    .then(res => ({
      file: res[0],
      groups: res[1],
      dirs: res[2],
      users: res[3],
    }))
    .then(data => mk_file_edit_form(data))
}

const render_read_btn = file_id => {
  const read_btn = document.querySelector("#editor-btn")
  read_btn.href = "/text_file/" + file_id

  return read_btn
}

const render_file_image = form => {
  const image = document.querySelector('[name="image-preview"]')
  image.src = form.image.url

  return form
}

const render_file_edit_form = form => {
  const name_input = document.querySelector("[name='file-name']")
  const dir_select = document.querySelector('[name="perm-parent-dir"]')
  const groups_select = document.querySelector('[name="perm-group-name"]')
  const owner_select = document.querySelector('[name="perm-owner"]')
  const group_perms_select = document.querySelector('[name="perm-group-perms"]')
  const other_perms_select = document.querySelector('[name="perm-other-perms"]')

  render_file_image(form)

  name_input.value = form.title

  const init_select = (select, list, active) => {
    list.forEach(item => {
      select.append(new Option(item.label, item.value))
    })
    select.value = active
  }

  init_select(dir_select, form.dirs.list, form.dirs.active)
  init_select(groups_select, form.group.list, form.group.active)
  init_select(owner_select, form.owner.list, form.owner.active)
  init_select(
    group_perms_select,
    form.group_perms.list,
    form.group_perms.active,
  )
  init_select(
    other_perms_select,
    form.other_perms.list,
    form.other_perms.active,
  )

  tinymce.init({
    selector: "#editor",
    menubar: false,
    branding: false,
    promotion: false,
    height: "100%",
    plugins: "lists link image code fullscreen preview",
    toolbar:
      "bold italic | blocks | bullist numlist | link image | code fullscreen preview",
    content_style: "body { font-family: monospace; }",
    setup: editor => {
      editor.on("init", () => editor.setContent(form.content || ""))
      editor.on("input change undo redo NodeChange", () => {
        const event = new CustomEvent("file_content_changed", {
          detail: { value: editor.getContent() },
        })
        document.dispatchEvent(event)
      })
    },
  })
  return form
}

const save_file_edit_form = async (form, file_id) => {
  const payload = {
    node_id: file_id,
    new_name: form.title,
    new_content: form.content,
    new_parent_id: form.dirs.active,
    new_owner: form.owner.active,
    new_group: form.group.active,
    new_permissions: combinePerms(
      form.group_perms.active,
      form.other_perms.active,
    ),
  }

  if (form.image.file) {
    payload.new_cover = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = () => reject(new Error("Failed to read image"))
      reader.readAsDataURL(form.image.file)
    })
  }

  return send_patch("/node/text_file/" + file_id, payload)
}
