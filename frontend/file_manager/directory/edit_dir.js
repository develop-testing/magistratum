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
  return (
    (g.includes("r") ? "r" : "-") +
    (g.includes("w") ? "w" : "-") +
    (o.includes("r") ? "r" : "-") +
    (o.includes("w") ? "w" : "-")
  )
}

const _dir_name = c => (c?.directory?.name || c?.name || "")
const _dir_img = c => (c?.decor?.cover || "")

const fetch_directory = dir_id => {
  return Promise.all([
    send_get("/node/" + dir_id, { data_type: "rich" }).then(node => ({
      ...node,
      ...node.permitions,
      image: _dir_img(node.value?.content),
    })),
    send_get("/nodes", { type_filter: "directory" }),
    send_get("/members"),
    send_get("/groups"),
  ]).then(res => ({
    dir: res[0],
    dirs: res[1],
    users: res[2],
    groups: res[3],
  }))
}

const mk_dir_edit_form = data => {
  const dir = data.dir || {}
  return {
    dir_id: dir.id || "",
    title: _dir_name(dir.value?.content),
    image: {
      url: dir.image || "",
      file: null,
    },
    dirs: {
      active: dir.parent_id || "",
      list: (data.dirs || [])
        .filter(d => d.id !== dir.id)
        .map(d => ({
          value: d.id,
          label: _dir_name(d.value?.content),
        })),
    },
    owner: {
      active: dir.owner || "",
      list: (data.users || []).map(u => ({
        value: u.username,
        label: u.username,
      })),
    },
    group: {
      active: dir.group || "",
      list: (data.groups || []).map(g => ({
        value: g.name,
        label: g.name,
      })),
    },
    group_perms: {
      active: mapPerms(dir.permitions, "group"),
      list: [
        { value: "", label: "Нет доступа" },
        { value: "r", label: "Чтение" },
        { value: "w", label: "Запись" },
        { value: "rw", label: "Чтение и запись" },
      ],
    },
    other_perms: {
      active: mapPerms(dir.permitions, "other"),
      list: [
        { value: "", label: "Нет доступа" },
        { value: "r", label: "Чтение" },
        { value: "w", label: "Запись" },
        { value: "rw", label: "Чтение и запись" },
      ],
    },
  }
}

const change_dir_edit_form = (form, field, value) => {
  if (field === "title") return { ...form, title: value }

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

const render_dir_image = form => {
  const image = document.querySelector('[name="image-preview"]')
  image.src = form.image.url

  return form
}

const save_dir_edit_form = async (form, dir_id) => {
  const payload = {
    node_id: dir_id,
    new_name: form.title,
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

  return send_patch("/node/directory/" + dir_id, payload)
}

const render_dir_edit_form = form => {
  const name_input = document.querySelector("[name='file-name']")
  const dir_select = document.querySelector('[name="perm-parent-dir"]')
  const groups_select = document.querySelector('[name="perm-group-name"]')
  const owner_select = document.querySelector('[name="perm-owner"]')
  const group_perms_select = document.querySelector('[name="perm-group-perms"]')
  const other_perms_select = document.querySelector('[name="perm-other-perms"]')
  const back_btn = document.querySelector("#back-btn")

  back_btn.href = form.dirs.active
    ? "/dashboard/directory/" + form.dirs.active
    : "/dashboard/root"
  render_dir_image(form)

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

  return form
}
