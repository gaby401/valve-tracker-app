// Main JavaScript for Heart Valve Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // File upload preview
    const fileInput = document.querySelector('.custom-file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0].name;
            const label = e.target.nextElementSibling;
            label.textContent = fileName;
        });
    }
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Toggle password visibility
    const togglePassword = document.querySelector('#togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordInput = document.querySelector('#password');
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('bi-eye');
            this.classList.toggle('bi-eye-slash');
        });
    }
    
    // Show loading spinner on form submit
    const forms = document.querySelectorAll('form:not(.no-spinner)');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const spinner = document.createElement('div');
            spinner.className = 'spinner-overlay';
            spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.body.appendChild(spinner);
        });
    });
    
    // Table sorting
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortField = this.dataset.sort;
            const currentSortDir = this.dataset.sortDir || 'asc';
            const newSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
            
            // Update URL with sort parameters
            const url = new URL(window.location);
            url.searchParams.set('sort_by', sortField);
            url.searchParams.set('sort_dir', newSortDir);
            window.location = url.toString();
        });
    });
    
    // File type preview handling
    const previewButtons = document.querySelectorAll('.btn-preview');
    previewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const fileUrl = this.dataset.fileUrl;
            const fileType = this.dataset.fileType;
            const previewModal = document.getElementById('previewModal');
            const previewContent = document.getElementById('previewContent');
            const previewTitle = document.getElementById('previewModalLabel');
            
            previewTitle.textContent = 'File Preview';
            previewContent.innerHTML = '';
            
            if (fileType === 'Image') {
                const img = document.createElement('img');
                img.src = fileUrl;
                img.className = 'img-fluid file-preview-image';
                previewContent.appendChild(img);
            } else if (fileType === 'PDF') {
                const iframe = document.createElement('iframe');
                iframe.src = fileUrl;
                iframe.className = 'file-preview-pdf';
                previewContent.appendChild(iframe);
            } else {
                previewContent.innerHTML = '<div class="alert alert-info">Preview not available for this file type. Please download the file to view it.</div>';
            }
            
            const modal = new bootstrap.Modal(previewModal);
            modal.show();
        });
    });
    
    // Dashboard charts initialization
    const statusChartCanvas = document.getElementById('statusChart');
    if (statusChartCanvas) {
        const statusData = JSON.parse(statusChartCanvas.dataset.values);
        const statusLabels = JSON.parse(statusChartCanvas.dataset.labels);
        const statusColors = [
            '#6c757d', // Received - secondary
            '#ffc107', // In Testing - warning
            '#28a745', // Passed - success
            '#dc3545', // Failed - danger
            '#17a2b8'  // On Hold - info
        ];
        
        new Chart(statusChartCanvas, {
            type: 'doughnut',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: statusColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }
    
    const typeChartCanvas = document.getElementById('typeChart');
    if (typeChartCanvas) {
        const typeData = JSON.parse(typeChartCanvas.dataset.values);
        const typeLabels = JSON.parse(typeChartCanvas.dataset.labels);
        
        new Chart(typeChartCanvas, {
            type: 'bar',
            data: {
                labels: typeLabels,
                datasets: [{
                    label: 'Valve Types',
                    data: typeData,
                    backgroundColor: 'rgba(0, 119, 204, 0.7)',
                    borderColor: 'rgba(0, 119, 204, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Date range picker for reports
    const dateRangePicker = document.getElementById('dateRange');
    if (dateRangePicker) {
        new DateRangePicker(dateRangePicker, {
            showOnFocus: true
        });
    }
    
    // Mobile navigation handling
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(event) {
            const isNavbarOpen = navbarCollapse.classList.contains('show');
            const clickedInsideNavbar = navbarCollapse.contains(event.target) || navbarToggler.contains(event.target);
            
            if (isNavbarOpen && !clickedInsideNavbar) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.hide();
            }
        });
    }
});
