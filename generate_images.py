from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import math
import random

# Create images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Common dimensions for product images
WIDTH, HEIGHT = 400, 500

def get_font(size):
    """Get font with fallback"""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        return ImageFont.load_default()

def create_tshirt_mockup(design_func, color='#ffffff'):
    """Create a realistic t-shirt mockup"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # T-shirt body shape
    tshirt_color = color
    
    # Shoulders
    draw.polygon([
        (80, 120), (100, 100), (150, 90), (200, 85),
        (250, 90), (300, 100), (320, 120),
        (280, 140), (120, 140)
    ], fill=tshirt_color, outline='#cccccc', width=2)
    
    # Main body
    draw.rectangle([120, 140, 280, 450], fill=tshirt_color, outline='#cccccc', width=2)
    
    # Sleeves
    draw.polygon([(80, 120), (100, 100), (60, 150), (90, 180), (120, 160)], 
                 fill=tshirt_color, outline='#cccccc', width=2)
    draw.polygon([(320, 120), (300, 100), (340, 150), (310, 180), (280, 160)], 
                 fill=tshirt_color, outline='#cccccc', width=2)
    
    # Collar (V-neck)
    draw.polygon([(180, 90), (200, 120), (220, 90)], fill='#e0e0e0', outline='#cccccc', width=1)
    
    # Add shadows for depth
    shadow_overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_overlay)
    
    # Side shadows
    for x in range(120, 135):
        alpha = int((135 - x) * 3)
        shadow_draw.line([(x, 140), (x, 450)], fill=(0, 0, 0, alpha))
    for x in range(265, 280):
        alpha = int((x - 265) * 3)
        shadow_draw.line([(x, 140), (x, 450)], fill=(0, 0, 0, alpha))
    
    img = Image.alpha_composite(img.convert('RGBA'), shadow_overlay).convert('RGB')
    
    return img

def create_hoodie_mockup(design_func, color='#2c3e50'):
    """Create a realistic hoodie mockup"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    hoodie_color = color
    
    # Hood
    draw.ellipse([150, 60, 250, 120], fill=hoodie_color, outline='#333333', width=2)
    draw.rectangle([150, 90, 250, 120], fill=hoodie_color)
    
    # Shoulders and body
    draw.polygon([
        (70, 120), (90, 105), (150, 95), (200, 90),
        (250, 95), (310, 105), (330, 120),
        (290, 150), (110, 150)
    ], fill=hoodie_color, outline='#333333', width=2)
    
    # Main body
    draw.rectangle([110, 150, 290, 480], fill=hoodie_color, outline='#333333', width=2)
    
    # Sleeves
    draw.polygon([(70, 120), (90, 105), (50, 180), (80, 200), (110, 170)], 
                 fill=hoodie_color, outline='#333333', width=2)
    draw.polygon([(330, 120), (310, 105), (350, 180), (320, 200), (290, 170)], 
                 fill=hoodie_color, outline='#333333', width=2)
    
    # Front zipper/center line
    draw.line([(200, 120), (200, 480)], fill='#555555', width=3)
    
    # Pockets
    for x in [130, 230]:
        draw.arc([x, 300, x+50, 340], start=0, end=180, fill='#444444', width=2)
        draw.line([(x, 320), (x, 350)], fill='#444444', width=2)
        draw.line([(x+50, 320), (x+50, 350)], fill='#444444', width=2)
    
    # Drawstrings
    draw.line([(180, 110), (160, 130)], fill='#cccccc', width=2)
    draw.line([(220, 110), (240, 130)], fill='#cccccc', width=2)
    
    return img

def create_tanjore_tshirt():
    """Tanjore Temple Graphic Tee"""
    img = create_tshirt_mockup(None, '#f5f5dc')
    draw = ImageDraw.Draw(img)
    
    # Center position for design
    center_x, center_y = 200, 280
    
    # Temple tower design
    tower_width = 80
    tower_height = 120
    
    # Base
    draw.rectangle([center_x-40, center_y+30, center_x+40, center_y+60], 
                   fill='#8b4513', outline='#000000', width=2)
    
    # Middle tier
    draw.rectangle([center_x-35, center_y-10, center_x+35, center_y+30], 
                   fill='#cd853f', outline='#000000', width=2)
    
    # Add tier details
    for y in range(int(center_y-5), int(center_y+25), 8):
        draw.line([center_x-32, y, center_x+32, y], fill='#8b4513', width=1)
    
    # Top vimana
    draw.polygon([center_x-30, center_y-10, center_x, center_y-60, center_x+30, center_y-10], 
                 fill='#daa520', outline='#000000', width=2)
    
    # Kalasha
    draw.ellipse([center_x-10, center_y-75, center_x+10, center_y-60], 
                 fill='#FFD700', outline='#000000', width=2)
    
    # Text
    title_font = get_font(20)
    small_font = get_font(10)
    
    draw.text((center_x, center_y-100), "BRIHADEESWARA", anchor="mm", font=title_font, fill='#8b4513')
    draw.text((center_x, center_y+90), "TANJORE 1010 CE", anchor="mm", font=small_font, fill='#8b4513')
    
    img.save('static/images/tanjore1.jpg', 'JPEG', quality=95)
    print("✓ Created tanjore1.jpg - Temple design on beige t-shirt")

def create_isro_hoodie():
    """ISRO Space Missions Hoodie"""
    img = create_hoodie_mockup(None, '#000033')
    draw = ImageDraw.Draw(img)
    
    # Space design on hoodie
    center_x, center_y = 200, 280
    
    # Add stars
    random.seed(42)
    for _ in range(80):
        x = random.randint(120, 280)
        y = random.randint(160, 450)
        size = random.randint(1, 2)
        draw.ellipse([x, y, x+size, y+size], fill='#ffffff')
    
    # Rocket
    rocket_x, rocket_y = center_x, center_y-50
    draw.rectangle([rocket_x-6, rocket_y, rocket_x+6, rocket_y+25], 
                   fill='#ffffff', outline='#FFD700', width=1)
    draw.polygon([rocket_x-8, rocket_y, rocket_x, rocket_y-12, rocket_x+8, rocket_y], 
                 fill='#e63946')
    draw.polygon([rocket_x-12, rocket_y+20, rocket_x-6, rocket_y+10, rocket_x-6, rocket_y+25], 
                 fill='#e63946')
    draw.polygon([rocket_x+12, rocket_y+20, rocket_x+6, rocket_y+10, rocket_x+6, rocket_y+25], 
                 fill='#e63946')
    # Flame
    draw.polygon([rocket_x-4, rocket_y+25, rocket_x, rocket_y+35, rocket_x+4, rocket_y+25], 
                 fill='#FF6B35')
    
    # ISRO logo circle
    draw.ellipse([center_x-40, center_y, center_x+40, center_y+80], 
                 outline='#FFD700', width=3)
    
    # Text
    title_font = get_font(24)
    mission_font = get_font(12)
    
    draw.text((center_x, center_y+40), "ISRO", anchor="mm", font=title_font, fill='#FFD700')
    
    # Missions with flag colors
    draw.text((center_x, center_y+110), "CHANDRAYAAN-3", anchor="mm", 
              font=mission_font, fill='#FF9933')
    draw.text((center_x, center_y+135), "MANGALYAAN", anchor="mm", 
              font=mission_font, fill='#ffffff')
    draw.text((center_x, center_y+160), "GAGANYAAN", anchor="mm", 
              font=mission_font, fill='#138808')
    
    img.save('static/images/isro1.jpg', 'JPEG', quality=95)
    print("✓ Created isro1.jpg - Space design on navy hoodie")

def create_gateway_bomber():
    """Gateway of India Bomber Jacket"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    bomber_color = '#d4a574'
    
    # Bomber jacket silhouette
    # Collar
    draw.ellipse([150, 90, 250, 130], fill='#8b7355', outline='#333333', width=2)
    
    # Shoulders
    draw.polygon([
        (80, 130), (100, 110), (150, 100), (200, 95),
        (250, 100), (300, 110), (320, 130),
        (290, 160), (110, 160)
    ], fill=bomber_color, outline='#8b7355', width=2)
    
    # Main body with ribbed bottom
    draw.rectangle([110, 160, 290, 420], fill=bomber_color, outline='#8b7355', width=2)
    
    # Ribbed waistband
    for y in range(420, 450, 5):
        draw.line([(110, y), (290, y)], fill='#8b7355', width=2)
    draw.rectangle([110, 420, 290, 450], outline='#8b7355', width=2)
    
    # Sleeves
    draw.polygon([(80, 130), (100, 110), (60, 200), (70, 240), (110, 200)], 
                 fill=bomber_color, outline='#8b7355', width=2)
    draw.polygon([(320, 130), (300, 110), (340, 200), (330, 240), (290, 200)], 
                 fill=bomber_color, outline='#8b7355', width=2)
    
    # Sleeve cuffs (ribbed)
    for y in range(235, 245, 3):
        draw.line([(60, y), (75, y)], fill='#8b7355', width=1)
        draw.line([(325, y), (340, y)], fill='#8b7355', width=1)
    
    # Front zipper
    draw.line([(200, 130), (200, 450)], fill='#555555', width=3)
    for y in range(140, 440, 15):
        draw.rectangle([198, y, 202, y+8], fill='#666666')
    
    # Side pockets
    for x in [130, 240]:
        draw.arc([x, 280, x+40, 320], start=0, end=180, fill='#8b7355', width=2)
    
    # Back design - Gateway of India
    center_x, center_y = 200, 270
    
    # Gateway arch
    draw.arc([center_x-50, center_y-40, center_x+50, center_y+20], 
             start=0, end=180, fill='#654321', width=3)
    
    # Pillars
    draw.rectangle([center_x-45, center_y-10, center_x-35, center_y+50], 
                   fill='#8b6914', outline='#000000', width=1)
    draw.rectangle([center_x+35, center_y-10, center_x+45, center_y+50], 
                   fill='#8b6914', outline='#000000', width=1)
    
    # Dome
    draw.ellipse([center_x-15, center_y-60, center_x+15, center_y-40], 
                 fill='#cd853f', outline='#000000', width=1)
    
    # Text
    draw.text((center_x, center_y-80), "GATEWAY OF INDIA", anchor="mm", 
              font=get_font(14), fill='#654321')
    draw.text((center_x, center_y+70), "MUMBAI 1924", anchor="mm", 
              font=get_font(10), fill='#654321')
    
    img.save('static/images/gateway1.jpg', 'JPEG', quality=95)
    print("✓ Created gateway1.jpg - Gateway design on tan bomber jacket")

def create_hampi_linen_shirt():
    """Hampi Ruins Linen Shirt"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    shirt_color = '#e2725b'
    
    # Button-up shirt
    # Collar
    draw.polygon([(170, 95), (150, 115), (200, 105)], fill='#d06550', outline='#333333', width=1)
    draw.polygon([(230, 95), (250, 115), (200, 105)], fill='#d06550', outline='#333333', width=1)
    
    # Shoulders
    draw.polygon([
        (90, 120), (110, 105), (150, 100), (200, 95),
        (250, 100), (290, 105), (310, 120),
        (280, 145), (120, 145)
    ], fill=shirt_color, outline='#333333', width=2)
    
    # Main body
    draw.rectangle([120, 145, 280, 480], fill=shirt_color, outline='#333333', width=2)
    
    # Sleeves (short)
    draw.polygon([(90, 120), (110, 105), (80, 160), (100, 180), (120, 165)], 
                 fill=shirt_color, outline='#333333', width=2)
    draw.polygon([(310, 120), (290, 105), (320, 160), (300, 180), (280, 165)], 
                 fill=shirt_color, outline='#333333', width=2)
    
    # Button placket
    draw.line([(200, 105), (200, 480)], fill='#d06550', width=4)
    for y in range(120, 460, 30):
        draw.ellipse([197, y, 203, y+6], fill='#8b4513', outline='#000000', width=1)
    
    # Chest pocket
    draw.rectangle([140, 180, 180, 220], outline='#d06550', width=2)
    
    # Hampi boulder design
    center_x, center_y = 200, 320
    
    # Boulders
    draw.ellipse([center_x-35, center_y-20, center_x-5, center_y+20], 
                 fill='#8b4513', outline='#000000', width=2)
    draw.ellipse([center_x+5, center_y-15, center_x+35, center_y+25], 
                 fill='#a0522d', outline='#000000', width=2)
    
    # Small temple
    draw.rectangle([center_x-15, center_y+30, center_x+15, center_y+60], 
                   fill='#cd853f', outline='#000000', width=1)
    draw.polygon([center_x-15, center_y+30, center_x, center_y+15, center_x+15, center_y+30], 
                 fill='#daa520', outline='#000000', width=1)
    
    # Text
    draw.text((center_x, center_y-50), "HAMPI", anchor="mm", 
              font=get_font(18), fill='#8b4513')
    draw.text((center_x, center_y+80), "VIJAYANAGARA", anchor="mm", 
              font=get_font(10), fill='#654321')
    
    img.save('static/images/hampi1.jpg', 'JPEG', quality=95)
    print("✓ Created hampi1.jpg - Boulder design on terracotta linen shirt")

def create_mysore_kurta():
    """Mysore Palace Embroidered Kurta"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    kurta_color = '#fffef0'
    
    # Kurta silhouette (long tunic)
    # Collar (mandarin)
    draw.rectangle([180, 95, 220, 105], fill='#daa520', outline='#8b4513', width=1)
    
    # Shoulders
    draw.polygon([
        (100, 120), (120, 105), (160, 100), (200, 95),
        (240, 100), (280, 105), (300, 120),
        (270, 145), (130, 145)
    ], fill=kurta_color, outline='#daa520', width=2)
    
    # Main body (longer than shirt)
    draw.rectangle([130, 145, 270, 490], fill=kurta_color, outline='#daa520', width=2)
    
    # Sleeves (3/4 length)
    draw.polygon([(100, 120), (120, 105), (85, 200), (110, 240), (130, 200)], 
                 fill=kurta_color, outline='#daa520', width=2)
    draw.polygon([(300, 120), (280, 105), (315, 200), (290, 240), (270, 200)], 
                 fill=kurta_color, outline='#daa520', width=2)
    
    # Embroidered placket
    draw.rectangle([190, 105, 210, 300], fill='#FFD700', outline='#8b4513', width=2)
    
    # Embroidery pattern (geometric)
    for y in range(115, 290, 15):
        draw.ellipse([195, y, 205, y+10], fill='#e63946', outline='#8b4513', width=1)
        draw.line([192, y+5, 208, y+5], fill='#8b4513', width=1)
        draw.line([200, y+2, 200, y+8], fill='#8b4513', width=1)
    
    # Mysore Palace design
    center_x, center_y = 200, 350
    
    # Palace with domes
    draw.rectangle([center_x-40, center_y-10, center_x+40, center_y+40], 
                   fill='#FFD700', outline='#8b4513', width=2)
    
    # Central dome
    draw.pieslice([center_x-25, center_y-40, center_x+25, center_y-10], 
                  start=0, end=180, fill='#daa520', outline='#8b4513', width=2)
    
    # Side domes
    for dx in [-30, 30]:
        draw.pieslice([center_x+dx-15, center_y-30, center_x+dx+15, center_y-5], 
                      start=0, end=180, fill='#daa520', outline='#8b4513', width=1)
    
    # Windows
    for wx in range(-30, 35, 15):
        for wy in range(0, 35, 15):
            draw.rectangle([center_x+wx, center_y+wy, center_x+wx+8, center_y+wy+10], 
                          fill='#8b4513', outline='#000000', width=1)
    
    # Text
    draw.text((center_x, center_y-55), "MYSORE PALACE", anchor="mm", 
              font=get_font(12), fill='#8b4513')
    
    img.save('static/images/mysore1.jpg', 'JPEG', quality=95)
    print("✓ Created mysore1.jpg - Palace embroidery on ivory kurta")

def create_konark_scarf():
    """Konark Sun Temple Mandala Scarf"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Scarf draped over shoulders
    scarf_color = '#c2b280'
    
    # Neck/drape area
    draw.ellipse([100, 80, 300, 160], fill=scarf_color, outline='#8b4513', width=2)
    
    # Left drape
    draw.polygon([
        (100, 120), (80, 150), (70, 300), (90, 450), (120, 480),
        (130, 400), (140, 200), (130, 140)
    ], fill=scarf_color, outline='#8b4513', width=2)
    
    # Right drape
    draw.polygon([
        (300, 120), (320, 150), (330, 300), (310, 450), (280, 480),
        (270, 400), (260, 200), (270, 140)
    ], fill=scarf_color, outline='#8b4513', width=2)
    
    # Front drape (center)
    draw.rectangle([160, 160, 240, 490], fill=scarf_color, outline='#8b4513', width=2)
    
    # Konark wheel design (centered on scarf)
    center_x, center_y = 200, 320
    outer_r = 60
    inner_r = 20
    
    # Outer circle
    draw.ellipse([center_x-outer_r, center_y-outer_r, center_x+outer_r, center_y+outer_r], 
                 outline='#8b4513', width=3)
    
    # Inner circle
    draw.ellipse([center_x-inner_r, center_y-inner_r, center_x+inner_r, center_y+inner_r], 
                 fill='#daa520', outline='#8b4513', width=2)
    
    # 24 spokes
    for i in range(24):
        angle = (i * 360 / 24) * math.pi / 180
        x1 = center_x + inner_r * math.cos(angle)
        y1 = center_y + inner_r * math.sin(angle)
        x2 = center_x + outer_r * math.cos(angle)
        y2 = center_y + outer_r * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill='#8b4513', width=2)
    
    # Decorative border pattern
    for y in range(170, 480, 20):
        draw.ellipse([165, y, 173, y+8], fill='#e63946')
        draw.ellipse([227, y, 235, y+8], fill='#e63946')
    
    # Text
    draw.text((center_x, center_y-90), "KONARK", anchor="mm", 
              font=get_font(16), fill='#8b4513')
    draw.text((center_x, center_y+85), "SUN TEMPLE", anchor="mm", 
              font=get_font(10), fill='#8b4513')
    
    img.save('static/images/konark1.jpg', 'JPEG', quality=95)
    print("✓ Created konark1.jpg - Wheel mandala on sandstone scarf")

def create_lotus_sweatshirt():
    """Lotus Temple Minimal Sweatshirt"""
    img = create_tshirt_mockup(None, '#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Sweatshirt modifications (ribbed cuffs and waist)
    # Ribbed bottom
    for y in range(445, 455, 3):
        draw.line([(120, y), (280, y)], fill='#e0e0e0', width=1)
    
    # Minimal lotus design
    center_x, center_y = 200, 280
    
    # Lotus petals (minimalist)
    petal_color = '#2b2d42'
    
    # Outer petals (simplified)
    for i in range(9):
        angle = (i * 360 / 9) * math.pi / 180
        x = center_x + 50 * math.cos(angle)
        y = center_y + 50 * math.sin(angle)
        # Petal shape
        draw.ellipse([x-15, y-20, x+15, y+20], outline=petal_color, width=2)
    
    # Center circle
    draw.ellipse([center_x-20, center_y-20, center_x+20, center_y+20], 
                 outline=petal_color, width=3)
    
    # Minimal text
    draw.text((center_x, center_y-80), "LOTUS TEMPLE", anchor="mm", 
              font=get_font(14), fill=petal_color)
    draw.text((center_x, center_y+70), "27 Petals • Unity", anchor="mm", 
              font=get_font(9), fill=petal_color)
    
    img.save('static/images/lotus1.jpg', 'JPEG', quality=95)
    print("✓ Created lotus1.jpg - Minimal lotus on white sweatshirt")

def create_meenakshi_joggers():
    """Meenakshi Temple Color Block Joggers"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Joggers silhouette
    # Waistband
    draw.rectangle([120, 120, 280, 145], fill='#333333', outline='#000000', width=2)
    # Drawstring
    draw.ellipse([185, 125, 215, 135], fill='#cccccc', outline='#333333', width=1)
    
    # Left leg
    draw.polygon([
        (120, 145), (140, 200), (145, 300), (140, 400), (150, 480),
        (130, 490), (110, 480), (115, 400), (120, 300), (115, 200)
    ], outline='#333333', width=2)
    
    # Right leg
    draw.polygon([
        (280, 145), (260, 200), (255, 300), (260, 400), (250, 480),
        (270, 490), (290, 480), (285, 400), (280, 300), (285, 200)
    ], outline='#333333', width=2)
    
    # Colorful vertical stripes (Meenakshi gopuram colors)
    colors = ['#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#FF6FB5', '#A78BFA']
    stripe_width = 160 // len(colors)
    
    for i, color in enumerate(colors):
        # Left leg stripes
        x = 120 + i * stripe_width
        draw.polygon([
            (x, 145), (x+stripe_width, 145),
            (x+stripe_width+2, 200), (x+2, 200),
            (x+3, 300), (x+stripe_width+3, 300),
            (x+2, 400), (x+stripe_width+2, 400),
            (x+5, 480), (x+stripe_width, 480),
            (x+stripe_width-5, 400), (x-2, 400),
            (x-3, 300), (x+stripe_width-3, 300),
            (x-2, 200), (x+stripe_width-2, 200)
        ], fill=color, outline='#333333', width=1)
        
        # Right leg stripes
        x = 280 - (i+1) * stripe_width
        draw.polygon([
            (x, 145), (x+stripe_width, 145),
            (x+stripe_width-2, 200), (x-2, 200),
            (x-3, 300), (x+stripe_width-3, 300),
            (x-2, 400), (x+stripe_width-2, 400),
            (x-5, 480), (x+stripe_width-5, 480),
            (x+stripe_width+2, 400), (x+2, 400),
            (x+3, 300), (x+stripe_width+3, 300),
            (x+2, 200), (x+stripe_width+2, 200)
        ], fill=color, outline='#333333', width=1)
    
    # Ankle cuffs
    draw.ellipse([125, 480, 155, 495], fill='#333333', outline='#000000', width=2)
    draw.ellipse([245, 480, 275, 495], fill='#333333', outline='#000000', width=2)
    
    # Text on thigh
    draw.text((200, 250), "MEENAKSHI", anchor="mm", font=get_font(16), fill='#ffffff')
    draw.text((200, 270), "TEMPLE", anchor="mm", font=get_font(12), fill='#ffffff')
    
    img.save('static/images/meenakshi1.jpg', 'JPEG', quality=95)
    print("✓ Created meenakshi1.jpg - Colorful stripes on joggers")

def create_railways_backpack():
    """Indian Railways Heritage Backpack"""
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    backpack_color = '#5a5a3d'
    
    # Backpack body
    draw.rectangle([120, 150, 280, 450], fill=backpack_color, outline='#333333', width=3)
    
    # Rounded top
    draw.pieslice([120, 100, 280, 200], start=0, end=180, fill=backpack_color, outline='#333333', width=3)
    
    # Front pocket
    draw.rectangle([140, 180, 260, 280], fill='#4a4a2d', outline='#333333', width=2)
    draw.arc([140, 170, 260, 190], start=0, end=180, fill='#333333', width=2)
    
    # Zipper
    draw.line([(150, 180), (250, 180)], fill='#888888', width=3)
    draw.rectangle([198, 178, 202, 185], fill='#666666', outline='#000000', width=1)
    
    # Side pockets
    draw.ellipse([110, 250, 130, 320], fill='#4a4a2d', outline='#333333', width=2)
    draw.ellipse([270, 250, 290, 320], fill='#4a4a2d', outline='#333333', width=2)
    
    # Straps
    draw.rectangle([140, 120, 155, 470], fill='#333333', outline='#000000', width=1)
    draw.rectangle([245, 120, 260, 470], fill='#333333', outline='#000000', width=1)
    
    # Buckles
    for y in [140, 460]:
        draw.rectangle([140, y, 155, y+15], fill='#666666', outline='#000000', width=1)
        draw.rectangle([245, y, 260, y+15], fill='#666666', outline='#000000', width=1)
    
    # Indian Railways design on front
    center_x, center_y = 200, 340
    
    # Vintage patch look
    draw.rectangle([center_x-50, center_y-50, center_x+50, center_y+50], 
                   fill='#d4a574', outline='#8b4513', width=3)
    
    # Train icon
    draw.rectangle([center_x-20, center_y-15, center_x+20, center_y+5], 
                   fill='#2f4f4f', outline='#000000', width=2)
    draw.ellipse([center_x-25, center_y-20, center_x-15, center_y-10], 
                 fill='#696969', outline='#000000', width=1)
    # Wheels
    for wx in [-15, 0, 15]:
        draw.ellipse([center_x+wx-5, center_y+5, center_x+wx+5, center_y+15], 
                     fill='#2f4f4f', outline='#000000', width=1)
    
    # Text
    draw.text((center_x, center_y+28), "INDIAN", anchor="mm", 
              font=get_font(10), fill='#8b4513')
    draw.text((center_x, center_y+40), "RAILWAYS", anchor="mm", 
              font=get_font(10), fill='#8b4513')
    
    # Indian flag strip
    flag_y = 200
    draw.rectangle([150, flag_y, 250, flag_y+3], fill='#FF9933')
    draw.rectangle([150, flag_y+3, 250, flag_y+6], fill='#ffffff')
    draw.rectangle([150, flag_y+6, 250, flag_y+9], fill='#138808')
    
    img.save('static/images/railways1.jpg', 'JPEG', quality=95)
    print("✓ Created railways1.jpg - Vintage patch on olive backpack")

# Generate all realistic product mockups
if __name__ == '__main__':
    print("👕 Generating Realistic Indian Heritage Apparel Mockups...\n")
    
    create_tanjore_tshirt()
    create_isro_hoodie()
    create_gateway_bomber()
    create_hampi_linen_shirt()
    create_mysore_kurta()
    create_konark_scarf()
    create_lotus_sweatshirt()
    create_meenakshi_joggers()
    create_railways_backpack()
    
    print("\n✅ All 9 realistic apparel mockups created!")
    print("📁 Images saved to: static/images/")
    print("👕 Features: Actual clothing with designs on T-shirts, hoodies, jackets, etc.")
