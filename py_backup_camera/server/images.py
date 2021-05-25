import png
import io
import numpy


def create_fake_file() -> io.BytesIO:

    width = 255
    height = 255
    img = []
    for y in range(height):
        row = ()
        for x in range(width):
            row = row + (x, max(0, 255 - x - y), y)
        img.append(row)
    file = io.BytesIO()

    w = png.Writer(width, height, greyscale=False)
    w.write(file, img)

    return file


def convert_array_to_png(array: numpy.ndarray, width: int, height: int) -> io.BytesIO:
    file = io.BytesIO()

    w = png.Writer(width, height, greyscale=False)
    w.write(file, array)

    return file
