// Header logic
document.addEventListener('DOMContentLoaded', function () {
    const currentPage = window.location.pathname;
    const dashboardLink = document.getElementById('dashboard-link');
    const archiveLink = document.getElementById('archive-link');
    const settingsLink = document.getElementById('settings-link');

    console.log("current page:", currentPage)
    
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

    if (currentPage === '/settings') {
        settingsLink.classList.add('active');
    } else {
        settingsLink.classList.remove('active');
    }
});
