const fetch_users = by_name => {
  return send_get("/members", { by_name })
}

const fetch_groups = (owner, member) => {
  return send_get("/groups", { owner, member })
}

const create_group = (group_name, owner) => {
  return send_post("/group", { name: group_name, owner, members: [] })
}

const update_group = (name, new_name, new_owner, new_members) => {
  return send_patch("/group", { name, new_name, new_owner, new_members })
}

const delete_group = group_name => {
  return send_delete("/group", { name: group_name })
}

const create_user = (username, password) => {
  return send_post("/auth/register", { username, password })
}

const delete_user = username => {
  return send_delete("/members/", { username })
}

const create_user_table_row = user => {
  const isRoot = user.username === "root"

  return `
    <tr>
        <td class="p-4" data-username>${user.username}</td>
        <td class="p-4">
            <div class="table-buttons">
                <button class="def-button flex-basic px-2" data-user-remove="${user.username}" ${isRoot ? "disabled" : ""}>Удалить</button>
            </div>
        </td>
    </tr>
  `
}

const create_group_table_row = (group, users) => {
  let usersHtml = ""
  let ownerHtml = ""

  users.forEach(user => {
    const isRoot = user.username === "root"
    const is_member = group.members.includes(user.username)
    const user_in_group = is_member ? "checked" : ""
    const rootDisabled = isRoot ? "disabled" : ""

    const is_owner = group.owner === user.username
    const owner_checked = is_owner ? "checked" : ""

    usersHtml += `
      <div class="checkbox">
          <label>
              <input
                data-member-input
                ${user_in_group}
                name="members[]"
                type="checkbox"
                value="${user.username}"
                ${rootDisabled}
              >
              <span>${user.username}</span>
          </label>
      </div>
    `

    ownerHtml += `
      <div class="checkbox">
          <label>
              <input
                data-owner-input
                ${owner_checked}
                name="owner-${group.name}-"
                type="radio"
                value="${user.username}"
                ${rootDisabled}
              >
              <span>${user.username}</span>
          </label>
      </div>
    `
  })

  const isRootGroup = group.name === "root"
  const buttonsDisabled = isRootGroup ? "disabled" : ""

  return `
    <tr>
        <td class="p-4">${group.name}</td>
        <td class="p-4">${ownerHtml}</td>
        <td class="p-4">
            <div class="checkbox-list">${usersHtml}</div>
        </td>
        <td class="p-4">
            <div class="table-buttons">
                <button class="def-button flex-basic px-2" data-group-remove="${group.name}" ${buttonsDisabled}>Удалить</button>
                <button class="def-button flex-basic px-2" data-group-save="${group.name}" ${buttonsDisabled}>Сохранить</button>
            </div>
        </td>
    </tr>
    `
}

const render_users = (users, table_tag) => {
  const table_body = document.querySelector(table_tag)
  let rows = ""

  users.forEach(user => (rows += create_user_table_row(user)))
  table_body.innerHTML = rows

  return users
}

const render_groups = (groups, users, table_tag) => {
  const table_body = document.querySelector(table_tag)
  let rows = ""

  groups.map(group => (rows += create_group_table_row(group, users)))
  table_body.innerHTML = rows

  return groups
}
