// Header logic
document.addEventListener('DOMContentLoaded', function () {
    const currentPage = window.location.pathname;
    const dashboardLink = document.getElementById('dashboard-link');
    const archiveLink = document.getElementById('archive-link');
    const configLink = document.getElementById('config-link');
    
    if (currentPage === '/' || currentPage === '/index') {
        dashboardLink.classList.add('active');
    } else {
        dashboardLink.classList.remove('active');
    }

    if (currentPage === '/archive') {
        archiveLink.classList.add('active');
    } else {
        archiveLink.classList.remove('active');
    }

    if (currentPage === '/config') {
        configLink.classList.add('active');
    } else {
        configLink.classList.remove('active');
    }
});
