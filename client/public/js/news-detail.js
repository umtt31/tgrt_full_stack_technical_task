// Global variable to store current news data
let currentNews = null;

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

  const urlParams = new URLSearchParams(window.location.search);
  const newsId = urlParams.get("id");

  if (!newsId) {
    showError("Haber ID'si bulunamadı");
    return;
  }

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
  document.getElementById("loading").classList.add("d-none");
  document.getElementById("newsDetail").classList.remove("d-none");

  document.getElementById("newsTitle").textContent =
    news.title || "Başlık bulunamadı";

  const contentElement = document.getElementById("newsContent");
  if (news.content) {
    const paragraphs = news.content.split("\n\n").filter((p) => p.trim());
    contentElement.innerHTML = paragraphs
      .map((p) => `<p>${p.trim()}</p>`)
      .join("");
  } else {
    contentElement.innerHTML = '<p class="text-muted">İçerik bulunamadı</p>';
  }

  // Handle video display
  const videoContainer = document.getElementById("newsVideoContainer");
  const videoElement = document.getElementById("newsVideo");
  const videoSource = document.getElementById("videoSource");

  if (news.video_url) {
    // Check if it's an iframe embed (YouTube, Vimeo, etc.)
    if (
      news.video_url.includes("youtube.com") ||
      news.video_url.includes("vimeo.com") ||
      news.video_url.includes("dailymotion.com") ||
      news.video_url.includes("facebook.com")
    ) {
      // Create iframe for embedded videos
      videoContainer.innerHTML = `
        <div class="video-container">
          <iframe src="${news.video_url}" frameborder="0" allowfullscreen></iframe>
        </div>
      `;
    } else {
      // Direct video file
      videoSource.src = news.video_url;
      videoElement.load();
    }
    videoContainer.classList.remove("d-none");
  } else {
    videoContainer.classList.add("d-none");
  }

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

  document.getElementById("newsUrl").href = news.url;
  document.getElementById("newsUrl").textContent = news.url;

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

  const metaLanguageElement = document.getElementById("metaLanguage");
  if (news.meta_lang) {
    const languageNames = {
      tr: "Türkçe",
      en: "İngilizce",
    };
    const languageName =
      languageNames[news.meta_lang] || news.meta_lang.toUpperCase();
    metaLanguageElement.innerHTML = `<span class="language-badge">${languageName}</span>`;
  } else {
    metaLanguageElement.textContent = "Belirtilmemiş";
  }

  // Display video info in sidebar
  const videoSection = document.getElementById("videoSection");
  const videoLink = document.getElementById("videoLink");
  if (news.video_url) {
    videoLink.href = news.video_url;
    videoSection.style.display = "block";
  } else {
    videoSection.style.display = "none";
  }

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

  const wordCount = news.content ? news.content.split(/\s+/).length : 0;
  const readingTime = Math.ceil(wordCount / 200);

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
