import gpxpy
import matplotlib.pyplot as plt
import folium
from folium.raster_layers import ImageOverlay
import seaborn as sns
from selenium import webdriver  # Correct import for Selenium WebDriver
import time
from PIL import Image, ImageEnhance  # Ensure this import is present

#### WIP for overlaying a heatmap on a Google Earth tilted soccer pitch screenshot ####

# Parse GPX file
gpx_file = open('soccer.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

lat = []
lon = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            lat.append(point.latitude)
            lon.append(point.longitude)

# Generate a seaborn-style heatmap and save as PNG with transparent background
sns.set(style="white")  # Use a clean style for better visual appeal
sns.despine(bottom=True, left=True)
plt.figure(figsize=(10, 10))  # Increase figure size for better resolution

# Adjust `thresh` to remove low-density areas (background)
sns.kdeplot(x=lon, y=lat, fill=True, cmap='RdYlGn_r', thresh=0.001, levels=10, alpha=0.7, bw_adjust=0.9)
# cmaps I like:  rainbow, CMRmap, RdYlBu_r, RdYlGn_r

plt.axis('off')  # Remove axes for a clean look
plt.savefig('soccer_heatmap_seaborn.png', dpi=300, pad_inches=0, transparent=True)
plt.close()

# Load the soccer pitch diagram
pitch_diagram_path = 'p_tilt-2.png'  # Replace with the path to your soccer pitch diagram
pitch_img = Image.open(pitch_diagram_path)

# Load the heatmap image
heatmap_path = 'soccer_heatmap_seaborn.png'
heatmap_img = Image.open(heatmap_path)

# Resize the heatmap to match the pitch dimensions using LANCZOS resampling
heatmap_img = heatmap_img.resize(pitch_img.size, Image.Resampling.LANCZOS)

# Rotate the heatmap image 30 degrees before creating the composite image
heatmap_img = heatmap_img.rotate(-20, expand=True)

# tilt the heatmap image 30 degrees


# Resize the rotated heatmap again to match the pitch dimensions
heatmap_img = heatmap_img.resize(pitch_img.size, Image.Resampling.LANCZOS)

# Ensure both images have the same size
# if pitch_img.size != heatmap_img.size:
#     print(f"Resizing pitch image to match heatmap dimensions: {heatmap_img.size}")
#     pitch_img = pitch_img.resize(heatmap_img.size, Image.Resampling.LANCZOS)

# Increase the size of pitch image by %
heatmap_img = heatmap_img.resize((int(pitch_img.width * 1), int(pitch_img.height * 0.8)), Image.Resampling.LANCZOS)

# increase vibrance
enhancer = ImageEnhance.Color(pitch_img)
pitch_img = enhancer.enhance(1.2)  # Adjust the factor as needed (1.0 is original, >1.0 increases color saturation)

# Overlay the heatmap on the pitch diagram with the heatmap on top with 50% opacity
combined_img = Image.new('RGBA', pitch_img.size)
combined_img.paste(pitch_img, (0, 0))
combined_img.paste(heatmap_img, (20, 30), heatmap_img.convert('RGBA').split()[-1])  # Use alpha channel for transparency

#enhance the contrast of the combined image
enhancer = ImageEnhance.Contrast(combined_img)
combined_img = enhancer.enhance(1.2)  # Adjust the factor as needed (1.0 is original, >1.0 increases contrast)
# decrease highlights
enhancer = ImageEnhance.Brightness(combined_img)
combined_img = enhancer.enhance(0.9)  # Adjust the factor as needed (1.0 is original, <1.0 decreases brightness)


# Save the combined image
combined_img_path = 'heatmap_tilt.png'
combined_img.save(combined_img_path)
print(f"Combined image saved to {combined_img_path}")