// Настройки лендинга: всё, что нужно поменять перед публикацией, находится здесь.
const CONFIG = {
  // Адрес формы на formspree.io, вида "https://formspree.io/f/xxxxxxx".
  formEndpoint: "https://formspree.io/f/xeaaqwye",
};

(() => {
  document.getElementById("year").textContent = new Date().getFullYear();

  const form = document.getElementById("lead-form");
  const status = form.querySelector(".form__status");
  const submit = form.querySelector("button[type=submit]");

  // Регион статуса всегда в DOM (пустой он схлопывается в CSS): так скринридер озвучивает и первое сообщение.
  const setStatus = (kind, text) => {
    status.className = "form__status " + kind;
    status.textContent = text;
  };

  const validate = () => {
    let ok = true;
    for (const name of ["email", "role"]) {
      const input = form.elements[name];
      const valid = name === "email"
        ? /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(input.value.trim())
        : input.value !== "";
      input.closest(".field").classList.toggle("invalid", !valid);
      form.querySelector(`.err[data-for=${name}]`).hidden = valid;
      input.setAttribute("aria-invalid", String(!valid));
      if (!valid && ok) input.focus();
      ok = ok && valid;
    }
    return ok;
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setStatus("", "");
    if (!validate()) return;

    if (!CONFIG.formEndpoint) {
      setStatus("fail", "Приём заявок пока не подключён.");
      return;
    }

    submit.disabled = true;
    try {
      const res = await fetch(CONFIG.formEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
        body: new URLSearchParams(new FormData(form)).toString(),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      form.reset();
      setStatus("ok", "Готово. Мы напишем, когда откроем доступ.");
    } catch (err) {
      setStatus("fail", "Не получилось отправить. Попробуйте ещё раз чуть позже.");
    } finally {
      submit.disabled = false;
    }
  });
})();
