/**
 * FoodExpress - Checkout & Payment Simulation JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  const paymentCodRadio = document.getElementById('payment-cod');
  const paymentOnlineRadio = document.getElementById('payment-online');
  const onlinePaymentDetails = document.getElementById('online-payment-details');
  const checkoutForm = document.getElementById('checkout-form');
  const placeOrderBtn = document.getElementById('place-order-btn');

  function togglePaymentFields() {
    if (paymentOnlineRadio && paymentOnlineRadio.checked) {
      if (onlinePaymentDetails) onlinePaymentDetails.style.display = 'block';
    } else {
      if (onlinePaymentDetails) onlinePaymentDetails.style.display = 'none';
    }
  }

  if (paymentCodRadio && paymentOnlineRadio) {
    paymentCodRadio.addEventListener('change', togglePaymentFields);
    paymentOnlineRadio.addEventListener('change', togglePaymentFields);
    togglePaymentFields();
  }

  // Handle Form Submission with Demo Payment Confirmation
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', function(e) {
      if (!checkoutForm.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        checkoutForm.classList.add('was-validated');
        return;
      }

      // If Online Demo payment is selected, show demo modal or processing state
      if (paymentOnlineRadio && paymentOnlineRadio.checked) {
        e.preventDefault();
        const demoModalEl = document.getElementById('demoPaymentModal');
        if (demoModalEl) {
          const demoModal = new bootstrap.Modal(demoModalEl);
          demoModal.show();
        } else {
          // Direct submission
          checkoutForm.submit();
        }
      } else {
        // Cash on delivery direct submission
        placeOrderBtn.disabled = true;
        placeOrderBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Placing Order...';
      }
    });
  }

  // Confirm demo payment button inside modal
  const confirmDemoPayBtn = document.getElementById('confirm-demo-payment-btn');
  if (confirmDemoPayBtn) {
    confirmDemoPayBtn.addEventListener('click', function() {
      confirmDemoPayBtn.disabled = true;
      confirmDemoPayBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing Demo Payment...';
      
      setTimeout(() => {
        if (checkoutForm) {
          checkoutForm.submit();
        }
      }, 1000);
    });
  }
});
