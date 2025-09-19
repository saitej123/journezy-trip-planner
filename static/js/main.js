// Initialize AOS
AOS.init({
    duration: 1000,
    once: true
});

// Fix floating labels for better visibility
function fixFloatingLabels() {
    const floatingInputs = document.querySelectorAll('.form-floating .form-control');
    
    floatingInputs.forEach(input => {
        // Check if input has value on page load
        if (input.value && input.value.trim() !== '') {
            input.classList.add('has-value');
        }
        
        // Add event listeners for input changes
        input.addEventListener('input', function() {
            if (this.value && this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
        
        // Handle focus events
        input.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('focused');
            if (this.value && this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
        
        // Handle change events for select elements
        input.addEventListener('change', function() {
            if (this.value && this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
}

// Fix image loading issues
function fixImageLoading() {
    const images = document.querySelectorAll('.itinerary-item-image img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            // Hide the broken image and show fallback
            this.style.display = 'none';
            const container = this.closest('.itinerary-item-image');
            if (container) {
                container.classList.add('image-error');
            }
        });
        
        img.addEventListener('load', function() {
            // Image loaded successfully
            this.style.display = 'block';
            const container = this.closest('.itinerary-item-image');
            if (container) {
                container.classList.remove('image-error');
            }
        });
    });
}

// Add logo container styles
document.addEventListener('DOMContentLoaded', function() {
    // Fix floating labels
    fixFloatingLabels();
    
    // Fix image loading
    fixImageLoading();
    // Style the logo containers
    const logoContainers = document.querySelectorAll('.logo-container');
    logoContainers.forEach(container => {
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.padding = '8px';
        container.style.borderRadius = '10px';
        container.style.background = 'rgba(255, 255, 255, 0.9)';
        container.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    });

    // Style the footer logo specifically
    const footerLogoWrapper = document.querySelector('.footer-logo-wrapper');
    if (footerLogoWrapper) {
        footerLogoWrapper.style.background = 'rgba(255, 255, 255, 0.95)';
        footerLogoWrapper.style.padding = '12px';
        footerLogoWrapper.style.borderRadius = '12px';
        footerLogoWrapper.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.15)';
    }

    // Style the logo text containers
    const logoTextContainers = document.querySelectorAll('.logo-text-container');
    logoTextContainers.forEach(container => {
        container.style.marginLeft = '10px';
        container.style.display = 'flex';
        container.style.flexDirection = 'row';
        container.style.alignItems = 'center';
        container.style.gap = '5px';
    });

    // Enhance logo text and AI badge
    const logoTexts = document.querySelectorAll('.logo-text');
    const logoAIs = document.querySelectorAll('.logo-ai');
    
    logoTexts.forEach(text => {
        text.style.fontWeight = '700';
        text.style.color = '#1a1a1a';
        text.style.fontSize = '1.4rem';
    });

    logoAIs.forEach(ai => {
        ai.style.background = 'linear-gradient(135deg, #00bf8f 0%, #001510 100%)';
        ai.style.color = 'white';
        ai.style.padding = '2px 8px';
        ai.style.borderRadius = '6px';
        ai.style.fontSize = '0.9rem';
        ai.style.fontWeight = '600';
    });

});

// Preloader
window.addEventListener('load', () => {
    document.getElementById('preloader').style.display = 'none';
});

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Tab Navigation
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons and panes
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        
        // Add active class to clicked button and corresponding pane
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// Search Mode Toggle Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form with default values
    const languageSelect = document.getElementById('language');
    const currencySelect = document.getElementById('currency');
    
    // Set default values
    if (languageSelect) {
        languageSelect.value = 'en';
    }
    if (currencySelect) {
        currencySelect.value = 'USD';
    }
    
    // Form submission is handled by the main event listener below
});

// Removed legacy browser search mode toggle and related DOM references
// Language selection
function getSelectedLanguage() {
    const lang = document.getElementById('language')?.value || 'en';
    return lang;
}

// Modify the existing handleTripPlanning function to include output section parameter
async function handleTripPlanning(outputSection) {
    const formData = {
        from_city: document.getElementById('from_city').value,
        to_city: document.getElementById('to_city').value,
        additional_instructions: document.getElementById('additional_instructions').value,
        language: getSelectedLanguage(),
        start_date: document.getElementById('start_date').value,
        end_date: document.getElementById('end_date').value,
        budget_amount: (document.getElementById('budget_amount')?.value || '').trim() ? Number(document.getElementById('budget_amount').value) : null,
        currency: (document.getElementById('currency')?.value || 'USD'),
        travelers: {
            adults: parseInt(document.getElementById('adults').value) || 1,
            children: parseInt(document.getElementById('children').value) || 0,
            seniors: parseInt(document.getElementById('seniors').value) || 0,
            children_under_5: parseInt(document.getElementById('children_under_5').value) || 0,
            itinerary_based_passengers: document.getElementById('itinerary_based_passengers')?.checked || false
        },
        flight_preferences: {
            avoid_red_eye: document.getElementById('avoid_red_eye')?.checked || false,
            avoid_early_morning: document.getElementById('avoid_early_morning')?.checked || false,
            child_friendly: document.getElementById('child_friendly')?.checked || false,
            senior_friendly: document.getElementById('senior_friendly')?.checked || false,
            direct_flights_only: document.getElementById('direct_flights_only')?.checked || false
        },
        itinerary_first: document.getElementById('itinerary_first')?.checked || false,
        consider_toddler_friendly: document.getElementById('consider_toddler_friendly')?.checked || false,
        consider_senior_friendly: document.getElementById('consider_senior_friendly')?.checked || false,
        safety_check: document.getElementById('safety_check')?.checked || true
    };

    // Store search context for citation links
    window.searchContext = {
        from: formData.from_city,
        to: formData.to_city,
        startDate: formData.start_date,
        endDate: formData.end_date,
        currency: formData.currency
    };

    const response = await fetch('/plan-trip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (data.status === 'success') {
        await displayResults(data);
        if (outputSection) {
            outputSection.classList.remove('hidden');
            outputSection.scrollIntoView({ behavior: 'smooth' });
        }
    } else {
        throw new Error(data.message || 'Trip planning failed');
    }
}

// This form submission handler is removed - using the main one below

// Helper Functions

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const formCard = document.querySelector('.planning-card');
    formCard.insertBefore(errorDiv, formCard.firstChild);
    
    // Scroll to error message
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}



function activateTab(tabId) {
    // Remove active class from all tabs and buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    // Add active class to the specified tab and its button
    const tabButton = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const tabPane = document.getElementById(tabId);
    
    if (tabButton && tabPane) {
        tabButton.classList.add('active');
        tabPane.classList.add('active');
    }
}

function handleLogout() {
    // Clear any stored data
    localStorage.clear();
    sessionStorage.clear();
    
    // Add fade out effect
    document.body.style.opacity = '0';
    
    // Redirect to login page after a short delay
    setTimeout(() => {
        window.location.href = '/';
    }, 300);
}

// Data Parsing Functions
function parseFlightsData(flightsString) {
    if (!flightsString) return [];
    
    try {
        const lines = flightsString.split('\n').filter(line => line.trim());
        
        // Remove the header line "Flights from X to Y:"
        lines.shift();
        
        const flights = [];
        let currentFlight = {};
        
        for (let line of lines) {
            if (line.includes(' - ')) {
                // If we have a current flight, save it
                if (Object.keys(currentFlight).length > 0) {
                    flights.push(currentFlight);
                }
                currentFlight = {};
                
                // Parse airline, route and aircraft info
                const [airline, routeInfo] = line.split(' - ');
                currentFlight.airline = airline.trim();
                
                // Parse route details
                const routeParts = routeInfo.split(' ');
                if (routeParts.length >= 6) {
                    currentFlight.origin = routeParts[0];
                    currentFlight.departureTime = routeParts[1];
                    currentFlight.destination = routeParts[3];
                    currentFlight.arrivalTime = routeParts[4];
                    currentFlight.duration = routeParts[5];
                }
                
                // Get aircraft type if available
                const aircraftMatch = line.match(/- ([^[]+)$/);
                if (aircraftMatch) {
                    currentFlight.aircraft = aircraftMatch[1].trim();
                }
            } else if (line.includes('Layover:')) {
                currentFlight.layover = line.trim();
            } else if (line.includes('Total Duration:')) {
                currentFlight.totalDuration = line.split(':')[1].trim();
            } else if (/^Price \(/.test(line)) {
                currentFlight.price = line.split(':')[1]?.trim();
                flights.push(currentFlight);
                currentFlight = {};
            }
        }
        
        // Add the last flight if any
        if (Object.keys(currentFlight).length > 0) {
            flights.push(currentFlight);
        }
        
        return flights;
    } catch (error) {
        console.error('Error parsing flights data:', error);
        return [];
    }
}

function parseHotelsData(hotelsString) {
    try {
        // Skip the first line which is "Accommodations in New York:"
        const hotels = hotelsString.split('\n\n').slice(1).filter(hotel => hotel.trim());
        
        return hotels.map(hotel => {
            const lines = hotel.split('\n').filter(line => line.trim());
            return {
                name: lines[0] || 'Hotel Name Not Available',
                rate: lines.find(l => l.includes('Rate per night:'))?.split(':')[1]?.trim() || 'Price not available',
                rating: lines.find(l => l.includes('Rating:'))?.match(/(\d+\.?\d*)/)?.[1] || '0',
                reviewCount: lines.find(l => l.includes('Rating:'))?.match(/\((\d+)\)/)?.[1] || '0',
                location: lines.find(l => l.includes('Location Rating:'))?.split(':')[1]?.trim() || 'N/A',
                amenities: lines.find(l => l.includes('Amenities:'))?.split(':')[1]?.split(',').map(a => a.trim()) || [],
                image: lines.find(l => l.includes('Image:'))?.replace('Image:', '').trim() || ''
            };
        });
    } catch (error) {
        console.error('Error parsing hotels data:', error);
        return [];
    }
}

function parsePlacesData(placesString) {
    try {
        console.log('🔍 [PARSE-PLACES] Raw places data:', placesString);
        
        if (!placesString || placesString.trim() === '') {
            console.log('⚠️ [PARSE-PLACES] Empty places data');
            return [];
        }
        
        // Skip the first line which is "Here are the top places to visit in [location]:"
        const lines = placesString.split('\n').filter(line => line.trim());
        console.log('📝 [PARSE-PLACES] Lines after filtering:', lines);
        
        if (lines.length > 0 && lines[0].includes('Here are the top places')) {
            lines.shift();
        }
        
        const places = [];
        let currentPlace = {};
        
        for (let line of lines) {
            console.log('🔍 [PARSE-PLACES] Processing line:', line);
            
            if (line.trim() === '') {
                // Empty line indicates end of current place
                if (Object.keys(currentPlace).length > 0) {
                    places.push(currentPlace);
                    currentPlace = {};
                }
            } else if (line.startsWith('Description:')) {
                currentPlace.description = line.replace('Description:', '').trim();
            } else if (line.startsWith('Rating:')) {
                const ratingMatch = line.match(/Rating:\s*([0-9.]+)\s*\(([^)]+)\)/);
                if (ratingMatch) {
                    currentPlace.rating = ratingMatch[1];
                    currentPlace.reviewCount = ratingMatch[2];
                } else {
                    currentPlace.rating = '0';
                    currentPlace.reviewCount = '0';
                }
            } else if (line.startsWith('Price:')) {
                currentPlace.price = line.replace('Price:', '').trim();
            } else if (line.startsWith('Image:')) {
                currentPlace.image = line.replace('Image:', '').trim();
            } else {
                // This should be the place name
                if (!currentPlace.name) {
                    currentPlace.name = line.trim();
                }
            }
        }
        
        // Add the last place if any
        if (Object.keys(currentPlace).length > 0) {
            places.push(currentPlace);
        }
        
        console.log('✅ [PARSE-PLACES] Parsed places:', places);
        return places;
    } catch (error) {
        console.error('❌ [PARSE-PLACES] Error parsing places data:', error);
        return [];
    }
}

async function displayResults(data) {
    try {
        // Display Flights
        const flightsPane = document.getElementById('flights');
        if (data?.itinerary?.flights?.data) {
            flightsPane.innerHTML = formatFlights(data.itinerary.flights.data);
        } else {
            flightsPane.innerHTML = '<div class="empty-state">No flight information available</div>';
        }

        // Display Hotels
        const hotelsPane = document.getElementById('hotels');
        if (data?.itinerary?.hotels?.data) {
            hotelsPane.innerHTML = formatHotels(data.itinerary.hotels.data);
        } else {
            hotelsPane.innerHTML = '<div class="empty-state">No hotel information available</div>';
        }

        // Display Places
        const placesPane = document.getElementById('places');
        if (data?.itinerary?.places?.data) {
            placesPane.innerHTML = formatPlaces(data.itinerary.places.data);
        } else {
            placesPane.innerHTML = '<div class="empty-state">No places information available</div>';
        }

        // Display Itinerary with new formatting
        const itineraryPane = document.getElementById('itinerary');
        if (data?.itinerary?.itinerary?.data) {
            const itineraryContent = formatItinerary(data.itinerary.itinerary.data);
            itineraryPane.innerHTML = `<div class="itinerary-content">${itineraryContent}</div>`;
        } else {
            itineraryPane.innerHTML = '<div class="empty-state">No itinerary available</div>';
        }

        // Show the output section
        const outputSection = document.getElementById('output');
        if (outputSection) {
            outputSection.classList.remove('hidden');
            outputSection.scrollIntoView({ behavior: 'smooth' });
        }

    } catch (error) {
        console.error('Error displaying results:', error);
        showError('Error displaying results. Please try again.');
    }
}

// Language selection
function getSelectedLanguage() {
    const lang = document.getElementById('language')?.value || 'en';
    return lang;
}

async function handleTripPlanning(outputSection) {
    try {
        console.log('🚀 [HANDLE-TRIP] Starting trip planning request...');
        
        const formData = {
            from_city: document.getElementById('from_city').value,
            to_city: document.getElementById('to_city').value,
            additional_instructions: document.getElementById('additional_instructions').value,
            language: getSelectedLanguage(),
            start_date: document.getElementById('start_date').value,
            end_date: document.getElementById('end_date').value,
            budget_amount: (document.getElementById('budget_amount')?.value || '').trim() ? Number(document.getElementById('budget_amount').value) : null,
            currency: (document.getElementById('currency')?.value || 'USD'),
            travelers: {
                adults: parseInt(document.getElementById('adults').value) || 1,
                children: parseInt(document.getElementById('children').value) || 0,
                seniors: parseInt(document.getElementById('seniors').value) || 0,
                children_under_5: parseInt(document.getElementById('children_under_5').value) || 0,
                itinerary_based_passengers: document.getElementById('itinerary_based_passengers')?.checked || false
            },
            flight_preferences: {
                avoid_red_eye: document.getElementById('avoid_red_eye')?.checked || false,
                avoid_early_morning: document.getElementById('avoid_early_morning')?.checked || false,
                child_friendly: document.getElementById('child_friendly')?.checked || false,
                senior_friendly: document.getElementById('senior_friendly')?.checked || false,
                direct_flights_only: document.getElementById('direct_flights_only')?.checked || false
            },
            itinerary_first: document.getElementById('itinerary_first')?.checked || false,
            consider_toddler_friendly: document.getElementById('consider_toddler_friendly')?.checked || false,
            consider_senior_friendly: document.getElementById('consider_senior_friendly')?.checked || false,
            safety_check: document.getElementById('safety_check')?.checked || true
        };

        console.log('📝 [HANDLE-TRIP] Form data prepared:', formData);

        // Store search context for citation links
        window.searchContext = {
            from: formData.from_city,
            to: formData.to_city,
            startDate: formData.start_date,
            endDate: formData.end_date,
            currency: formData.currency
        };

        console.log('🌐 [HANDLE-TRIP] Sending request to /plan-trip...');
        
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout
        
        try {
            const response = await fetch('/plan-trip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            console.log('📡 [HANDLE-TRIP] Response received, status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('📊 [HANDLE-TRIP] Response data:', data);

            if (data.status === 'success') {
                console.log('✅ [HANDLE-TRIP] Success response received');
                await displayResults(data);
                if (outputSection) {
                    outputSection.classList.remove('hidden');
                    outputSection.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.error('❌ [HANDLE-TRIP] Error response:', data.message);
                throw new Error(data.message || 'Unknown error occurred');
            }
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out. Please try again with a simpler request.');
            }
            throw error;
        }
    } catch (error) {
        console.error('❌ [HANDLE-TRIP] Error in handleTripPlanning:', error);
        throw error; // Re-throw to be caught by the calling function
    }
}

// Main form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tripForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('🚀 [FORM] Form submission started');
            
            const loading = document.getElementById('loading');
            const outputSection = document.getElementById('output');
            const submitButton = e.target.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            // Prevent multiple submissions
            if (submitButton.disabled) {
                console.log('⚠️ [FORM] Form already processing, ignoring submission');
                return;
            }
            
            try {
                // Hide output and show loading
                if (outputSection) {
                    outputSection.classList.add('hidden');
                }
                loading.classList.remove('hidden');
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                console.log('🚀 [FORM] Starting trip planning...');
                await handleTripPlanning(outputSection);
                console.log('✅ [FORM] Trip planning completed successfully');
                
            } catch (error) {
                console.error('❌ [FORM] Error during trip planning:', error);
                showError('An error occurred. Please try again.');
            } finally {
                // Always reset the button state
                loading.classList.add('hidden');
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                console.log('🔄 [FORM] Button state reset');
            }
        });
    }
});

// Helper Functions
function formatFlights(flights) {
    if (!flights) return '<div class="empty-state">No flight information available</div>';
    
    try {
        const flightsData = parseFlightsData(flights);
        if (!flightsData || !Array.isArray(flightsData) || flightsData.length === 0) {
            return '<div class="empty-state">No flight information available</div>';
        }
        
        return flightsData.map((flight, index) => {
            // Provide fallbacks for missing data
            const airline = flight.airline || 'Unknown Airline';
            const flightNumber = flight.flightNumber || '';
            const origin = flight.origin || 'N/A';
            const departureTime = flight.departureTime || 'N/A';
            const destination = flight.destination || 'N/A';
            const arrivalTime = flight.arrivalTime || 'N/A';
            const duration = flight.duration || 'N/A';
            const aircraft = flight.aircraft || '';
            const price = flight.price || 'Price not available';
            const layover = flight.layover || '';
            const totalDuration = flight.totalDuration || '';
            
            return `
                <div class="flight-card" data-aos="fade-up">
                    <div class="flight-details">
                        <div class="airline">
                            <i class="fas fa-plane"></i>
                            <span>${airline}</span>
                            ${flightNumber ? `<span class="flight-number">${flightNumber}</span>` : ''}
                            ${aircraft ? `<span class="aircraft">(${aircraft})</span>` : ''}
                        </div>
                        <div class="times">
                            <div class="departure">
                                <div class="city">${origin}</div>
                                <div class="time">${departureTime}</div>
                            </div>
                            <div class="duration">
                                <div class="line"></div>
                                <div class="time">${duration}</div>
                                ${layover ? `<div class="layover">${layover}</div>` : ''}
                                ${totalDuration ? `<div class="total-duration">Total: ${totalDuration}</div>` : ''}
                            </div>
                            <div class="arrival">
                                <div class="city">${destination}</div>
                                <div class="time">${arrivalTime}</div>
                            </div>
                        </div>
                        <div class="price">
                            <span class="amount">${price}</span>
                        </div>
                        <div class="booking-links" style="margin-top:8px; font-size:0.9rem;">
                            <a href="${(() => {
                                const from = (window.searchContext?.from || '').toUpperCase();
                                const to = (window.searchContext?.to || '').toUpperCase();
                                const startDate = window.searchContext?.startDate || '';
                                const endDate = window.searchContext?.endDate || '';
                                const currency = window.searchContext?.currency || 'USD';
                                
                                if (endDate) {
                                    return `https://flight.easemytrip.com/FlightList/Index?srch=${from}-${to}-${startDate}&rtn=${to}-${from}-${endDate}&px=1-0-0&cbn=0&ar=0&isow=0`;
                                }
                                return `https://flight.easemytrip.com/FlightList/Index?srch=${from}-${to}-${startDate}&px=1-0-0&cbn=0&ar=0&isow=1`;
                            })()}" target="_blank" rel="noopener" style="color: #007bff; text-decoration: none;">
                                <i class="fas fa-external-link-alt me-1"></i>Book on EaseMyTrip
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error formatting flights:', error);
        return '<div class="empty-state">Error displaying flight information</div>';
    }
}

function formatHotels(hotels) {
    if (!hotels) return '<div class="empty-state">No hotel information available</div>';
    
    try {
        const hotelsData = parseHotelsData(hotels);
        if (!hotelsData || !Array.isArray(hotelsData) || hotelsData.length === 0) {
            return '<div class="empty-state">No hotel information available</div>';
        }

        return `
        <div class="hotels-grid">
            ${hotelsData.map(hotel => `
                <div class="hotel-card">
                    <div class="image-container loading">
                        <img src="${hotel.image || ''}" 
                             alt="${hotel.name || 'Hotel'}"
                             onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'fallback-image\\'><i class=\\'fas fa-hotel\\'></i></div>';"
                             onload="this.parentElement.classList.remove('loading')"
                             loading="lazy">
                    </div>
                    <div class="hotel-details">
                        <h3>${hotel.name || 'Hotel Name Not Available'}</h3>
                        <p class="price"><i class="fas fa-tag"></i> ${hotel.rate ? hotel.rate : 'Price not available'} per night</p>
                        <p class="rating"><i class="fas fa-star"></i> ${hotel.rating || '0'} (${hotel.reviewCount || '0'} reviews)</p>
                        <p class="location"><i class="fas fa-map-marker-alt"></i> Location Rating: ${hotel.location || 'N/A'}</p>
                        <div class="amenities">
                            ${(hotel.amenities || []).map(amenity => `
                                <span class="amenity">
                                    <i class="fas fa-check"></i>
                                    ${amenity}
                                </span>
                            `).join('')}
                        </div>
                        <div class="booking-links" style="margin-top:8px; font-size:0.9rem;">
                            <a href="${(() => {
                                const city = document.getElementById('to_city')?.value || '';
                                const checkIn = document.getElementById('start_date')?.value || '';
                                const checkOut = document.getElementById('end_date')?.value || '';
                                return `https://www.easemytrip.com/hotels/search?city=${encodeURIComponent(city)}&checkin=${checkIn}&checkout=${checkOut}&rooms=1&adults=1`;
                            })()}" target="_blank" rel="noopener" style="color: #007bff; text-decoration: none;">
                                <i class="fas fa-external-link-alt me-1"></i>Book on EaseMyTrip
                            </a>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>`;
    } catch (error) {
        console.error('Error formatting hotels:', error);
        return '<div class="empty-state">Error displaying hotel information</div>';
    }
}

function formatPlaces(places) {
    if (!places) return '<div class="empty-state">No places information available</div>';
    
    try {
        const placesData = parsePlacesData(places);
        if (!placesData || !Array.isArray(placesData) || placesData.length === 0) {
            return '<div class="empty-state">No places information available</div>';
        }

        return `
        <div class="places-grid">
            ${placesData.map(place => `
                <div class="place-card">
                    <div class="image-container loading">
                        <img src="${place.image || ''}" 
                             alt="${place.name || 'Place'}"
                             onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'fallback-image\\'><i class=\\'fas fa-map-marker-alt\\'></i></div>';"
                             onload="this.parentElement.classList.remove('loading')"
                             loading="lazy">
                    </div>
                    <div class="place-details">
                        <h3>${place.name || 'Place Name Not Available'}</h3>
                        <p class="description">${place.description || 'No description available'}</p>
                        <p class="rating"><i class="fas fa-star"></i> ${place.rating || '0'} (${place.reviewCount || '0'} reviews)</p>
                        ${place.price ? `<p class="price"><i class="fas fa-tag"></i> ${place.price}</p>` : '<p class="price"><i class="fas fa-tag"></i> Free Entry</p>'}
                    </div>
                </div>
            `).join('')}
        </div>`;
    } catch (error) {
        console.error('Error formatting places:', error);
        return '<div class="empty-state">Error displaying places information</div>';
    }
}

// Helper Functions
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    return stars;
}

function formatAmenities(amenities) {
    const icons = {
        'wifi': 'fa-wifi',
        'pool': 'fa-swimming-pool',
        'parking': 'fa-parking',
        'restaurant': 'fa-utensils',
        // Add more amenity icons
    };
    
    return amenities.map(amenity => `
        <span class="amenity">
            <i class="fas ${icons[amenity.toLowerCase()] || 'fa-check'}"></i>
            ${amenity}
        </span>
    `).join('');
}

// Download and Share Functions
async function downloadPDF() {
    console.log('🖱️ [DOWNLOAD-PDF] Download PDF button clicked');

    // Log to server
    try {
        console.log('📡 [DOWNLOAD-PDF] Sending download log to server...');
        const response = await fetch('/log-download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        console.log('✅ [DOWNLOAD-PDF] Server log sent successfully');
    } catch (error) {
        console.warn('⚠️ [DOWNLOAD-PDF] Failed to log to server:', error);
    }

    if (!window.pdfData) {
        console.error('❌ [DOWNLOAD-PDF] No PDF data available in window.pdfData');
        showError('No PDF data available for download');
        return;
    }

    console.log(`📊 [DOWNLOAD-PDF] PDF data length: ${window.pdfData.length} characters`);
    console.log(`🔍 [DOWNLOAD-PDF] PDF data preview: ${window.pdfData.substring(0, 100)}...`);

    try {
        console.log('🔄 [DOWNLOAD-PDF] Converting base64 to binary...');
        // Support optional data URLs and detect markdown/plain text
        let raw = window.pdfData || '';
        const docType = (window.documentType || '').toLowerCase();
        if (raw.startsWith('data:')) {
            const commaIdx = raw.indexOf(',');
            if (commaIdx !== -1) raw = raw.substring(commaIdx + 1);
        }

        // If not clearly base64 or server sent markdown, fall back to text download
        const cleaned = raw.replace(/\s+/g, '').replace(/-/g, '+').replace(/_/g, '/');
        const base64Regex = /^[A-Za-z0-9+/=]+$/;
        const looksLikeBase64 = base64Regex.test(cleaned) && cleaned.length > 0;
        const shouldDownloadAsText = docType === 'markdown' || !looksLikeBase64;

        if (shouldDownloadAsText) {
            console.log('📝 [DOWNLOAD] Falling back to text/markdown download');
            const blob = new Blob([window.pdfData], { type: docType === 'markdown' ? 'text/markdown' : 'text/plain' });
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = docType === 'markdown' ? 'trip-itinerary.md' : 'trip-itinerary.txt';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);
            return;
        }

        // Pad base64 if needed and convert to binary
        let padded = cleaned;
        const mod = padded.length % 4;
        if (mod === 2) padded += '==';
        else if (mod === 3) padded += '=';
        else if (mod === 1) {
            console.warn('⚠️ [DOWNLOAD-PDF] Invalid base64 length, forcing text fallback');
            const blob = new Blob([window.pdfData], { type: 'text/plain' });
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'trip-itinerary.txt';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);
            return;
        }

        const byteCharacters = atob(padded);
        console.log(`✅ [DOWNLOAD-PDF] Base64 decoded, byte length: ${byteCharacters.length}`);

        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        console.log(`📦 [DOWNLOAD-PDF] Created Uint8Array, length: ${byteArray.length}`);

        const blob = new Blob([byteArray], { type: 'application/pdf' });
        console.log(`📄 [DOWNLOAD-PDF] Created PDF blob, size: ${blob.size} bytes`);

        // Create and click download link
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'trip-itinerary.pdf';
        console.log(`🔗 [DOWNLOAD-PDF] Created download link with URL: ${link.href}`);

        document.body.appendChild(link); // Needed for Firefox
        console.log('🎯 [DOWNLOAD-PDF] Clicking download link...');
        link.click();
        console.log('✅ [DOWNLOAD-PDF] Download initiated');

        document.body.removeChild(link); // Clean up
        window.URL.revokeObjectURL(link.href); // Clean up
        console.log('🧹 [DOWNLOAD-PDF] Cleanup completed');

    } catch (error) {
        console.error('❌ [DOWNLOAD-PDF] Error downloading PDF:', error);
        console.error('❌ [DOWNLOAD-PDF] Error stack:', error.stack);
        showError('Error downloading PDF. Please try again.');
    }

    console.log('🏁 [DOWNLOAD-PDF] Download PDF function completed');
}

// Style action buttons
document.addEventListener('DOMContentLoaded', function() {
    const actionButtons = document.querySelector('.action-buttons');
    if (actionButtons) {
        actionButtons.style.display = 'flex';
        actionButtons.style.justifyContent = 'center';
        actionButtons.style.gap = '20px';
        actionButtons.style.marginTop = '30px';
        
        // Style all buttons in action buttons
        const buttons = actionButtons.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.style.minWidth = '180px';
            button.style.padding = '12px 24px';
            button.style.fontSize = '1.1rem';
            button.style.transition = 'all 0.3s ease';
        });
    }
});

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const formCard = document.querySelector('.planning-card');
    formCard.insertBefore(errorDiv, formCard.firstChild);
    
    // Scroll to error message
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        errorDiv.classList.remove('show');
        setTimeout(() => errorDiv.remove(), 150);
    }, 5000);
}

async function displayResults(data) {
    try {
        console.log('📊 [DISPLAY-RESULTS] Starting to display results...');
        console.log('📊 [DISPLAY-RESULTS] Data received:', data);

        const outputSection = document.getElementById('output');
        if (outputSection) {
            outputSection.classList.remove('hidden');
            console.log('✅ [DISPLAY-RESULTS] Output section made visible');
        }

        // Display Itinerary first (since it's now the first tab)
        const itineraryPane = document.getElementById('itinerary');
        if (itineraryPane) {
            if (data?.itinerary?.itinerary?.data) {
                console.log('📋 [DISPLAY-RESULTS] Displaying itinerary...');
                const itineraryContent = formatItinerary(data.itinerary.itinerary.data);
                itineraryPane.innerHTML = `<div class="itinerary-content">${itineraryContent}</div>`;
                
                // Show the download button header
                const itineraryHeader = document.querySelector('.itinerary-header');
                if (itineraryHeader) {
                    itineraryHeader.style.display = 'block';
                }
                
                console.log('✅ [DISPLAY-RESULTS] Itinerary displayed');
            } else {
                itineraryPane.innerHTML = '<div class="empty-state">No itinerary available</div>';
                
                // Hide the download button header
                const itineraryHeader = document.querySelector('.itinerary-header');
                if (itineraryHeader) {
                    itineraryHeader.style.display = 'none';
                }
                
                console.log('⚠️ [DISPLAY-RESULTS] No itinerary data available');
            }
        }

        // Display Flights
        const flightsPane = document.getElementById('flights');
        if (flightsPane) {
            if (data?.itinerary?.flights?.data) {
                console.log('✈️ [DISPLAY-RESULTS] Displaying flights...');
                console.log('✈️ [DISPLAY-RESULTS] Raw flights data:', data.itinerary.flights.data);
                flightsPane.innerHTML = formatFlights(data.itinerary.flights.data);
                console.log('✅ [DISPLAY-RESULTS] Flights displayed');
            } else {
                flightsPane.innerHTML = '<div class="empty-state">No flight information available</div>';
                console.log('⚠️ [DISPLAY-RESULTS] No flight data available');
                console.log('⚠️ [DISPLAY-RESULTS] Data structure:', data);
            }
        }

        // Display Hotels
        const hotelsPane = document.getElementById('hotels');
        if (hotelsPane) {
            if (data?.itinerary?.hotels?.data) {
                console.log('🏨 [DISPLAY-RESULTS] Displaying hotels...');
                hotelsPane.innerHTML = formatHotels(data.itinerary.hotels.data);
                console.log('✅ [DISPLAY-RESULTS] Hotels displayed');
            } else {
                hotelsPane.innerHTML = '<div class="empty-state">No hotel information available</div>';
                console.log('⚠️ [DISPLAY-RESULTS] No hotel data available');
            }
        }

        // Display Places
        const placesPane = document.getElementById('places');
        if (placesPane) {
            if (data?.itinerary?.places?.data) {
                console.log('📍 [DISPLAY-RESULTS] Displaying places...');
                console.log('📍 [DISPLAY-RESULTS] Raw places data:', data.itinerary.places.data);
                placesPane.innerHTML = formatPlaces(data.itinerary.places.data);
                console.log('✅ [DISPLAY-RESULTS] Places displayed');
            } else {
                placesPane.innerHTML = '<div class="empty-state">No places information available</div>';
                console.log('⚠️ [DISPLAY-RESULTS] No places data available');
                console.log('⚠️ [DISPLAY-RESULTS] Data structure:', data);
            }
        }

        // Store PDF data for download if available
        if (data?.document) {
            console.log('📥 [PDF-DATA] Received document data from server');
            console.log(`📊 [PDF-DATA] Document data length: ${data.document.length} characters`);
            console.log(`🔍 [PDF-DATA] Document data preview: ${data.document.substring(0, 100)}...`);
            console.log(`📋 [PDF-DATA] Document type: ${data.document_type}`);

            window.pdfData = data.document;
            window.documentType = data.document_type;
            console.log('✅ [PDF-DATA] PDF data stored in window.pdfData');
            console.log('🎯 [PDF-DATA] Download PDF button is now ready');
        } else {
            console.warn('⚠️ [PDF-DATA] No document data received from server');
        }

        // Show the first tab by default (Itinerary)
        const firstTab = document.querySelector('.tab-btn[data-tab="itinerary"]');
        if (firstTab) {
            firstTab.click();
            console.log('✅ [DISPLAY-RESULTS] Activated itinerary tab');
        }

        console.log('🎉 [DISPLAY-RESULTS] All results displayed successfully');
    } catch (error) {
        console.error('❌ [DISPLAY-RESULTS] Error displaying results:', error);
        showError('Error displaying trip results. Please try again.');
    }
}

function formatItinerary(itineraryData) {
    if (!itineraryData) return '<p>No itinerary data available</p>';
    
    try {
        // If itineraryData is already a string and starts with '#' or other markdown indicators,
        // it's likely markdown content, so use it directly
        let contentToFormat = itineraryData;
        
        // If it's a JSON string or object, try to extract the content
        if (typeof itineraryData === 'string' && itineraryData.trim().startsWith('{')) {
            const parsedData = JSON.parse(itineraryData);
            contentToFormat = parsedData.content || parsedData;
        } else if (typeof itineraryData === 'object') {
            contentToFormat = itineraryData.content || itineraryData;
        }
        
        // If contentToFormat is an object, convert it to string
        if (typeof contentToFormat === 'object') {
            contentToFormat = JSON.stringify(contentToFormat);
        }
        
        // Convert markdown to HTML using marked
        const htmlContent = marked.parse(contentToFormat, {
            breaks: true,
            gfm: true,
            headerIds: true,
            mangle: false,
            sanitize: false, // Allow images and other HTML
            smartLists: true,
            smartypants: true
        });
        
        // Create a container with proper styling
        return `
            <div class="itinerary-content">
                <div class="markdown-body">
                    ${htmlContent}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error formatting itinerary:', error);
        // If there's an error parsing JSON, try to render the content directly as markdown
        try {
            const htmlContent = marked.parse(itineraryData, {
                breaks: true,
                gfm: true,
                headerIds: true,
                mangle: false
            });
            
            return `
                <div class="itinerary-content">
                    <div class="markdown-body">
                        ${htmlContent}
                    </div>
                </div>
            `;
        } catch (markdownError) {
            console.error('Error parsing markdown:', markdownError);
            return '<p>Error formatting itinerary data</p>';
        }
    }
}

// Add this helper function to format details
function formatDetail(detail) {
    if (detail.startsWith('Rating:')) {
        const rating = parseFloat(detail.split(':')[1]);
        return `<p class="rating">
            <i class="fas fa-star"></i> 
            ${rating} ${detail.match(/\((.*?)\)/)?.[1] || ''}
        </p>`;
    }
    if (detail.startsWith('Price:') || detail.startsWith('Rate per night:')) {
        return `<p class="price"><i class="fas fa-tag"></i> ${detail}</p>`;
    }
    if (detail.startsWith('Amenities:')) {
        const amenities = detail.replace('Amenities:', '').split(',');
        return `<p class="amenities">
            ${amenities.map(a => `<span class="amenity"><i class="fas fa-check"></i>${a.trim()}</span>`).join('')}
        </p>`;
    }
    return `<p>${detail}</p>`;
}

function activateTab(tabId) {
    // Remove active class from all buttons and panes
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    // Add active class to the specified tab and its button
    const tabButton = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const tabPane = document.getElementById(tabId);
    
    if (tabButton && tabPane) {
        tabButton.classList.add('active');
        tabPane.classList.add('active');
    }
}

// Initialize form validation
document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Add validation on submit
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
        
        // Add validation on input change
        form.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', () => {
                if (input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
            });
        });
    });
    
    // Initialize PDF download functionality
    initializePdfDownload();
});

// PDF Download Functionality
function initializePdfDownload() {
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', generatePdf);
    }
}

function generatePdf() {
    try {
        console.log('📄 [PDF] Starting PDF generation...');
        
        // Show loading state
        const downloadBtn = document.getElementById('downloadPdfBtn');
        const originalText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating PDF...';
        downloadBtn.disabled = true;
        
        // Get the itinerary content
        const itineraryContent = document.getElementById('itinerary');
        if (!itineraryContent) {
            throw new Error('Itinerary content not found');
        }
        
        // Create a new jsPDF instance
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        
        // Set up fonts and colors
        doc.setFont('helvetica');
        
        // Add title
        doc.setFontSize(20);
        doc.setTextColor(30, 58, 138); // Blue color
        doc.text('Travel Itinerary', 20, 30);
        
        // Add search context info
        if (window.searchContext) {
            doc.setFontSize(12);
            doc.setTextColor(100, 100, 100);
            const from = window.searchContext.from || 'Origin';
            const to = window.searchContext.to || 'Destination';
            const startDate = window.searchContext.startDate || '';
            const endDate = window.searchContext.endDate || '';
            
            doc.text(`Trip: ${from} to ${to}`, 20, 45);
            if (startDate) {
                doc.text(`Dates: ${startDate}${endDate ? ' - ' + endDate : ''}`, 20, 52);
            }
        }
        
        // Add a line separator
        doc.setDrawColor(30, 58, 138);
        doc.setLineWidth(0.5);
        doc.line(20, 60, 190, 60);
        
        // Get all the content from the itinerary
        const contentElements = itineraryContent.querySelectorAll('.itinerary-content, .itinerary-day, .markdown-body');
        let yPosition = 70;
        const pageHeight = 280; // A4 page height minus margins
        const margin = 20;
        const maxWidth = 170; // A4 width minus margins
        
        // Process each content element
        contentElements.forEach(element => {
            if (yPosition > pageHeight) {
                doc.addPage();
                yPosition = 20;
            }
            
            // Extract text content and format it
            const text = extractTextFromElement(element);
            if (text.trim()) {
                const lines = doc.splitTextToSize(text, maxWidth);
                doc.setFontSize(10);
                doc.setTextColor(0, 0, 0);
                
                lines.forEach(line => {
                    if (yPosition > pageHeight) {
                        doc.addPage();
                        yPosition = 20;
                    }
                    doc.text(line, margin, yPosition);
                    yPosition += 6;
                });
                
                yPosition += 10; // Add space between sections
            }
        });
        
        // If no content found, add a message
        if (yPosition === 70) {
            doc.setFontSize(12);
            doc.setTextColor(100, 100, 100);
            doc.text('No itinerary content available for download.', margin, yPosition);
        }
        
        // Add footer
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            doc.text(`Page ${i} of ${pageCount}`, 20, 290);
            doc.text('Generated by Journezy Trip Planner', 120, 290);
        }
        
        // Save the PDF
        const fileName = `travel-itinerary-${new Date().toISOString().split('T')[0]}.pdf`;
        doc.save(fileName);
        
        console.log('✅ [PDF] PDF generated successfully');
        
    } catch (error) {
        console.error('❌ [PDF] Error generating PDF:', error);
        alert('Error generating PDF. Please try again.');
    } finally {
        // Reset button state
        const downloadBtn = document.getElementById('downloadPdfBtn');
        if (downloadBtn) {
            downloadBtn.innerHTML = '<i class="fas fa-download me-2"></i>Download PDF';
            downloadBtn.disabled = false;
        }
    }
}

function extractTextFromElement(element) {
    let text = '';
    
    // Handle different types of elements
    if (element.tagName === 'H1' || element.tagName === 'H2' || element.tagName === 'H3') {
        text += '\n' + element.textContent.trim() + '\n';
    } else if (element.tagName === 'P') {
        text += element.textContent.trim() + '\n';
    } else if (element.tagName === 'UL' || element.tagName === 'OL') {
        const items = element.querySelectorAll('li');
        items.forEach(item => {
            text += '• ' + item.textContent.trim() + '\n';
        });
    } else if (element.classList.contains('markdown-body')) {
        // For markdown content, extract all text
        const paragraphs = element.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, div');
        paragraphs.forEach(p => {
            if (p.textContent.trim()) {
                text += p.textContent.trim() + '\n';
            }
        });
    } else {
        // For other elements, get all text content
        text = element.textContent.trim();
    }
    
    return text;
}

function handleLogout() {
    // Add a simple fade out animation
    document.body.style.opacity = '0';
    
    // Redirect to login page after a short delay
    setTimeout(() => {
        window.location.href = '/';
    }, 300);
}

// Data Parsing Functions
function parseFlightsData(flightsString) {
    try {
        console.log('🔍 [PARSE-FLIGHTS] Raw flights data:', flightsString);
        
        if (!flightsString || flightsString.trim() === '') {
            console.log('⚠️ [PARSE-FLIGHTS] Empty flights data');
            return [];
        }
        
        // Split the string into lines and remove empty lines
        const lines = flightsString.split('\n').filter(line => line.trim());
        console.log('📝 [PARSE-FLIGHTS] Lines after filtering:', lines);
        
        // Remove the header line "Flights from X to Y:"
        if (lines.length > 0 && lines[0].includes('Flights from')) {
            lines.shift();
        }
        
        const flights = [];
        let currentFlight = {};
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            console.log('🔍 [PARSE-FLIGHTS] Processing line:', line);
            
            // Check if this is a flight line (contains airline and route info)
            if (line.includes(' - ') && (line.includes(' -> ') || line.includes('(') && line.includes(')'))) {
                // Save previous flight if exists
                if (Object.keys(currentFlight).length > 0) {
                    flights.push({...currentFlight});
                }
                currentFlight = {};
                
                // Try multiple parsing patterns
                let parsed = false;
                
                // Pattern 1: "Airline FlightNo - DEP (time) -> ARR (time) [duration] - Aircraft"
                let match = line.match(/^(.+?)\s+([A-Z0-9]+)\s+-\s+([A-Z]{3})\s+\(([^)]+)\)\s+->\s+([A-Z]{3})\s+\(([^)]+)\)\s+\[([^\]]+)\]\s+-\s+(.+)$/);
                if (match) {
                    currentFlight.airline = match[1].trim();
                    currentFlight.flightNumber = match[2].trim();
                    currentFlight.origin = match[3].trim();
                    currentFlight.departureTime = match[4].trim();
                    currentFlight.destination = match[5].trim();
                    currentFlight.arrivalTime = match[6].trim();
                    currentFlight.duration = match[7].trim();
                    currentFlight.aircraft = match[8].trim();
                    parsed = true;
                }
                
                // Pattern 2: "Airline - DEP (time) -> ARR (time) [duration] - Aircraft"
                if (!parsed) {
                    match = line.match(/^(.+?)\s+-\s+([A-Z]{3})\s+\(([^)]+)\)\s+->\s+([A-Z]{3})\s+\(([^)]+)\)\s+\[([^\]]+)\]\s+-\s+(.+)$/);
                    if (match) {
                        currentFlight.airline = match[1].trim();
                        currentFlight.flightNumber = '';
                        currentFlight.origin = match[2].trim();
                        currentFlight.departureTime = match[3].trim();
                        currentFlight.destination = match[4].trim();
                        currentFlight.arrivalTime = match[5].trim();
                        currentFlight.duration = match[6].trim();
                        currentFlight.aircraft = match[7].trim();
                        parsed = true;
                    }
                }
                
                // Pattern 3: "Airline FlightNo - DEP (time) -> ARR (time) [duration]"
                if (!parsed) {
                    match = line.match(/^(.+?)\s+([A-Z0-9]+)\s+-\s+([A-Z]{3})\s+\(([^)]+)\)\s+->\s+([A-Z]{3})\s+\(([^)]+)\)\s+\[([^\]]+)\]$/);
                    if (match) {
                        currentFlight.airline = match[1].trim();
                        currentFlight.flightNumber = match[2].trim();
                        currentFlight.origin = match[3].trim();
                        currentFlight.departureTime = match[4].trim();
                        currentFlight.destination = match[5].trim();
                        currentFlight.arrivalTime = match[6].trim();
                        currentFlight.duration = match[7].trim();
                        currentFlight.aircraft = '';
                        parsed = true;
                    }
                }
                
                // Pattern 4: Simple format "Airline - DEP -> ARR"
                if (!parsed) {
                    match = line.match(/^(.+?)\s+-\s+([A-Z]{3})\s+->\s+([A-Z]{3})/);
                    if (match) {
                        currentFlight.airline = match[1].trim();
                        currentFlight.flightNumber = '';
                        currentFlight.origin = match[2].trim();
                        currentFlight.departureTime = '';
                        currentFlight.destination = match[3].trim();
                        currentFlight.arrivalTime = '';
                        currentFlight.duration = '';
                        currentFlight.aircraft = '';
                        parsed = true;
                    }
                }
                
                // If no pattern matched, try to extract basic info
                if (!parsed) {
                    const parts = line.split(' - ');
                    if (parts.length >= 2) {
                        currentFlight.airline = parts[0].trim();
                        currentFlight.flightNumber = '';
                        currentFlight.origin = '';
                        currentFlight.departureTime = '';
                        currentFlight.destination = '';
                        currentFlight.arrivalTime = '';
                        currentFlight.duration = '';
                        currentFlight.aircraft = '';
                        
                        // Try to extract more info from the route part
                        const routeInfo = parts[1];
                        const routeMatch = routeInfo.match(/([A-Z]{3})\s*\(([^)]+)\)\s*->\s*([A-Z]{3})\s*\(([^)]+)\)\s*\[([^\]]+)\]/);
                        if (routeMatch) {
                            currentFlight.origin = routeMatch[1];
                            currentFlight.departureTime = routeMatch[2];
                            currentFlight.destination = routeMatch[3];
                            currentFlight.arrivalTime = routeMatch[4];
                            currentFlight.duration = routeMatch[5];
                        }
                        
                        // Extract aircraft from end of line
                        const aircraftMatch = line.match(/- ([^-]+)$/);
                        if (aircraftMatch) {
                            currentFlight.aircraft = aircraftMatch[1].trim();
                        }
                    }
                }
                
                console.log('🔍 [PARSE-FLIGHTS] Parsed flight:', currentFlight);
            } 
            // Check for layover information
            else if (line.includes('Layover at') || line.includes('Layover:')) {
                currentFlight.layover = line.replace(/Layover at|Layover:/, '').trim();
            } 
            // Check for total duration
            else if (line.includes('Total Duration:')) {
                currentFlight.totalDuration = line.split(':')[1]?.trim() || '';
            } 
            // Check for price information
            else if (/^Price \(/.test(line)) {
                currentFlight.price = line.split(':')[1]?.trim() || '';
                flights.push({...currentFlight});
                currentFlight = {};
            }
        }
        
        // Add the last flight if any
        if (Object.keys(currentFlight).length > 0) {
            flights.push({...currentFlight});
        }
        
        console.log('✅ [PARSE-FLIGHTS] Parsed flights:', flights);
        
        // If no flights were parsed, create a fallback flight
        if (flights.length === 0) {
            console.log('⚠️ [PARSE-FLIGHTS] No flights parsed, creating fallback');
            const fallbackFlight = {
                airline: 'Flight Available',
                flightNumber: '',
                origin: 'Origin',
                departureTime: 'Check times',
                destination: 'Destination',
                arrivalTime: 'Check times',
                duration: 'Duration varies',
                aircraft: '',
                price: 'Price on request',
                layover: '',
                totalDuration: ''
            };
            flights.push(fallbackFlight);
        }
        
        return flights;
    } catch (error) {
        console.error('❌ [PARSE-FLIGHTS] Error parsing flights data:', error);
        
        // Return a fallback flight even on error
        const fallbackFlight = {
            airline: 'Flight Available',
            flightNumber: '',
            origin: 'Origin',
            departureTime: 'Check times',
            destination: 'Destination',
            arrivalTime: 'Check times',
            duration: 'Duration varies',
            aircraft: '',
            price: 'Price on request',
            layover: '',
            totalDuration: ''
        };
        return [fallbackFlight];
    }
}

function parseHotelsData(hotelsString) {
    try {
        // Skip the first line which is "Accommodations in New York:"
        const hotels = hotelsString.split('\n\n').slice(1).filter(hotel => hotel.trim());
        
        return hotels.map(hotel => {
            const lines = hotel.split('\n');
            return {
                name: lines[0]?.split(':')[0]?.trim() || 'Hotel Name Not Available',
                rate: lines.find(l => l.includes('Rate per night:'))?.split('$')[1]?.trim() || 'Price not available',
                rating: lines.find(l => l.includes('Rating:'))?.match(/\d+\.?\d*/)?.[0] || '0',
                reviewCount: lines.find(l => l.includes('Rating:'))?.match(/\((\d+)\)/)?.[1] || '0',
                location: lines.find(l => l.includes('Location Rating:'))?.split(':')[1]?.trim() || 'N/A',
                amenities: lines.find(l => l.includes('Amenities:'))?.split(':')[1]?.split(',').map(a => a.trim()) || [],
                image: lines.find(l => l.includes('Image:'))?.replace('Image:', '').trim() || ''
            };
        });
    } catch (error) {
        console.error('Error parsing hotels data:', error);
        return [];
    }
}

function parsePlacesData(placesString) {
    try {
        console.log('🔍 [PARSE-PLACES] Raw places data:', placesString);
        
        if (!placesString || placesString.trim() === '') {
            console.log('⚠️ [PARSE-PLACES] Empty places data');
            return [];
        }
        
        // Skip the first line which is "Here are the top places to visit in [location]:"
        const lines = placesString.split('\n').filter(line => line.trim());
        console.log('📝 [PARSE-PLACES] Lines after filtering:', lines);
        
        if (lines.length > 0 && lines[0].includes('Here are the top places')) {
            lines.shift();
        }
        
        const places = [];
        let currentPlace = {};
        
        for (let line of lines) {
            console.log('🔍 [PARSE-PLACES] Processing line:', line);
            
            if (line.trim() === '') {
                // Empty line indicates end of current place
                if (Object.keys(currentPlace).length > 0) {
                    places.push(currentPlace);
                    currentPlace = {};
                }
            } else if (line.startsWith('Description:')) {
                currentPlace.description = line.replace('Description:', '').trim();
            } else if (line.startsWith('Rating:')) {
                const ratingMatch = line.match(/Rating:\s*([0-9.]+)\s*\(([^)]+)\)/);
                if (ratingMatch) {
                    currentPlace.rating = ratingMatch[1];
                    currentPlace.reviewCount = ratingMatch[2];
                } else {
                    currentPlace.rating = '0';
                    currentPlace.reviewCount = '0';
                }
            } else if (line.startsWith('Price:')) {
                currentPlace.price = line.replace('Price:', '').trim();
            } else if (line.startsWith('Image:')) {
                currentPlace.image = line.replace('Image:', '').trim();
            } else {
                // This should be the place name
                if (!currentPlace.name) {
                    currentPlace.name = line.trim();
                }
            }
        }
        
        // Add the last place if any
        if (Object.keys(currentPlace).length > 0) {
            places.push(currentPlace);
        }
        
        console.log('✅ [PARSE-PLACES] Parsed places:', places);
        return places;
    } catch (error) {
        console.error('❌ [PARSE-PLACES] Error parsing places data:', error);
        return [];
    }
} 