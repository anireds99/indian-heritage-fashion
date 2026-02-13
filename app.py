"""
Indian Heritage Fashion Brand - Main Application
Professional e-commerce platform with authentication system.
Following SOLID principles and best practices.
"""
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timezone
import os

# Import configuration
from config import config

# Import database
from models import db

# Import controllers
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.admin_controller import admin_bp

# Create Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

# Indian Heritage Fashion Products
PRODUCTS = [
    {
        'id': 1,
        'name': 'Tanjore Temple Graphic Tee',
        'category': 'streetwear',
        'price': 1299.99,
        'image': 'mockups/tanjore.jpg',
        'description': 'Premium organic cotton tee featuring intricate Tanjore Brihadeeswara Temple architecture. Celebrating 1000 years of Dravidian heritage.',
        'culture': 'Indian',
        'story': 'Inspired by the UNESCO World Heritage Chola dynasty temple built in 1010 CE. The design captures the majestic vimana (tower) and intricate stone carvings that define South Indian temple architecture.'
    },
    {
        'id': 2,
        'name': 'ISRO Space Missions Hoodie',
        'category': 'streetwear',
        'price': 1999.99,
        'image': 'mockups/isro_1st_rocket.jpg',
        'description': 'Premium hoodie featuring the iconic "Reach for the Stars" design - celebrating ISRO\'s humble beginnings with scientists carrying India\'s first rocket on a bicycle.',
        'culture': 'Indian',
        'story': 'From a bicycle-transported rocket in 1963 to landing on the Moon\'s south pole. This design honors the legendary image of ISRO scientists carrying rocket parts on a bicycle through Kerala streets - a testament to Indian innovation, determination, and the journey from modest beginnings to cosmic achievements. Chandrayaan-3, Mangalyaan, and Gaganyaan missions prove that dreams have no limits.'
    },
    {
        'id': 3,
        'name': 'Hampi Ruins Heritage Tee',
        'category': 'heritage',
        'price': 1399.99,
        'image': 'mockups/hampi_temple_tshirt.jpg',
        'description': 'Cotton tee with print inspired by Hampi\'s Vijayanagara Empire boulder landscape and temple ruins.',
        'culture': 'Indian',
        'story': 'Capturing the mystical beauty of Karnataka\'s 14th-century UNESCO site. Each boulder and temple tells tales of a once-glorious empire.'
    },
    {
        'id': 4,
        'name': 'Mysore Palace Heritage Tee',
        'category': 'heritage',
        'price': 1499.99,
        'image': 'mockups/mysore.jpg',
        'description': 'Modern tee featuring gold-inspired print of Mysore Palace\'s Indo-Saracenic architecture and royal heritage.',
        'culture': 'Indian',
        'story': 'The Palace of Mysore, illuminated by 100,000 lights during Dussehra, inspires this regal piece. Celebrating Karnataka\'s royal traditions.'
    },
    {
        'id': 5,
        'name': 'Hyderabad Charminar Heritage Tee',
        'category': 'heritage',
        'price': 1499.99,
        'image': 'mockups/hyderabad.jpg',
        'description': 'Contemporary tee featuring the iconic Charminar monument, a symbol of Hyderabad\'s rich Qutb Shahi heritage.',
        'culture': 'Indian',
        'story': 'Built in 1591, Charminar stands as a testament to Indo-Islamic architecture. Its four grand arches represent the first four Caliphs of Islam, while its minarets watch over the historic city of pearls and biryani.'
    },
    {
        'id': 6,
        'name': 'Lonavala Hills Heritage Tee',
        'category': 'heritage',
        'price': 1399.99,
        'image': 'mockups/lonavala.jpg',
        'description': 'Nature-inspired tee featuring Lonavala\'s scenic Western Ghats landscape and monsoon beauty.',
        'culture': 'Indian',
        'story': 'Celebrating the lush green hills of Maharashtra\'s favorite hill station. From ancient Buddhist caves to misty viewpoints, Lonavala embodies the natural heritage of the Sahyadri mountains.'
    },
    {
        'id': 7,
        'name': 'Lonavala Hills Model Tee',
        'category': 'premium',
        'price': 1599.99,
        'image': 'mockups/lonavala_model.jpg',
        'description': 'Premium model fit tee with Lonavala\'s scenic beauty - perfect for outdoor enthusiasts and nature lovers.',
        'culture': 'Indian',
        'story': 'Worn by models who appreciate the misty mountains and verdant valleys of the Western Ghats. This premium design celebrates Maharashtra\'s natural beauty in style.'
    },
    {
        'id': 8,
        'name': 'Lucknow Heritage Round Collar Tee',
        'category': 'heritage',
        'price': 1599.99,
        'image': 'mockups/lucknow_round_collar.jpg',
        'description': 'Elegant round collar tee celebrating Lucknow\'s Nawabi culture, featuring intricate designs inspired by the city of tehzeeb.',
        'culture': 'Indian',
        'story': 'The city of Nawabs, known for its refined etiquette, poetry, and architecture. This design captures the essence of Awadhi culture - from the Bara Imambara to the delicate chikankari embroidery that defines Lucknow\'s artistic heritage.'
    },
    {
        'id': 9,
        'name': 'Lucknow Heritage Premium Model Tee',
        'category': 'premium',
        'price': 1899.99,
        'image': 'mockups/lucknow_model_rc.jpg',
        'description': 'Premium model fit tee with sophisticated Lucknow heritage design, perfect for those who appreciate refined Indian culture.',
        'culture': 'Indian',
        'story': 'Lucknow, where poetry meets architecture. This premium piece embodies the sophistication of Nawabi culture - a tribute to the city that gave India its most refined cuisine, language, and lifestyle.'
    },
    {
        'id': 10,
        'name': 'Nagpur Orange City Heritage Tee',
        'category': 'heritage',
        'price': 1399.99,
        'image': 'mockups/nagpur_round_collar.jpg',
        'description': 'Round collar tee celebrating Nagpur, the Orange City and geographic heart of India.',
        'culture': 'Indian',
        'story': 'At the exact center of India lies Nagpur - the Orange City. This design honors Maharashtra\'s second capital, known for its juicy Nagpur oranges, the Zero Mile marker, and its role as a major trade and cultural hub of central India.'
    },
    {
        'id': 11,
        'name': 'Nagpur Heritage Model Collection',
        'category': 'premium',
        'price': 1699.99,
        'image': 'mockups/nagpur_models.jpg',
        'description': 'Premium model collection featuring Nagpur\'s unique identity as the Orange City and geographic center of India.',
        'culture': 'Indian',
        'story': 'From the Zero Mile marker to the sweetest oranges, Nagpur represents the heart of India in more ways than one. This premium design celebrates central India\'s cultural crossroads.'
    },
    {
        'id': 12,
        'name': 'Assam Heritage Model Tee',
        'category': 'premium',
        'price': 1699.99,
        'image': 'mockups/assam_model.jpg',
        'description': 'Premium model tee celebrating Assam\'s rich tea gardens, wildlife, and vibrant Bihu culture.',
        'culture': 'Indian',
        'story': 'From the mighty Brahmaputra to the lush tea estates of the Northeast. Assam - land of the one-horned rhino, Kaziranga wildlife, and the world\'s finest tea. This design celebrates the gateway to India\'s Northeast.'
    },
    {
        'id': 13,
        'name': 'Kolkata Heritage Model Tee',
        'category': 'premium',
        'price': 1699.99,
        'image': 'mockups/kolkata_model.jpg',
        'description': 'Premium model tee honoring Kolkata - the City of Joy, cultural capital of India.',
        'culture': 'Indian',
        'story': 'Kolkata, where Rabindranath Tagore wrote poetry and the trams still run through bustling streets. From Victoria Memorial to Howrah Bridge, this design celebrates Bengal\'s intellectual and artistic legacy - home to literature, cinema, and revolution.'
    },
    {
        'id': 14,
        'name': 'Maharashtra Pride Heritage Tee',
        'category': 'heritage',
        'price': 1499.99,
        'image': 'mockups/maharashtra.jpg',
        'description': 'Bold tee celebrating Maharashtra\'s warrior heritage, from Shivaji Maharaj to modern Mumbai.',
        'culture': 'Indian',
        'story': 'Maharashtra - land of Maratha warriors and Bollywood dreams. From the forts of the Sahyadris to the streets of Mumbai, this state embodies courage, culture, and commerce. Jai Maharashtra!'
    },
    {
        'id': 15,
        'name': 'Chhatrapati Shivaji Maharaj Hoodie',
        'category': 'streetwear',
        'price': 2099.99,
        'image': 'mockups/siaji_hoodie.jpg',
        'description': 'Premium hoodie honoring Chhatrapati Shivaji Maharaj - the legendary Maratha warrior king and symbol of Swarajya.',
        'culture': 'Indian',
        'story': 'Shivaji Maharaj - the warrior king who established Hindavi Swarajya and stood against the mightiest empires. His legacy of courage, justice, and administration inspires millions. This hoodie celebrates the father of Indian Navy and protector of his people. Har Har Mahadev!'
    }
]

# Newsletter subscribers (in-memory storage)
subscribers = []

# Public routes
@app.route('/')
def home():
    featured_products = PRODUCTS[:6]
    return render_template('index.html', products=featured_products)

@app.route('/shop')
def shop():
    category = request.args.get('category', 'all')
    if category == 'all':
        products = PRODUCTS
    else:
        products = [p for p in PRODUCTS if p['category'] == category]
    return render_template('shop.html', products=products, category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        return render_template('product.html', product=product)
    return "Product not found", 404

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/indian-heritage')
def indian_heritage():
    indian_products = [p for p in PRODUCTS if p['culture'] == 'Indian']
    return render_template('indian_heritage.html', products=indian_products)

@app.route('/design-gallery')
def design_gallery():
    return render_template('design_gallery.html')

# API routes
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    if email and email not in subscribers:
        subscribers.append(email)
        return jsonify({'success': True, 'message': 'Thank you for subscribing!'})
    return jsonify({'success': False, 'message': 'Invalid email or already subscribed'})

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    return jsonify({'success': True, 'message': 'Thank you for your message! We will get back to you soon.'})

# Context processors
@app.context_processor
def inject_now():
    return {'now': datetime.now(timezone.utc)}

@app.context_processor
def inject_user():
    """Inject current user into templates."""
    user_info = {
        'is_authenticated': 'user_id' in session,
        'is_admin': 'admin_id' in session,
        'username': session.get('username') or session.get('admin_username'),
        'user_id': session.get('user_id'),
        'admin_id': session.get('admin_id')
    }
    return {'current_user': user_info}

# Database initialization
def init_database():
    """Initialize database tables."""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create default super admin if doesn't exist
        from repositories import AdminRepository
        if not AdminRepository.find_by_username('superadmin'):
            AdminRepository.create(
                email='admin@indianheritage.com',
                username='superadmin',
                password='Admin@123456',
                full_name='Super Administrator',
                role='super_admin'
            )
            print("✅ Default super admin created!")
            print("   Username: superadmin")
            print("   Password: Admin@123456")
            print("   ⚠️  Please change this password immediately!")

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5001)
