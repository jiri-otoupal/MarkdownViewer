#!/usr/bin/env python3
"""
Script to create icon files from SVG for the Markdown Viewer application.
"""

import os
from pathlib import Path

def create_icon():
    """Create icon files from SVG."""
    try:
        # Try to use Pillow with cairosvg for SVG conversion
        from PIL import Image
        import cairosvg
        import io
        
        svg_path = Path("src/resources/icon.svg")
        ico_path = Path("src/resources/icon.ico")
        png_path = Path("src/resources/icon.png")
        
        if not svg_path.exists():
            print("❌ SVG file not found!")
            return False
        
        # Convert SVG to PNG first
        png_data = cairosvg.svg2png(url=str(svg_path), output_width=256, output_height=256)
        
        # Create PIL Image from PNG data
        image = Image.open(io.BytesIO(png_data))
        
        # Save as PNG
        image.save(png_path, "PNG")
        print(f"✅ Created PNG: {png_path}")
        
        # Create ICO with multiple sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        images = []
        
        for size in sizes:
            resized = image.resize(size, Image.Resampling.LANCZOS)
            images.append(resized)
        
        # Save as ICO
        images[0].save(ico_path, format='ICO', sizes=[img.size for img in images])
        print(f"✅ Created ICO: {ico_path}")
        
        return True
        
    except ImportError:
        print("⚠️  Pillow and cairosvg not available. Creating simple ICO...")
        return create_simple_icon()
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return create_simple_icon()

def create_simple_icon():
    """Create a simple icon using basic PIL operations."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        ico_path = Path("src/resources/icon.ico")
        png_path = Path("src/resources/icon.png")
        
        # Create a simple icon programmatically
        size = 256
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Background circle
        margin = 20
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(45, 45, 48, 255), outline=(0, 122, 204, 255), width=4)
        
        # Document rectangle
        doc_margin = 60
        draw.rectangle([doc_margin, doc_margin+20, size-doc_margin, size-doc_margin], 
                      fill=(22, 27, 34, 255), outline=(48, 54, 61, 255), width=2)
        
        # Split line
        center_x = size // 2
        draw.line([center_x, doc_margin+30, center_x, size-doc_margin-10], 
                 fill=(48, 54, 61, 255), width=2)
        
        # Text "MD"
        try:
            # Try to use a font
            font_size = 48
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        text = "MD"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 + 20
        
        draw.text((text_x, text_y), text, fill=(88, 166, 255, 255), font=font)
        
        # Save as PNG
        image.save(png_path, "PNG")
        print(f"✅ Created PNG: {png_path}")
        
        # Create ICO with multiple sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        images = []
        
        for size_tuple in sizes:
            resized = image.resize(size_tuple, Image.Resampling.LANCZOS)
            images.append(resized)
        
        # Save as ICO
        images[0].save(ico_path, format='ICO', sizes=[img.size for img in images])
        print(f"✅ Created ICO: {ico_path}")
        
        return True
        
    except ImportError:
        print("❌ Pillow not available. Please install: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Error creating simple icon: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Creating Markdown Viewer icon...")
    
    # Ensure resources directory exists
    Path("src/resources").mkdir(parents=True, exist_ok=True)
    
    success = create_icon()
    
    if success:
        print("🎉 Icon creation completed!")
    else:
        print("❌ Icon creation failed!")
