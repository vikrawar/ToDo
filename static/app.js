/**
 * Browser-side code for the Todo app.
 *
 * This file talks to our FastAPI server using `fetch` (built into modern browsers).
 * The server responds with JSON lists/objects; we turn that data into HTML on the page.
 *
 * If you are new to JavaScript, read top-to-bottom — later functions call earlier ones.
 */

// Same-origin API (FastAPI serves this JS and the `/api/...` routes).
const API_URL = "/api/todos";

// --- DOM references (cached after page load) ---------------------------------

let inputEl;
let submitBtn;
let listEl;

/**
 * `document` is the live representation of the HTML page in memory.
 * `getElementById` finds a single element by its `id="..."` attribute.
 */
function cacheDom() {
  inputEl = document.getElementById("todo-input");
  submitBtn = document.getElementById("submit-todo");
  listEl = document.getElementById("todo-list");
}

// --- Small UI helpers -------------------------------------------------------

/**
 * The round button should look grey when there is nothing to submit,
 * and green when `.trim()` has at least one character.
 *
 * `.trim()` removes spaces from both ends — "  hi  " becomes "hi".
 * We use a CSS class `.is-armed` that `style.css` styles as green.
 */
function refreshSubmitAppearance() {
  const text = inputEl.value;
  const hasRealText = text.trim().length > 0;
  submitBtn.classList.toggle("is-armed", hasRealText);
}

// --- Networking helpers -----------------------------------------------------

/**
 * `async function` means we can use `await` inside to pause until a Promise finishes.
 * `fetch` returns a Promise that resolves to a `Response` object.
 *
 * We read JSON with `.json()` — also async — which turns the HTTP body into plain
 * JavaScript objects/arrays (very similar to Python dicts/lists).
 */
async function getTodos() {
  const response = await fetch(API_URL);
  if (!response.ok) {
    throw new Error(`GET failed: ${response.status}`);
  }
  return response.json();
}

async function postTodo(title) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // `JSON.stringify` turns a JS object into a JSON text payload (like json.dumps).
    body: JSON.stringify({ title }),
  });
  if (!response.ok) {
    throw new Error(`POST failed: ${response.status}`);
  }
  return response.json();
}

async function patchTodo(id, completed) {
  const response = await fetch(`${API_URL}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed }),
  });
  if (!response.ok) {
    throw new Error(`PATCH failed: ${response.status}`);
  }
  return response.json();
}

async function deleteTodoRequest(id) {
  const response = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(`DELETE failed: ${response.status}`);
  }
  // Server returns `{"ok": true}` — we do not need the body here.
  return response.json();
}

// --- Render the list --------------------------------------------------------

/**
 * We rebuild the list from scratch each time data refreshes.
 * That is simpler than surgically editing individual rows and avoids stale state bugs.
 */
function renderTodos(todos) {
  // `innerHTML = ""` removes all child elements quickly.
  listEl.innerHTML = "";

  // `for...of` loops over iterable values (like Python's `for x in items`).
  for (const todo of todos) {
    const row = document.createElement("li");
    row.className = "todo-row" + (todo.completed ? " todo-row--done" : "");
    // `dataset.*` becomes data-* attributes; handy for debugging in DevTools.
    row.dataset.id = String(todo.id);

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "todo-check";
    checkbox.checked = todo.completed;
    /**
     * Arrow function `(event) => { ... }` is like a small anonymous function.
     * `change` fires when the checkbox toggles (mouse or keyboard).
     *
     * `checkbox.checked` is the NEW value after the user action.
     */
    checkbox.addEventListener("change", async () => {
      try {
        await patchTodo(todo.id, checkbox.checked);
        await refreshFromServer();
      } catch (err) {
        console.error(err);
        // Put UI back in sync with the server if something went wrong.
        await refreshFromServer();
      }
    });

    const title = document.createElement("span");
    title.className = "todo-title";
    // `textContent` inserts plain text safely (no accidental HTML injection).
    title.textContent = todo.title;

    const delBtn = document.createElement("button");
    delBtn.type = "button";
    delBtn.className = "todo-delete";
    delBtn.setAttribute("aria-label", "Delete todo");
    delBtn.innerHTML = "&times;"; // renders "×"

    /**
     * `stopPropagation()` keeps the click from bubbling to parent elements.
     * Not always required here, but it is a good habit for toolbar buttons.
     */
    delBtn.addEventListener("click", async (event) => {
      event.stopPropagation();
      try {
        await deleteTodoRequest(todo.id);
        await refreshFromServer();
      } catch (err) {
        console.error(err);
      }
    });

    // `appendChild` adds an element at the end of another element's children.
    row.appendChild(checkbox);
    row.appendChild(title);
    row.appendChild(delBtn);
    listEl.appendChild(row);
  }
}

/** Ask the server for the latest ordering, then repaint. */
async function refreshFromServer() {
  const todos = await getTodos();
  renderTodos(todos);
}

/** Reads the input, validates locally, POSTs, then clears + reloads. */
async function tryCreateTodo() {
  const title = inputEl.value.trim();
  if (!title) {
    return;
  }
  try {
    await postTodo(title);
    inputEl.value = "";
    refreshSubmitAppearance();
    await refreshFromServer();
  } catch (err) {
    console.error(err);
  }
}

/**
 * Wire all browser events once.
 *
 * `addEventListener` attaches a function that runs later when the event happens.
 * It does NOT run the function immediately — that is why we pass a reference.
 */
function bindEvents() {
  // Any typing updates the green/grey affordance.
  inputEl.addEventListener("input", refreshSubmitAppearance);

  /**
   * `keydown` fires when a key is pressed down.
   * We only care about Enter, and we prevent the default action (forms use this for submits).
   */
  inputEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      tryCreateTodo();
    }
  });

  // Clicking the round checkmark also submits.
  submitBtn.addEventListener("click", () => {
    tryCreateTodo();
  });
}

/**
 * `DOMContentLoaded` means: HTML is parsed and elements exist.
 * The `<script>` tag uses `defer`, so this file already runs late — but waiting
 * for this event is a common, easy-to-remember pattern while you are learning.
 */
function init() {
  cacheDom();
  bindEvents();
  refreshSubmitAppearance();
  refreshFromServer().catch((err) => console.error(err));
}

document.addEventListener("DOMContentLoaded", init);
