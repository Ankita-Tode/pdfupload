const form = document.getElementById("ask-form");
const chatlog = document.getElementById("chatlog");
const sourcesDiv = document.getElementById("sources");
const input = document.getElementById("question");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  // append user message
  appendMsg("user", question);
  input.value = "";
  sourcesDiv.textContent = "Thinking...";

  try {
    const res = await fetch(form.dataset.url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": document.querySelector('input[name="csrfmiddlewaretoken"]').value,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ question })
    });

    const data = await res.json();
    appendMsg("assistant", data.answer);
    if (data.sources && data.sources.length) {
      sourcesDiv.innerHTML = "Sources: " + data.sources
        .map(s => `pages ${s.pages[0]}–${s.pages[1]} (score ${s.score.toFixed(3)})`)
        .join(", ");
    } else {
      sourcesDiv.textContent = "No sources found.";
    }
    chatlog.scrollTop = chatlog.scrollHeight;
  } catch (err) {
    appendMsg("assistant", "Sorry, there was an error answering your question.");
    sourcesDiv.textContent = "";
    console.error(err);
  }
});

function appendMsg(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  wrap.innerHTML = `
    <div class="bubble">
      <div class="role">${role[0].toUpperCase() + role.slice(1)}</div>
      <div class="content"></div>
    </div>`;
  wrap.querySelector(".content").textContent = text;
  chatlog.appendChild(wrap);
}

