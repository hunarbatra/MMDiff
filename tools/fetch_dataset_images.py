"""Download the dataset sample images used by the Feature lab on the MMDiff project page.

Run from the website root (the folder that contains index.html):

    python3 tools/fetch_dataset_images.py

Writes small JPEG thumbnails to assets/data/. Uses only the standard library;
if Pillow is installed the images are also resized to 480 px on the long side.
Sources: VSR (COCO train2017 images), OCRBench and VLSBench via the Hugging Face
datasets-server API.
"""
import io, json, os, sys, urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "data")
os.makedirs(OUT, exist_ok=True)

# VSR (cambridgeltl/vsr_random, test split): COCO train2017 image ids
VSR = ["000000342259", "000000111911", "000000456376", "000000287427", "000000236925",
       "000000450711", "000000469728", "000000422469", "000000419473", "000000120007",
       "000000579591", "000000202998", "000000001139"]
# (dataset, config, split, row index, output name)
ROWS = [("echo840/OCRBench", "default", "test", 305, "ocr_305"),
        ("echo840/OCRBench", "default", "test", 301, "ocr_301"),
        ("echo840/OCRBench", "default", "test", 200, "ocr_200"),
        ("echo840/OCRBench", "default", "test", 54, "ocr_54"),
        ("Foreshhh/vlsbench", "default", "train", 169, "vls_169"),
        ("Foreshhh/vlsbench", "default", "train", 95, "vls_95"),
        ("Foreshhh/vlsbench", "default", "train", 0, "vls_0")]

UA = {"User-Agent": "mmdiff-site/1.0"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

def save(data, name):
    path = os.path.join(OUT, name + ".jpg")
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((480, 480))
        im.save(path, quality=86)
    except ImportError:
        open(path, "wb").write(data)
    print("saved", path)

for cid in VSR:
    save(get(f"http://images.cocodataset.org/train2017/{cid}.jpg"), "vsr_" + cid.lstrip("0"))

for ds, cfg, split, idx, name in ROWS:
    api = (f"https://datasets-server.huggingface.co/rows?dataset={ds}&config={cfg}"
           f"&split={split}&offset={idx}&length=1")
    row = json.loads(get(api))["rows"][0]["row"]
    save(get(row["image"]["src"]), name)

print("done:", len(VSR) + len(ROWS), "images in", os.path.normpath(OUT))
