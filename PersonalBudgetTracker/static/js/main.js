// Main JavaScript for the application

// DOM ready handler
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUploads();
    initializeTooltips();
    setupFormHandlers();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Initialize file upload areas
function initializeFileUploads() {
    const fileUploads = document.querySelectorAll('.file-upload');
    
    fileUploads.forEach(upload => {
        const input = upload.querySelector('input[type="file"]');
        const uploadArea = upload.querySelector('.upload-area');
        const fileNameDisplay = upload.querySelector('.file-name');
        
        if (!uploadArea || !input) return;
        
        uploadArea.addEventListener('click', () => {
            input.click();
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('active');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('active');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('active');
            
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                updateFileName(input, fileNameDisplay);
            }
        });
        
        input.addEventListener('change', () => {
            updateFileName(input, fileNameDisplay);
        });
    });
}

// Update file name display after selection
function updateFileName(input, display) {
    if (!display) return;
    
    if (input.files.length) {
        display.textContent = input.files[0].name;
        display.classList.remove('d-none');
    } else {
        display.textContent = '';
        display.classList.add('d-none');
    }
}

// Setup form submission handlers
function setupFormHandlers() {
    const jdForm = document.getElementById('jd-upload-form');
    const cvForm = document.getElementById('cv-upload-form');
    
    if (jdForm) {
        jdForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = jdForm.querySelector('button[type="submit"]');
            const loadingSpinner = jdForm.querySelector('.spinner-container');
            
            // Show loading state
            if (submitBtn) submitBtn.disabled = true;
            if (loadingSpinner) loadingSpinner.classList.remove('d-none');
            
            fetch('/api/job-description', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Success - show success message and update UI
                showAlert('success', 'Job description uploaded and analyzed successfully!');
                
                // If there's a results container, populate it
                const resultsContainer = document.getElementById('jd-results');
                if (resultsContainer && data.analysis) {
                    populateJdResults(data.analysis, resultsContainer);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Failed to upload job description. Please try again.');
            })
            .finally(() => {
                // Reset loading state
                if (submitBtn) submitBtn.disabled = false;
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
            });
        });
    }
    
    if (cvForm) {
        cvForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = cvForm.querySelector('button[type="submit"]');
            const loadingSpinner = cvForm.querySelector('.spinner-container');
            
            // Show loading state
            if (submitBtn) submitBtn.disabled = true;
            if (loadingSpinner) loadingSpinner.classList.remove('d-none');
            
            fetch('/api/resume', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Success - show success message
                showAlert('success', 'Resume uploaded and analyzed successfully!');
                
                // Redirect to dashboard if processing completed
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Failed to upload resume. Please try again.');
            })
            .finally(() => {
                // Reset loading state
                if (submitBtn) submitBtn.disabled = false;
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
            });
        });
    }
}

// Populate JD analysis results
function populateJdResults(analysis, container) {
    if (!container) return;
    
    // Clear previous content
    container.innerHTML = '';
    
    // Create sections for different parts of analysis
    const sections = {
        skills: createAnalysisSection('Required Skills', analysis.skills || []),
        experience: createAnalysisSection('Experience Requirements', analysis.experience || []),
        qualifications: createAnalysisSection('Qualifications', analysis.qualifications || []),
        responsibilities: createAnalysisSection('Responsibilities', analysis.responsibilities || [])
    };
    
    // Append all sections to container
    Object.values(sections).forEach(section => {
        container.appendChild(section);
    });
    
    // Show the container with animation
    container.classList.add('fade-in');
    container.classList.remove('d-none');
}

// Create a section for analysis results
function createAnalysisSection(title, items) {
    const section = document.createElement('div');
    section.className = 'mb-4';
    
    const heading = document.createElement('h5');
    heading.textContent = title;
    section.appendChild(heading);
    
    if (items.length === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.className = 'text-muted fst-italic';
        emptyMsg.textContent = 'No items detected';
        section.appendChild(emptyMsg);
    } else {
        const list = document.createElement('ul');
        list.className = 'list-group';
        
        items.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.textContent = item;
            list.appendChild(listItem);
        });
        
        section.appendChild(list);
    }
    
    return section;
}

// Show alert message
function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}
