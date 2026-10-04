/**
 * FoodExpress - Shopping Cart JavaScript
 */

// Add item to cart via AJAX
async function addToCart(foodId, quantity = 1) {
  try {
    const response = await fetch('/cart/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ food_id: foodId, quantity: quantity })
    });

    const data = await response.json();

    if (response.status === 401) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
      return;
    }

    if (data.success) {
      showToast(data.message || 'Item added to cart!');
      updateCartBadge(data.cart_count);
    } else {
      showToast(data.message || 'Could not add item to cart', 'danger');
    }
  } catch (error) {
    console.error('Error adding to cart:', error);
    showToast('Network error, please try again.', 'danger');
  }
}

// Update navbar cart badge counter
function updateCartBadge(count) {
  const badge = document.getElementById('navbar-cart-count');
  if (badge) {
    badge.innerText = count;
    badge.style.display = count > 0 ? 'inline-block' : 'none';
    badge.style.transform = 'scale(1.3)';
    setTimeout(() => { badge.style.transform = 'scale(1)'; }, 200);
  }
}

// Update cart item quantity on cart page
async function updateCartItemQty(cartItemId, newQty) {
  const qty = parseInt(newQty, 10);
  if (isNaN(qty) || qty < 1) {
    return removeCartItem(cartItemId);
  }

  try {
    const response = await fetch('/cart/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ cart_id: cartItemId, quantity: qty })
    });

    const data = await response.json();

    if (data.success) {
      // Reload cart page to update all summaries cleanly or update DOM
      window.location.reload();
    } else {
      showToast(data.message || 'Could not update quantity', 'danger');
    }
  } catch (error) {
    console.error('Error updating cart quantity:', error);
  }
}

// Remove item from cart
async function removeCartItem(cartItemId) {
  if (!confirm('Are you sure you want to remove this item from your cart?')) {
    return;
  }

  try {
    const response = await fetch(`/cart/remove/${cartItemId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    const data = await response.json();

    if (data.success) {
      window.location.reload();
    } else {
      showToast(data.message || 'Could not remove item', 'danger');
    }
  } catch (error) {
    console.error('Error removing item:', error);
    window.location.reload();
  }
}

// Clear entire cart
async function clearCart() {
  if (!confirm('Are you sure you want to clear your entire cart?')) {
    return;
  }

  try {
    const response = await fetch('/cart/clear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    const data = await response.json();
    if (data.success) {
      window.location.reload();
    }
  } catch (error) {
    console.error('Error clearing cart:', error);
  }
}

// Delegated event listener for cart actions
document.addEventListener('click', function(event) {
  // Quantity buttons (minus / plus)
  const qtyBtn = event.target.closest('.qty-btn');
  if (qtyBtn && qtyBtn.dataset.cartId) {
    const cartId = qtyBtn.dataset.cartId;
    let targetQty = parseInt(qtyBtn.dataset.qty, 10);
    if (isNaN(targetQty)) {
      const selector = qtyBtn.closest('.qty-selector');
      const valElem = selector ? selector.querySelector('.qty-value') : null;
      const current = valElem ? parseInt(valElem.textContent.trim(), 10) : 1;
      targetQty = qtyBtn.classList.contains('minus') ? current - 1 : current + 1;
    }
    updateCartItemQty(cartId, targetQty);
    return;
  }

  // Remove item button
  const removeBtn = event.target.closest('.btn-remove-item');
  if (removeBtn && removeBtn.dataset.cartId) {
    removeCartItem(removeBtn.dataset.cartId);
    return;
  }

  // Clear cart button
  const clearBtn = event.target.closest('#btn-clear-cart');
  if (clearBtn) {
    clearCart();
    return;
  }
});

// Global image fallback using capture phase for error event
document.addEventListener('error', function(event) {
  const target = event.target;
  if (target && target.tagName === 'IMG' && target.dataset && target.dataset.fallback) {
    if (target.src !== target.dataset.fallback) {
      target.src = target.dataset.fallback;
    }
  }
}, true);

