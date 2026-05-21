(() => {
  function initAmenitySelector(root) {
    const searchInput = root.querySelector('[data-amenity-search]');
    const cards = Array.from(root.querySelectorAll('[data-amenity-card]'));
    const chips = root.querySelector('[data-amenity-chips]');
    const counter = root.querySelector('[data-amenity-counter]');
    const btnSelectVisible = root.querySelector('[data-amenity-select-visible]');
    const btnClear = root.querySelector('[data-amenity-clear]');
    if (!searchInput || !cards.length) return;

    const update = () => {
      const term = searchInput.value.trim().toLowerCase();
      let checked = 0;
      cards.forEach((card) => {
        const text = (card.dataset.amenityText || '').toLowerCase();
        card.style.display = text.includes(term) ? '' : 'none';
        const input = card.querySelector('input[type="checkbox"]');
        if (input && input.checked) checked += 1;
      });
      if (counter) counter.textContent = String(checked);
      if (chips) {
        chips.innerHTML = '';
        cards.forEach((card) => {
          const input = card.querySelector('input[type="checkbox"]');
          if (!input || !input.checked) return;
          const label = card.querySelector('[data-amenity-label]');
          const icon = card.querySelector('i');
          const chip = document.createElement('span');
          chip.className = 'badge rounded-pill text-bg-light border me-2 mb-2';
          chip.innerHTML = `${icon ? icon.outerHTML : ''} ${label ? label.textContent : ''}`;
          chips.appendChild(chip);
        });
      }
    };

    searchInput.addEventListener('input', update);
    cards.forEach((card) => {
      const input = card.querySelector('input[type="checkbox"]');
      if (input) input.addEventListener('change', update);
    });
    if (btnSelectVisible) {
      btnSelectVisible.addEventListener('click', () => {
        cards.forEach((card) => {
          if (card.style.display === 'none') return;
          const input = card.querySelector('input[type="checkbox"]');
          if (input) input.checked = true;
        });
        update();
      });
    }
    if (btnClear) {
      btnClear.addEventListener('click', () => {
        cards.forEach((card) => {
          const input = card.querySelector('input[type="checkbox"]');
          if (input) input.checked = false;
        });
        update();
      });
    }
    update();
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-amenity-selector]').forEach(initAmenitySelector);
  });
})();
