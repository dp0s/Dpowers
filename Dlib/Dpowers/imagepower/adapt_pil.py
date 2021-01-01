from PIL import Image

image_class = Image.Image

def load(file):
    return Image.open(file)

def save(obj, destination):
    obj.save(destination)
    
def close(obj):
    obj.close()