const mapPerms = permString => {
  if (!permString) return ""
  if (permString.length === 4) {
    const g =
      (permString[0] === "r" ? "r" : "") +
      (permString[1] === "w" ? "w" : "")
    return g || ""
  }
  const lower = permString.toLowerCase()
  if (lower.includes("read") && lower.includes("write")) return "rw"
  if (lower.includes("read")) return "r"
  if (lower.includes("write")) return "w"
  return ""
}

const fetch_directory = dir_id => {
  const dirs_url = new URL("http://127.0.0.1:8800/directories")
  dirs_url.searchParams.append("by_id", dir_id)
  dirs_url.searchParams.append("data_type", "rich")

  const all_dirs_url = new URL("http://127.0.0.1:8800/directories")
  all_dirs_url.searchParams.append("only_can_write", true)

  const users_url = new URL("http://127.0.0.1:8800/auth/members")

  const groups_url = new URL("http://127.0.0.1:8800/groups")

  return Promise.all([
    fetch(dirs_url, { credentials: "include" })
      .then(res => res.json())
      .then(items => {
        const item = items[0] || {}
        return {
          ...(item.directory || {}),
          ...(item.perms || {}),
          image: item.image || "",
        }
      }),
    fetch(all_dirs_url, { credentials: "include" }).then(res => res.json()),
    fetch(users_url, { credentials: "include" }).then(res => res.json()),
    fetch(groups_url, { credentials: "include" }).then(res => res.json()),
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
    dir_id: dir.dir_id || "",
    title: dir.name || "",
    image: {
      url: dir.image || "",
      file: null,
    },
    dirs: {
      active: dir.parent_id || "",
      list: (data.dirs || []).map(d => ({
        value: d.dir_id,
        label: d.name,
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
      active: mapPerms(dir.group_perms),
      list: [
        { value: "r", label: "Чтение" },
        { value: "w", label: "Запись" },
        { value: "rw", label: "Чтение и запись" },
      ],
    },
    other_perms: {
      active: mapPerms(dir.other_perms),
      list: [
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

const save_dir_edit_form = (form, dir_id) => {
  const get_cover = new Promise(resolve => {
    if (form.image.file === null) {
      resolve("")
      return
    }

    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.readAsDataURL(form.image.file)
  })

  return get_cover.then(cover_data => {
    return fetch("http://127.0.0.1:8800/directory", {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        dir_id: dir_id,
        new_name: form.title,
        new_parent_id: form.dirs.active,
        new_owner: form.owner.active,
        new_group_name: form.group.active,
        new_group_perms: form.group_perms.active,
        new_other_perms: form.other_perms.active,
        new_cover: cover_data,
      }),
    }).then(res => res)
  })
}

const render_dir_edit_form = form => {
  const name_input = document.querySelector("[name='file-name']")
  const dir_select = document.querySelector('[name="perm-parent-dir"]')
  const groups_select = document.querySelector('[name="perm-group-name"]')
  const owner_select = document.querySelector('[name="perm-owner"]')
  const group_perms_select = document.querySelector(
    '[name="perm-group-perms"]',
  )
  const other_perms_select = document.querySelector(
    '[name="perm-other-perms"]',
  )

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
