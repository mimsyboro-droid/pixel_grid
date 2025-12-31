import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Constants for grid styling
SQUARE_SIZE = 15 
SPACING = 5
HEADER_SIZE = 40
BLOCK_SIZE = SQUARE_SIZE + SPACING 

def build_new_image(grid_width, grid_height, pixel_data_img, custom_palette):
    # 1. Re-palletize using Pillow's quantize method
    palette_img = Image.new("P", (1, 1))
    flat_palette = []
    for color in custom_palette:
        flat_palette.extend(color)
    
    # Pad the palette to 768 values (256 colors * 3) as required by Pillow
    if len(flat_palette) < 768:
        flat_palette.extend([0] * (768 - len(flat_palette)))
    palette_img.putpalette(flat_palette)

    # Quantize the resized source image using our custom palette
    quantized_result = pixel_data_img.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
    pixels = quantized_result.load()

    # 2. Draw the grid
    grid_out_width = (grid_width * BLOCK_SIZE) + HEADER_SIZE
    grid_out_height = (grid_height * BLOCK_SIZE) + HEADER_SIZE

    new_img = Image.new('RGB', (grid_out_width, grid_out_height), color='white')
    draw = ImageDraw.Draw(new_img)

    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        font = ImageFont.load_default()
    
    for row in range(grid_height):
        header_y_center = HEADER_SIZE + row * BLOCK_SIZE + SQUARE_SIZE / 2
        draw.text((10, header_y_center), str(row+1), fill='black', font=font, anchor="mm")

        for col in range(grid_width):
            display_color = pixels[col, row]
            x0 = HEADER_SIZE + col * BLOCK_SIZE
            y0 = HEADER_SIZE + row * BLOCK_SIZE
            x1 = x0 + SQUARE_SIZE
            y1 = y0 + SQUARE_SIZE
            draw.rectangle([x0, y0, x1, y1], fill=display_color, outline=(220, 220, 220))

            if row == 0:
                header_x_center = x0 + SQUARE_SIZE / 2
                draw.text((header_x_center, 10), str(col+1), fill='black', font=font, anchor="mm")

    return new_img

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def main():
    st.set_page_config(layout="wide")
    st.title("Interactive Pixel Grid Art Generator")

    st.sidebar.header("1. Upload Image")
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "png", "jpeg", "tiff"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.sidebar.image(image, caption="Original Image", use_container_width=True)
        
        st.sidebar.header("2. Grid Settings")
        grid_width = st.sidebar.number_input("Grid Width", min_value=8, max_value=120, value=32)
        grid_height = st.sidebar.number_input("Grid Height", min_value=8, max_value=120, value=32)
        num_colors_req = st.sidebar.number_input("Target Colors", min_value=2, max_value=64, value=8)
        
        # Initial Processing: Resize
        resized_img = image.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
        
        # Get initial palette via quantization
        quant_source = resized_img.quantize(colors=num_colors_req).convert("RGB")
        initial_unique_colors = []
        q_pixels = quant_source.load()
        for y in range(grid_height):
            for x in range(grid_width):
                c = q_pixels[x, y]
                if c not in initial_unique_colors:
                    initial_unique_colors.append(c)
        
        # Ensure we have enough colors if quantization returned fewer
        while len(initial_unique_colors) < num_colors_req:
            initial_unique_colors.append((255, 255, 255))

        # --- Palette State Management ---
        st.write("### 3. Customize Your Palette")
        
        # Reset Logic
        if st.button("Reset Palette"):
            for i in range(64): # Clear potential keys
                if f"cp_{i}" in st.session_state:
                    del st.session_state[f"cp_{i}"]
            st.rerun()

        st.info("Modify colors below. The grid uses Pillow's quantization to map the original image to your custom palette.")
        
        cols = st.columns(8)
        current_palette = []
        
        for i in range(num_colors_req):
            col_idx = i % 8
            with cols[col_idx]:
                default_color = initial_unique_colors[i]
                hex_val = rgb_to_hex(default_color)
                
                # The color_picker will use the session state value if it exists, 
                # otherwise it uses 'value'. Deleting from session state triggers a reset.
                new_hex = st.color_picker(f"Color {i+1}", value=hex_val, key=f"cp_{i}")
                current_palette.append(hex_to_rgb(new_hex))
        
        st.write("---")
        st.write("### 4. Final Grid Design")
        
        final_grid = build_new_image(grid_width, grid_height, resized_img, current_palette)
        st.image(final_grid, caption="Quantized Pixel Grid", use_container_width=True)

        buffered = io.BytesIO()
        final_grid.save(buffered, format="PNG")
        st.download_button(
            label="Download Final Design",
            data=buffered.getvalue(),
            file_name="quantized_pixel_design.png",
            mime="image/png",
        )
    else:
        st.info("Please upload an image in the sidebar to begin.")

if __name__ == "__main__":
    main()
