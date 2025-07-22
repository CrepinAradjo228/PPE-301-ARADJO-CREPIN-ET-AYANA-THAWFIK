// property-search.js
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('propertySearchForm');
    const searchInput = document.getElementById('propertySearchInput');
    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        filterProperties();
    });

    function filterProperties() {
        const searchQuery = searchInput.value.toLowerCase();
        const propertyCards = document.querySelectorAll('.property-item');
        let hasResults = false;

        // Séparer la localisation et le type de bien
        const [locationQuery, typeQuery] = searchQuery.split(',').map(item => item.trim());

        propertyCards.forEach(card => {
            const cardLocation = card.querySelector('.icon-map-marker').nextSibling.textContent.toLowerCase();
            const cardType = card.querySelector('a.d-block.h5.mb-2').textContent.toLowerCase();
            
            // Vérifier les correspondances
            const locationMatch = !locationQuery || cardLocation.includes(locationQuery);
            const typeMatch = !typeQuery || cardType.includes(typeQuery);
            
            // Afficher ou masquer la carte
            const parentCol = card.closest('.col-md-6');
            if (locationMatch && typeMatch) {
                parentCol.style.display = 'block';
                hasResults = true;
            } else {
                parentCol.style.display = 'none';
            }
        });

        // Gérer l'affichage du message "Aucun résultat"
        const noResultsElement = document.querySelector('.no-results-message');
        if (!hasResults) {
            if (!noResultsElement) {
                const noResults = document.createElement('div');
                noResults.className = 'col-12 text-center no-results-message';
                noResults.innerHTML = '<p class="text-muted">Aucun résultat trouvé pour votre recherche.</p>';
                document.querySelector('.row').appendChild(noResults);
            }
        } else if (noResultsElement) {
            noResultsElement.remove();
        }
    }
});