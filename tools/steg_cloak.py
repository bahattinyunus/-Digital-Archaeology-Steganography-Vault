import argparse
import sys
from PIL import Image

def text_to_bits(text):
    """Convert string to a list of bits."""
    bits = []
    for char in text:
        bin_val = bin(ord(char))[2:].rjust(8, '0')
        bits.extend([int(b) for b in bin_val])
    return bits

def bits_to_text(bits):
    """Convert list of bits to string."""
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: break
        char_val = int(''.join(str(b) for b in byte), 2)
        chars.append(chr(char_val))
    return "".join(chars)

def encode(image_path, output_path, secret_text):
    """Hide text in image using LSB."""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB") # Ensure RGB
        pixels = list(img.getdata())
        
        # delimiter to mark end of message
        secret_text += "<STOP>"
        bits = text_to_bits(secret_text)
        
        if len(bits) > len(pixels) * 3:
            print("Error: Message too long for this image.")
            return

        new_pixels = []
        bit_idx = 0
        
        for pixel in pixels:
            if bit_idx < len(bits):
                r, g, b = pixel
                
                # Modify Red LSB
                if bit_idx < len(bits):
                    r = (r & ~1) | bits[bit_idx]
                    bit_idx += 1
                
                # Modify Green LSB
                if bit_idx < len(bits):
                    g = (g & ~1) | bits[bit_idx]
                    bit_idx += 1
                    
                # Modify Blue LSB
                if bit_idx < len(bits):
                    b = (b & ~1) | bits[bit_idx]
                    bit_idx += 1
                
                new_pixels.append((r, g, b))
            else:
                new_pixels.append(pixel)
        
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(new_pixels)
        new_img.save(output_path)
        print(f"Message hidden successfully in {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

def decode(image_path):
    """extract text from image LSB."""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = list(img.getdata())
        
        bits = []
        for pixel in pixels:
            r, g, b = pixel
            bits.append(r & 1)
            bits.append(g & 1)
            bits.append(b & 1)
            
        text = bits_to_text(bits)
        
        if "<STOP>" in text:
            print("Hidden Message Found:")
            print(text.split("<STOP>")[0])
        else:
            print("No hidden message found or message corrupted (missing delimiter).")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="StegCloak: Simple LSB Steganography Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Hide command
    hide_parser = subparsers.add_parser("hide", help="Hide a message in an image")
    hide_parser.add_argument("image", help="Input image path")
    hide_parser.add_argument("output", help="Output image path")
    hide_parser.add_argument("message", help="Secret message to hide")
    
    # Reveal command
    reveal_parser = subparsers.add_parser("reveal", help="Reveal a message from an image")
    reveal_parser.add_argument("image", help="Input image path")
    
    args = parser.parse_args()
    
    if args.command == "hide":
        encode(args.image, args.output, args.message)
    elif args.command == "reveal":
        decode(args.image)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
