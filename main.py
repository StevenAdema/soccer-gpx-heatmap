from PIL import Image, ImageEnhance
import gpxpy
import seaborn as sns
import matplotlib.pyplot as plt

def generate_soccer_heatmap(
    gpx_file_path, pitch_image_path, cmap, thresh, levels, alpha, adjust, rotation, resize_factor, x_offset, y_offset, vignette, output_file
):
    '''Generate a soccer heatmap overlay on a pitch image from GPX data.
    Args:
        gpx_file_path (str): Path to the GPX file containing GPS data.
        pitch_image_path (str): Path to the soccer pitch image.
        cmap (str): Colormap for the heatmap.
        thresh (float): Threshold for KDE plot.
        levels (int): Number of contour levels in the heatmap.
        alpha (float): Transparency level for the heatmap.
        adjust (float): Bandwidth adjustment for KDE.
        rotation (int): Rotation angle for the heatmap image.
        resize_factor (float): Factor to resize the heatmap image.
        x_offset (int): Horizontal offset for the heatmap overlay.
        y_offset (int): Vertical offset for the heatmap overlay.
        vignette (bool): Whether to apply a vignette effect.
        output_file (str): Path to save the final composite image.
    Returns:
        None
        Saves
    '''
    # Parse GPX file
    gpx_file = open(gpx_file_path, 'r')
    gpx = gpxpy.parse(gpx_file)
    lat, lon = [], []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lat.append(point.latitude)
                lon.append(point.longitude)

    # Create heatmap
    sns.set(style="white")
    plt.figure(figsize=(10, 10))
    sns.kdeplot(x=lon, y=lat, fill=True, cmap=cmap, thresh=thresh, levels=levels, alpha=alpha, bw_adjust=adjust)
    plt.axis('off')
    heatmap_path = 'img/temp_heatmap.png'
    plt.savefig(heatmap_path, dpi=300, pad_inches=0, transparent=True)
    plt.close()

    # Load images
    pitch_img = Image.open(pitch_image_path)
    heatmap_img = Image.open(heatmap_path)

    # Resize and rotate heatmap
    heatmap_img = heatmap_img.resize(pitch_img.size, Image.Resampling.LANCZOS)
    heatmap_img = heatmap_img.rotate(rotation, expand=True)
    heatmap_img = heatmap_img.resize((int(pitch_img.width * resize_factor), int(pitch_img.height * resize_factor)), Image.Resampling.LANCZOS)

    # Combine images
    combined_img = Image.new('RGBA', pitch_img.size)
    combined_img.paste(pitch_img, (0, 0))
    combined_img.paste(heatmap_img, (x_offset, y_offset), heatmap_img.convert('RGBA').split()[-1])

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(combined_img)
    combined_img = enhancer.enhance(1.4)

    # Add a slight vignetting effect
    if vignette:
        vignette = Image.new('L', combined_img.size, 0)
        for x in range(combined_img.width):
            for y in range(combined_img.height):
                distance = ((x - combined_img.width / 2) ** 2 + (y - combined_img.height / 2) ** 2) ** 0.35
                vignette.putpixel((x, y), int(255 * (1 - distance / (combined_img.width / 2))))
        vignette = vignette.resize(combined_img.size, Image.Resampling.LANCZOS)
        combined_img.putalpha(vignette)

    # Save final image
    combined_img.save(output_file)
    print(f"Image saved to {output_file}")

# Example usage: traditional heatmap
generate_soccer_heatmap(
    gpx_file_path='data/soccer.gpx',
    pitch_image_path='img/pitch.png',
    cmap='RdYlGn_r',  # cmaps I like:  rainbow, CMRmap, RdYlBu_r, RdYlGn_r
    thresh=0.02,
    levels=10,
    alpha=0.8,
    adjust=0.4,
    rotation=-50,
    resize_factor=1.3,
    x_offset=-80,
    y_offset=-170,
    vignette=True,
    output_file='soccer_heatmap_traditional.png'
)

# Example usage: smooth
generate_soccer_heatmap(
    gpx_file_path='data/soccer.gpx',
    pitch_image_path='img/pitch.png',
    cmap='RdYlBu_r',  # cmaps I like:  rainbow, CMRmap, RdYlBu_r, RdYlGn_r
    thresh=0.005,
    levels=100,
    alpha=0.6,
    adjust=1,
    rotation=-50,
    resize_factor=1.3,
    x_offset=-80,
    y_offset=-170,
    vignette=True,
    output_file='soccer_heatmap_rainbow.png'
)