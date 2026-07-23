const fetch_users = by_name => {
  const users_url = new URL("http://127.0.0.1:8800/members")

  if (by_name !== "") {
    users_url.searchParams.append("by_name", by_name)
  }

  return fetch(users_url, { credentials: "include" }).then(res => res.json())
}

const fetch_groups = (owner, member) => {
  const groups_url = new URL("http://127.0.0.1:8800/groups")

  if (owner !== "") {
    groups_url.searchParams.append("owner", owner)
  }

  if (member !== "") {
    groups_url.searchParams.append("member", member)
  }

  return fetch(groups_url, { credentials: "include" }).then(res => res.json())
}

const create_user = (username, password) => {
  const create_user_url = "http://127.0.0.1:8800/auth/register"

  return fetch(create_user_url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  }).then(res => {
    if (res.ok) return res.json()
    return res.text()
  })
}

const delete_user = username => {
  const remove_user_url = new URL("http://127.0.0.1:8800/members/")

  return fetch(remove_user_url, {
    method: "DELETE",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  }).then(res => res.json())
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

  users.forEach(user => {
    const isMember = group.members.includes(user.username)
    const checkedAttr = isMember ? "checked" : ""

    usersHtml += `
      <div class="checkbox">
          <label>
              <input ${checkedAttr} type="checkbox" value="${user.username}">
              <span>${user.username}</span>
          </label>
      </div>
    `
  })

  return `
    <tr>
        <td>${group.name}</td>
        <td>${group.owner}</td>
        <td>
            <div class="checkbox-list">${usersHtml}</div>
        </td>
        <td>
            <div class="table-buttons">
                <button data-user-remove="${group.name}">Удалить</button>
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
