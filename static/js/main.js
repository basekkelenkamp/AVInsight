document.querySelectorAll('.info-icon').forEach(function(icon) {
    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');
    tooltip.innerHTML = icon.dataset.description.replace(/\. /g, '.<br>');
    icon.parentNode.appendChild(tooltip);
    icon.addEventListener('mouseover', function() {
        const rect = icon.getBoundingClientRect();
        tooltip.style.visibility = 'hidden';
        tooltip.style.opacity = '0';
        // force a recalc of the tooltip dimensions
        tooltip.offsetHeight;

        let tooltipLeft = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;

        // Check if the tooltip goes off the left side of the screen
        if (tooltipLeft < 0 || tooltipLeft < tooltip.offsetWidth / 2) {
            tooltipLeft = 0;
        }

        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        tooltip.style.left = tooltipLeft + 'px';
        tooltip.style.visibility = 'visible';
        tooltip.style.opacity = '1';
    });
    icon.addEventListener('mouseout', function() {
        tooltip.style.visibility = 'hidden';
        tooltip.style.opacity = '0';
    });
});
