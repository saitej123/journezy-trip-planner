from PIL import Image, ImageDraw, ImageFont

# Create a simple fallback image
img = Image.new('RGB', (400, 300), color='#f0f0f0')
draw = ImageDraw.Draw(img)

# Draw a border
draw.rectangle([(50, 50), (350, 250)], outline='#cccccc', width=2)

# Add text
try:
    # Try to use a default font
    font = ImageFont.truetype("arial.ttf", 36)
except:
    # Fallback to default font
    font = ImageFont.load_default()

# Calculate text position
text = "No Image Available"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (400 - text_width) // 2
y = (300 - text_height) // 2

draw.text((x, y), text, fill='#999999', font=font)

# Save the image
img.save('static/images/fallbacks/no-image.png')
print('✅ Created fallback image: static/images/fallbacks/no-image.png')
