from PIL import Image, ImageDraw

# Create a new image with a white background
img = Image.new('RGB', (256, 256), color='white')
d = ImageDraw.Draw(img)

# Draw a simple icon (you can modify this to create your own design)
d.ellipse([(20, 20), (236, 236)], fill='orange', outline='black', width=2)

# Save as ICO
img.save('icon.ico', format='ICO')