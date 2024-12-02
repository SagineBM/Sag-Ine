from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 256x256 image with transparency
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Define colors
    dark_blue = (26, 35, 126, 255)  # Dark blue
    light_blue = (48, 63, 159, 255)  # Light blue
    
    # Draw circular background
    padding = 10
    draw.ellipse([padding, padding, size-padding, size-padding], fill=dark_blue)
    
    # Draw the "S" and "I" letters
    try:
        # Try to use a modern font, fall back to default if not available
        font_size = 120
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Draw "S"
    draw.text((size//4, size//4), "S", fill=light_blue, font=font)
    # Draw "I"
    draw.text((size//2, size//4), "I", fill=light_blue, font=font)
    
    # Save in different sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Create icons directory if it doesn't exist
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # Save the main icon
    image.save('icons/sag_ine.png')
    
    # Save ICO file with multiple sizes
    icons = []
    for size in icon_sizes:
        icons.append(image.resize(size, Image.Resampling.LANCZOS))
    
    # Save as ICO file
    icons[0].save('icons/sag_ine.ico', format='ICO', sizes=[(x, x) for x in [16, 32, 48, 64, 128, 256]], append_images=icons[1:])
    
    return 'icons/sag_ine.ico'

if __name__ == "__main__":
    create_icon()
