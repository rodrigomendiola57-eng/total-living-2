// Total Living - JavaScript Principal Mejorado

document.addEventListener('DOMContentLoaded', function() {
    // Usar Bootstrap nativo para dropdowns - SIN JavaScript personalizado
    // Bootstrap maneja los dropdowns automáticamente

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Animación de entrada para cards
    const cards = document.querySelectorAll('.property-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Lazy loading para imágenes
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Mejorar experiencia de filtros
    const filterForm = document.querySelector('form[method="get"]');
    if (filterForm) {
        const selects = filterForm.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', function() {
                // Opcional: auto-submit cuando cambian los filtros
                // filterForm.submit();
            });
        });
    }

    // Scroll to top button
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollTopBtn.className = 'btn btn-primary rounded-circle position-fixed';
    scrollTopBtn.style.cssText = 'bottom: 30px; right: 30px; width: 50px; height: 50px; z-index: 1000; display: none; box-shadow: 0 5px 15px rgba(0,0,0,0.3);';
    scrollTopBtn.id = 'scrollTopBtn';
    document.body.appendChild(scrollTopBtn);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.style.display = 'block';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    });

    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Detectar zoom y ajustar layout automáticamente
    function detectarZoom() {
        // Método más preciso para detectar zoom
        var zoom = 100;
        
        // Método 1: Usar devicePixelRatio (más confiable)
        if (window.devicePixelRatio) {
            zoom = Math.round(window.devicePixelRatio * 100);
        }
        
        // Método 2: Comparar dimensiones (fallback)
        if (window.outerWidth && window.innerWidth) {
            var zoomCalculado = Math.round((window.outerWidth / window.innerWidth) * 100);
            if (zoomCalculado > 0 && zoomCalculado < 200) {
                zoom = zoomCalculado;
            }
        }
        
        // Método 3: Usar visualViewport si está disponible
        if (window.visualViewport) {
            var viewportZoom = Math.round((window.visualViewport.width / window.innerWidth) * 100);
            if (viewportZoom > 0 && viewportZoom < 200) {
                zoom = viewportZoom;
            }
        }
        
        // Si el zoom es mayor a 110%, ajustar el layout
        if (zoom > 110) {
            document.documentElement.classList.add('zoom-alto');
            document.body.classList.add('zoom-alto');
            
            // Ajustar el ancho máximo del contenedor
            var containers = document.querySelectorAll('.container, .container-fluid');
            containers.forEach(function(container) {
                container.style.maxWidth = '100%';
                container.style.width = '100%';
            });
            
            // Asegurar que no haya overflow-x oculto
            document.documentElement.style.overflowX = 'auto';
            document.body.style.overflowX = 'auto';
            
            // Ajustar todos los elementos principales
            var mainElements = document.querySelectorAll('main, .main-content, .content-wrapper');
            mainElements.forEach(function(element) {
                element.style.maxWidth = '100%';
                element.style.width = '100%';
            });
        } else {
            document.documentElement.classList.remove('zoom-alto');
            document.body.classList.remove('zoom-alto');
            
            // Restaurar estilos normales
            document.documentElement.style.overflowX = 'hidden';
            document.body.style.overflowX = 'hidden';
        }
    }
    
    // Detectar zoom al cargar
    setTimeout(detectarZoom, 100);
    
    // Detectar zoom al cambiar el tamaño de la ventana
    window.addEventListener('resize', function() {
        setTimeout(detectarZoom, 100);
    });
    
    // Detectar zoom cuando cambia el visualViewport
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', function() {
            setTimeout(detectarZoom, 100);
        });
    }
    
    // Detectar zoom periódicamente (por si cambia sin evento resize)
    setInterval(detectarZoom, 1000);
    
    // ========== AUTocompletado de Estados y Regiones ==========
    const estadoInput = document.getElementById('estado-input');
    const regionInput = document.getElementById('region-input');
    const estadoSuggestions = document.getElementById('estado-suggestions');
    const regionSuggestions = document.getElementById('region-suggestions');
    
    let estadoTimeout;
    let regionTimeout;
    let currentState = '';
    
    // Función para crear sugerencias
    function createSuggestionsList(suggestions, container, input, onSelect) {
        container.innerHTML = '';
        if (suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        suggestions.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.textContent = item;
            div.addEventListener('click', () => {
                input.value = item;
                container.style.display = 'none';
                if (onSelect) onSelect(item);
            });
            container.appendChild(div);
        });
        
        container.style.display = 'block';
    }
    
    // Autocompletado de estados
    if (estadoInput) {
        estadoInput.addEventListener('input', function() {
            clearTimeout(estadoTimeout);
            const query = this.value.trim();
            
            if (query.length < 1) {
                estadoSuggestions.style.display = 'none';
                // Si se borra el estado, limpiar región
                if (query.length === 0) {
                    if (regionInput) {
                        regionInput.value = '';
                        regionInput.disabled = true;
                        regionInput.placeholder = 'Selecciona un estado primero';
                    }
                    currentState = '';
                }
                return;
            }
            
            estadoTimeout = setTimeout(() => {
                fetch(`/search/api/cities/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        createSuggestionsList(data.cities, estadoSuggestions, estadoInput, (selectedState) => {
                            currentState = selectedState;
                            loadRegions(selectedState);
                        });
                    })
                    .catch(error => {
                        console.error('Error al buscar estados:', error);
                        estadoSuggestions.style.display = 'none';
                    });
            }, 200);
        });
        
        // Mostrar todos los estados al hacer focus
        estadoInput.addEventListener('focus', function() {
            if (this.value.trim().length === 0) {
                fetch(`/search/api/cities/`)
                    .then(response => response.json())
                    .then(data => {
                        createSuggestionsList(data.cities, estadoSuggestions, estadoInput, (selectedState) => {
                            currentState = selectedState;
                            loadRegions(selectedState);
                        });
                    })
                    .catch(error => {
                        console.error('Error al cargar estados:', error);
                    });
            }
        });
        
        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (estadoInput && estadoSuggestions) {
                if (!estadoInput.contains(e.target) && !estadoSuggestions.contains(e.target)) {
                    estadoSuggestions.style.display = 'none';
                }
            }
        });
    }
    
    // Cargar regiones según el estado
    function loadRegions(state) {
        if (!state || state.trim() === '') {
            if (regionInput) {
                regionInput.value = '';
                regionInput.disabled = true;
                regionInput.placeholder = 'Selecciona un estado primero';
            }
            return;
        }
        
        if (!regionInput) return;
        
        regionInput.disabled = false;
        regionInput.placeholder = 'Cargando regiones...';
        
        fetch(`/search/api/regions/?city=${encodeURIComponent(state.toLowerCase())}`)
            .then(response => response.json())
            .then(data => {
                if (data.regions && data.regions.length > 0) {
                    regionInput.placeholder = 'Ej: ' + data.regions[0];
                    currentState = state;
                } else {
                    regionInput.placeholder = 'No hay regiones disponibles para este estado';
                }
            })
            .catch(error => {
                console.error('Error al cargar regiones:', error);
                regionInput.placeholder = 'Error al cargar regiones';
            });
    }
    
    // Autocompletado de regiones
    if (regionInput) {
        regionInput.addEventListener('input', function() {
            if (this.disabled || !currentState) return;
            
            clearTimeout(regionTimeout);
            const query = this.value.trim();
            
            if (query.length < 1) {
                regionSuggestions.style.display = 'none';
                return;
            }
            
            regionTimeout = setTimeout(() => {
                fetch(`/search/api/regions/?city=${encodeURIComponent(currentState.toLowerCase())}`)
                    .then(response => response.json())
                    .then(data => {
                        // Filtrar regiones que coincidan con la búsqueda
                        const filtered = data.regions.filter(region => 
                            region.toLowerCase().includes(query.toLowerCase())
                        );
                        createSuggestionsList(filtered, regionSuggestions, regionInput);
                    })
                    .catch(error => {
                        console.error('Error al buscar regiones:', error);
                        regionSuggestions.style.display = 'none';
                    });
            }, 300);
        });
        
        // Cargar todas las regiones al hacer focus
        regionInput.addEventListener('focus', function() {
            if (!this.disabled && currentState) {
                fetch(`/search/api/regions/?city=${encodeURIComponent(currentState.toLowerCase())}`)
                    .then(response => response.json())
                    .then(data => {
                        createSuggestionsList(data.regions, regionSuggestions, regionInput);
                    })
                    .catch(error => {
                        console.error('Error al cargar regiones:', error);
                    });
            }
        });
        
        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (regionInput && regionSuggestions) {
                if (!regionInput.contains(e.target) && !regionSuggestions.contains(e.target)) {
                    regionSuggestions.style.display = 'none';
                }
            }
        });
    }
    
    // Detectar cuando se selecciona un estado (también al perder focus si hay valor)
    if (estadoInput) {
        estadoInput.addEventListener('blur', function() {
            setTimeout(() => {
                if (this.value.trim() && this.value.trim() !== currentState) {
                    currentState = this.value.trim();
                    loadRegions(currentState);
                }
            }, 200);
        });
    }
});
