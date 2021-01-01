from wand import image

image_class = image.Image


def load(file):
    return image.Image(filename=file)

def save(obj, destination):
    obj.save(filename = destination)
    
def close(obj):
    obj.destroy()