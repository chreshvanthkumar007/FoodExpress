/**
 * FoodExpress - Main JavaScript
 */

// Toast notification helper
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `custom-toast ${type === 'danger' ? 'bg-danger' : 'bg-dark'}`;
  
  const icon = type === 'danger' ? '⚠️' : '✅';
  toast.innerHTML = `<span>${icon}</span><span style="font-weight: 500;">${message}</span>`;
  
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// Global Quantity Selector Logic
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss standard alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // Quantity input controls
  document.querySelectorAll('.qty-btn').forEach(btn => {
    // Skip if button has its own specific onclick action (e.g., in cart table)
    if (btn.hasAttribute('onclick')) return;

    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const parent = this.closest('.qty-selector');
      const input = parent.querySelector('input[type="number"], .qty-value');
      let currentVal = parseInt(input.value || input.innerText || '1');
      const isIncrement = this.classList.contains('plus');
      
      if (isIncrement) {
        currentVal++;
      } else if (currentVal > 1) {
        currentVal--;
      }
      
      if (input.tagName === 'INPUT') {
        input.value = currentVal;
      } else {
        input.innerText = currentVal;
      }
    });
  });
});
