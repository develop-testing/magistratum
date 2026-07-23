const fetch_users = by_name => {
  return send_get("/members", { by_name })
}

const fetch_groups = (owner, member) => {
  return send_get("/groups", { owner, member })
}

const create_group = (group_name, owner) => {
  return send_post("/group", { name: group_name, owner, members: [] })
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
  return `
    <tr>
        <td data-username>${user.username}</td>
        <td>
            <div class="table-buttons">
                <button data-user-remove="${user.username}">Удалить</button>
            </div>
        </td>
    </tr>
    `
}

const create_group_table_row = (group, users) => {
  let usersHtml = ""
  let ownerHtml = ""

  users.forEach(user => {
    const is_owner = group.owner === user
    const is_member = group.members.includes(user.username)
    const owner_checked = is_owner ? "checked" : ""
    const user_in_group = is_member ? "checked" : ""

    usersHtml += `
      <div class="checkbox">
          <label>
              <input ${user_in_group} name="members[]" type="checkbox" value="${user.username}">
              <span>${user.username}</span>
          </label>
      </div>
    `

    ownerHtml += `
      <div class="checkbox">
          <label>
              <input
                ${user_in_group}
                name="owner-${group.name}-"
                type="radio"
                value="${user.username}"
              >
              <span>${user.username}</span>
          </label>
      </div>
    `
  })

  return `
    <tr>
        <td>${group.name}</td>
        <td>${ownerHtml}</td>
        <td>
            <div class="checkbox-list">${usersHtml}</div>
        </td>
        <td>
            <div class="table-buttons">
                <button data-group-remove="${group.name}">Удалить</button>
                <button data-save="${group.name}">Сохранить</button>
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
