// Header logic
document.addEventListener('DOMContentLoaded', function () {
    const currentPage = window.location.pathname;
    const dashboardLink = document.getElementById('dashboard-link');
    const archiveLink = document.getElementById('archive-link');
    const configLink = document.getElementById('config-link');
    const dataReportLink = document.getElementById('data-report-link');
    
    if (currentPage === '/' || currentPage.startsWith('/index')) {
        dashboardLink.classList.add('active');
    } else {
        dashboardLink.classList.remove('active');
    }

    if (currentPage.startsWith('/archive')) {
        archiveLink.classList.add('active');
    } else {
        archiveLink.classList.remove('active');
    }

    if (currentPage.startsWith('/config')) {
        configLink.classList.add('active');
    } else {
        configLink.classList.remove('active');
    }

    if (currentPage.startsWith('/data_report')) {
        dataReportLink.classList.add('active');
    } else {
        dataReportLink.classList.remove('active');
    }
});
