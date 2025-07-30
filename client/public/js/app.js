document.addEventListener("DOMContentLoaded", function () {
  if (!isAuthenticated()) {
    window.location.href = "login.html";
    return;
  }

  const user = getCurrentUser();
  if (user) {
    document.getElementById(
      "username"
    ).textContent = `Merhaba, ${user.username}`;
  }

  initializeNewsTable();

  document
    .getElementById("newsForm")
    .addEventListener("submit", handleNewsSubmit);
});

async function handleNewsSubmit(e) {
  e.preventDefault();

  const url = document.getElementById("newsUrl").value;
  const loading = document.getElementById("loading");
  const submitBtn = e.target.querySelector('button[type="submit"]');

  loading.classList.remove("d-none");
  submitBtn.disabled = true;

  try {
    const response = await fetch("/api/news/extract", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ url: url }),
    });

    if (response.ok) {
      const news = await response.json();
      showSuccess("Haber başarıyla çıkarıldı!");
      document.getElementById("newsUrl").value = "";

      $("#newsTable").DataTable().ajax.reload();
    } else {
      const error = await response.json();
      showError(error.detail || "Haber çıkarılamadı");
    }
  } catch (error) {
    showError("Bağlantı hatası");
  } finally {
    loading.classList.add("d-none");
    submitBtn.disabled = false;
  }
}

function initializeNewsTable() {
  $("#newsTable").DataTable({
    ajax: {
      url: "/api/news/",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      dataSrc: "",
    },
    columns: [
      {
        data: "title",
        render: function (data, type, row) {
          return `<a href="${
            row.url
          }" target="_blank" class="text-decoration-none">${
            data || "Başlık bulunamadı"
          }</a>`;
        },
      },
      {
        data: "url",
        render: function (data) {
          return `<a href="${data}" target="_blank" class="text-primary">${data.substring(
            0,
            50
          )}...</a>`;
        },
      },
      {
        data: "meta_lang",
        render: function (data) {
          if (!data) return "Belirtilmemiş";

          const languageNames = {
            tr: "Türkçe",
            en: "İngilizce",
            ar: "Arapça",
            he: "İbranice",
            fr: "Fransızca",
            de: "Almanca",
            es: "İspanyolca",
            it: "İtalyanca",
            ru: "Rusça",
            zh: "Çince",
            ja: "Japonca",
            ko: "Korece",
          };
          const languageName = languageNames[data] || data.toUpperCase();
          return `<span class="language-badge">${languageName}</span>`;
        },
      },
      {
        data: "meta_keywords",
        render: function (data) {
          if (!data) return "Belirtilmemiş";

          try {
            const keywords = JSON.parse(data);
            if (Array.isArray(keywords) && keywords.length > 0) {
              const keywordTags = keywords
                .slice(0, 3)
                .map((keyword) => `<span class="keyword-tag">${keyword}</span>`)
                .join("");
              const moreText =
                keywords.length > 3 ? ` +${keywords.length - 3} daha` : "";
              return (
                keywordTags +
                (moreText ? `<span class="text-muted">${moreText}</span>` : "")
              );
            }
          } catch (e) {
            if (data.trim()) {
              return `<span class="keyword-tag">${data}</span>`;
            }
          }
          return "Belirtilmemiş";
        },
      },
      {
        data: "publish_date",
        render: function (data) {
          return data
            ? new Date(data).toLocaleDateString("tr-TR")
            : "Belirtilmemiş";
        },
      },
      {
        data: "created_at",
        render: function (data) {
          return new Date(data).toLocaleDateString("tr-TR");
        },
      },
      {
        data: null,
        render: function (data, type, row) {
          return `
                        <button class="btn btn-sm btn-info" onclick="viewNews(${row.id})">Görüntüle</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteNews(${row.id})">Sil</button>
                    `;
        },
      },
    ],
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/tr.json",
    },
    responsive: true,
    pageLength: 10,
  });
}

async function deleteNews(id) {
  if (!confirm("Bu haberi silmek istediğinizden emin misiniz?")) {
    return;
  }

  try {
    const response = await fetch(`/api/news/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (response.ok) {
      showSuccess("Haber silindi");
      $("#newsTable").DataTable().ajax.reload();
    } else {
      showError("Haber silinemedi");
    }
  } catch (error) {
    showError("Bağlantı hatası");
  }
}

function viewNews(id) {
  window.location.href = `news-detail.html?id=${id}`;
}

function showSuccess(message) {
  alert(message);
}

function showError(message) {
  alert("Hata: " + message);
}
