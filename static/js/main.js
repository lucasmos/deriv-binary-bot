// Initialize tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })
  
  // Initialize popovers
  $(function () {
    $('[data-toggle="popover"]').popover()
  })
  
  // Form validation
  document.addEventListener('DOMContentLoaded', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation')
    
    // Loop over them and prevent submission
    Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add('was-validated')
      }, false)
    })
  }, false)
  
  // AJAX CSRF setup for Django (adjust for Flask if needed)
  $(document).ajaxSend(function(event, xhr, settings) {
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'))
    }
  })
  
  function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';')
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }
  
  // Notification handler
  function showNotification(type, message) {
    const alert = $(`<div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`)
    
    $('#notifications').append(alert)
    
    setTimeout(() => {
      alert.alert('close')
    }, 5000)
  }
  
  // Handle flash messages from server
  document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.flash-message')
    flashes.forEach(flash => {
      const type = flash.dataset.type || 'info'
      const message = flash.textContent
      showNotification(type, message)
    })
  })