// Global variable to store current news data
let currentNews = null;

// Check authentication on page load
document.addEventListener("DOMContentLoaded", function () {
  if (!isAuthenticated()) {
    window.location.href = "login.html";
    return;
  }

  // Set username
  const user = getCurrentUser();
  if (user) {
    document.getElementById(
      "username"
    ).textContent = `Merhaba, ${user.username}`;
  }

  // Get news ID from URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const newsId = urlParams.get("id");

  if (!newsId) {
    showError("Haber ID'si bulunamadı");
    return;
  }

  // Load news details
  loadNewsDetail(newsId);
});

async function loadNewsDetail(newsId) {
  try {
    const response = await fetch(`/api/news/${newsId}`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (response.ok) {
      const news = await response.json();
      currentNews = news;
      displayNewsDetail(news);
    } else {
      const error = await response.json();
      showError(error.detail || "Haber yüklenemedi");
    }
  } catch (error) {
    showError("Bağlantı hatası");
  }
}

function displayNewsDetail(news) {
  // Hide loading, show content
  document.getElementById("loading").classList.add("d-none");
  document.getElementById("newsDetail").classList.remove("d-none");

  // Set title
  document.getElementById("newsTitle").textContent =
    news.title || "Başlık bulunamadı";

  // Set content
  const contentElement = document.getElementById("newsContent");
  if (news.content) {
    // Split content into paragraphs for better readability
    const paragraphs = news.content.split("\n\n").filter((p) => p.trim());
    contentElement.innerHTML = paragraphs
      .map((p) => `<p>${p.trim()}</p>`)
      .join("");
  } else {
    contentElement.innerHTML = '<p class="text-muted">İçerik bulunamadı</p>';
  }

  // Set image if available
  const imageContainer = document.getElementById("newsImageContainer");
  const imageElement = document.getElementById("newsImage");
  if (news.image_url) {
    imageElement.src = news.image_url;
    imageElement.onerror = function () {
      imageContainer.classList.add("d-none");
    };
    imageContainer.classList.remove("d-none");
  } else {
    imageContainer.classList.add("d-none");
  }

  // Set metadata
  document.getElementById("newsUrl").href = news.url;
  document.getElementById("newsUrl").textContent = news.url;

  // Format dates
  if (news.publish_date) {
    document.getElementById("publishDate").textContent = new Date(
      news.publish_date
    ).toLocaleDateString("tr-TR");
  } else {
    document.getElementById("publishDate").textContent = "Belirtilmemiş";
  }

  document.getElementById("createdDate").textContent = new Date(
    news.created_at
  ).toLocaleDateString("tr-TR");

  // Display meta language
  const metaLanguageElement = document.getElementById("metaLanguage");
  if (news.meta_lang) {
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
    const languageName =
      languageNames[news.meta_lang] || news.meta_lang.toUpperCase();
    metaLanguageElement.innerHTML = `<span class="language-badge">${languageName}</span>`;
  } else {
    metaLanguageElement.textContent = "Belirtilmemiş";
  }

  // Display meta keywords
  const keywordsSection = document.getElementById("keywordsSection");
  const metaKeywordsElement = document.getElementById("metaKeywords");
  if (news.meta_keywords) {
    try {
      const keywords = JSON.parse(news.meta_keywords);
      if (Array.isArray(keywords) && keywords.length > 0) {
        const keywordTags = keywords
          .map((keyword) => `<span class="keyword-tag">${keyword}</span>`)
          .join("");
        metaKeywordsElement.innerHTML = keywordTags;
        keywordsSection.style.display = "block";
      } else {
        keywordsSection.style.display = "none";
      }
    } catch (e) {
      // If parsing fails, try to display as string
      if (news.meta_keywords.trim()) {
        metaKeywordsElement.innerHTML = `<span class="keyword-tag">${news.meta_keywords}</span>`;
        keywordsSection.style.display = "block";
      } else {
        keywordsSection.style.display = "none";
      }
    }
  } else {
    keywordsSection.style.display = "none";
  }

  // Calculate word count and reading time
  const wordCount = news.content ? news.content.split(/\s+/).length : 0;
  const readingTime = Math.ceil(wordCount / 200); // Average reading speed: 200 words per minute

  document.getElementById("wordCount").textContent =
    wordCount.toLocaleString("tr-TR");
  document.getElementById("readingTime").textContent = `${readingTime} dakika`;
}

function openOriginalUrl() {
  if (currentNews && currentNews.url) {
    window.open(currentNews.url, "_blank");
  }
}

async function deleteNews() {
  if (!currentNews) return;

  if (!confirm("Bu haberi silmek istediğinizden emin misiniz?")) {
    return;
  }

  try {
    const response = await fetch(`/api/news/${currentNews.id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (response.ok) {
      alert("Haber başarıyla silindi");
      goBack();
    } else {
      const error = await response.json();
      showError(error.detail || "Haber silinemedi");
    }
  } catch (error) {
    showError("Bağlantı hatası");
  }
}

function goBack() {
  window.history.back();
}

function showError(message) {
  document.getElementById("loading").classList.add("d-none");
  document.getElementById("newsDetail").classList.add("d-none");

  const errorElement = document.getElementById("errorMessage");
  const errorText = document.getElementById("errorText");

  errorText.textContent = message;
  errorElement.classList.remove("d-none");
}
