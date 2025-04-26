// Trading charts initialization
class TradingCharts {
    constructor() {
      this.charts = {}
      this.defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        }
      }
    }
    
    initChart(canvasId, type, data, options = {}) {
      const ctx = document.getElementById(canvasId).getContext('2d')
      const mergedOptions = {...this.defaultOptions, ...options}
      
      this.charts[canvasId] = new Chart(ctx, {
        type: type,
        data: data,
        options: mergedOptions
      })
      
      return this.charts[canvasId]
    }
    
    updateChart(canvasId, data) {
      if (this.charts[canvasId]) {
        this.charts[canvasId].data = data
        this.charts[canvasId].update()
        return true
      }
      return false
    }
    
    destroyChart(canvasId) {
      if (this.charts[canvasId]) {
        this.charts[canvasId].destroy()
        delete this.charts[canvasId]
        return true
      }
      return false
    }
  }
  
  // Initialize main price chart
  function initPriceChart() {
    const chart = new TradingCharts()
    
    const data = {
      labels: [],
      datasets: [{
        label: 'Price',
        data: [],
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1
      }]
    }
    
    chart.initChart('priceChart', 'line', data, {
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return `Price: $${context.parsed.y.toFixed(2)}`
            }
          }
        }
      }
    })
    
    // Simulate data updates
    setInterval(() => {
      const now = new Date()
      data.labels.push(now.toLocaleTimeString())
      data.datasets[0].data.push(Math.random() * 100 + 100)
      
      // Keep only last 50 points
      if (data.labels.length > 50) {
        data.labels.shift()
        data.datasets[0].data.shift()
      }
      
      chart.updateChart('priceChart', data)
    }, 1000)
  }
  
  // Initialize when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('priceChart')) {
      initPriceChart()
    }
    
    // Initialize other chart types as needed
  })