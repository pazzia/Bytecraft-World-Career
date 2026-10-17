from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

for path in Path('android/app/src/main/res').glob('mipmap-*/ic_launcher.png'):
    image = Image.open(path).convert('RGBA')
    size = image.size[0]
    badge = max(18, int(size * 0.42))
    pad = max(2, int(size * 0.04))
    left = size - badge - pad
    top = size - badge - pad
    right = size - pad
    bottom = size - pad

    draw = ImageDraw.Draw(image)
    draw.ellipse((left, top, right, bottom), fill=(19, 180, 120, 255), outline=(255, 255, 255, 255), width=max(1, int(size * 0.025)))

    font = ImageFont.load_default()
    text = 'C'
    box = draw.textbbox((0, 0), text, font=font)
    text_w = box[2] - box[0]
    text_h = box[3] - box[1]
    x = left + (badge - text_w) / 2
    y = top + (badge - text_h) / 2 - 1
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    image.save(path)
    print(f'Branded {path}')
