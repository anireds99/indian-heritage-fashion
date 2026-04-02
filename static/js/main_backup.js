// Newsletter subscription
document.getElementById('newsletterForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('newsletterEmail').value;
    const messageDiv = document.getElementById('newsletterMessage');
    
    try {
        const response = await fetch('/api/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = data.message;
            messageDiv.className = 'success';
            document.getElementById('newsletterEmail').value = '';
        } else {
            messageDiv.textContent = data.message;
            messageDiv.className = 'error';
        }
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
        
    } catch (error) {
        messageDiv.textContent = 'An error occurred. Please try again.';
        messageDiv.className = 'error';
    }
});

// Contact form submission
document.getElementById('contactForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const messageDiv = document.getElementById('contactMessage');
    
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        subject: document.getElementById('subject').value,
        message: document.getElementById('message').value
    };
    
    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = data.message;
            messageDiv.className = 'success';
            document.getElementById('contactForm').reset();
        } else {
            messageDiv.textContent = data.message;
            messageDiv.className = 'error';
        }
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
        
    } catch (error) {
        messageDiv.textContent = 'An error occurred. Please try again.';
        messageDiv.className = 'error';
    }
});

// Mobile menu toggle
document.querySelector('.mobile-menu-toggle')?.addEventListener('click', () => {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
});

// Add to Cart functionality
async function addToCart(productId, productName, price, image) {
    try {
        const response = await fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                product_name: productName,
                price: price,
                product_image: image,
                quantity: 1,
                size: 'M'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update cart badge
            updateCartBadge(data.cart_count);
            
            // Show success message
            showNotification('✅ ' + productName + ' added to cart!', 'success');
        } else {
            showNotification('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to add item to cart', 'error');
        console.error('Error:', error);
    }
}

// Add to Cart with custom quantity
async function addToCartWithQty(productId, productName, price, image, qtyInputId) {
    const qtyInput = document.getElementById(qtyInputId);
    const quantity = parseInt(qtyInput.value) || 1;
    
    if (quantity < 1) {
        showNotification('❌ Quantity must be at least 1', 'error');
        return;
    }
    
    if (quantity > 10) {
        showNotification('❌ Maximum quantity is 10 per item (inventory limit)', 'error');
        return;
    }
    
    try {
        const response = await fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                product_name: productName,
                price: price,
                product_image: image,
                quantity: quantity,
                size: 'M'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update cart badge
            updateCartBadge(data.cart_count);
            
            // Show success message with quantity
            if (quantity === 1) {
                showNotification('✅ ' + productName + ' added to cart!', 'success');
            } else {
                showNotification('✅ ' + quantity + 'x ' + productName + ' added to cart!', 'success');
            }
            
            // Reset quantity to 1
            qtyInput.value = 1;
        } else {
            showNotification('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to add item to cart', 'error');
        console.error('Error:', error);
    }
}

// Update cart badge count
function updateCartBadge(count) {
    const badge = document.getElementById('cartBadge');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.classList.add('active');
        } else {
            badge.classList.remove('active');
        }
    }
}

// Load cart count on page load
async function loadCartCount() {
    try {
        const response = await fetch('/cart/count');
        const data = await response.json();
        if (data.success) {
            updateCartBadge(data.count);
        }
    } catch (error) {
        console.error('Error loading cart count:', error);
    }
}

// Show notification toast
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification-toast');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
        color: ${type === 'success' ? '#155724' : '#721c24'};
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        font-weight: 600;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Load cart count when page loads
if (document.querySelector('.cart-icon')) {
    loadCartCount();
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Image lazy loading
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img').forEach(img => {
        imageObserver.observe(img);
    });
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('ROOTS Fashion Website - Loaded Successfully');
