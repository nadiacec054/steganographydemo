from PIL import Image

DELIMITER = "#####END#####"

def message_to_binary(message):
    return ''.join(format(ord(c), '08b') for c in message)

def binary_to_message(binary):
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def encode_image(input_path, output_path, secret_message):
    image = Image.open(input_path).convert("RGB")
    pixels = list(image.getdata())

    secret_message += DELIMITER
    binary_message = message_to_binary(secret_message)

    if len(binary_message) > len(pixels) * 3:
        raise ValueError("Message too large")

    new_pixels = []
    bit_index = 0

    for pixel in pixels:
        r, g, b = pixel

        if bit_index < len(binary_message):
            r = (r & ~1) | int(binary_message[bit_index])
            bit_index += 1

        if bit_index < len(binary_message):
            g = (g & ~1) | int(binary_message[bit_index])
            bit_index += 1

        if bit_index < len(binary_message):
            b = (b & ~1) | int(binary_message[bit_index])
            bit_index += 1

        new_pixels.append((r, g, b))

    encoded = Image.new("RGB", image.size)
    encoded.putdata(new_pixels)
    encoded.save(output_path)

def decode_image(image_path):
    image = Image.open(image_path).convert("RGB")
    pixels = list(image.getdata())

    binary_data = ""

    for pixel in pixels:
        r, g, b = pixel
        binary_data += str(r & 1)
        binary_data += str(g & 1)
        binary_data += str(b & 1)

    message = binary_to_message(binary_data)

    if DELIMITER in message:
        return message.split(DELIMITER)[0]

    return ""
