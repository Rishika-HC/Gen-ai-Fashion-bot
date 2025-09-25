from flask import Flask, request, render_template, jsonify
import random
import pyttsx3
import os
import time
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# -----------------------------
# Clipdrop API Key (Optional)
# -----------------------------
CLIPDROP_API_KEY = "YOUR_API_KEY"

# -----------------------------
# Complete Outfit Suggestions
# -----------------------------
outfits = {
    "casual": {
        "men": {
            "tops": ["t-shirt", "polo shirt", "casual shirt", "hoodie"],
            "bottoms": ["jeans", "chinos", "shorts", "cargo pants"],
            "footwear": ["sneakers", "loafers", "sandals"],
            "accessories": ["watch", "cap", "bracelet", "sunglasses"]
        },
        "women": {
            "tops": ["t-shirt", "tank top", "blouse", "crop top", "off-shoulder top"],
            "bottoms": ["jeans", "shorts", "skirt", "leggings", "palazzo pants"],
            "footwear": ["sneakers", "flats", "sandals", "espadrilles"],
            "accessories": ["watch", "necklace", "bracelet", "earrings", "hat"]
        }
    },
    "office": {
        "men": {
            "tops": ["button-down shirt", "formal shirt", "sweater", "vest"],
            "bottoms": ["chinos", "dress pants", "formal trousers"],
            "footwear": ["loafers", "oxfords", "dress shoes"],
            "accessories": ["watch", "belt", "tie", "cufflinks"]
        },
        "women": {
            "tops": ["blouse", "shirt", "formal top", "sweater"],
            "bottoms": ["trousers", "pencil skirt", "palazzo pants", "formal skirt"],
            "footwear": ["flats", "heels", "loafers"],
            "accessories": ["watch", "necklace", "earrings", "bracelet"]
        }
    },
    "lunch_with_colleagues": {
        "men": {
            "tops": ["polo shirt", "casual shirt", "sweater", "light jacket"],
            "bottoms": ["chinos", "jeans", "khakis"],
            "footwear": ["loafers", "sneakers", "boots"],
            "accessories": ["watch", "belt", "bracelet"]
        },
        "women": {
            "tops": ["blouse", "shirt", "knee-length dress", "cardigan"],
            "bottoms": ["skirt", "trousers", "palazzo pants", "jeans"],
            "footwear": ["flats", "heels", "loafers"],
            "accessories": ["watch", "necklace", "earrings", "scarf"]
        }
    },
    "dinner_date": {
        "men": {
            "tops": ["dress shirt", "turtleneck", "blazer", "suit jacket"],
            "bottoms": ["dress pants", "jeans", "chinos"],
            "footwear": ["oxfords", "loafers", "boots"],
            "accessories": ["watch", "bracelet", "belt", "pocket square"]
        },
        "women": {
            "tops": ["silk blouse", "off-shoulder top", "cocktail dress", "satin top"],
            "bottoms": ["skirt", "trousers", "dress"],
            "footwear": ["heels", "flats", "boots"],
            "accessories": ["necklace", "earrings", "bracelet", "clutch"]
        }
    },
    "beach": {
        "men": {
            "tops": ["tank top", "short sleeve shirt", "t-shirt", "linen shirt"],
            "bottoms": ["shorts", "swim trunks", "linen pants"],
            "footwear": ["flip-flops", "sandals", "boat shoes"],
            "accessories": ["sunglasses", "cap", "bracelet"]
        },
        "women": {
            "tops": ["flowy kurti", "light cotton top", "tunic", "off-shoulder blouse", "bikini top"],
            "bottoms": ["cotton palazzo pants", "capris", "maxi skirt", "shorts", "swim skirt"],
            "footwear": ["sandals", "flats", "espadrilles"],
            "accessories": ["sunglasses", "hat", "anklet", "scarf"]
        }
    },
    "indian_wedding": {
        "men": {
            "tops": ["kurta", "sherwani", "bandhgala", "jodhpuri jacket"],
            "bottoms": ["churidar", "dhoti", "trousers"],
            "footwear": ["mojris", "formal shoes", "sandals"],
            "accessories": ["watch", "brooch", "neck chain", "shawl"]
        },
        "women": {
            "tops": ["blouse", "kurti", "choli", "designer top"],
            "bottoms": ["lehenga skirt", "saree", "palazzo pants"],
            "footwear": ["mojris", "heels", "flats"],
            "accessories": ["bangles", "necklace", "earrings", "maang tikka", "clutch"]
        }
    },
    "family_gathering": {
        "men": {
            "tops": ["casual shirt", "kurta", "sweater"],
            "bottoms": ["jeans", "chinos", "dhoti pants"],
            "footwear": ["loafers", "sandals"],
            "accessories": ["watch", "bracelet"]
        },
        "women": {
            "tops": ["kurti", "blouse", "tunic", "sweater"],
            "bottoms": ["palazzo pants", "skirt", "jeans"],
            "footwear": ["flats", "sandals"],
            "accessories": ["bangles", "necklace", "earrings"]
        }
    },
    "trip": {
        "men": {
            "tops": ["t-shirt", "casual shirt", "hoodie", "jacket"],
            "bottoms": ["jeans", "cargo shorts", "chinos", "track pants"],
            "footwear": ["sneakers", "sandals", "boots"],
            "accessories": ["cap", "sunglasses", "watch", "backpack"]
        },
        "women": {
            "tops": ["t-shirt", "tank top", "kurti", "blouse", "jacket"],
            "bottoms": ["jeans", "leggings", "palazzo pants", "shorts", "skirt"],
            "footwear": ["flats", "sneakers", "sandals"],
            "accessories": ["sunglasses", "hat", "bracelet", "bag"]
        }
    },
    "religious_visit": {
        "men": {
            "tops": ["kurta", "shirt", "sweater"],
            "bottoms": ["trousers", "dhoti pants", "chinos"],
            "footwear": ["mojris", "sandals"],
            "accessories": ["watch", "prayer beads"]
        },
        "women": {
            "tops": ["kurti", "blouse", "tunic", "shawl"],
            "bottoms": ["palazzo pants", "lehenga skirt", "long skirt"],
            "footwear": ["flats", "mojris"],
            "accessories": ["bangles", "necklace", "scarf"]
        }
    }
}

# -----------------------------
# Generate Outfit Text
# -----------------------------
def generate_outfit_text(occasion, gender):
    key = occasion.lower().replace(" ", "_")
    if key not in outfits or gender not in ["men", "women"]:
        return None
    data = outfits[key][gender]
    top = random.choice(data["tops"])
    bottom = random.choice(data["bottoms"])
    footwear = random.choice(data["footwear"])
    accessory = random.choice(data["accessories"])
    return f"Pair {top} with {bottom} and {footwear}. Add {accessory}."

# -----------------------------
# Text-to-Speech
# -----------------------------
def text_to_speech(text):
    engine = pyttsx3.init()
    timestamp = int(time.time() * 1000)
    filename = f"outfit_{timestamp}.mp3"
    path = os.path.join("static", filename)
    engine.save_to_file(text, path)
    engine.runAndWait()
    return f"/static/{filename}"

# -----------------------------
# Clipdrop Image Generation (optional)
# -----------------------------
def generate_outfit_image(prompt):
    url = "https://clipdrop-api.co/text-to-image/v1"
    headers = {"x-api-key": CLIPDROP_API_KEY}
    json_data = {"prompt": prompt}
    try:
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            timestamp = int(time.time() * 1000)
            filename = f"static/outfit_{timestamp}.png"
            with open(filename, "wb") as f:
                f.write(response.content)
            return f"/{filename}"
        else:
            print(f"[ERROR] Clipdrop API failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return None

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    occasion = data.get("occasion", "").strip()
    gender = data.get("gender", "").strip().lower()

    outfit_text = generate_outfit_text(occasion, gender)
    if not outfit_text:
        return jsonify({"error": "No suggestions available for this occasion or gender."})

    audio = text_to_speech(outfit_text)
    prompt = f"A {gender} wearing {outfit_text}"
    image_url = generate_outfit_image(prompt)

    return jsonify({"suggestion": outfit_text, "audio": audio, "image": image_url})

# -----------------------------
# Handle Favicon
# -----------------------------
@app.route('/favicon.ico')
def favicon():
    return '', 204

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
