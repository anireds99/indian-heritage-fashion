from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor, ImageEnhance
import os
import math
import random

# Create mockups directory
os.makedirs('static/images/mockups', exist_ok=True)
os.makedirs('static/images/mockup_templates', exist_ok=True)

WIDTH, HEIGHT = 1400, 1600  # Increased resolution for better quality

def get_font(size):
    """Get font with fallback"""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
        except:
            return ImageFont.load_default()

def create_premium_fabric_texture(width, height, base_color):
    """Create ultra-realistic premium fabric texture with fine weave pattern"""
    img = Image.new('RGB', (width, height), base_color)
    pixels = img.load()
    
    r_base, g_base, b_base = ImageColor.getrgb(base_color)
    
    # Create fine fabric weave with multiple layers
    for i in range(width):
        for j in range(height):
            # Micro weave pattern
            weave1 = math.sin(i * 0.3) * math.cos(j * 0.3) * 2
            weave2 = math.sin(i * 0.8) * math.cos(j * 0.8) * 1.5
            # Fabric grain texture
            grain = (math.sin(i * 0.1) + math.cos(j * 0.1)) * 1.5
            # Random fiber variation
            noise = random.randint(-5, 5)
            
            variation = weave1 + weave2 + grain + noise
            
            pixels[i, j] = (
                max(0, min(255, r_base + int(variation))),
                max(0, min(255, g_base + int(variation))),
                max(0, min(255, b_base + int(variation)))
            )
    
    # Apply subtle blur for soft cotton/fleece texture
    img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
    
    # Enhance contrast slightly for depth
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)
    
    return img

def add_realistic_fabric_folds(img, garment_area):
    """Add professional fabric folds and natural wrinkles"""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Convert float coordinates to integers
    garment_area = [int(x) for x in garment_area]
    
    # Add natural vertical folds
    for x in range(garment_area[0] + 50, garment_area[2] - 50, 60):
        offset = random.randint(-15, 15)
        points = []
        for y in range(garment_area[1], garment_area[3], 40):
            wave = math.sin(y * 0.02) * 8
            points.append((x + offset + int(wave) + random.randint(-3, 3), y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=(0, 0, 0, 8), width=3)
    
    # Add horizontal stress lines around shoulders
    for y in range(garment_area[1], garment_area[1] + 150, 25):
        points = []
        for x in range(garment_area[0], garment_area[2], 30):
            points.append((x + random.randint(-5, 5), y + random.randint(-3, 3)))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=(0, 0, 0, 4), width=2)
    
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=4))
    return overlay

def create_studio_background_premium(width, height):
    """Create professional photography studio background with soft lighting"""
    img = Image.new('RGB', (width, height), 'white')
    pixels = img.load()
    
    # Create soft radial gradient
    center_x, center_y = width // 2, height // 3
    max_radius = math.sqrt(width**2 + height**2)
    
    for y in range(height):
        for x in range(width):
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            ratio = distance / max_radius
            
            # Very subtle gradient for professional look
            brightness = int(250 - (ratio * 35))
            brightness = max(230, min(255, brightness))
            
            # Slight warm tone for natural look
            pixels[x, y] = (brightness, brightness, min(255, brightness + 2))
    
    # Apply very subtle noise for texture
    for _ in range(width * height // 100):
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        current = pixels[x, y]
        variation = random.randint(-3, 3)
        pixels[x, y] = tuple(max(0, min(255, c + variation)) for c in current)
    
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img

def add_drop_shadow(img, garment_area, intensity=40):
    """Add realistic drop shadow beneath garment"""
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    
    # Shadow at bottom of garment
    shadow_y = garment_area[3] - 50
    shadow_width = (garment_area[2] - garment_area[0]) * 0.7
    shadow_center = (garment_area[0] + garment_area[2]) // 2
    
    # Draw elliptical shadow
    draw.ellipse([
        shadow_center - shadow_width // 2, shadow_y - 20,
        shadow_center + shadow_width // 2, shadow_y + 30
    ], fill=(0, 0, 0, intensity))
    
    # Blur for soft shadow
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=25))
    return shadow

def draw_realistic_tshirt_with_shadows(draw, img, center_x, center_y, color, width=550, height=650):
    """Draw photorealistic t-shirt with professional lighting and shadows"""
    
    # Create garment layer
    garment = Image.new('RGBA', img.size, (0, 0, 0, 0))
    garment_draw = ImageDraw.Draw(garment)
    
    # Main body with natural shape
    body_points = [
        (center_x - width//2, center_y - height//2.3),
        (center_x - width//2 + 60, center_y - height//2.1),
        (center_x + width//2 - 60, center_y - height//2.1),
        (center_x + width//2, center_y - height//2.3),
        (center_x + width//2 - 40, center_y + height//2),
        (center_x - width//2 + 40, center_y + height//2),
    ]
    garment_draw.polygon(body_points, fill=color)
    
    # Draw sleeves with proper depth
    sleeve_color = tuple(max(0, c - 10) for c in ImageColor.getrgb(color))
    
    left_sleeve = [
        (center_x - width//2, center_y - height//2.3),
        (center_x - width//2 - 90, center_y - height//2.3 + 90),
        (center_x - width//2 - 70, center_y - height//2.3 + 160),
        (center_x - width//2 + 40, center_y - height//2.3 + 120),
    ]
    garment_draw.polygon(left_sleeve, fill=sleeve_color)
    
    right_sleeve = [
        (center_x + width//2, center_y - height//2.3),
        (center_x + width//2 + 90, center_y - height//2.3 + 90),
        (center_x + width//2 + 70, center_y - height//2.3 + 160),
        (center_x + width//2 - 40, center_y - height//2.3 + 120),
    ]
    garment_draw.polygon(right_sleeve, fill=sleeve_color)
    
    # Collar/neck opening
    neck_color = tuple(max(0, c - 35) for c in ImageColor.getrgb(color))
    garment_draw.ellipse([center_x - 65, center_y - height//2.1 - 45,
                          center_x + 65, center_y - height//2.1 + 15],
                         fill=neck_color)
    
    # Collar rim
    garment_draw.arc([center_x - 65, center_y - height//2.1 - 45,
                      center_x + 65, center_y - height//2.1 + 15],
                     30, 150, fill=tuple(max(0, c - 15) for c in ImageColor.getrgb(color)), width=3)
    
    img.paste(garment, (0, 0), garment)
    
    # Add professional lighting - left shadow
    shadow_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_overlay)
    shadow_draw.polygon([
        (center_x - width//2, center_y - height//2.3),
        (center_x - width//6, center_y - height//2.3),
        (center_x - width//6, center_y + height//2),
        (center_x - width//2 + 40, center_y + height//2),
    ], fill=(0, 0, 0, 40))
    shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(radius=45))
    img.paste(shadow_overlay, (0, 0), shadow_overlay)
    
    # Add highlights - right side
    highlight_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    highlight_draw = ImageDraw.Draw(highlight_overlay)
    highlight_draw.polygon([
        (center_x + width//6, center_y - height//2.3),
        (center_x + width//2, center_y - height//2.3),
        (center_x + width//2 - 40, center_y + height//2),
        (center_x + width//6, center_y + height//2),
    ], fill=(255, 255, 255, 35))
    highlight_overlay = highlight_overlay.filter(ImageFilter.GaussianBlur(radius=45))
    img.paste(highlight_overlay, (0, 0), highlight_overlay)
    
    # Add fabric folds
    folds = add_realistic_fabric_folds(img, [center_x - width//2, center_y - height//2.3,
                                              center_x + width//2, center_y + height//2])
    img.paste(folds, (0, 0), folds)
    
    # Add drop shadow
    drop_shadow = add_drop_shadow(img, [center_x - width//2, center_y - height//2.3,
                                         center_x + width//2, center_y + height//2], intensity=35)
    img.paste(drop_shadow, (0, 0), drop_shadow)
    
    return (center_x - width//3.2, center_y - height//4.5)

def draw_realistic_hoodie_with_shadows(draw, img, center_x, center_y, color, width=600, height=700):
    """Draw photorealistic hoodie inspired by the reference image - with hood, drawstrings, and premium details"""
    
    # Create garment layer
    garment = Image.new('RGBA', img.size, (0, 0, 0, 0))
    garment_draw = ImageDraw.Draw(garment)
    
    # Main hoodie body with natural drape
    body_points = [
        (center_x - width//2, center_y - height//2.4),
        (center_x + width//2, center_y - height//2.4),
        (center_x + width//2 - 30, center_y + height//2),
        (center_x - width//2 + 30, center_y + height//2),
    ]
    garment_draw.polygon(body_points, fill=color)
    
    # Draw hood with realistic depth and layers
    hood_outer = [
        (center_x - 110, center_y - height//2.4),
        (center_x - 85, center_y - height//2.4 - 110),
        (center_x - 30, center_y - height//2.4 - 135),
        (center_x + 30, center_y - height//2.4 - 135),
        (center_x + 85, center_y - height//2.4 - 110),
        (center_x + 110, center_y - height//2.4),
    ]
    garment_draw.polygon(hood_outer, fill=color)
    
    # Hood inner shadow for depth
    hood_shadow_color = tuple(max(0, c - 50) for c in ImageColor.getrgb(color))
    hood_inner = [
        (center_x - 80, center_y - height//2.4),
        (center_x - 60, center_y - height//2.4 - 80),
        (center_x - 20, center_y - height//2.4 - 95),
        (center_x + 20, center_y - height//2.4 - 95),
        (center_x + 60, center_y - height//2.4 - 80),
        (center_x + 80, center_y - height//2.4),
    ]
    garment_draw.polygon(hood_inner, fill=hood_shadow_color)
    
    # Hood rim/edge
    hood_rim = tuple(max(0, c - 20) for c in ImageColor.getrgb(color))
    garment_draw.arc([center_x - 85, center_y - height//2.4 - 110,
                      center_x + 85, center_y - height//2.4 + 20],
                     150, 390, fill=hood_rim, width=4)
    
    # Draw sleeves with natural folds
    sleeve_color = tuple(max(0, c - 8) for c in ImageColor.getrgb(color))
    
    left_sleeve = [
        (center_x - width//2, center_y - height//2.4),
        (center_x - width//2 - 110, center_y - height//2.4 + 110),
        (center_x - width//2 - 80, center_y - height//2.4 + 240),
        (center_x - width//2 + 35, center_y - height//2.4 + 200),
    ]
    garment_draw.polygon(left_sleeve, fill=sleeve_color)
    
    right_sleeve = [
        (center_x + width//2, center_y - height//2.4),
        (center_x + width//2 + 110, center_y - height//2.4 + 110),
        (center_x + width//2 + 80, center_y - height//2.4 + 240),
        (center_x + width//2 - 35, center_y - height//2.4 + 200),
    ]
    garment_draw.polygon(right_sleeve, fill=sleeve_color)
    
    # Kangaroo pocket with realistic depth
    pocket_color = tuple(max(0, c - 30) for c in ImageColor.getrgb(color))
    pocket_rect = [center_x - 140, center_y - 80, center_x + 140, center_y + 100]
    garment_draw.rounded_rectangle(pocket_rect, radius=25, fill=pocket_color)
    
    # Pocket opening with shadow
    pocket_shadow = tuple(max(0, c - 60) for c in ImageColor.getrgb(color))
    garment_draw.rounded_rectangle([center_x - 130, center_y - 70, center_x + 130, center_y - 50],
                                   radius=5, fill=pocket_shadow)
    
    # Pocket stitching details
    stitch_color = tuple(max(0, c - 40) for c in ImageColor.getrgb(color))
    garment_draw.rounded_rectangle([center_x - 140, center_y - 80, center_x + 140, center_y + 100],
                                   radius=25, outline=stitch_color, width=2)
    
    # Drawstrings with aglets (metal tips)
    drawstring_y = center_y - height//2.4 - 5
    
    # Left drawstring
    garment_draw.ellipse([center_x - 45, drawstring_y - 15,
                          center_x - 28, drawstring_y],
                         fill='#EEEEEE')
    garment_draw.line([center_x - 36, drawstring_y, center_x - 40, drawstring_y + 70],
                      fill='#DDDDDD', width=5)
    # Aglet (metal tip)
    garment_draw.ellipse([center_x - 43, drawstring_y + 70,
                          center_x - 37, drawstring_y + 85],
                         fill='#999999')
    
    # Right drawstring
    garment_draw.ellipse([center_x + 28, drawstring_y - 15,
                          center_x + 45, drawstring_y],
                         fill='#EEEEEE')
    garment_draw.line([center_x + 36, drawstring_y, center_x + 40, drawstring_y + 70],
                      fill='#DDDDDD', width=5)
    # Aglet
    garment_draw.ellipse([center_x + 37, drawstring_y + 70,
                          center_x + 43, drawstring_y + 85],
                         fill='#999999')
    
    # Ribbed cuffs and hem (bottom band)
    rib_color = tuple(max(0, c - 18) for c in ImageColor.getrgb(color))
    garment_draw.rectangle([center_x - width//2 + 30, center_y + height//2 - 40,
                           center_x + width//2 - 30, center_y + height//2],
                          fill=rib_color)
    
    # Ribbed texture on cuffs
    for i in range(5):
        y_pos = center_y + height//2 - 35 + (i * 15)
        garment_draw.line([center_x - width//2 + 35, y_pos,
                          center_x + width//2 - 35, y_pos],
                         fill=tuple(max(0, c - 25) for c in ImageColor.getrgb(color)), width=1)
    
    img.paste(garment, (0, 0), garment)
    
    # Professional studio lighting - left side shadow
    shadow_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_overlay)
    shadow_draw.polygon([
        (center_x - width//2, center_y - height//2.4),
        (center_x - width//5, center_y - height//2.4),
        (center_x - width//5, center_y + height//2),
        (center_x - width//2 + 30, center_y + height//2),
    ], fill=(0, 0, 0, 45))
    shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(radius=55))
    img.paste(shadow_overlay, (0, 0), shadow_overlay)
    
    # Highlight - right side
    highlight_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    highlight_draw = ImageDraw.Draw(highlight_overlay)
    highlight_draw.polygon([
        (center_x + width//5, center_y - height//2.4),
        (center_x + width//2, center_y - height//2.4),
        (center_x + width//2 - 30, center_y + height//2),
        (center_x + width//5, center_y + height//2),
    ], fill=(255, 255, 255, 40))
    highlight_overlay = highlight_overlay.filter(ImageFilter.GaussianBlur(radius=55))
    img.paste(highlight_overlay, (0, 0), highlight_overlay)
    
    # Add natural fabric folds
    folds = add_realistic_fabric_folds(img, [center_x - width//2, center_y - height//2.4,
                                              center_x + width//2, center_y + height//2])
    img.paste(folds, (0, 0), folds)
    
    # Add drop shadow
    drop_shadow = add_drop_shadow(img, [center_x - width//2, center_y - height//2.4,
                                         center_x + width//2, center_y + height//2], intensity=45)
    img.paste(drop_shadow, (0, 0), drop_shadow)
    
    return (center_x - width//3.8, center_y - height//6)

def apply_design_to_garment(img, design, position, size, curvature=0.03):
    """Apply design with realistic perspective, curvature, and fabric integration"""
    design_resized = design.resize(size, Image.Resampling.LANCZOS)
    
    # Create design with subtle curvature
    curved_design = Image.new('RGBA', design_resized.size, (0, 0, 0, 0))
    
    for y in range(design_resized.height):
        progress = y / design_resized.height
        # Subtle barrel distortion for fabric curvature
        curve_offset = int(math.sin(progress * math.pi) * size[0] * curvature)
        
        for x in range(design_resized.width):
            try:
                pixel = design_resized.getpixel((x, y))
                if pixel[3] > 0:  # Not transparent
                    # Slight lighting variation to match fabric
                    light_factor = 1.0 + (math.sin(progress * math.pi) * 0.08)
                    new_pixel = (
                        int(min(255, pixel[0] * light_factor)),
                        int(min(255, pixel[1] * light_factor)),
                        int(min(255, pixel[2] * light_factor)),
                        pixel[3]
                    )
                    curved_design.putpixel((x, y), new_pixel)
            except:
                pass
    
    # Subtle edge blur for print integration
    curved_design = curved_design.filter(ImageFilter.GaussianBlur(radius=0.2))
    
    # Apply design to garment
    img.paste(curved_design, position, curved_design)
    
    return img

def add_floor_shadow(img):
    """Add realistic floor/surface shadow"""
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    
    # Elliptical shadow at bottom
    shadow_rect = [WIDTH // 4, HEIGHT - 200, WIDTH * 3 // 4, HEIGHT - 50]
    draw.ellipse(shadow_rect, fill=(0, 0, 0, 25))
    
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(shadow, (0, 0), shadow)
    
    return img

def create_professional_mockup(design_path, output_path, product_type='tshirt', garment_color='#ffffff'):
    """
    Create ultra-realistic product mockup with studio lighting
    """
    print(f"  🎨 Rendering {product_type} in {garment_color}...")
    
    # Create professional studio background
    img = create_studio_background_premium(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Load design
    try:
        design = Image.open(design_path).convert('RGBA')
    except Exception as e:
        print(f"  ❌ Error loading design: {e}")
        return
    
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # Draw garment based on type
    if product_type == 'hoodie':
        design_position = draw_realistic_hoodie_with_shadows(draw, img, center_x, center_y, garment_color)
        design_size = (400, 400)
    else:  # tshirt
        design_position = draw_realistic_tshirt_with_shadows(draw, img, center_x, center_y, garment_color)
        design_size = (380, 380)
    
    # Apply design to garment with realism
    img = apply_design_to_garment(img, design, design_position, design_size, curvature=0.03)
    
    # Add floor shadow
    img = add_floor_shadow(img)
    
    # Add subtle vignette
    vignette = Image.new('RGBA', img.size, (0, 0, 0, 0))
    vignette_draw = ImageDraw.Draw(vignette)
    for i in range(80):
        alpha = int((i / 80) ** 2 * 40)
        vignette_draw.rectangle([i, i, WIDTH - i, HEIGHT - i], outline=(0, 0, 0, alpha))
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=50))
    img.paste(vignette, (0, 0), vignette)
    
    # Final image enhancements
    img = img.convert('RGB')
    
    # Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.08)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.15)
    
    # Subtle color enhancement
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.05)
    
    # Save high-quality output
    img.save(output_path, 'JPEG', quality=95, optimize=True)
    print(f"  ✅ Saved: {output_path}")

def generate_all_mockups():
    """Generate realistic mockups for all designs"""
    
    products = [
        {
            'name': 'Tanjore Temple',
            'design': 'static/images/tanjore1.jpg',
            'garment': 'tshirt',
            'color': '#F5F5DC'  # Beige
        },
        {
            'name': 'ISRO Space',
            'design': 'static/images/isro1.jpg',
            'garment': 'hoodie',
            'color': '#1a1a2e'  # Dark navy
        },
        {
            'name': 'Gateway of India',
            'design': 'static/images/gateway1.jpg',
            'garment': 'tshirt',
            'color': '#E8DCC4'  # Sand
        },
        {
            'name': 'Hampi Ruins',
            'design': 'static/images/hampi1.jpg',
            'garment': 'tshirt',
            'color': '#E8998D'  # Terracotta
        },
        {
            'name': 'Mysore Palace',
            'design': 'static/images/mysore1.jpg',
            'garment': 'tshirt',
            'color': '#FFF8DC'  # Cream
        },
        {
            'name': 'Konark Sun Temple',
            'design': 'static/images/konark1.jpg',
            'garment': 'tshirt',
            'color': '#D2B48C'  # Tan
        },
        {
            'name': 'Lotus Temple',
            'design': 'static/images/lotus1.jpg',
            'garment': 'hoodie',
            'color': '#FFFFFF'  # White
        },
        {
            'name': 'Meenakshi Temple',
            'design': 'static/images/meenakshi1.jpg',
            'garment': 'tshirt',
            'color': '#FFD700'  # Gold
        },
        {
            'name': 'Indian Railways',
            'design': 'static/images/railways1.jpg',
            'garment': 'hoodie',
            'color': '#8B4513'  # Saddle Brown
        }
    ]
    
    print("\n" + "=" * 60)
    print("🎨 GENERATING ULTRA-REALISTIC PRODUCT MOCKUPS")
    print("=" * 60)
    
    for i, product in enumerate(products, 1):
        output_filename = f"{product['name'].lower().replace(' ', '_')}_{product['garment']}.jpg"
        output_path = f"static/images/mockups/{output_filename}"
        
        print(f"\n[{i}/{len(products)}] {product['name']} ({product['garment'].upper()})")
        
        if os.path.exists(product['design']):
            create_professional_mockup(
                product['design'],
                output_path,
                product['garment'],
                product['color']
            )
        else:
            print(f"  ❌ Design not found: {product['design']}")
    
    print("\n" + "=" * 60)
    print("✨ All mockups generated successfully!")
    print(f"📁 Location: static/images/mockups/")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    generate_all_mockups()
