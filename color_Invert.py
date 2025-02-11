import fitz  # PyMuPDF
from PIL import Image, ImageOps
import os
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from collections import Counter
import shutil


# image_list = []




# Get pdf files from the folder
def get_pdf_files(folder_path):
    pdf_files = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(folder_path, file_name))
    return pdf_files




# Finding dominant colour
def get_dominant_color(image):

    # colors = list(image.getdata())

    # # Count the occurrences of each color
    # color_counts = Counter(colors)

    # # Get the most common color (dominant color)
    # dominant_color = color_counts.most_common(1)[0][0]

    dominant_color = sum(image.getdata()) // len(image.getdata())

    return dominant_color

# inverting black pixels to white
def invert_colors(input_path, output_path, page):
    original_image = Image.open(input_path)

    # Convert the image to grayscale (black and white)
    black_white_image = ImageOps.grayscale(original_image)

    autocon_image = ImageOps.autocontrast(black_white_image, cutoff=0, preserve_tone=False) ## need to change values here

    # Detect the most dominant color in the black and white version of the image
    dominant_color_before = get_dominant_color(black_white_image)
    dominant_color_after = get_dominant_color(autocon_image)

    print(f"Page:{page} : {dominant_color_before} ==> {dominant_color_after}")

    # If the most dominant color is white, do not invert the colors
    if dominant_color_after > 200:            # 255 white
        print("Colors will not be inverted.\n")
        # Save the original black and white image
        autocon_image.save(output_path)
    else:
        # Invert the colors of the black and white image
        inverted_image = ImageOps.invert(autocon_image)

        dominant_color_inv = get_dominant_color(inverted_image)
        
        # Save the inverted image
        inverted_image.save(output_path)
        print(f"Colors inverted : dominant_color = {dominant_color_inv}.\n")


# Extracting pages from pdf
def pdf_to_images(input_path, temp_directory):
    pdf_document = fitz.open(input_path)

    # Create the output directory if it doesn't exist
    os.makedirs(temp_directory, exist_ok=True)

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image = page.get_pixmap()

        # Convert the image to PIL Image
        pil_image = Image.frombytes("RGB", [image.width, image.height], image.samples)

        # Save the PIL Image as a PNG file
        image_filename = f"{temp_directory}/page_{page_number + 1}.png"
        pil_image.save(image_filename)

        invert_colors(image_filename, image_filename, page_number)
        image_list.append(image_filename)

    print("All pages extracted")
    pdf_document.close()



# creating pdf and adding images to it
def create_pdf_with_images(image_paths, output_directory, filename):

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    output_pdf_path = filename.replace('pdf_in/','')
    output_pdf_path = f'{output_directory}/{output_pdf_path}'

    # Get the dimensions of the first image
    first_image = Image.open(image_paths[0])
    img_width, img_height = first_image.size

    # Set PDF size to match the image size in landscape mode
    pdf_width, pdf_height = landscape((img_width, img_height))

    c = canvas.Canvas(output_pdf_path, pagesize=(pdf_width, pdf_height))

    for image_path in image_paths:
        # Open the PNG image using Pillow
        image = Image.open(image_path)

        # Draw the image on the PDF canvas, preserving aspect ratio and centering the image
        aspect_ratio = image.width / image.height
        if aspect_ratio > 1:
            new_width = img_width
            new_height = img_width / aspect_ratio
        else:
            new_width = img_height * aspect_ratio
            new_height = img_height

        x_offset = (pdf_width - new_width) / 2
        y_offset = (pdf_height - new_height) / 2

        c.drawImage(image_path, x_offset, y_offset, width=new_width, height=new_height)

        # Add a new page for the next image
        c.showPage()

    c.save()



if __name__ =="__main__":

    temp_directory = "temp"
    pdf_input_folder = "pdf_in" 
    pdf_output_folder = "pdf_out"
    pdf_files_list = get_pdf_files(pdf_input_folder)


    for pdf in pdf_files_list:

        image_list = []

        print('\n')
        print(f'###### Processing ==> {pdf} \n')

        # extracting images and inversing colours
        pdf_to_images(pdf, temp_directory)

        # creating pdf
        print("Creating pdf.............")
        create_pdf_with_images(image_list, pdf_output_folder, pdf)


        # deleting temp folder & input pdf
        shutil.rmtree(temp_directory)
        print('Temp directory is removed........')
        os.remove(pdf)
        print('Input pdf is removed........')






    

    
    