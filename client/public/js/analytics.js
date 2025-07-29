// Analytics and visualization functionality

class NewsAnalytics {
  constructor() {
    this.charts = {};
  }

  async loadOverviewStats() {
    try {
      const response = await fetch("/api/analytics/stats/overview", {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      });

      if (response.ok) {
        const stats = await response.json();
        this.displayOverviewStats(stats);
      }
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  }

  displayOverviewStats(stats) {
    const container = document.getElementById("statsOverview");
    if (!container) return;

    container.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-card bg-primary text-white">
                        <h3>${stats.total_articles}</h3>
                        <p>Toplam Haber</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card bg-success text-white">
                        <h3>${stats.recent_articles}</h3>
                        <p>Son 30 Gün</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card bg-info text-white">
                        <h3>${stats.articles_with_images}</h3>
                        <p>Görselli Haberler</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card bg-warning text-white">
                        <h3>${
                          stats.latest_article_date
                            ? this.formatDate(stats.latest_article_date)
                            : "Yok"
                        }</h3>
                        <p>Son Ekleme</p>
                    </div>
                </div>
            </div>
        `;
  }

  async loadTimelineChart(days = 30) {
    try {
      const response = await fetch(
        `/api/analytics/stats/timeline?days=${days}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        this.renderTimelineChart(data);
      }
    } catch (error) {
      console.error("Error loading timeline:", error);
    }
  }

  renderTimelineChart(data) {
    const ctx = document.getElementById("timelineChart");
    if (!ctx) return;

    if (this.charts.timeline) {
      this.charts.timeline.destroy();
    }

    this.charts.timeline = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map((d) => this.formatDate(d.date)),
        datasets: [
          {
            label: "Günlük Haber Sayısı",
            data: data.map((d) => d.count),
            borderColor: "rgb(75, 192, 192)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            tension: 0.1,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Haber Çıkarma Zaman Çizelgesi",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  async loadDomainsChart() {
    try {
      const response = await fetch("/api/analytics/stats/domains", {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        this.renderDomainsChart(data);
      }
    } catch (error) {
      console.error("Error loading domains:", error);
    }
  }

  renderDomainsChart(data) {
    const ctx = document.getElementById("domainsChart");
    if (!ctx) return;

    if (this.charts.domains) {
      this.charts.domains.destroy();
    }

    const colors = this.generateColors(data.length);

    this.charts.domains = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: data.map((d) => d.domain),
        datasets: [
          {
            data: data.map((d) => d.count),
            backgroundColor: colors,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "En Çok Kullanılan Kaynaklar",
          },
          legend: {
            position: "right",
          },
        },
      },
    });
  }

  generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
      const hue = ((i * 360) / count) % 360;
      colors.push(`hsl(${hue}, 70%, 60%)`);
    }
    return colors;
  }

  formatDate(dateString) {
    return new Date(dateString).toLocaleDateString("tr-TR");
  }
}

// Initialize analytics when needed
const analytics = new NewsAnalytics();
