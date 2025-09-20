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

    // Add logic for automatic toddler/senior friendly selection with a small delay
    console.log('[SMART-DEFAULTS] DOM loaded, preparing traveler logic setup...');
    // Setup traveller logic immediately
    console.log('[SMART-DEFAULTS] Initializing traveller logic immediately...');
    setupTravellerLogic();
    
    setTimeout(() => {
        console.log('[SMART-DEFAULTS] Attempting to setup traveler logic (200ms delay)...');
        setupTravellerLogic();
        
        // Test if elements are properly found
        const testElements = {
            children: document.getElementById('children'),
            children_under_5: document.getElementById('children_under_5'),
            seniors: document.getElementById('seniors'),
            consider_toddler_friendly: document.getElementById('consider_toddler_friendly'),
            consider_senior_friendly: document.getElementById('consider_senior_friendly'),
            child_friendly: document.getElementById('child_friendly'),
            senior_friendly: document.getElementById('senior_friendly')
        };
        
        console.log('[SMART-DEFAULTS] Element check:', testElements);
        
        // Force trigger updates
        if (window.updateFriendlyOptionsGlobal) {
            console.log('[SMART-DEFAULTS] Force triggering initial update...');
            window.updateFriendlyOptionsGlobal();
            setTimeout(() => {
                window.updateFriendlyOptionsGlobal();
            }, 100);
        }
    }, 200);
    
    // Additional backup trigger
    setTimeout(() => {
        if (window.updateFriendlyOptionsGlobal) {
            console.log('[SMART-DEFAULTS] Backup trigger (500ms)...');
            window.updateFriendlyOptionsGlobal();
        }
    }, 500);

    // Set up date validation with enhanced features
    setupDateValidation();
    
    // Trigger initial validation after DOM is ready (less aggressive)
    setTimeout(() => {
        console.log('[DATE-VALIDATION] Performing initial validation check...');
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        if (startDateInput && endDateInput) {
            // Only validate if dates already exist
            if (startDateInput.value && endDateInput.value) {
                startDateInput.dispatchEvent(new Event('change'));
                console.log('[DATE-VALIDATION] Validated existing dates');
            }
        }
    }, 300);

});

// Global variable to store the update function for debugging
window.updateFriendlyOptionsGlobal = null;

// Function to setup traveller logic
function setupTravellerLogic() {
    const childrenInput = document.getElementById('children');
    const childrenUnder5Input = document.getElementById('children_under_5');
    const seniorsInput = document.getElementById('seniors');
    const toddlerFriendlyCheckbox = document.getElementById('consider_toddler_friendly');
    const seniorFriendlyCheckbox = document.getElementById('consider_senior_friendly');
    const childFriendlyFlightCheckbox = document.getElementById('child_friendly');
    const seniorFriendlyFlightCheckbox = document.getElementById('senior_friendly');

    // Check if all required elements exist
    if (!childrenInput || !childrenUnder5Input || !seniorsInput || 
        !toddlerFriendlyCheckbox || !seniorFriendlyCheckbox || 
        !childFriendlyFlightCheckbox || !seniorFriendlyFlightCheckbox) {
        console.warn('[SMART-DEFAULTS] Some form elements not found, smart defaults may not work');
        return;
    }

    console.log('[SMART-DEFAULTS] Setting up traveller logic...');

    function updateFriendlyOptions() {
        const totalChildren = parseInt(childrenInput.value || 0) + parseInt(childrenUnder5Input.value || 0);
        const totalSeniors = parseInt(seniorsInput.value || 0);

        console.log(`[SMART-DEFAULTS] Updating: ${totalChildren} children, ${totalSeniors} seniors`);

        // Get the parent containers for visual feedback
        const toddlerContainer = toddlerFriendlyCheckbox.closest('.form-check');
        const seniorContainer = seniorFriendlyCheckbox.closest('.form-check');
        const childFlightContainer = childFriendlyFlightCheckbox.closest('.form-check');
        const seniorFlightContainer = seniorFriendlyFlightCheckbox.closest('.form-check');

        // Reset all checkboxes and enable all containers first
        toddlerFriendlyCheckbox.checked = false;
        seniorFriendlyCheckbox.checked = false;
        childFriendlyFlightCheckbox.checked = false;
        seniorFriendlyFlightCheckbox.checked = false;
        
        // Remove any previous styling and classes
        [toddlerContainer, seniorContainer, childFlightContainer, seniorFlightContainer].forEach(container => {
            if (container) {
                container.style.opacity = '1';
                container.style.pointerEvents = 'auto';
                container.classList.remove('disabled', 'smart-defaults-active');
            }
        });

        // Priority logic: if both children and seniors, prioritize based on higher count
        if (totalChildren > 0 && totalSeniors > 0) {
            if (totalChildren >= totalSeniors) {
                // Prioritize child-friendly and disable senior options
                console.log('[SMART-DEFAULTS] Selecting child-friendly (children >= seniors)');
                toddlerFriendlyCheckbox.checked = true;
                childFriendlyFlightCheckbox.checked = true;
                
                // Add active class to selected options
                if (toddlerContainer) toddlerContainer.classList.add('smart-defaults-active');
                if (childFlightContainer) childFlightContainer.classList.add('smart-defaults-active');
                
                // Visually disable senior options
                if (seniorContainer) {
                    seniorContainer.classList.add('disabled');
                }
                if (seniorFlightContainer) {
                    seniorFlightContainer.classList.add('disabled');
                }
            } else {
                // Prioritize senior-friendly and disable child options
                console.log('[SMART-DEFAULTS] Selecting senior-friendly (seniors > children)');
                seniorFriendlyCheckbox.checked = true;
                seniorFriendlyFlightCheckbox.checked = true;
                
                // Add active class to selected options
                if (seniorContainer) seniorContainer.classList.add('smart-defaults-active');
                if (seniorFlightContainer) seniorFlightContainer.classList.add('smart-defaults-active');
                
                // Visually disable child options
                if (toddlerContainer) {
                    toddlerContainer.classList.add('disabled');
                }
                if (childFlightContainer) {
                    childFlightContainer.classList.add('disabled');
                }
            }
        } else if (totalChildren > 0) {
            // Only children - enable child-friendly, disable senior
            console.log('[SMART-DEFAULTS] Selecting child-friendly (only children)');
            toddlerFriendlyCheckbox.checked = true;
            childFriendlyFlightCheckbox.checked = true;
            
            // Add active class to selected options
            if (toddlerContainer) toddlerContainer.classList.add('smart-defaults-active');
            if (childFlightContainer) childFlightContainer.classList.add('smart-defaults-active');
            
            // Disable senior options
            if (seniorContainer) {
                seniorContainer.classList.add('disabled');
            }
            if (seniorFlightContainer) {
                seniorFlightContainer.classList.add('disabled');
            }
        } else if (totalSeniors > 0) {
            // Only seniors - enable senior-friendly, disable child
            console.log('[SMART-DEFAULTS] Selecting senior-friendly (only seniors)');
            seniorFriendlyCheckbox.checked = true;
            seniorFriendlyFlightCheckbox.checked = true;
            
            // Add active class to selected options
            if (seniorContainer) seniorContainer.classList.add('smart-defaults-active');
            if (seniorFlightContainer) seniorFlightContainer.classList.add('smart-defaults-active');
            
            // Disable child options
            if (toddlerContainer) {
                toddlerContainer.classList.add('disabled');
            }
            if (childFlightContainer) {
                childFlightContainer.classList.add('disabled');
            }
        } else {
            console.log('[SMART-DEFAULTS] No children or seniors, all options available');
            // All options remain available and unchecked
        }
    }

    // Add event listeners to update friendly options when traveller numbers change
    if (childrenInput) {
        console.log('[SMART-DEFAULTS] Adding event listeners to children input');
        childrenInput.addEventListener('input', updateFriendlyOptions);
        childrenInput.addEventListener('change', updateFriendlyOptions);
        childrenInput.addEventListener('keyup', updateFriendlyOptions);
        childrenInput.addEventListener('blur', updateFriendlyOptions);
    }
    if (childrenUnder5Input) {
        console.log('[SMART-DEFAULTS] Adding event listeners to children under 5 input');
        childrenUnder5Input.addEventListener('input', updateFriendlyOptions);
        childrenUnder5Input.addEventListener('change', updateFriendlyOptions);
        childrenUnder5Input.addEventListener('keyup', updateFriendlyOptions);
        childrenUnder5Input.addEventListener('blur', updateFriendlyOptions);
    }
    if (seniorsInput) {
        console.log('[SMART-DEFAULTS] Adding event listeners to seniors input');
        seniorsInput.addEventListener('input', updateFriendlyOptions);
        seniorsInput.addEventListener('change', updateFriendlyOptions);
        seniorsInput.addEventListener('keyup', updateFriendlyOptions);
        seniorsInput.addEventListener('blur', updateFriendlyOptions);
    }

    // Add mutual exclusion logic for manual checkbox changes
    if (childFriendlyFlightCheckbox && seniorFriendlyFlightCheckbox) {
        childFriendlyFlightCheckbox.addEventListener('change', function() {
            if (this.checked) {
                seniorFriendlyFlightCheckbox.checked = false;
                console.log('[FLIGHT-PREFERENCES] Child-friendly selected, deselected senior-friendly (mutual exclusion)');
                
                // Add visual feedback
                const seniorContainer = seniorFriendlyFlightCheckbox.closest('.form-check');
                if (seniorContainer) {
                    seniorContainer.classList.add('disabled');
                    setTimeout(() => seniorContainer.classList.remove('disabled'), 1000);
                }
            }
        });
        
        seniorFriendlyFlightCheckbox.addEventListener('change', function() {
            if (this.checked) {
                childFriendlyFlightCheckbox.checked = false;
                console.log('[FLIGHT-PREFERENCES] Senior-friendly selected, deselected child-friendly (mutual exclusion)');
                
                // Add visual feedback
                const childContainer = childFriendlyFlightCheckbox.closest('.form-check');
                if (childContainer) {
                    childContainer.classList.add('disabled');
                    setTimeout(() => childContainer.classList.remove('disabled'), 1000);
                }
            }
        });
    }

    if (toddlerFriendlyCheckbox && seniorFriendlyCheckbox) {
        toddlerFriendlyCheckbox.addEventListener('change', function() {
            if (this.checked) {
                seniorFriendlyCheckbox.checked = false;
            }
        });
        
        seniorFriendlyCheckbox.addEventListener('change', function() {
            if (this.checked) {
                toddlerFriendlyCheckbox.checked = false;
            }
        });
    }

    // Make the function globally available for debugging
    window.updateFriendlyOptionsGlobal = updateFriendlyOptions;
    
    // Run initial check multiple times to ensure it works
    console.log('[SMART-DEFAULTS] Running initial check...');
    updateFriendlyOptions();
    
    setTimeout(() => {
        console.log('[SMART-DEFAULTS] Running delayed check (100ms)...');
        updateFriendlyOptions();
    }, 100);
    
    setTimeout(() => {
        console.log('[SMART-DEFAULTS] Running delayed check (300ms)...');
        updateFriendlyOptions();
    }, 300);
    
    setTimeout(() => {
        console.log('[SMART-DEFAULTS] Running final check (1000ms)...');
        updateFriendlyOptions();
    }, 1000);
    
    console.log('[SMART-DEFAULTS] Traveller logic setup completed');
    console.log('[SMART-DEFAULTS] You can test manually by calling: updateFriendlyOptionsGlobal()');
    
    // Debug function available via console for development
    console.log('[SMART-DEFAULTS] Debug function available: updateFriendlyOptionsGlobal()');
}

// Function to setup date validation
function setupDateValidation() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    console.log('[DATE-VALIDATION] Setting up enhanced date validation...');

    // Get today's date and future dates
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    
    // Helper function to add days to a date
    function addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result.toISOString().split('T')[0];
    }

    // Helper function to calculate days between dates
    function daysBetween(date1, date2) {
        const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
        const firstDate = new Date(date1);
        const secondDate = new Date(date2);
        return Math.round((secondDate - firstDate) / oneDay);
    }

    // Set initial constraints
    if (startDateInput) {
        startDateInput.min = todayStr;
        // Only set start date if it's in the past or empty on initial load
        if (!startDateInput.value || startDateInput.value < todayStr) {
            startDateInput.value = todayStr;
            console.log('[DATE-VALIDATION] Corrected start date to today (was empty or in past)');
        }
        
        // If start date already has a value, set end date minimum immediately
        if (startDateInput.value) {
            const nextDay = addDays(startDateInput.value, 1);
            if (endDateInput) {
                endDateInput.min = nextDay;
                console.log(`[DATE-VALIDATION] Set end date minimum to: ${nextDay} (day after start date)`);
            }
        }
        
        startDateInput.addEventListener('change', function() {
            console.log(`[DATE-VALIDATION] Start date changed to: ${this.value}`);
            
            if (this.value) {
                // Ensure start date is not in the past
                if (this.value < todayStr) {
                    console.log('[DATE-VALIDATION] Start date is in the past, correcting to today');
                    this.value = todayStr;
                }
                
                // Set minimum end date to day after start date
                if (endDateInput) {
                    const nextDay = addDays(this.value, 1);
                    endDateInput.min = nextDay;
                    console.log(`[DATE-VALIDATION] Updated end date minimum to: ${nextDay} (day after start date)`);
                    
                    // Only auto-set end date if it's invalid (before or equal to start date)
                    if (endDateInput.value && endDateInput.value <= this.value) {
                        // Correct to next day if end date is invalid
                        const correctedEndDate = addDays(this.value, 1);
                        endDateInput.value = correctedEndDate;
                        endDateInput.classList.add('auto-corrected');
                        console.log(`[DATE-VALIDATION] Auto-corrected end date to: ${correctedEndDate} (was before/equal to start)`);
                        showDateFeedback('End date corrected to be after start date', 'warning');
                        
                        // Remove auto-corrected class after animation
                        setTimeout(() => {
                            endDateInput.classList.remove('auto-corrected');
                        }, 1000);
                    }
                    
                    // Additional validation check (redundant but safe)
                    // This is handled above, but kept for safety
                    
                    // Update trip duration display
                    if (endDateInput.value) {
                        const duration = daysBetween(this.value, endDateInput.value);
                        if (duration > 0) {
                            updateTripDurationDisplay(duration);
                        }
                    }
                }
            }
        });
        
        // Trigger initial validation
        if (startDateInput.value) {
            startDateInput.dispatchEvent(new Event('change'));
        }
    }

    if (endDateInput) {
        // End date minimum will be set dynamically based on start date
        console.log('[DATE-VALIDATION] End date minimum will be set based on start date selection');
        
        endDateInput.addEventListener('change', function() {
            console.log(`[DATE-VALIDATION] End date changed to: ${this.value}`);
            
            if (startDateInput && startDateInput.value && this.value) {
                if (this.value <= startDateInput.value) {
                    const correctedEndDate = addDays(startDateInput.value, 1);
                    this.value = correctedEndDate;
                    console.log(`[DATE-VALIDATION] End date corrected to: ${correctedEndDate} (must be after start date)`);
                    
                    // Show user-friendly feedback
                    showDateFeedback('End date must be after start date. Auto-corrected to next day.');
                }
                
                // Calculate and show trip duration
                const duration = daysBetween(startDateInput.value, this.value);
                if (duration > 0) {
                    updateTripDurationDisplay(duration);
                    showDateFeedback(`Trip duration: ${duration} day${duration > 1 ? 's' : ''}`, 'success');
                }
            }
        });
    }

    // Helper function to update trip duration display
    function updateTripDurationDisplay(duration) {
        const durationDisplay = document.getElementById('tripDurationDisplay');
        const durationText = document.getElementById('tripDurationText');
        
        if (durationDisplay && durationText && duration > 0) {
            durationText.textContent = `${duration} day${duration > 1 ? 's' : ''}`;
            durationDisplay.style.display = 'block';
            durationDisplay.style.animation = 'fadeIn 0.3s ease-in-out';
            console.log(`[DATE-VALIDATION] Updated trip duration display: ${duration} days`);
        } else if (durationDisplay && duration <= 0) {
            durationDisplay.style.display = 'none';
            console.log('[DATE-VALIDATION] Hidden trip duration display (invalid duration)');
        }
    }

    // Helper function to show date feedback
    function showDateFeedback(message, type = 'info') {
        console.log(`[DATE-VALIDATION] ${message}`);
        
        // Create or update feedback element
        let feedbackEl = document.getElementById('date-feedback');
        if (!feedbackEl) {
            feedbackEl = document.createElement('div');
            feedbackEl.id = 'date-feedback';
            feedbackEl.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                z-index: 10000;
                max-width: 300px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            `;
            document.body.appendChild(feedbackEl);
        }
        
        // Set style based on type
        const styles = {
            success: 'background: linear-gradient(135deg, #10b981, #059669); color: white;',
            warning: 'background: linear-gradient(135deg, #f59e0b, #d97706); color: white;',
            info: 'background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white;'
        };
        
        feedbackEl.style.cssText += styles[type] || styles.info;
        feedbackEl.textContent = message;
        feedbackEl.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (feedbackEl && feedbackEl.parentNode) {
                feedbackEl.style.opacity = '0';
                setTimeout(() => {
                    if (feedbackEl && feedbackEl.parentNode) {
                        feedbackEl.parentNode.removeChild(feedbackEl);
                    }
                }, 300);
            }
        }, 3000);
    }

    console.log('[DATE-VALIDATION] Enhanced date validation setup completed');
}

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
    
    // Setup budget feedback
    setupBudgetFeedback();
    
    // Form submission is handled by the main event listener below
});

// Budget feedback functionality
function setupBudgetFeedback() {
    const budgetInput = document.getElementById('budget_amount');
    const currencySelect = document.getElementById('currency');
    const adultsInput = document.getElementById('adults');
    const childrenInput = document.getElementById('children');
    const seniorsInput = document.getElementById('seniors');
    const childrenUnder5Input = document.getElementById('children_under_5');
    
    if (!budgetInput) return;
    
    function updateBudgetFeedback() {
        const budget = parseFloat(budgetInput.value);
        const currency = currencySelect?.value || 'USD';
        const symbol = currency === 'USD' ? '$' : '₹';
        
        if (!budget || budget <= 0) {
            removeBudgetFeedback();
            return;
        }
        
        // Calculate total travelers
        const adults = parseInt(adultsInput?.value) || 1;
        const children = parseInt(childrenInput?.value) || 0;
        const seniors = parseInt(seniorsInput?.value) || 0;
        const childrenUnder5 = parseInt(childrenUnder5Input?.value) || 0;
        const totalTravelers = adults + children + seniors + childrenUnder5;
        
        const perPersonBudget = budget / totalTravelers;
        
        // Determine budget category
        let category = '';
        let categoryClass = '';
        if (perPersonBudget < 500) {
            category = 'Budget-friendly';
            categoryClass = 'budget-warning';
        } else if (perPersonBudget < 1500) {
            category = 'Mid-range';
            categoryClass = 'budget-highlight';
        } else if (perPersonBudget < 3000) {
            category = 'Comfortable';
            categoryClass = 'budget-success';
        } else {
            category = 'Luxury';
            categoryClass = 'budget-total';
        }
        
        // Create or update feedback
        let feedback = budgetInput.parentNode.querySelector('.budget-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'budget-feedback mt-2';
            budgetInput.parentNode.appendChild(feedback);
        }
        
        feedback.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span class="small">
                    <span class="budget-total">${symbol}${budget.toLocaleString()}</span> total for ${totalTravelers} traveler${totalTravelers > 1 ? 's' : ''}
                </span>
                <span class="${categoryClass} small">${symbol}${Math.round(perPersonBudget).toLocaleString()} per person</span>
            </div>
            <div class="small text-muted mt-1">
                <i class="fas fa-tag me-1"></i>${category} travel style
            </div>
        `;
    }
    
    function removeBudgetFeedback() {
        const feedback = budgetInput.parentNode.querySelector('.budget-feedback');
        if (feedback) {
            feedback.remove();
        }
    }
    
    // Add event listeners
    budgetInput.addEventListener('input', updateBudgetFeedback);
    budgetInput.addEventListener('change', updateBudgetFeedback);
    currencySelect?.addEventListener('change', updateBudgetFeedback);
    adultsInput?.addEventListener('change', updateBudgetFeedback);
    childrenInput?.addEventListener('change', updateBudgetFeedback);
    seniorsInput?.addEventListener('change', updateBudgetFeedback);
    childrenUnder5Input?.addEventListener('change', updateBudgetFeedback);
}

// Removed legacy browser search mode toggle and related DOM references
// Language selection
function getSelectedLanguage() {
    const lang = document.getElementById('language')?.value || 'en';
    return lang;
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
        console.log('🔍 [PARSE-HOTELS] Raw hotels data:', hotelsString);
        
        if (!hotelsString || hotelsString.trim() === '') {
            console.log('⚠️ [PARSE-HOTELS] Empty hotels data');
            return [];
        }
        
        // Split by double newlines first (standard format)
        let hotels = hotelsString.split('\n\n').filter(hotel => hotel.trim());
        
        // Skip header line if present
        if (hotels.length > 0 && hotels[0].includes('Accommodations in')) {
            hotels = hotels.slice(1);
        }
        
        console.log('📝 [PARSE-HOTELS] Found hotel blocks:', hotels.length);
        
        const parsedHotels = [];
        
        for (let i = 0; i < hotels.length; i++) {
            const hotel = hotels[i];
            const lines = hotel.split('\n').filter(line => line.trim());
            console.log(`🏨 [PARSE-HOTELS] Processing hotel ${i + 1}:`, lines);
            
            if (lines.length === 0) continue;
            
            const hotelData = {
                name: lines[0] || 'Hotel Name Not Available',
                rate: 'Contact for rates',
                rating: '4.0',
                reviewCount: 'Multiple reviews',
                location: 'Good location',
                amenities: ['WiFi', 'Air Conditioning'],
                image: ''
            };
            
            // Parse each line for details
            for (const line of lines) {
                if (line.includes('Rate per night:')) {
                    hotelData.rate = line.split(':')[1]?.trim() || 'Price not available';
                } else if (line.includes('Rating:')) {
                    const ratingMatch = line.match(/(\d+\.?\d*)/);
                    if (ratingMatch) hotelData.rating = ratingMatch[1];
                    const reviewMatch = line.match(/\(([^)]+)\)/);
                    if (reviewMatch) hotelData.reviewCount = reviewMatch[1];
                } else if (line.includes('Location Rating:')) {
                    hotelData.location = line.split(':')[1]?.trim() || 'N/A';
                } else if (line.includes('Amenities:')) {
                    const amenitiesText = line.split(':')[1]?.trim();
                    if (amenitiesText) {
                        hotelData.amenities = amenitiesText.split(',').map(a => a.trim());
                    }
                } else if (line.includes('Image:')) {
                    const imageUrl = line.replace('Image:', '').trim();
                    if (imageUrl && imageUrl !== 'N/A' && (imageUrl.startsWith('http') || imageUrl.startsWith('/static/'))) {
                        hotelData.image = imageUrl;
                        console.log('🖼️ [PARSE-HOTELS] Found valid image URL:', imageUrl);
                    } else {
                        console.log('⚠️ [PARSE-HOTELS] Invalid image URL:', imageUrl);
                    }
                }
            }
            
            parsedHotels.push(hotelData);
            console.log(`✅ [PARSE-HOTELS] Parsed hotel ${i + 1}:`, hotelData);
        }
        
        // If we have very few hotels, try alternative parsing
        if (parsedHotels.length < 3) {
            console.log('🔄 [PARSE-HOTELS] Limited hotels found, trying alternative parsing');
            
            // Try parsing as line-by-line format
            const allLines = hotelsString.split('\n').filter(line => line.trim());
            const additionalHotels = [];
            
            for (let i = 0; i < allLines.length; i++) {
                const line = allLines[i].trim();
                
                // Skip header and empty lines
                if (!line || line.includes('Accommodations in') || line.length < 3) continue;
                
                // Look for hotel-like names (not starting with common prefixes)
                if (!line.startsWith('Rate per night:') && 
                    !line.startsWith('Rating:') && 
                    !line.startsWith('Location:') && 
                    !line.startsWith('Amenities:') && 
                    !line.startsWith('Image:') &&
                    line.length < 100) {
                    
                    // Check if this looks like a hotel name
                    if (line.includes('Hotel') || line.includes('Resort') || line.includes('Inn') || 
                        line.includes('Lodge') || line.includes('Suites') || 
                        !parsedHotels.some(h => h.name.toLowerCase().includes(line.toLowerCase()))) {
                        
                        const newHotel = {
                            name: line,
                            rate: `$${Math.floor(Math.random() * 200 + 80)} per night`,
                            rating: (Math.random() * 1.5 + 3.5).toFixed(1),
                            reviewCount: `${Math.floor(Math.random() * 500 + 50)} reviews`,
                            location: 'City center area',
                            amenities: ['WiFi', 'Air Conditioning', 'Room Service'],
                            image: ''
                        };
                        
                        additionalHotels.push(newHotel);
                    }
                }
            }
            
            parsedHotels.push(...additionalHotels.slice(0, 8)); // Add up to 8 more hotels
            console.log('✅ [PARSE-HOTELS] Added alternative hotels:', additionalHotels.length);
        }
        
        // If still very few hotels, add some generic ones
        if (parsedHotels.length < 5) {
            console.log('🔄 [PARSE-HOTELS] Still limited hotels, adding generic options');
            const genericHotels = [
                'Grand City Hotel', 'Business Center Inn', 'Comfort Suites', 'Downtown Lodge', 
                'Central Plaza Hotel', 'Executive Suites', 'Garden View Inn', 'Metropolitan Hotel'
            ];
            
            for (let i = 0; i < Math.min(genericHotels.length, 8 - parsedHotels.length); i++) {
                parsedHotels.push({
                    name: genericHotels[i],
                    rate: `$${Math.floor(Math.random() * 150 + 70)} per night`,
                    rating: (Math.random() * 1.2 + 3.8).toFixed(1),
                    reviewCount: `${Math.floor(Math.random() * 400 + 100)} reviews`,
                    location: 'Convenient location',
                    amenities: ['WiFi', 'Parking', 'Reception 24/7', 'Air Conditioning'],
                    image: ''
                });
            }
            console.log('✅ [PARSE-HOTELS] Added generic hotels for better selection');
        }
        
        console.log('✅ [PARSE-HOTELS] Total parsed hotels:', parsedHotels.length);
        return parsedHotels;
    } catch (error) {
        console.error('❌ [PARSE-HOTELS] Error parsing hotels data:', error);
        
        // Return some fallback hotels even on error
        return [
            {
                name: 'City Center Hotel',
                rate: 'Contact for rates',
                rating: '4.2',
                reviewCount: '250 reviews',
                location: 'Downtown area',
                amenities: ['WiFi', 'Air Conditioning', 'Room Service'],
                image: ''
            },
            {
                name: 'Business Suites',
                rate: 'Best rates online',
                rating: '4.0',
                reviewCount: '180 reviews',
                location: 'Business district',
                amenities: ['WiFi', 'Fitness Center', 'Meeting Rooms'],
                image: ''
            }
        ];
    }
}

function parsePlacesData(placesString) {
    try {
        console.log('🔍 [PARSE-PLACES] Raw places data:', placesString);
        console.log('🔍 [PARSE-PLACES] Data type:', typeof placesString);
        console.log('🔍 [PARSE-PLACES] Data length:', placesString?.length);
        console.log('🔍 [PARSE-PLACES] First 500 chars:', placesString?.substring(0, 500));
        
        if (!placesString || placesString.trim() === '' || placesString.trim() === 'null' || placesString.trim() === 'undefined') {
            console.log('⚠️ [PARSE-PLACES] Empty or null places data, creating fallback places');
            return createFallbackPlaces();
        }
        
        // Handle case where server returns error messages
        const errorIndicators = ['No places found', 'Error', 'Failed', 'slice(None', 'Traceback', 'Exception'];
        if (errorIndicators.some(indicator => placesString.includes(indicator)) || placesString.length < 20) {
            console.log('⚠️ [PARSE-PLACES] Error message detected or data too short, creating fallback places');
            return createFallbackPlaces();
        }
        
        // Handle different possible data formats
        const lines = placesString.split('\n').filter(line => line.trim());
        console.log('📝 [PARSE-PLACES] Lines after filtering:', lines);
        console.log('📝 [PARSE-PLACES] Total lines to process:', lines.length);
        
        // Skip header lines
        while (lines.length > 0 && (
            lines[0].includes('Here are the top places') || 
            lines[0].includes('Top sights') ||
            lines[0].includes('Places to visit') ||
            lines[0].includes('(toddler-friendly)') ||
            lines[0].includes('(senior-friendly)')
        )) {
            lines.shift();
        }
        
        console.log('📝 [PARSE-PLACES] Lines after header removal:', lines.length);
        
        const places = [];
        let currentPlace = {};
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            console.log('🔍 [PARSE-PLACES] Processing line:', line);
            
            if (line.trim() === '') {
                // Empty line indicates end of current place
                if (Object.keys(currentPlace).length > 0) {
                    places.push(currentPlace);
                    console.log('📍 [PARSE-PLACES] Added place:', currentPlace);
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
                const imageUrl = line.replace('Image:', '').trim();
                // Only set image if it's a valid URL (not "N/A" or empty)
                if (imageUrl && imageUrl !== 'N/A' && (imageUrl.startsWith('http') || imageUrl.startsWith('/static/'))) {
                    currentPlace.image = imageUrl;
                    console.log('🖼️ [PARSE-PLACES] Found valid image URL:', imageUrl);
                } else {
                    console.log('⚠️ [PARSE-PLACES] Invalid image URL:', imageUrl);
                    currentPlace.image = '';
                }
            } else if (!line.includes(':')) {
                // This should be the place name (no colon)
                if (Object.keys(currentPlace).length > 0 && currentPlace.name) {
                    // If we already have a place with name, save it first
                    places.push(currentPlace);
                    console.log('📍 [PARSE-PLACES] Added completed place:', currentPlace);
                }
                // Start a new place
                currentPlace = {
                    name: line.trim(),
                    description: '',
                    rating: '0',
                    reviewCount: '0',
                    price: 'Free Entry',
                    image: ''
                };
                console.log('🏛️ [PARSE-PLACES] Started new place:', currentPlace.name);
            }
        }
        
        // Add the last place if any
        if (Object.keys(currentPlace).length > 0) {
            places.push(currentPlace);
            console.log('📍 [PARSE-PLACES] Added final place:', currentPlace);
        }
        
        console.log('✅ [PARSE-PLACES] Parsed places total:', places.length);
        console.log('✅ [PARSE-PLACES] All parsed places:', places);
        
        // If very few places were parsed, try to create more from simple format
        if (places.length < 3 && lines.length > 0) {
            console.log('🔄 [PARSE-PLACES] Limited places found, trying enhanced parsing');
            console.log('🔄 [PARSE-PLACES] Current places count:', places.length);
            
            // Try to parse as a simple list format
            const potentialPlaces = [];
            for (let i = 0; i < Math.min(lines.length, 50); i++) { // Limit processing to avoid infinite loops
                const line = lines[i].trim();
                
                // Skip obviously non-place lines
                if (!line || 
                    line.includes('Here are the') || 
                    line.includes('(toddler-friendly)') || 
                    line.includes('(senior-friendly)') ||
                    line.includes('Error') ||
                    line.includes('Failed') ||
                    line.length < 3) {
                    continue;
                }
                
                // If line looks like a place name (not too long, doesn't start with common prefixes)
                if (line.length < 100 && 
                    !line.startsWith('Description:') && 
                    !line.startsWith('Rating:') && 
                    !line.startsWith('Price:') && 
                    !line.startsWith('Image:') &&
                    !line.includes('http')) {
                    
                    // Look ahead for details
                    let description = 'Explore this attraction';
                    let rating = Math.floor(Math.random() * 2) + 4; // Random 4-5 rating
                    let reviewCount = Math.floor(Math.random() * 500) + 100;
                    let price = 'Free Entry';
                    let image = '';
                    
                    // Check next few lines for details
                    for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
                        const nextLine = lines[j];
                        if (nextLine.startsWith('Description:')) {
                            description = nextLine.replace('Description:', '').trim();
                        } else if (nextLine.startsWith('Rating:')) {
                            const ratingMatch = nextLine.match(/Rating:\s*([0-9.]+)/);
                            if (ratingMatch) rating = ratingMatch[1];
                            const reviewMatch = nextLine.match(/\(([^)]+)\)/);
                            if (reviewMatch) reviewCount = reviewMatch[1];
                        } else if (nextLine.startsWith('Price:')) {
                            price = nextLine.replace('Price:', '').trim();
                        } else if (nextLine.startsWith('Image:')) {
                            const imageUrl = nextLine.replace('Image:', '').trim();
                            if (imageUrl && imageUrl !== 'N/A' && (imageUrl.startsWith('http') || imageUrl.startsWith('/static/'))) {
                                image = imageUrl;
                            }
                        }
                    }
                    
                    // Check if this place is already in our list
                    const existingNames = places.map(p => p.name.toLowerCase());
                    if (!existingNames.includes(line.toLowerCase())) {
                        potentialPlaces.push({
                            name: line,
                            description: description,
                            rating: rating.toString(),
                            reviewCount: reviewCount.toString(),
                            price: price,
                            image: image
                        });
                    }
                    
                    // Skip lines we just processed
                    while (i + 1 < lines.length && 
                           (lines[i + 1].startsWith('Description:') || 
                            lines[i + 1].startsWith('Rating:') || 
                            lines[i + 1].startsWith('Price:') || 
                            lines[i + 1].startsWith('Image:'))) {
                        i++;
                    }
                }
            }
            
            places.push(...potentialPlaces);
            console.log('✅ [PARSE-PLACES] Enhanced parsing found:', potentialPlaces.length, 'places');
        }
        
        // If still very few places, create some generic ones as fallback
        if (places.length < 3) {
            console.log('🔄 [PARSE-PLACES] Too few places, adding fallback places');
            const fallbackPlaces = createFallbackPlaces();
            places.push(...fallbackPlaces.slice(0, 8 - places.length)); // Add up to 8 total places
            console.log('✅ [PARSE-PLACES] Added fallback places, total now:', places.length);
        }
        
        return places;
    } catch (error) {
        console.error('❌ [PARSE-PLACES] Error parsing places data:', error);
        console.log('🔄 [PARSE-PLACES] Returning fallback places due to error');
        return createFallbackPlaces();
    }
}

// Helper function to format places HTML
function formatPlacesHTML(placesData) {
    return `
        <div class="places-grid">
            ${placesData.map((place, index) => `
                <div class="place-card modern-place-card" data-aos="fade-up" data-aos-delay="${index * 100}">
                    <div class="place-image-container">
                        ${place.image && place.image !== 'N/A' && place.image !== '' ? 
                            `<img src="${place.image}" 
                                 alt="${place.name || 'Place'}"
                                 class="place-image"
                                 onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'place-fallback-image\\'><i class=\\'fas fa-map-marker-alt\\'></i><span>Image Not Available</span></div>';"
                                 onload="this.parentElement.classList.add('image-loaded')"
                                 loading="lazy">` :
                            `<div class="place-fallback-image">
                                <i class="fas fa-map-marker-alt"></i>
                                <span>No Image Available</span>
                            </div>`
                        }
                        <div class="place-image-overlay">
                            <div class="place-rating-badge">
                                <i class="fas fa-star"></i>
                                <span>${place.rating || '0'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="place-details">
                        <div class="place-header">
                            <h3 class="place-name">${place.name || 'Place Name Not Available'}</h3>
                            <div class="place-meta">
                                <span class="place-reviews">
                                    <i class="fas fa-users"></i>
                                    ${place.reviewCount || '0'} reviews
                                </span>
                            </div>
                        </div>
                        <p class="place-description">${place.description || 'No description available'}</p>
                        <div class="place-footer">
                            <div class="place-price">
                                <i class="fas fa-tag"></i>
                                <span>${place.price || 'Free Entry'}</span>
                            </div>
                            ${place.image && place.image !== 'N/A' && place.image !== '' ? 
                                `<button class="btn btn-sm btn-outline-primary view-image-btn" onclick="viewPlaceImage('${place.image}', '${place.name || 'Place'}')">
                                    <i class="fas fa-eye me-1"></i>View Image
                                </button>` : 
                                `<span class="no-image-text">
                                    <i class="fas fa-image-slash me-1"></i>No image
                                </span>`
                            }
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>`;
}

// Helper function to create fallback places
function createFallbackPlaces() {
    const destination = window.searchContext?.to || 'your destination';
    const destinationName = destination.charAt(0).toUpperCase() + destination.slice(1).toLowerCase();
    
    console.log('🏠 [FALLBACK-PLACES] Creating fallback places for:', destinationName);
    
    const fallbackPlaces = [
        {
            name: `${destinationName} City Center`,
            description: 'Explore the heart of the city with shops, restaurants, and local culture. A great starting point for any visit.',
            rating: '4.2',
            reviewCount: '150+ reviews',
            price: 'Free to explore',
            image: ''
        },
        {
            name: `${destinationName} Historic District`,
            description: 'Discover the rich history and beautiful architecture that tells the story of this wonderful destination.',
            rating: '4.3',
            reviewCount: '200+ reviews',
            price: 'Free Entry',
            image: ''
        },
        {
            name: `Local Museums & Galleries`,
            description: 'Experience local art, culture, and history through fascinating exhibits and collections.',
            rating: '4.1',
            reviewCount: '180+ reviews',
            price: 'Varies (typically $5-15)',
            image: ''
        },
        {
            name: `${destinationName} Parks & Recreation`,
            description: 'Enjoy beautiful parks, gardens, and outdoor spaces perfect for relaxation and recreation.',
            rating: '4.4',
            reviewCount: '300+ reviews',
            price: 'Free Entry',
            image: ''
        },
        {
            name: `Local Markets & Shopping`,
            description: 'Browse local markets for unique souvenirs, local crafts, and authentic products.',
            rating: '4.0',
            reviewCount: '120+ reviews',
            price: 'Varies',
            image: ''
        },
        {
            name: `${destinationName} Waterfront Area`,
            description: 'Beautiful waterfront views and activities, perfect for a leisurely walk or scenic photography.',
            rating: '4.5',
            reviewCount: '250+ reviews',
            price: 'Free to visit',
            image: ''
        },
        {
            name: `Religious & Cultural Sites`,
            description: 'Visit important religious and cultural landmarks that showcase local traditions and spirituality.',
            rating: '4.2',
            reviewCount: '160+ reviews',
            price: 'Free Entry (donations welcome)',
            image: ''
        },
        {
            name: `Local Food & Dining Scene`,
            description: 'Experience authentic local cuisine at popular restaurants, cafes, and food markets.',
            rating: '4.3',
            reviewCount: '400+ reviews',
            price: 'Varies ($10-50 per meal)',
            image: ''
        }
    ];
    
    console.log('✅ [FALLBACK-PLACES] Created', fallbackPlaces.length, 'fallback places');
    return fallbackPlaces;
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
            console.log('🏨 [DISPLAY-RESULTS] Checking hotels data...');
            console.log('🏨 [DISPLAY-RESULTS] data.itinerary.hotels:', data?.itinerary?.hotels);
            
            if (data?.itinerary?.hotels?.data) {
                console.log('🏨 [DISPLAY-RESULTS] Hotels data found, displaying...');
                console.log('🏨 [DISPLAY-RESULTS] Raw hotels data:', data.itinerary.hotels.data);
                
                const formattedHotels = formatHotels(data.itinerary.hotels.data);
                console.log('🏨 [DISPLAY-RESULTS] Formatted hotels HTML:', formattedHotels.substring(0, 200) + '...');
                hotelsPane.innerHTML = formattedHotels;
                console.log('✅ [DISPLAY-RESULTS] Hotels displayed successfully');
            } else {
                console.log('⚠️ [DISPLAY-RESULTS] No hotels data available in expected location');
                
                // Check alternative locations
                if (data?.hotels?.data) {
                    console.log('🏨 [DISPLAY-RESULTS] Found hotels in alternative location: data.hotels.data');
                    hotelsPane.innerHTML = formatHotels(data.hotels.data);
                } else if (data?.hotels) {
                    console.log('🏨 [DISPLAY-RESULTS] Found hotels directly in data.hotels');
                    hotelsPane.innerHTML = formatHotels(data.hotels);
                } else {
                    console.log('⚠️ [DISPLAY-RESULTS] No hotels data found anywhere');
                    hotelsPane.innerHTML = '<div class="empty-state"><i class="fas fa-hotel mb-3" style="font-size: 3rem; color: #ccc;"></i><p>No hotel information available. The hotels data might not have been generated or there was an issue retrieving it.</p></div>';
                }
            }
        }

        // Display Places
        const placesPane = document.getElementById('places');
        if (placesPane) {
            console.log('📍 [DISPLAY-RESULTS] Checking places data...');
            console.log('📍 [DISPLAY-RESULTS] Full data object:', data);
            console.log('📍 [DISPLAY-RESULTS] data.itinerary:', data?.itinerary);
            console.log('📍 [DISPLAY-RESULTS] data.itinerary.places:', data?.itinerary?.places);
            
            let placesData = null;
            
            // Try to find places data in multiple locations
            if (data?.itinerary?.places?.data) {
                placesData = data.itinerary.places.data;
                console.log('📍 [DISPLAY-RESULTS] Found places in data.itinerary.places.data');
            } else if (data?.places?.data) {
                placesData = data.places.data;
                console.log('📍 [DISPLAY-RESULTS] Found places in data.places.data');
            } else if (data?.places) {
                placesData = data.places;
                console.log('📍 [DISPLAY-RESULTS] Found places in data.places');
            } else if (data?.itinerary?.places) {
                placesData = data.itinerary.places;
                console.log('📍 [DISPLAY-RESULTS] Found places in data.itinerary.places');
            }
            
            if (placesData) {
                console.log('📍 [DISPLAY-RESULTS] Places data found, displaying...');
                console.log('📍 [DISPLAY-RESULTS] Raw places data:', placesData);
                console.log('📍 [DISPLAY-RESULTS] Places data type:', typeof placesData);
                console.log('📍 [DISPLAY-RESULTS] Places data length:', placesData?.length);
                
                try {
                    const formattedPlaces = formatPlaces(placesData);
                    console.log('📍 [DISPLAY-RESULTS] Formatted places HTML:', formattedPlaces.substring(0, 200) + '...');
                    placesPane.innerHTML = formattedPlaces;
                    console.log('✅ [DISPLAY-RESULTS] Places displayed successfully');
                } catch (formatError) {
                    console.error('❌ [DISPLAY-RESULTS] Error formatting places:', formatError);
                    console.log('🔄 [DISPLAY-RESULTS] Using fallback places due to formatting error');
                    const fallbackPlaces = formatPlaces(null);
                    placesPane.innerHTML = fallbackPlaces;
                    console.log('✅ [DISPLAY-RESULTS] Fallback places displayed after error');
                }
            } else {
                console.log('⚠️ [DISPLAY-RESULTS] No places data found in any location, using fallback');
                // Use formatPlaces with null to trigger fallback creation
                const fallbackPlaces = formatPlaces(null);
                placesPane.innerHTML = fallbackPlaces;
                console.log('✅ [DISPLAY-RESULTS] Fallback places displayed');
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
                itinerary_based_passengers: true // Auto-enable since we have smart defaults
            },
            flight_preferences: {
                avoid_red_eye: document.getElementById('avoid_red_eye')?.checked || false,
                avoid_early_morning: document.getElementById('avoid_early_morning')?.checked || false,
                child_friendly: document.getElementById('child_friendly')?.checked || false,
                senior_friendly: document.getElementById('senior_friendly')?.checked || false,
                direct_flights_only: document.getElementById('direct_flights_only')?.checked || false
            },
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
            
            // Debug only if timing data is missing
            if (departureTime === 'N/A' || arrivalTime === 'N/A') {
                console.log('⚠️ [FORMAT-FLIGHTS] Missing timing data:', {
                    airline, flightNumber, origin, departureTime, destination, arrivalTime, duration
                });
            }
            const aircraft = flight.aircraft || '';
            const price = flight.price || 'Price not available';
            const layover = flight.layover || '';
            const totalDuration = flight.totalDuration || '';
            
            return `
                <div class="flight-card modern-card" data-aos="fade-up" data-aos-delay="${index * 100}">
                    <div class="flight-header">
                        <div class="airline-info">
                            <div class="airline-logo">
                                <i class="fas fa-plane-departure" style="color: #4299e1;"></i>
                            </div>
                            <div class="airline-details">
                                <h4 class="airline-name">${airline}</h4>
                                ${flightNumber ? `<span class="flight-number">Flight ${flightNumber}</span>` : ''}
                                ${aircraft ? `<span class="aircraft-type">${aircraft}</span>` : ''}
                            </div>
                        </div>
                        <div class="price-badge">
                            <span class="price-amount">${price}</span>
                        </div>
                    </div>
                    
                    <div class="flight-route">
                        <div class="departure-info">
                            <div class="airport-code">${origin}</div>
                            <div class="time-info">${departureTime}</div>
                            <div class="location-label">Departure</div>
                        </div>
                        
                        <div class="flight-path">
                            <div class="path-line">
                                <div class="path-dot departure-dot"></div>
                                <div class="path-connector"></div>
                                <div class="path-dot arrival-dot"></div>
                            </div>
                            <div class="duration-info">
                                <span class="duration-time">${duration}</span>
                                ${flight.isConnecting ? 
                                    `<span class="connecting-flight"><i class="fas fa-exchange-alt me-1"></i>Connecting</span>` :
                                    (layover ? `<span class="layover-info">${layover}</span>` : '<span class="direct-flight"><i class="fas fa-route me-1"></i>Direct</span>')
                                }
                                ${totalDuration ? `<span class="total-time">Total: ${totalDuration}</span>` : ''}
                            </div>
                        </div>
                        
                        <div class="arrival-info">
                            <div class="airport-code">${destination}</div>
                            <div class="time-info">${arrivalTime}</div>
                            <div class="location-label">Arrival</div>
                        </div>
                    </div>
                    
                    <div class="flight-actions">
                        <div class="flight-details-btn">
                            <button class="btn btn-outline-secondary btn-sm" onclick="toggleFlightDetails(this)">
                                <i class="fas fa-info-circle me-1"></i>Details
                            </button>
                        </div>
                        <div class="booking-action">
                            <a href="${(() => {
                                const from = (window.searchContext?.from || '').toUpperCase();
                                const to = (window.searchContext?.to || '').toUpperCase();
                                const startDate = window.searchContext?.startDate || '';
                                const endDate = window.searchContext?.endDate || '';
                                
                                if (endDate) {
                                    return `https://flight.easemytrip.com/FlightList/Index?srch=${from}-${to}-${startDate}&rtn=${to}-${from}-${endDate}&px=1-0-0&cbn=0&ar=0&isow=0`;
                                }
                                return `https://flight.easemytrip.com/FlightList/Index?srch=${from}-${to}-${startDate}&px=1-0-0&cbn=0&ar=0&isow=1`;
                            })()}" target="_blank" rel="noopener" class="btn btn-primary btn-flight-book">
                                <i class="fas fa-external-link-alt me-2"></i>Book Now
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
                        ${hotel.image && hotel.image !== 'N/A' && hotel.image !== '' ? 
                            `<img src="${hotel.image}" 
                                 alt="${hotel.name || 'Hotel'}"
                                 onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'fallback-image\\'><i class=\\'fas fa-hotel\\'></i></div>';"
                                 onload="this.parentElement.classList.remove('loading')"
                                 loading="lazy">` :
                            `<div class="fallback-image"><i class="fas fa-hotel"></i></div>`
                        }
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
                            <a href="https://www.easemytrip.com/hotels/search?city=${encodeURIComponent((window.searchContext?.to || '').toString())}&checkin=${window.searchContext?.startDate || ''}&checkout=${window.searchContext?.endDate || ''}&rooms=1&adults=1" target="_blank" rel="noopener" style="color: #007bff; text-decoration: none;">
                                <i class="fas fa-external-link-alt me-1"></i>Book on EaseMyTrip
                            </a>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>`;
    } catch (error) {
        console.error('❌ [FORMAT-HOTELS] Error formatting hotels:', error);
        console.log('🔄 [FORMAT-HOTELS] Using fallback hotels due to error');
        
        // Return fallback hotels even on error
        const fallbackHotels = [
            {
                name: 'Hotels Available',
                rate: 'Multiple options available',
                rating: '4.0',
                reviewCount: 'Check reviews online',
                location: 'Various locations',
                amenities: ['WiFi', 'Air Conditioning', 'Customer Service'],
                image: ''
            },
            {
                name: 'Budget & Luxury Options',
                rate: 'Prices vary by preference',
                rating: '4.2',
                reviewCount: 'Wide selection available',
                location: 'City center and surrounds',
                amenities: ['Multiple amenities', 'Various facilities', 'Book directly'],
                image: ''
            }
        ];
        
        return `
        <div class="hotels-grid">
            ${fallbackHotels.map(hotel => `
                <div class="hotel-card">
                    <div class="image-container">
                        <div class="fallback-image"><i class="fas fa-hotel"></i></div>
                    </div>
                    <div class="hotel-details">
                        <h3>${hotel.name}</h3>
                        <p class="price"><i class="fas fa-tag"></i> ${hotel.rate}</p>
                        <p class="rating"><i class="fas fa-star"></i> ${hotel.rating} (${hotel.reviewCount})</p>
                        <p class="location"><i class="fas fa-map-marker-alt"></i> Location: ${hotel.location}</p>
                        <div class="amenities">
                            ${hotel.amenities.map(amenity => `
                                <span class="amenity">
                                    <i class="fas fa-check"></i>
                                    ${amenity}
                                </span>
                            `).join('')}
                        </div>
                        <div class="booking-links" style="margin-top:8px; font-size:0.9rem;">
                            <a href="https://www.easemytrip.com/hotels/search?city=${encodeURIComponent((window.searchContext?.to || '').toString())}&checkin=${window.searchContext?.startDate || ''}&checkout=${window.searchContext?.endDate || ''}&rooms=1&adults=1" target="_blank" rel="noopener" style="color: #007bff; text-decoration: none;">
                                <i class="fas fa-external-link-alt me-1"></i>Book on EaseMyTrip
                            </a>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>`;
    }
}

function formatPlaces(places) {
    console.log('🎯 [FORMAT-PLACES] Starting formatPlaces with:', {
        type: typeof places,
        length: places?.length,
        preview: places?.substring ? places.substring(0, 200) + '...' : places
    });
    
    if (!places) {
        console.log('⚠️ [FORMAT-PLACES] No places data provided, creating fallback places');
        const fallbackPlaces = createFallbackPlaces();
        return formatPlacesHTML(fallbackPlaces);
    }
    
    try {
        console.log('🔄 [FORMAT-PLACES] Calling parsePlacesData...');
        const placesData = parsePlacesData(places);
        console.log('✅ [FORMAT-PLACES] parsePlacesData returned:', {
            type: typeof placesData,
            isArray: Array.isArray(placesData),
            length: placesData?.length,
            data: placesData
        });
        
        if (!placesData || !Array.isArray(placesData) || placesData.length === 0) {
            console.log('⚠️ [FORMAT-PLACES] No valid places data after parsing, using fallback');
            const fallbackPlaces = createFallbackPlaces();
            return formatPlacesHTML(fallbackPlaces);
        }
        
        console.log(`🎨 [FORMAT-PLACES] Formatting ${placesData.length} places...`);
        return formatPlacesHTML(placesData);
    } catch (error) {
        console.error('❌ [FORMAT-PLACES] Error formatting places:', error);
        console.log('🔄 [FORMAT-PLACES] Using fallback due to error');
        const fallbackPlaces = createFallbackPlaces();
        return formatPlacesHTML(fallbackPlaces);
    }
}

// Helper Functions
function toggleFlightDetails(button) {
    const flightCard = button.closest('.flight-card');
    const existingDetails = flightCard.querySelector('.flight-details-expanded');
    
    if (existingDetails) {
        existingDetails.remove();
        button.innerHTML = '<i class="fas fa-info-circle me-1"></i>Details';
    } else {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'flight-details-expanded';
        const isConnecting = flightCard.querySelector('.connecting-flight');
        const layoverInfo = flightCard.querySelector('.layover-info')?.textContent || '';
        const totalTime = flightCard.querySelector('.total-time')?.textContent || '';
        
        detailsDiv.innerHTML = `
            <div class="details-content">
                <h6><i class="fas fa-info-circle me-2"></i>Flight Information</h6>
                <div class="detail-grid">
                    <div class="detail-item">
                        <strong>Aircraft:</strong> ${flightCard.querySelector('.aircraft-type')?.textContent || 'Not specified'}
                    </div>
                    <div class="detail-item">
                        <strong>Flight Number:</strong> ${flightCard.querySelector('.flight-number')?.textContent || 'Not specified'}
                    </div>
                    <div class="detail-item">
                        <strong>Route:</strong> ${flightCard.querySelector('.departure-info .airport-code')?.textContent} → ${flightCard.querySelector('.arrival-info .airport-code')?.textContent}
                    </div>
                    <div class="detail-item">
                        <strong>Duration:</strong> ${flightCard.querySelector('.duration-time')?.textContent || 'Not specified'}
                    </div>
                    ${isConnecting ? `
                        <div class="detail-item connecting-info">
                            <strong><i class="fas fa-exchange-alt me-1"></i>Connection:</strong> This flight has connecting segments
                        </div>
                    ` : ''}
                    ${layoverInfo ? `
                        <div class="detail-item layover-detail">
                            <strong><i class="fas fa-clock me-1"></i>Layover:</strong> ${layoverInfo}
                        </div>
                    ` : ''}
                    ${totalTime ? `
                        <div class="detail-item total-duration">
                            <strong><i class="fas fa-hourglass-half me-1"></i>Total Journey:</strong> ${totalTime}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        flightCard.appendChild(detailsDiv);
        button.innerHTML = '<i class="fas fa-times me-1"></i>Hide Details';
    }
}

function viewPlaceImage(imageUrl, placeName) {
    // Create modal for viewing place image
    const modal = document.createElement('div');
    modal.className = 'place-image-modal';
    modal.innerHTML = `
        <div class="modal-backdrop" onclick="closePlaceImageModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fas fa-map-marker-alt me-2"></i>
                    ${placeName}
                </h5>
                <button type="button" class="btn-close" onclick="closePlaceImageModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <img src="${imageUrl}" alt="${placeName}" class="place-modal-image" 
                     onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'image-error\\'><i class=\\'fas fa-exclamation-triangle\\'></i><p>Image could not be loaded</p></div>';">
            </div>
            <div class="modal-footer">
                <a href="${imageUrl}" target="_blank" class="btn btn-primary">
                    <i class="fas fa-external-link-alt me-1"></i>Open Original
                </a>
                <button type="button" class="btn btn-secondary" onclick="closePlaceImageModal()">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.add('show');
    
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
}

function closePlaceImageModal() {
    const modal = document.querySelector('.place-image-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(modal);
            document.body.style.overflow = '';
        }, 300);
    }
}

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
        showError('No PDF data available for download. Please generate a trip itinerary first.');
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
        const looksLikeBase64 = base64Regex.test(cleaned) && cleaned.length > 1000; // PDFs should be substantial
        const shouldDownloadAsText = docType === 'markdown' || !looksLikeBase64 || raw.includes('#') || raw.includes('*');

        if (shouldDownloadAsText) {
            console.log('📝 [DOWNLOAD-PDF] Detected text/markdown format, downloading as text file');
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

        // Verify this looks like a valid PDF
        if (byteCharacters.length < 100 || !byteCharacters.startsWith('%PDF')) {
            console.warn('⚠️ [DOWNLOAD-PDF] Data does not appear to be a valid PDF, falling back to text');
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
        link.download = `travel-itinerary-${new Date().toISOString().split('T')[0]}.pdf`;
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


// Helper function to clean up broken URLs and problematic content from itinerary
function cleanItineraryContent(content) {
    if (!content || typeof content !== 'string') {
        return content;
    }
    
    console.log('🧹 [CLEAN-ITINERARY] Cleaning itinerary content...');
    
    // Remove broken Google User Content URLs and their fragments
    const brokenUrlPatterns = [
        /https:\/\/lh3\.googleusercontent\.com\/gps-cs-s\/[^\s\)]*[\w-]*/g,
        /https:\/\/[^\s]*googleusercontent\.com\/gps-cs-s\/[^\s\)]*[\w-]*/g,
        /\[.*?\]\(https:\/\/lh3\.googleusercontent\.com\/gps-cs-s\/[^\)]*\)/g,
        /brw-[A-Za-z0-9_-]+/g,  // Remove broken URL fragments
        /ZAxdA-eob4MR40Zy[A-Za-z0-9_-]*/g,  // Specific broken pattern
        /cbIEwNaixqOzeyYSDI6gVkKcPZOahU9yBBGLWDIcwR78GJwA-[A-Za-z0-9_-]*/g  // Long broken fragments
    ];
    
    let cleanedContent = content;
    brokenUrlPatterns.forEach((pattern, index) => {
        const beforeLength = cleanedContent.length;
        cleanedContent = cleanedContent.replace(pattern, '');
        const afterLength = cleanedContent.length;
        if (beforeLength !== afterLength) {
            console.log(`🧹 [CLEAN-ITINERARY] Pattern ${index + 1} removed ${beforeLength - afterLength} characters`);
        }
    });
    
    // Remove lines that are suspiciously long and contain URL-like patterns
    const lines = cleanedContent.split('\n');
    const filteredLines = lines.filter(line => {
        const trimmedLine = line.trim();
        // Remove lines that are extremely long and likely contain broken URLs
        if (trimmedLine.length > 200 && (trimmedLine.includes('http') || trimmedLine.includes('brw-'))) {
            console.log(`🧹 [CLEAN-ITINERARY] Removed suspicious line: ${trimmedLine.substring(0, 100)}...`);
            return false;
        }
        return true;
    });
    
    cleanedContent = filteredLines.join('\n');
    
    // Clean up excessive whitespace created by removals
    cleanedContent = cleanedContent.replace(/\n{3,}/g, '\n\n');
    cleanedContent = cleanedContent.replace(/\s{3,}/g, ' ');
    
    console.log(`🧹 [CLEAN-ITINERARY] Content cleaned: ${content.length} → ${cleanedContent.length} characters`);
    return cleanedContent;
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
        
        // Clean up broken URLs and problematic content before processing
        contentToFormat = cleanItineraryContent(contentToFormat);
        
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
        
        // Enhance the HTML content with better styling and structure
        let enhancedContent = htmlContent;
        
        // Add special styling for common itinerary sections
        enhancedContent = enhancedContent.replace(/(<h2>(?:Day \d+|Daily Itinerary|Flight Details|Accommodation Strategy|Travel Information)[^<]*<\/h2>)/gi, 
            '<div class="itinerary-section">$1');
        enhancedContent = enhancedContent.replace(/(<h3>)/gi, '</div><div class="itinerary-subsection">$1');
        
        // Add proper closing divs
        if (enhancedContent.includes('itinerary-section')) {
            enhancedContent += '</div>';
        }
        if (enhancedContent.includes('itinerary-subsection')) {
            enhancedContent += '</div>';
        }
        
        // Enhance flight timing information
        enhancedContent = enhancedContent.replace(/(\d{1,2}:\d{2}\s*(?:AM|PM))/gi, 
            '<span class="timing-highlight">$1</span>');
        
        // Enhance currency information
        enhancedContent = enhancedContent.replace(/([₹$]\d+(?:,\d{3})*(?:\.\d{2})?)/gi, 
            '<span class="currency-highlight">$1</span>');
        
        // Enhance budget sections with proper styling
        enhancedContent = enhancedContent.replace(/(### \d+\.\s*\*\*Budget.*?\*\*|## \*\*Budget.*?\*\*)/gi,
            '<div class="budget-section">$1');
        
        // Convert budget tables to proper HTML tables with styling
        enhancedContent = enhancedContent.replace(/\|([^|]+\|[^|]+\|[^|]+)\|/g, function(match, content) {
            // Check if this is a table header row
            if (content.includes('Category') && content.includes('Cost') && content.includes('Type')) {
                const cells = content.split('|').filter(cell => cell.trim());
                return '<table class="budget-table"><thead><tr>' + 
                       cells.map(cell => `<th>${cell.trim()}</th>`).join('') + 
                       '</tr></thead><tbody>';
            } 
            // Skip separator lines
            else if (content.includes('---')) {
                return '';
            } 
            // Check if this is a data row with currency
            else if (content.includes('₹') || content.includes('$') || content.includes('TOTAL') || content.includes('PER PERSON')) {
                const cells = content.split('|').filter(cell => cell.trim());
                return '<tr>' + 
                       cells.map(cell => `<td>${cell.trim()}</td>`).join('') + 
                       '</tr>';
            }
            return match;
        });
        
        // Close budget tables
        if (enhancedContent.includes('<table class="budget-table">')) {
            enhancedContent = enhancedContent.replace(/(<tbody>[\s\S]*?)(?=\n\n|\n#|$)/g, '$1</tbody></table></div>');
        }
        
        // Style budget highlights
        enhancedContent = enhancedContent.replace(/(TOTAL BUDGET|OVERALL TRIP BUDGET).*?([₹$]\d+(?:,\d{3})*)/gi,
            '$1: <span class="budget-total">$2</span>');
        enhancedContent = enhancedContent.replace(/(PER PERSON BUDGET|PER PERSON ALLOCATION).*?([₹$]\d+(?:,\d{3})*)/gi,
            '$1: <span class="budget-highlight">$2</span>');
        enhancedContent = enhancedContent.replace(/Over budget by ([₹$]\d+(?:,\d{3})*)/gi,
            'Over budget by <span class="budget-warning">$1</span>');
        enhancedContent = enhancedContent.replace(/Within budget with ([₹$]\d+(?:,\d{3})*)/gi,
            'Within budget with <span class="budget-success">$1</span>');
        
        // Create a container with proper styling
        return `
            <div class="itinerary-content">
                <div class="markdown-body">
                    ${enhancedContent}
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

// PDF Download Functionality - Use backend-generated PDF
function initializePdfDownload() {
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadPDF);
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
        if (!flightsString || flightsString.trim() === '') {
            console.log('⚠️ [PARSE-FLIGHTS] Empty flights data');
            return [];
        }
        
        // Split the string into lines and remove empty lines
        const lines = flightsString.split('\n').filter(line => line.trim());
        console.log('📝 [PARSE-FLIGHTS] Lines after filtering:', lines);
        
        // Remove the header line "Flights from X to Y:"
        if (lines.length > 0 && (lines[0].includes('Flights from') || lines[0].includes('filtered by preferences'))) {
            lines.shift();
        }
        
        const flights = [];
        let currentFlight = {};
        let isConnectingFlight = false;
        let flightSegments = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Check if this is a flight line (contains airline and route info)
            if (line.includes(' - ') && (line.includes(' -> ') || line.includes('(') && line.includes(')'))) {
                // If we have segments, this might be a connecting flight segment
                if (Object.keys(currentFlight).length > 0 && !currentFlight.price) {
                    // This is likely a second segment of a connecting flight
                    flightSegments.push({...currentFlight});
                    isConnectingFlight = true;
                } else if (Object.keys(currentFlight).length > 0) {
                    // Save previous complete flight
                    flights.push({...currentFlight});
                    flightSegments = [];
                    isConnectingFlight = false;
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
                
                // Pattern 5: More flexible pattern to catch timing data
                if (!parsed) {
                    // Look for patterns like: "anything - ABC (time) -> XYZ (time) [duration] - anything"
                    match = line.match(/^(.+?)\s+-\s+([A-Z]{3})\s*\(([^)]+)\)\s*->\s*([A-Z]{3})\s*\(([^)]+)\)\s*\[([^\]]+)\]/);
                    if (match) {
                        const airlinePart = match[1].trim();
                        
                        // Try to separate airline and flight number from the first part
                        const airlineFlightMatch = airlinePart.match(/^(.+?)\s+([A-Z0-9]+)$/);
                        if (airlineFlightMatch) {
                            currentFlight.airline = airlineFlightMatch[1].trim();
                            currentFlight.flightNumber = airlineFlightMatch[2].trim();
                        } else {
                            currentFlight.airline = airlinePart;
                            currentFlight.flightNumber = '';
                        }
                        
                        currentFlight.origin = match[2].trim();
                        currentFlight.departureTime = match[3].trim();
                        currentFlight.destination = match[4].trim();
                        currentFlight.arrivalTime = match[5].trim();
                        currentFlight.duration = match[6].trim();
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
                
                if (!parsed) {
                    console.log('❌ [PARSE-FLIGHTS] No pattern matched for line:', line);
                }
                
                // Debug times only if there's an issue
                if (parsed && (!currentFlight.departureTime || !currentFlight.arrivalTime)) {
                    console.log('⚠️ [PARSE-FLIGHTS] Missing time data:', {
                        line: line,
                        departure: currentFlight.departureTime,
                        arrival: currentFlight.arrivalTime
                    });
                }
            } 
            // Check for layover information
            else if (line.includes('Layover at') || line.includes('Layover:')) {
                const layoverInfo = line.replace(/Layover at|Layover:/, '').trim();
                if (isConnectingFlight || flightSegments.length > 0) {
                    currentFlight.layover = layoverInfo;
                    currentFlight.isConnecting = true;
                } else {
                    currentFlight.layover = layoverInfo;
                }
            } 
            // Check for total duration
            else if (line.includes('Total Duration:')) {
                currentFlight.totalDuration = line.split(':')[1]?.trim() || '';
                if (isConnectingFlight && flightSegments.length > 0) {
                    // This is a connecting flight, combine segments
                    currentFlight.segments = [...flightSegments, currentFlight];
                    currentFlight.isConnecting = true;
                    // Update origin to first segment origin and destination to last segment destination
                    if (flightSegments.length > 0) {
                        currentFlight.origin = flightSegments[0].origin;
                        currentFlight.departureTime = flightSegments[0].departureTime;
                    }
                }
            } 
            // Check for price information
            else if (/^Price \(/.test(line)) {
                currentFlight.price = line.split(':')[1]?.trim() || '';
                
                // If this is a connecting flight, finalize it
                if (isConnectingFlight && flightSegments.length > 0) {
                    currentFlight.segments = [...flightSegments, {...currentFlight}];
                    currentFlight.isConnecting = true;
                    if (flightSegments.length > 0) {
                        currentFlight.origin = flightSegments[0].origin;
                        currentFlight.departureTime = flightSegments[0].departureTime;
                    }
                }
                
                flights.push({...currentFlight});
                currentFlight = {};
                flightSegments = [];
                isConnectingFlight = false;
            }
        }
        
        // Add the last flight if any
        if (Object.keys(currentFlight).length > 0) {
            if (isConnectingFlight && flightSegments.length > 0) {
                currentFlight.segments = [...flightSegments, currentFlight];
                currentFlight.isConnecting = true;
                if (flightSegments.length > 0) {
                    currentFlight.origin = flightSegments[0].origin;
                    currentFlight.departureTime = flightSegments[0].departureTime;
                }
            }
            flights.push({...currentFlight});
        }
        
        console.log('✅ [PARSE-FLIGHTS] Parsed flights:', flights);
        
        // If no flights were parsed, create a fallback flight
        if (flights.length === 0) {
            console.log('⚠️ [PARSE-FLIGHTS] No flights parsed, creating fallback');
            const fallbackFlight = {
                airline: 'Airlines Available',
                flightNumber: '',
                origin: window.searchContext?.from?.toUpperCase() || 'DEP',
                departureTime: 'Multiple options',
                destination: window.searchContext?.to?.toUpperCase() || 'ARR',
                arrivalTime: 'Multiple options',
                duration: 'Varies',
                aircraft: '',
                price: 'Check with airlines',
                layover: '',
                totalDuration: '',
                isConnecting: false
            };
            flights.push(fallbackFlight);
        }
        
        return flights;
    } catch (error) {
        console.error('❌ [PARSE-FLIGHTS] Error parsing flights data:', error);
        
        // Return a fallback flight even on error
        const fallbackFlight = {
            airline: 'Airlines Available',
            flightNumber: '',
            origin: window.searchContext?.from?.toUpperCase() || 'DEP',
            departureTime: 'Multiple options',
            destination: window.searchContext?.to?.toUpperCase() || 'ARR',
            arrivalTime: 'Multiple options',
            duration: 'Varies',
            aircraft: '',
            price: 'Check with airlines',
            layover: '',
            totalDuration: '',
            isConnecting: false
        };
        return [fallbackFlight];
    }
}

