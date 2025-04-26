class StrategyEditor {
    constructor() {
      this.editor = null
      this.initCodeEditor()
      this.bindEvents()
    }
    
    initCodeEditor() {
      const editorElement = document.getElementById('strategyCodeEditor')
      if (editorElement) {
        this.editor = CodeMirror.fromTextArea(editorElement, {
          mode: 'python',
          theme: 'dracula',
          lineNumbers: true,
          indentUnit: 4,
          tabSize: 4,
          extraKeys: {
            'Tab': function(cm) {
              if (cm.somethingSelected()) {
                cm.indentSelection('add')
              } else {
                cm.replaceSelection(cm.getOption('indentWithTabs') ? '\t' : 
                  Array(cm.getOption('indentUnit') + 1).join(' '), 'end', '+input')
              }
            },
            'Shift-Tab': function(cm) {
              cm.indentSelection('subtract')
            }
          }
        })
      }
    }
    
    bindEvents() {
      // Strategy validation
      document.getElementById('validateStrategyBtn')?.addEventListener('click', this.validateStrategy.bind(this))
      
      // Strategy save
      document.getElementById('saveStrategyBtn')?.addEventListener('click', this.saveStrategy.bind(this))
      
      // Strategy test
      document.getElementById('testStrategyBtn')?.addEventListener('click', this.testStrategy.bind(this))
    }
    
    validateStrategy() {
      const code = this.editor.getValue()
      
      // Basic validation - check for required functions
      const requiredFunctions = ['generate_signal', 'analyze']
      const missingFunctions = requiredFunctions.filter(fn => !code.includes(`def ${fn}(`))
      
      if (missingFunctions.length > 0) {
        showNotification('danger', `Missing required functions: ${missingFunctions.join(', ')}`)
        return false
      }
      
      showNotification('success', 'Strategy code is valid!')
      return true
    }
    
    saveStrategy() {
      if (!this.validateStrategy()) return
      
      const form = document.getElementById('strategyForm')
      const codeInput = document.getElementById('strategyCode')
      codeInput.value = this.editor.getValue()
      
      // Submit form
      form.submit()
    }
    
    async testStrategy() {
      if (!this.validateStrategy()) return
      
      const code = this.editor.getValue()
      const response = await fetch('/api/v1/strategies/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ code })
      })
      
      const result = await response.json()
      
      if (result.success) {
        showNotification('success', 'Strategy test passed!')
        this.displayTestResults(result.data)
      } else {
        showNotification('danger', result.message || 'Strategy test failed')
      }
    }
    
    displayTestResults(results) {
      const resultsContainer = document.getElementById('testResults')
      if (!resultsContainer) return
      
      resultsContainer.innerHTML = `
        <div class="card">
          <div class="card-header">
            <h5>Test Results</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Win Rate:</strong> ${(results.win_rate * 100).toFixed(2)}%</p>
                <p><strong>Profit Factor:</strong> ${results.profit_factor.toFixed(2)}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Total Trades:</strong> ${results.total_trades}</p>
                <p><strong>Max Drawdown:</strong> ${(results.max_drawdown * 100).toFixed(2)}%</p>
              </div>
            </div>
            <div class="mt-3">
              <canvas id="backtestChart" height="200"></canvas>
            </div>
          </div>
        </div>
      `
      
      // Initialize chart with backtest results
      this.initBacktestChart(results.performance)
    }
    
    initBacktestChart(performanceData) {
      const ctx = document.getElementById('backtestChart').getContext('2d')
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: performanceData.labels,
          datasets: [{
            label: 'Equity Curve',
            data: performanceData.equity,
            borderColor: '#2ecc71',
            backgroundColor: 'rgba(46, 204, 113, 0.1)',
            borderWidth: 2,
            fill: true
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `Equity: $${context.parsed.y.toFixed(2)}`
                }
              }
            }
          },
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
          }
        }
      })
    }
  }
  
  // Initialize when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('strategyCodeEditor')) {
      new StrategyEditor()
    }
  })