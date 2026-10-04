/**
 * FoodExpress - Admin Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile sidebar toggle
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.admin-sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }

  // Generic table filter/search input
  const tableSearchInput = document.getElementById('admin-table-search');
  if (tableSearchInput) {
    tableSearchInput.addEventListener('keyup', function() {
      const filter = this.value.toLowerCase();
      const rows = document.querySelectorAll('.admin-table tbody tr');
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  }

  // Delete item confirmation
  document.querySelectorAll('.btn-delete-confirm').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const itemTitle = this.getAttribute('data-item') || 'this item';
      if (!confirm(`Are you sure you want to permanently delete ${itemTitle}? This action cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });
});
