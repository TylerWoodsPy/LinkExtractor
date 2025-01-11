import pyautogui
from PIL import Image, ImageDraw
from pytesseract import pytesseract
import re
from pystray import Icon, Menu, MenuItem
import threading
import webbrowser
import os

# Path to Tesseract OCR executable (Update this path as per your installation)
pytesseract.tesseract_cmd = './Tesseract-OCR/tesseract.exe'

# Directory for saving screenshots and HTML file
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


def take_screenshot():
    """Take a screenshot and save it as a file."""
    screenshot_path = os.path.join(output_dir, "screenshot.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path


def extract_text(image_path):
    """Extract text from an image using Tesseract OCR."""
    text = pytesseract.image_to_string(Image.open(image_path))
    return text


def find_links(text):
    """
    Extract URLs from text, including those with or without http(s):// prefix

    Args:
        text (str): Input text containing URLs

    Returns:
        list: List of extracted URLs
    """
    # Regex pattern to match URLs
    pattern = r'(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=%-]*)?'

    # Find all matches
    matches = re.findall(pattern, text)

    # Clean up matches and ensure they all have http:// prefix
    cleaned_urls = []
    for url in matches:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        cleaned_urls.append(url)

    return cleaned_urls


def generate_html(links):
    """Generate an HTML file with clickable links."""
    html_path = os.path.join(output_dir, "links.html")
    html_content = "<html><body>\n"
    if links:
        for link in links:
            html_content += f'<a href="{link}" target="_blank">{link}</a><br>\n'
    else:
        html_content += "<p>No links found.</p>\n"
    html_content += "</body></html>"

    with open(html_path, "w") as file:
        file.write(html_content)

    return html_path


def process_screenshot():
    """Take a screenshot, extract links, and generate an HTML file."""
    screenshot_path = take_screenshot()
    text = extract_text(screenshot_path)
    print(text)
    links = find_links(text)
    print(links)
    html_path = generate_html(links)
    webbrowser.open(html_path)


def on_activate():
    """Callback for the system tray menu."""
    threading.Thread(target=process_screenshot).start()


def create_image():
    """Create an icon image for the system tray."""
    image = Image.new("RGB", (64, 64), color="blue")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="white")
    return image


# Create system tray menu
menu = Menu(
    MenuItem("Take Screenshot", on_activate),
    MenuItem("Exit", lambda: icon.stop())
)

# Create and run system tray icon
icon = Icon("Link Extractor", create_image(), menu=menu)
icon.run()
