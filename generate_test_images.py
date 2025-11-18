"""Generate test images for the API"""
from PIL import Image, ImageDraw, ImageFont
import random

def create_character_image(filename, color, shape, size=(512, 512)):
    """Create a simple character image with a shape"""
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)

    center_x, center_y = size[0] // 2, size[1] // 2

    if shape == 'circle':
        # Draw a character-like circle with features
        # Body
        draw.ellipse([center_x-100, center_y-100, center_x+100, center_y+100], fill=color)
        # Eyes
        draw.ellipse([center_x-40, center_y-40, center_x-20, center_y-20], fill='black')
        draw.ellipse([center_x+20, center_y-40, center_x+40, center_y-20], fill='black')
        # Mouth
        draw.arc([center_x-50, center_y-10, center_x+50, center_y+50], 0, 180, fill='black', width=3)
    elif shape == 'square':
        # Draw a character-like square with features
        # Body
        draw.rectangle([center_x-100, center_y-100, center_x+100, center_y+100], fill=color)
        # Eyes
        draw.rectangle([center_x-40, center_y-40, center_x-20, center_y-20], fill='black')
        draw.rectangle([center_x+20, center_y-40, center_x+40, center_y-20], fill='black')
        # Mouth
        draw.rectangle([center_x-40, center_y+20, center_x+40, center_y+30], fill='black')

    img.save(filename)
    print(f"Created {filename}")

def create_style_image(filename, palette, pattern, size=(512, 512)):
    """Create an image with a specific style"""
    img = Image.new('RGB', size, color=palette[0])
    draw = ImageDraw.Draw(img)

    if pattern == 'stripes':
        # Vertical stripes
        stripe_width = 40
        for i in range(0, size[0], stripe_width * 2):
            draw.rectangle([i, 0, i + stripe_width, size[1]], fill=palette[1])
    elif pattern == 'dots':
        # Polka dots
        dot_spacing = 60
        dot_radius = 20
        for x in range(dot_spacing, size[0], dot_spacing):
            for y in range(dot_spacing, size[1], dot_spacing):
                draw.ellipse([x-dot_radius, y-dot_radius, x+dot_radius, y+dot_radius], fill=palette[1])
    elif pattern == 'gradient':
        # Simple gradient effect with rectangles
        for i in range(size[1]):
            ratio = i / size[1]
            r = int(palette[0][0] * (1-ratio) + palette[1][0] * ratio)
            g = int(palette[0][1] * (1-ratio) + palette[1][1] * ratio)
            b = int(palette[0][2] * (1-ratio) + palette[1][2] * ratio)
            draw.line([(0, i), (size[0], i)], fill=(r, g, b))

    img.save(filename)
    print(f"Created {filename}")

# Create character test images
print("Creating character test images...")
# Same character, different colors (should match on character, not exact appearance)
create_character_image('test_images/character1_blue.jpg', color='blue', shape='circle')
create_character_image('test_images/character1_red.jpg', color='red', shape='circle')
create_character_image('test_images/character2_green.jpg', color='green', shape='square')

# Create style test images
print("\nCreating style test images...")
# Similar style (blue/navy palette with stripes)
create_style_image('test_images/style1_blue_stripes.jpg', palette=[(30, 60, 120), (100, 150, 200)], pattern='stripes')
create_style_image('test_images/style1_blue_stripes2.jpg', palette=[(40, 70, 130), (90, 140, 190)], pattern='stripes')
# Different style (warm colors with dots)
create_style_image('test_images/style2_warm_dots.jpg', palette=[(200, 100, 50), (250, 200, 100)], pattern='dots')
# Different style (gradient)
create_style_image('test_images/style3_gradient.jpg', palette=[(150, 50, 150), (250, 150, 200)], pattern='gradient')

print("\nTest images created successfully!")
