/* ============================================================
   MAkONGO JUU SDA FINANCE DASHBOARD - Main JavaScript
   ============================================================ */

// TSH Currency Formatter
function formatTSH(amount) {
    if (isNaN(amount)) return '0.00';
    return amount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format all TSH values on page load
function formatAllTSH() {
    document.querySelectorAll('.tsh-value').forEach(el => {
        const raw = parseFloat(el.textContent.replace(/,/g, '').trim());
        if (!isNaN(raw)) {
            el.textContent = formatTSH(raw);
        }
    });
}

// Auto-dismiss alerts
function initAlerts() {
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
}

// Active nav link detection
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-pill, .mobile-nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

// Clickable table rows
function initClickableRows() {
    document.querySelectorAll('.table-row-clickable').forEach(row => {
        row.addEventListener('click', function(e) {
            if (!e.target.closest('.action-cell') && !e.target.closest('form') && !e.target.closest('button') && !e.target.closest('a')) {
                const url = this.dataset.url;
                if (url) window.location.href = url;
            }
        });
    });
}

// Confirm delete actions
function initDeleteConfirm() {
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const msg = this.dataset.confirm || 'Are you sure you want to delete this record?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
}

// Inline amount editing for fixed income rows
function initInlineEdit() {
    document.querySelectorAll('.inline-amount-input').forEach(input => {
        input.addEventListener('focus', function() {
            this.select();
        });
        input.addEventListener('blur', function() {
            const form = this.closest('form');
            if (form) form.submit();
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const form = this.closest('form');
                if (form) form.submit();
            }
        });
    });
}

// Number input formatting
function initNumberInputs() {
    document.querySelectorAll('input[type="number"][data-format="tsh"]').forEach(input => {
        input.addEventListener('blur', function() {
            const val = parseFloat(this.value);
            if (!isNaN(val)) {
                this.dataset.rawValue = val;
            }
        });
    });
}

// Mobile menu toggle
function initMobileMenu() {
    const toggler = document.getElementById('mobileMenuToggler');
    if (toggler) {
        toggler.addEventListener('click', function() {
            const offcanvas = document.getElementById('mobileOffcanvas');
            if (offcanvas) {
                const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(offcanvas);
                bsOffcanvas.show();
            }
        });
    }
}

// Date range quick selectors
function setDateRange(days) {
    const today = new Date();
    const from = new Date(today);
    from.setDate(today.getDate() - days);

    const toInput = document.querySelector('input[name="date_to"]');
    const fromInput = document.querySelector('input[name="date_from"]');

    if (fromInput) fromInput.value = from.toISOString().split('T')[0];
    if (toInput) toInput.value = today.toISOString().split('T')[0];
}

// Tooltip initialization
function initTooltips() {
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(el => new bootstrap.Tooltip(el));
}

// Chart.js helpers
function createBarChart(canvasId, labels, datasets, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    return new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { font: { size: 12 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => `TSH ${formatTSH(ctx.parsed.y)}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: val => 'TSH ' + formatTSH(val),
                        font: { size: 11 }
                    },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: {
                    ticks: { font: { size: 11 } },
                    grid: { display: false }
                }
            },
            ...options
        }
    });
}

function createDoughnutChart(canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    return new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { font: { size: 12 }, padding: 16 } },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.label}: TSH ${formatTSH(ctx.parsed)}`
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Source name toggle for income form
function toggleSourceName() {
    const source = document.getElementById('id_source');
    const group = document.getElementById('sourceNameGroup');
    if (source && group) {
        group.style.display = source.value === 'other' ? 'block' : 'none';
    }
}

// Password visibility toggle
function togglePassword(fieldId, iconId) {
    const field = document.getElementById(fieldId || 'passwordField');
    const icon = document.getElementById(iconId || 'eyeIcon');
    if (field && icon) {
        if (field.type === 'password') {
            field.type = 'text';
            icon.classList.replace('fa-eye', 'fa-eye-slash');
        } else {
            field.type = 'password';
            icon.classList.replace('fa-eye-slash', 'fa-eye');
        }
    }
}

// Status modal opener
function openStatusModal(pk, currentStatus) {
    const form = document.getElementById('statusForm');
    const select = document.getElementById('statusSelect');
    if (form) form.action = `/expenses/${pk}/status/`;
    if (select) select.value = currentStatus;
}

// Print page
function printPage() {
    window.print();
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tr');
    const csvData = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => {
            let text = col.innerText.replace(/\n/g, ' ').trim();
            if (text.includes(',')) text = `"${text}"`;
            return text;
        });
        csvData.push(rowData.join(','));
    });

    const csvString = csvData.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize everything on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    formatAllTSH();
    initAlerts();
    setActiveNavLink();
    initClickableRows();
    initDeleteConfirm();
    initInlineEdit();
    initNumberInputs();
    initMobileMenu();
    initTooltips();

    // Set today's date on empty date inputs
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value && input.dataset.defaultToday !== 'false') {
            // Don't auto-set filter inputs
            if (!input.name.includes('date_from') && !input.name.includes('date_to')) {
                input.value = new Date().toISOString().split('T')[0];
            }
        }
    });

    // Source name toggle on load
    toggleSourceName();
});
