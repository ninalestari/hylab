from super_image import EdsrModel, ImageLoader, DrlnModel
from PIL import Image
import requests
import time
from datetime import datetime

try:
    # Ensure the file path is correct
    url = "D:/labwork/download_image/ff116e8e8e73-dSJzxEC78.jpg"
    image = Image.open(url)
    
    # Timing the operation
    start = datetime.now()
    print("Start:", start)

    # Load the model
    model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=3)
    #model = DrlnModel.from_pretrained('eugenesiow/drln', scale=3)
    
    # Process the image
    inputs = ImageLoader.load_image(image)
    preds = model(inputs)
    
    # Save the outputs
    ImageLoader.save_image(preds, './new_scaled_3x_2.png')
    print("Upscaled image saved.")

    ImageLoader.save_compare(inputs, preds, './new_scaled_3x_2_compare.png')
    print("Comparison image saved.")

    # End timing
    end = datetime.now()
    total = end - start
    print("End:", end)
    print("Duration:", total)

except Exception as e:
    print("An error occurred:", str(e))

