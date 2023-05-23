document.querySelectorAll('.info-icon').forEach(function(icon) {
    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');
    tooltip.innerHTML = icon.dataset.description.replace(/\. /g, '.<br>');
    icon.parentNode.appendChild(tooltip);
    icon.addEventListener('mouseover', function() {
        const rect = icon.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        tooltip.style.visibility = 'visible';
        tooltip.style.opacity = '1';
    });
    icon.addEventListener('mouseout', function() {
        tooltip.style.visibility = 'hidden';
        tooltip.style.opacity = '0';
    });
});
