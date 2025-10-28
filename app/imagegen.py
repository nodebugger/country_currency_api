from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

CACHE_DIR = "cache"
IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

def generate_summary_image(total_countries: int, top5_list: list, last_refreshed_at: str):
    ensure_cache_dir()
    width, height = 1000, 600
    bg_color = (255, 255, 255)
    text_color = (20, 20, 20)
    title_font_size = 36
    normal_font_size = 20

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", title_font_size)
        font_normal = ImageFont.truetype("DejaVuSans.ttf", normal_font_size)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()

    x = 40
    y = 40
    draw.text((x, y), f"Countries Cached: {total_countries}", font=font_title, fill=text_color)
    y += 60
    draw.text((x, y), f"Last refreshed: {last_refreshed_at}", font=font_normal, fill=text_color)
    y += 40
    draw.text((x, y), "Top 5 Countries by Estimated GDP", font=font_normal, fill=text_color)
    y += 30

    for i, item in enumerate(top5_list, start=1):
        name = item.get("name")
        gdp = item.get("estimated_gdp")
        gdp_text = f"{gdp:,.2f}" if gdp is not None else "N/A"
        draw.text((x, y), f"{i}. {name} — {gdp_text}", font=font_normal, fill=text_color)
        y += 30

    img.save(IMAGE_PATH)
    return IMAGE_PATH
