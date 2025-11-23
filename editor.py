import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFilter, ImageFont
import io

SQUARE_SIZE = 15 
# The spacing between the squares
SPACING = 5
# The size of the header area (for row/column numbers)
HEADER_SIZE = 40
# Calculate the size of one block (square + spacing)
BLOCK_SIZE = SQUARE_SIZE + SPACING 

def build_new_image(grid_width, grid_height, pixels):
    grid_out_width = (grid_width * BLOCK_SIZE) + HEADER_SIZE
    grid_out_height = (grid_height * BLOCK_SIZE) + HEADER_SIZE

    new_img = Image.new('RGB', (grid_out_width, grid_out_height), color='white')
    draw = ImageDraw.Draw(new_img)

    # --- Set up Font for Headers ---
    # Try to use a common monospaced font, otherwise use the default Pillow font
    try:
        # Example font path (adjust as needed for your OS)
        font = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        font = ImageFont.load_default()
    
    # --- Draw the Pixel Grid and Headers ---

    # Draw the grid squares (the main part of the image)
    for row in range(grid_height):
        for col in range(grid_width):
            # Get the color of the original pixel at (col, row)
            color = pixels[col, row]
            
            # Calculate the top-left corner of the new 10x10 square
            # This accounts for the header size
            x0 = HEADER_SIZE + col * BLOCK_SIZE
            y0 = HEADER_SIZE + row * BLOCK_SIZE
            
            # Calculate the bottom-right corner
            x1 = x0 + SQUARE_SIZE
            y1 = y0 + SQUARE_SIZE
            print(color)
            # Draw the 10x10 square
            draw.rectangle([x0, y0, x1, y1], fill=color)

            # --- Draw Column Headers (Top) ---
            if row == 0:
                # Calculate the center x-position of the block
                header_x_center = x0 + SQUARE_SIZE / 2
                # Draw the column number (0 to 63) centered above the column
                draw.text((header_x_center, 10), str(col+1), fill='black', font=font, anchor="mm")

        # --- Draw Row Headers (Left) ---
        # Calculate the center y-position of the block
        header_y_center = HEADER_SIZE + row * BLOCK_SIZE + SQUARE_SIZE / 2
        # Draw the row number (0 to 63) centered to the left of the row
        draw.text((10, header_y_center), str(row+1), fill='black', font=font, anchor="mm")
    return new_img
            
def main():
    st.title("Advanced Image Editor")

    st.sidebar.write("## Upload Image")
    uploaded_file = st.sidebar.file_uploader("original", type=["jpg", "png", "jpeg", "tiff"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Uploaded Image", width="stretch")
        
        st.write("## Edited Image")

        # Rotation
        grid_width = st.sidebar.number_input(label="Grid Width", min_value=16, max_value=120, value=36)
        grid_height = st.sidebar.number_input(label="Grid Height", min_value=16, max_value=120, value=36)
        resized_img = image.resize((grid_width, grid_height), Image.Resampling.NEAREST)
        num_color = st.sidebar.number_input("Colors", min_value=4, max_value=256, value=8)
        quant_image = resized_img.quantize(colors=num_color)    
        pallete = quant_image.getpalette()
        quant_image = quant_image.convert(mode="RGB")
        pixel_data = quant_image.load()
        edited_image = build_new_image(grid_width, grid_height, pixel_data)
        st.image(edited_image, caption="Edited Image", width="stretch")

        # Download Button
        buffered = io.BytesIO()
        edited_image.save(buffered, format="PNG")
        img_str = buffered.getvalue()
        st.download_button(
            "Download Edited Image",
            img_str,
            file_name="edited_image.png",
            mime="image/png",
        )

if __name__ == "__main__":
    main()
