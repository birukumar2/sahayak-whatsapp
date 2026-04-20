"""
Sahayak - WhatsApp First Aid Bot
Twilio WhatsApp API
Mediokart | Buxar, Bihar
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# State yaad rakhne ke liye
user_state = {}

def get_reply(phone, text):
    text = text.lower().strip()
    state = user_state.get(phone)

    # ── /start ya hello ──────────────────────────────────────
    if any(w in text for w in ["hi","hello","start","namaste","helo","sahayak"]):
        user_state[phone] = None
        return """🙏 Namaste! Main Sahayak hoon.
Mediokart | Buxar, Bihar 🇮🇳

Aapko kya problem hai? Likhiye:

1️⃣ Bukhar (Fever)
2️⃣ Chot / Khoon (Injury)
3️⃣ Jalan (Burn)
4️⃣ Heart Attack ❤️
5️⃣ Saanp / Keeda 🐍
6️⃣ Brain / Stroke 🧠
7️⃣ Pregnancy 🤰
8️⃣ Pet Dard / Ulti 🤢
9️⃣ Chakkar / Behoshi 😵

*pharmacy* - Paas mein pharmacy
*ambulance* - Nearest hospital
*doctor* - Free online doctor
*emergency* - Emergency numbers

⚠️ WHO, MoHFW & Red Cross guidelines
pe aadharit hai yeh jankari."""

    # ── PHARMACY ─────────────────────────────────────────────
    elif "pharmacy" in text:
        return """💊 Paas mein Pharmacy

🗺️ OpenStreetMap:
https://www.openstreetmap.org/search?query=pharmacy

🏪 Jan Aushadhi (Govt - Sasti Dawa):
https://janaushadhi.gov.in/StoreLocator.aspx

🗺️ Google Maps:
https://www.google.com/maps/search/medical+store+near+me

📌 Source: Jan Aushadhi, Govt. of India"""

    # ── AMBULANCE ────────────────────────────────────────────
    elif "ambulance" in text:
        return """🚑 Ambulance / Nearest Hospital

📞 *ABHI 108 CALL KARO (FREE)*

🗺️ Paas mein hospital:
https://www.openstreetmap.org/search?query=hospital

🗺️ Google Maps:
https://www.google.com/maps/search/hospital+near+me

⚡ 108 call karo - woh khud aayenge!"""

    # ── DOCTOR ───────────────────────────────────────────────
    elif "doctor" in text:
        return """🏥 Free Online Doctor

🆓 eSanjeevani (Govt - BILKUL FREE):
https://esanjeevani.mohfw.gov.in

🗺️ Paas mein doctor:
https://www.google.com/maps/search/doctor+near+me

📌 Source: MoHFW, Govt. of India"""

    # ── EMERGENCY ────────────────────────────────────────────
    elif "emergency" in text:
        return """🚨 EMERGENCY NUMBERS

📞 108 — Ambulance (FREE)
📞 102 — Pregnancy (FREE)
📞 104 — Health Helpline (FREE)
📞 112 — Police/Fire/Ambulance
📞 1800-180-1104 — Poison Control

📌 Source: MoHFW, Govt. of India"""

    # ── 1. BUKHAR ────────────────────────────────────────────
    elif any(w in text for w in ["bukhar","fever","bukhaar"]) or text == "1":
        user_state[phone] = "bukhar"
        return """🌡️ Bukhar hai — Temperature kitna hai?

A) Halka (99-101°F)
B) Zyada (101-103°F)
C) Bahut zyada (103°F+) — emergency"""

    # ── 2. CHOT ──────────────────────────────────────────────
    elif any(w in text for w in ["chot","khoon","bleeding","cut","injury"]) or text == "2":
        user_state[phone] = "chot"
        return """🩸 Chot lagi — Kitna khoon aa raha hai?

A) Thoda (band ho sakta)
B) Zyada (lagatar aa raha)
C) Bahut zyada (band nahi ho raha)"""

    # ── 3. JALAN ─────────────────────────────────────────────
    elif any(w in text for w in ["jalan","burn","jala","aag"]) or text == "3":
        user_state[phone] = "jalan"
        return """🔥 Jalan hui — Kitna bada hissa jala?

A) Thoda (ungli/chhota hissa)
B) Zyada (haath/pair)
C) Bahut zyada (seena/peeth/chehra)"""

    # ── 4. HEART ATTACK ──────────────────────────────────────
    elif any(w in text for w in ["heart","dil","chest pain","cardiac","seene"]) or text == "4":
        user_state[phone] = None
        return """❤️ HEART ATTACK
🚨 TURANT 108 CALL KARO!

Jab tak ambulance aaye:
1. Bithao — seedhe, aaram se
2. Kapde dhile karo
3. Shant rakho
4. Hosh hai → aspirin (300mg) chababao
5. Hosh nahi → CPR shuru karo:
   • Seene pe haath rakho
   • 30 baar tezi se dabaao
   • 2 baar saanso do — repeat

❌ Akela mat chodo
❌ Khaana/paani mat do

📞 108 — Ambulance (FREE)
📌 Fortis Healthcare, MoHFW, Red Cross"""

    # ── 5. SAANP ─────────────────────────────────────────────
    elif any(w in text for w in ["saanp","snake","bichhu","scorpion","keeda","kaata","daank"]) or text == "5":
        user_state[phone] = None
        return """🐍 SAANP KAATNA
🚨 TURANT 108 CALL KARO!

ABHI KARO:
1. HILNA MAT — pulse slow karo
2. Kaate hisse ko dil se NEECHE rakho
3. Tight kapde/jewellery hatao
4. Saanp ka rang yaad rakho

❌ Daant se zeher mat choosna
❌ Kaata jagah mat kaatna
❌ Barf NAHI lagana
❌ Khaana/paani NAHI dena

📞 108 — Ambulance (FREE)
🏥 Govt hospital mein ASV FREE hai!
📌 MoHFW Snake Bite Guidelines 2017"""

    # ── 6. BRAIN / STROKE ────────────────────────────────────
    elif any(w in text for w in ["brain","stroke","laqwa","paralysis","muh tedha","haemorrhage"]) or text == "6":
        user_state[phone] = None
        return """🧠 BRAIN / STROKE
🚨 TURANT 108 CALL KARO!

FAST Test se pehchano:
F — Chehra tedha?
A — Ek haath uthane mein dikkat?
S — Baat karne mein dikkat?
T — Haan → TURANT 108!

ABHI KARO:
1. 108 CALL KARO
2. Leitao — sar upar
3. Khaana/paani MAT do
4. Akele mat chodo

⏱️ Golden Hour: 4.5 ghante!

📌 MoHFW Stroke Guidelines, AIIMS"""

    # ── 7. PREGNANCY ─────────────────────────────────────────
    elif any(w in text for w in ["pregnancy","pregnant","delivery","labour","prasav","garbh"]) or text == "7":
        user_state[phone] = "pregnancy"
        return """🤰 Pregnancy Emergency — Kya ho raha hai?

A) Pet mein dard / contractions
B) Paani toot gaya (water break)
C) Khoon aa raha hai"""

    # ── 8. PET DARD ──────────────────────────────────────────
    elif any(w in text for w in ["pet","ulti","dast","vomit","loose motion","matli","pait"]) or text == "8":
        user_state[phone] = "pet"
        return """🤢 Pet ki problem — Kya ho raha hai?

A) Sirf pet dard
B) Ulti aa rahi hai
C) Dast lag rahe hain"""

    # ── 9. CHAKKAR ───────────────────────────────────────────
    elif any(w in text for w in ["chakkar","behosh","faint","unconscious","dizzy"]) or text == "9":
        user_state[phone] = "chakkar"
        return """😵 Chakkar / Behoshi — Kya situation hai?

A) Sirf chakkar (hosh hai)
B) Behosh hone wala hai
C) Behosh hai — hosh nahi"""

    # ── A REPLIES ────────────────────────────────────────────
    elif text in ["a","a)"] and state:
        replies = {
            "bukhar": "✅ Halka Bukhar\n\n1. Paani/ORS piyo\n2. Aaram karo\n3. Mathe pe geela kapda\n4. 2 din mein theek na ho → Doctor\n\n📌 WHO Guidelines, NHP India",
            "chot": "✅ Halki Chot\n\n1. Saaf paani se dhoo\n2. 10 min dabao\n3. Antiseptic lagao (Dettol/Savlon)\n4. Bandage karo\n\n📌 Indian Red Cross Manual",
            "jalan": "✅ Halki Jalan\n\n1. 20 min thande paani mein rakho (BARF NAHI!)\n2. Toothpaste/Tel NAHI\n3. Saaf kapde se dhako\n4. Chhale mat phodo\n\n📌 WHO Burn Guidelines",
            "pregnancy": "🤰 Contractions\n\n1. 📞 102 CALL KARO (FREE)\n2. Lait jao\n3. Time note karo\n4. Akele mat raho\n\n📌 MoHFW Maternal Guidelines",
            "pet": "🤢 Pet Dard\n\n1. Thoda thoda paani piyo\n2. 2-3 ghante khaana band\n3. Ghutne mor ke leto\n\n🔴 6 ghante baad → Doctor",
            "chakkar": "😵 Chakkar\n\n1. Baith jao / lait jao\n2. Thanda paani piyo\n3. Khaana khao agar khaya na ho\n4. Aaram karo\n\n📌 WHO First Aid Guidelines"
        }
        user_state[phone] = None
        return replies.get(state, "Samajh nahi aaya. *hi* type karo.")

    # ── B REPLIES ────────────────────────────────────────────
    elif text in ["b","b)"] and state:
        replies = {
            "bukhar": "⚠️ Zyada Bukhar\n\n1. ORS/paani baar baar piyo\n2. Thanda kapda mathe pe\n3. Halke kapde pehno\n\n🔴 3 din se zyada → Doctor\n📞 104 — Helpline (FREE)\n\n📌 WHO, NHP India",
            "chot": "⚠️ Gehri Chot\n\n1. Kaskar dabao 15 min\n2. Haath upar uthao\n3. Doctor ke paas jao — tanka lagega\n\n📌 Red Cross Manual",
            "jalan": "⚠️ Badi Jalan\n\n1. 20 min thande paani se dhoo\n2. Kapde dheeray utaaro\n3. ABHI doctor ke paas jao\n\n📌 WHO Burn Guidelines",
            "pregnancy": "🚨 Paani Toot Gaya!\n\n1. 📞 102 CALL KARO TURANT!\n2. Lait jao\n3. Hospital ke liye nikal jao\n\n📌 MoHFW Maternal Guidelines",
            "pet": "🤢 Ulti\n\n1. Ghunt ghunt paani piyo\n2. ORS piyo baar baar\n3. Solid khaana band karo\n\n🔴 Khoon aaye → TURANT 108!\n📌 WHO ORS Guidelines",
            "chakkar": "⚠️ Behosh Hone Wala\n\n1. TURANT bithao/laitao\n2. Pair upar uthao\n3. Hawa karo\n\n🔴 5 min mein theek na ho → 108"
        }
        user_state[phone] = None
        return replies.get(state, "Samajh nahi aaya. *hi* type karo.")

    # ── C REPLIES ────────────────────────────────────────────
    elif text in ["c","c)"] and state:
        if state in ["bukhar","chot","jalan"]:
            msg = "🚨 EMERGENCY!\n\n📞 108 CALL KARO — ABHI!\n\n1. Akele mat raho\n2. Kuch mat khilao/pilao\n3. Leitao rakho\n\n📌 MoHFW Emergency Guidelines"
        elif state == "pregnancy":
            msg = "🚨 Pregnancy Emergency!\n\n1. 📞 102 CALL KARO TURANT!\n2. 📞 108 bhi call karo\n3. Lait jao\n4. Akele mat raho\n\n📌 MoHFW Maternal Guidelines"
        elif state == "pet":
            msg = "💧 Dast\n\n1. ORS piyo baar baar\n2. Ghar par ORS:\n   1L paani + 6tsp cheeni + ½tsp namak\n3. Solid khaana band\n\n🔴 Khoon aaye → TURANT 108!\n📌 WHO, UNICEF"
        elif state == "chakkar":
            msg = "🚨 BEHOSH HAI!\n\n1. 📞 108 CALL KARO!\n2. Seedhe laitao — pair upar\n3. CPR shuru karo:\n   • Seene pe haath\n   • 30 baar dabaao\n   • 2 baar saanso do\n\n📌 WHO CPR, Red Cross"
        else:
            msg = "🚨 EMERGENCY!\n📞 108 CALL KARO ABHI!"
        user_state[phone] = None
        return msg

    # ── UNRECOGNIZED ─────────────────────────────────────────
    else:
        return """Samajh nahi aaya 🙏

*hi* ya number type karein:
1 → Bukhar
2 → Chot/Khoon
3 → Jalan
4 → Heart Attack
5 → Saanp/Keeda
6 → Brain/Stroke
7 → Pregnancy
8 → Pet Dard/Ulti
9 → Chakkar/Behoshi

*emergency* → Emergency numbers
*pharmacy* → Paas mein pharmacy
*ambulance* → Nearest hospital"""


# ─── Flask Webhook ────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")

    reply_text = get_reply(from_number, incoming_msg)

    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "✅ Sahayak WhatsApp Bot chal raha hai! | Mediokart | Buxar, Bihar"


if __name__ == "__main__":
    print("✅ Sahayak WhatsApp Bot shuru ho raha hai...")
    print("📍 Mediokart | Buxar, Bihar")
    print("🌐 Webhook: http://localhost:5000/webhook")
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
