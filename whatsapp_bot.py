"""
Sahayak - WhatsApp Fever Specialist Bot
Conversational AI style - Hindi + English
Mediokart | Buxar, Bihar
"""
 
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
 
app = Flask(__name__)
 
# ─── Session Store ────────────────────────────────────────────
sessions = {}
 
def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {
            "lang": None,
            "step": "welcome",
            "data": {},
            "agreed": False
        }
    return sessions[phone]
 
def reset_session(phone):
    sessions[phone] = {
        "lang": None,
        "step": "welcome",
        "data": {},
        "agreed": False
    }
 
# ─── Helpers ──────────────────────────────────────────────────
def is_yes(text):
    return any(w in text.lower() for w in ["yes","haan","ha","haa","ji","bilkul","yeah","yep","ho","han","y"])
 
def is_no(text):
    return any(w in text.lower() for w in ["no","nahi","nhi","nope","na","nah","n","nai"])
 
def extract_temp(text):
    match = re.search(r'\b(\d{2,3}(?:\.\d)?)\b', text)
    if match:
        temp = float(match.group(1))
        if temp < 45:  # Celsius
            temp = round((temp * 9/5) + 32, 1)
        return temp
    return None
 
def temp_category(temp):
    if temp < 99:
        return "normal"
    elif temp < 100.4:
        return "low"
    elif temp < 102:
        return "mild"
    elif temp < 104:
        return "moderate"
    else:
        return "high"
 
# ─── Privacy Policy ───────────────────────────────────────────
PRIVACY_HI = """📋 *Sahayak — Privacy Policy & Terms*
 
*हमारी सेवा के बारे में:*
Sahayak एक AI-powered health information service है जो Mediokart, Buxar, Bihar द्वारा संचालित है।
 
*⚠️ महत्वपूर्ण Disclaimer:*
• Sahayak केवल *सामान्य स्वास्थ्य जानकारी* प्रदान करता है
• यह किसी *डॉक्टर का विकल्प नहीं* है
• हमारी जानकारी WHO, MoHFW और Red Cross guidelines पर आधारित है
• किसी भी गंभीर स्थिति में तुरंत डॉक्टर से मिलें
 
*🔒 आपकी Privacy:*
• आपकी बातचीत सुरक्षित है
• हम आपका डेटा किसी third party को नहीं देते
• Session data temporarily store होता है
 
*📞 Emergency:*
किसी भी आपात स्थिति में 108 call करें — FREE है।
 
क्या आप इन terms से सहमत हैं?
*हाँ* लिखें आगे बढ़ने के लिए"""
 
PRIVACY_EN = """📋 *Sahayak — Privacy Policy & Terms*
 
*About our service:*
Sahayak is an AI-powered health information service operated by Mediokart, Buxar, Bihar.
 
*⚠️ Important Disclaimer:*
• Sahayak provides *general health information only*
• It is *NOT a substitute for a doctor*
• Our information is based on WHO, MoHFW & Red Cross guidelines
• In any serious condition, consult a doctor immediately
 
*🔒 Your Privacy:*
• Your conversation is secure
• We do not share your data with any third party
• Session data is stored temporarily only
 
*📞 Emergency:*
In any emergency, call 108 — it's FREE.
 
Do you agree to these terms?
Type *Yes* to continue"""
 
# ─── Fever Analysis Engine ────────────────────────────────────
def analyze_and_advise(data, lang):
    temp = data.get("temperature", 101)
    temp_unknown = data.get("temp_unknown", False)
    duration = data.get("duration", "")
    symptoms = data.get("symptoms", [])
    danger_signs = data.get("danger_signs", [])
    condition = data.get("condition", "none")
 
    cat = temp_category(temp) if not temp_unknown else "mild"
    has_danger = len(danger_signs) > 0
    has_comorbidity = condition.lower() not in ["none","koi nahi","no","nahi","kuch nahi",""]
 
    # ── Possible Diagnosis ────────────────────────────────────
    possible = []
    symp_str = " ".join(symptoms).lower()
 
    if "cough" in symp_str or "khansi" in symp_str or "throat" in symp_str or "gala" in symp_str:
        possible.append("Viral fever / Flu" if lang == "english" else "वायरल बुखार / फ्लू")
    if "rash" in symp_str or "daane" in symp_str or "chatte" in symp_str:
        possible.append("Dengue / Measles" if lang == "english" else "डेंगू / खसरा")
    if "loose motion" in symp_str or "dast" in symp_str or "diarrhea" in symp_str or "ulti" in symp_str or "vomit" in symp_str:
        possible.append("Gastroenteritis / Typhoid" if lang == "english" else "गैस्ट्रोएंटेराइटिस / टाइफाइड")
    if "body ache" in symp_str or "badan dard" in symp_str or "joint" in symp_str or "jodo" in symp_str:
        possible.append("Chikungunya / Dengue / Flu" if lang == "english" else "चिकनगुनिया / डेंगू / फ्लू")
    if not possible:
        possible.append("Viral fever" if lang == "english" else "वायरल बुखार")
 
    # ── Build Response ────────────────────────────────────────
    if lang == "hindi":
 
        # DANGER / HIGH FEVER
        if has_danger or cat == "high":
            resp = f"""🚨 *तुरंत डॉक्टर के पास जाएं!*
 
आपके लक्षण गंभीर हैं।
"""
            if danger_signs:
                resp += "\n*खतरे के संकेत:*\n"
                for d in danger_signs:
                    resp += f"• {d}\n"
 
            resp += f"""
*अभी करें:*
1. 📞 *108 call करें* — Ambulance FREE है
2. 🏥 नज़दीकी अस्पताल जाएं
3. या FREE doctor से बात करें:
   esanjeevani.mohfw.gov.in
 
📞 104 — Health Helpline (FREE)
 
⚠️ _Source: WHO Emergency Guidelines, MoHFW_"""
            return resp
 
        # SUMMARY
        resp = f"""📋 *आपकी जानकारी का सारांश:*
• तापमान: {"पता नहीं" if temp_unknown else f"{temp}°F"}
• बुखार कब से: {duration}
• लक्षण: {", ".join(symptoms) if symptoms else "बताया नहीं"}
• संभावित कारण: {", ".join(possible)}
 
"""
        # MODERATE FEVER
        if cat == "moderate":
            resp += f"""⚠️ *यह बुखार ध्यान देने योग्य है।*
 
{temp}°F बुखार थोड़ा ज़्यादा है।
आमतौर पर 3-5 दिन में ठीक होता है।
 
*अभी करें:*
💧 पानी, ORS, नारियल पानी खूब पियें
🧊 माथे और बाहों पर ठंडा गीला कपड़ा रखें
👕 हल्के कपड़े पहनें
🛏️ आराम करें — काम/स्कूल न जाएं
🌡️ हर 4-6 घंटे में temperature check करें
 
*डॉक्टर के पास कब जाएं:*
• 2-3 दिन में बुखार कम न हो
• नए लक्षण आएं (सांस की तकलीफ, rash, confusion)
• Temperature 104°F से ऊपर जाए
"""
 
        # MILD FEVER
        elif cat in ["mild","low"]:
            resp += f"""✅ *घबराएं नहीं — हल्का बुखार है।*
 
{temp if not temp_unknown else "~101"}°F — यह सामान्य वायरल बुखार लग रहा है।
3-5 दिन में ठीक हो जाता है।
 
*अभी करें:*
💧 पानी और ORS खूब पियें
🛏️ भरपूर आराम करें
🧊 माथे पर ठंडा गीला कपड़ा रखें
👕 हल्के कपड़े पहनें
 
*डॉक्टर के पास कब जाएं:*
• 2 दिन में ठीक न हो
• Temperature बढ़े या नए लक्षण आएं
"""
 
        # COMORBIDITY WARNING
        if has_comorbidity:
            resp += f"\n⚠️ *आपको {condition} है — इसलिए डॉक्टर से जल्दी मिलें।*\n"
 
        # FEVER DO's AND DON'Ts
        resp += """
---
*🌡️ Fever में क्या करें — क्या न करें:*
 
✅ *करें:*
• हर 4-6 घंटे में temperature check करें
• ORS पियें — घर पर बनाएं:
  1L पानी + 6 tsp चीनी + ½ tsp नमक
• हल्का खाना खाएं — खिचड़ी, दलिया
• पूरी नींद लें
 
❌ *न करें:*
• ठंडे पानी से नहाएं नहीं (गुनगुना ठीक है)
• बर्फ सीधे शरीर पर न लगाएं
• भूखे न रहें
• बिना डॉक्टर के antibiotics न लें
 
---
📞 *Emergency Numbers:*
• 108 — Ambulance (FREE)
• 104 — Health Helpline (FREE)
• eSanjeevani: esanjeevani.mohfw.gov.in
 
_⚠️ यह जानकारी WHO, MoHFW और Indian Red Cross guidelines पर आधारित है। यह डॉक्टर की सलाह का विकल्प नहीं है।_
 
नया सवाल पूछने के लिए *restart* लिखें। 🙏"""
 
    else:  # ENGLISH
 
        # DANGER / HIGH FEVER
        if has_danger or cat == "high":
            resp = f"""🚨 *Go to a doctor IMMEDIATELY!*
 
Your symptoms are serious.
"""
            if danger_signs:
                resp += "\n*Danger signs detected:*\n"
                for d in danger_signs:
                    resp += f"• {d}\n"
 
            resp += f"""
*Do this RIGHT NOW:*
1. 📞 *Call 108* — Ambulance is FREE
2. 🏥 Go to nearest hospital
3. Or consult a FREE doctor at:
   esanjeevani.mohfw.gov.in
 
📞 104 — Health Helpline (FREE)
 
⚠️ _Source: WHO Emergency Guidelines, MoHFW_"""
            return resp
 
        # SUMMARY
        resp = f"""📋 *Here's a summary of what you told me:*
• Temperature: {"Unknown" if temp_unknown else f"{temp}°F"}
• Fever since: {duration}
• Symptoms: {", ".join(symptoms) if symptoms else "Not mentioned"}
• Most likely: {", ".join(possible)}
 
"""
 
        # MODERATE FEVER
        if cat == "moderate":
            resp += f"""⚠️ *This fever needs attention.*
 
{temp}°F is a notable fever.
It usually resolves in 3-5 days.
 
*What to do now:*
💧 Stay hydrated — water, ORS, coconut water
🧊 Cool compress on forehead & arms
👕 Wear light, comfortable clothing
🛏️ Rest — avoid work/school
🌡️ Check temperature every 4-6 hours
 
*See a doctor if:*
• Fever doesn't improve in 2-3 days
• New symptoms appear (breathlessness, rash, confusion)
• Temperature crosses 104°F
"""
 
        # MILD FEVER
        elif cat in ["mild","low"]:
            resp += f"""✅ *Don't worry — it's a mild fever.*
 
{temp if not temp_unknown else "~101"}°F — This looks like a normal viral fever.
Usually resolves in 3-5 days.
 
*What to do:*
💧 Drink plenty of water and ORS
🛏️ Get plenty of rest
🧊 Cool compress on forehead
👕 Wear light clothing
 
*See a doctor if:*
• No improvement in 2 days
• Temperature rises or new symptoms appear
"""
 
        # COMORBIDITY WARNING
        if has_comorbidity:
            resp += f"\n⚠️ *You have {condition} — please consult a doctor sooner.*\n"
 
        # FEVER DO's AND DON'Ts
        resp += """
---
*🌡️ Fever Do's & Don'ts:*
 
✅ *Do:*
• Check temperature every 4-6 hours
• Drink ORS — make at home:
  1L water + 6 tsp sugar + ½ tsp salt
• Eat light food — khichdi, porridge
• Get full sleep
 
❌ *Don't:*
• Don't take cold baths (lukewarm is fine)
• Don't apply ice directly on body
• Don't skip meals
• Don't take antibiotics without doctor's advice
 
---
📞 *Emergency Numbers:*
• 108 — Ambulance (FREE)
• 104 — Health Helpline (FREE)
• eSanjeevani: esanjeevani.mohfw.gov.in
 
_⚠️ This information is based on WHO, MoHFW & Indian Red Cross guidelines. It is not a substitute for medical advice._
 
Type *restart* to ask a new question. 🙏"""
 
    return resp
 
# ─── Main Conversation Handler ────────────────────────────────
def handle_message(phone, text):
    session = get_session(phone)
    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    step = session["step"]
    lang = session["lang"]
 
    # RESTART
    if any(w in text_lower for w in ["restart","reset","start over","dobara","firse","phirse"]):
        reset_session(phone)
        step = "welcome"
        session = get_session(phone)
 
    # ── WELCOME ───────────────────────────────────────────────
    if step == "welcome" or any(w in text_lower for w in ["hi","hello","namaste","sahayak","hey","helo","start"]):
        reset_session(phone)
        session = get_session(phone)
        session["step"] = "lang_select"
        return """👋 *Hi! I'm Sahayak, your health companion.*
_By Mediokart | Buxar, Bihar_ 🇮🇳
 
I provide health information — *for fever only* right now.
 
Please choose your language / भाषा चुनें:
*1* → हिंदी
*2* → English"""
 
    # ── LANGUAGE SELECT ───────────────────────────────────────
    elif step == "lang_select":
        if text_lower in ["1","hindi","हिंदी","h"]:
            session["lang"] = "hindi"
            lang = "hindi"
            session["step"] = "privacy"
            return PRIVACY_HI
        elif text_lower in ["2","english","en","e"]:
            session["lang"] = "english"
            lang = "english"
            session["step"] = "privacy"
            return PRIVACY_EN
        else:
            return """Please choose / चुनें:
*1* → हिंदी
*2* → English"""
 
    # ── PRIVACY AGREEMENT ─────────────────────────────────────
    elif step == "privacy":
        if is_yes(text_lower):
            session["agreed"] = True
            session["step"] = "how_long"
            if lang == "hindi":
                return """धन्यवाद! 🙏
 
मैं आपकी बात समझने की कोशिश करूंगा।
 
*बुखार कब से है?*
_(जैसे: आज सुबह से, 2 दिन से, कल से)_"""
            else:
                return """Thank you! 🙏
 
I'll try to understand what's going on with you.
 
*How long have you had this fever?*
_(e.g., since this morning, 2 days, since yesterday)_"""
        else:
            return """आप बिना agree किए आगे नहीं बढ़ सकते।
You cannot proceed without agreeing.
 
Type *हाँ / Yes* to continue."""
 
    # ── HOW LONG ─────────────────────────────────────────────
    elif step == "how_long":
        session["data"]["duration"] = text_stripped
        session["step"] = "temperature"
        if lang == "hindi":
            return f"""समझ गया — {text_stripped} से बुखार है।
 
*अभी temperature कितना है?*
 
Thermometer से check करके बताएं।
_(जैसे: 101, 102.5, 103 — °F या °C दोनों ठीक हैं)_
 
Thermometer नहीं है? → *पता नहीं* लिखें"""
        else:
            return f"""Got it — fever since {text_stripped}.
 
*What is your temperature right now?*
 
Check with a thermometer and let me know.
_(e.g., 101, 102.5, 103 — °F or °C both are fine)_
 
No thermometer? → type *don't know*"""
 
    # ── TEMPERATURE ───────────────────────────────────────────
    elif step == "temperature":
        if any(w in text_lower for w in ["pata nahi","don't know","dont know","nahi pata","nahi","unknown","patta nahi"]):
            session["data"]["temperature"] = 101
            session["data"]["temp_unknown"] = True
        else:
            temp = extract_temp(text_stripped)
            if temp:
                session["data"]["temperature"] = temp
                session["data"]["temp_unknown"] = False
            else:
                if lang == "hindi":
                    return "Temperature समझ नहीं आया। सिर्फ number लिखें जैसे *102* या *103.5*"
                else:
                    return "Couldn't understand the temperature. Please type just the number like *102* or *103.5*"
 
        session["step"] = "other_symptoms"
        temp_val = session["data"]["temperature"]
        cat = temp_category(temp_val)
 
        if lang == "hindi":
            resp = ""
            if cat == "high":
                resp = f"⚠️ *{temp_val}°F — यह बहुत ज़्यादा है!*\n\n"
            elif cat == "moderate":
                resp = f"ठीक है, {temp_val}°F — थोड़ा ज़्यादा है।\n\n"
            elif cat in ["mild","low"]:
                resp = f"ठीक है, {temp_val}°F — हल्का बुखार है।\n\n"
 
            resp += """बुखार के साथ *और क्या लक्षण हैं?*
 
जो भी हो वो लिखें:
• बदन दर्द (body ache)
• सिरदर्द (headache)
• ठंड लगना (chills)
• उल्टी (vomiting)
• दस्त (loose motion)
• खांसी (cough)
• गले में दर्द (sore throat)
• भूख न लगना
• कमज़ोरी / थकान
• आंखों में दर्द
• शरीर पर दाने (rash)
• कोई नहीं
 
_(एक या ज़्यादा लिख सकते हैं)_"""
            return resp
        else:
            resp = ""
            if cat == "high":
                resp = f"⚠️ *{temp_val}°F — That's quite high!*\n\n"
            elif cat == "moderate":
                resp = f"Okay, {temp_val}°F — that's a notable fever.\n\n"
            elif cat in ["mild","low"]:
                resp = f"Okay, {temp_val}°F — that's a mild fever.\n\n"
 
            resp += """*Besides the fever, what other symptoms are you experiencing?*
 
Mention all that apply:
• Body aches
• Headache
• Chills / Shivering
• Vomiting / Nausea
• Loose motion / Diarrhea
• Cough
• Sore throat
• Loss of appetite
• Weakness / Fatigue
• Eye pain / Red eyes
• Skin rash / Spots
• None
 
_(You can mention one or more)_"""
            return resp
 
    # ── OTHER SYMPTOMS ────────────────────────────────────────
    elif step == "other_symptoms":
        symptoms_raw = text_stripped
        symptoms_list = [s.strip() for s in re.split(r'[,،\n•\-]', symptoms_raw) if s.strip()]
        session["data"]["symptoms"] = symptoms_list
        session["step"] = "danger_signs"
 
        if lang == "hindi":
            return """समझ गया। 👍
 
अब एक ज़रूरी सवाल —
 
*क्या इनमें से कुछ हो रहा है?*
 
🚨 *1* → सांस लेने में तकलीफ
🚨 *2* → बहुत तेज़ सिरदर्द (असहनीय)
🚨 *3* → बेहोशी / Confusion / चक्कर
🚨 *4* → शरीर पर लाल चकत्ते / rash
🚨 *5* → गर्दन में अकड़न
🚨 *6* → बहुत कमज़ोरी — उठ नहीं पा रहे
✅ *0* → इनमें से कुछ नहीं
 
_(जो हो उसका नंबर लिखें, जैसे: 1,3)_"""
        else:
            return """Got it. 👍
 
Now one important question —
 
*Are you experiencing any of these warning signs?*
 
🚨 *1* → Difficulty breathing
🚨 *2* → Severe unbearable headache
🚨 *3* → Confusion / Fainting / Dizziness
🚨 *4* → Skin rash or red spots
🚨 *5* → Stiff neck
🚨 *6* → Extreme weakness — can't get up
✅ *0* → None of the above
 
_(Type the number, e.g., 1,3 or 0)_"""
 
    # ── DANGER SIGNS ─────────────────────────────────────────
    elif step == "danger_signs":
        danger_map = {
            "1": ("सांस की तकलीफ", "Difficulty breathing"),
            "2": ("बहुत तेज़ सिरदर्द", "Severe headache"),
            "3": ("बेहोशी / Confusion", "Confusion/Fainting"),
            "4": ("शरीर पर rash", "Skin rash"),
            "5": ("गर्दन में अकड़न", "Stiff neck"),
            "6": ("बहुत ज़्यादा कमज़ोरी", "Extreme weakness")
        }
 
        danger_signs = []
        if "0" not in text_lower and not is_no(text_lower):
            for k, v in danger_map.items():
                if k in text:
                    danger_signs.append(v[0] if lang == "hindi" else v[1])
 
        session["data"]["danger_signs"] = danger_signs
        session["step"] = "condition"
 
        if lang == "hindi":
            return """एक आखिरी सवाल —
 
*क्या आपको पहले से कोई बीमारी है?*
 
• मधुमेह (Diabetes)
• BP (High/Low)
• दिल की बीमारी
• अस्थमा
• कोई नहीं
 
_(जो हो वो लिखें)_"""
        else:
            return """One last question —
 
*Do you have any existing medical condition?*
 
• Diabetes
• High/Low BP
• Heart disease
• Asthma
• None
 
_(Type whatever applies)_"""
 
    # ── EXISTING CONDITION → FINAL ADVICE ────────────────────
    elif step == "condition":
        session["data"]["condition"] = text_stripped
        session["step"] = "done"
 
        if lang == "hindi":
            loading = "🔍 आपके लक्षणों का विश्लेषण हो रहा है...\n\n"
        else:
            loading = "🔍 Analyzing your symptoms...\n\n"
 
        advice = analyze_and_advise(session["data"], lang)
        return loading + advice
 
    # ── DONE ─────────────────────────────────────────────────
    elif step == "done":
        if lang == "hindi":
            return """नया सवाल पूछने के लिए *restart* लिखें। 🙏
 
Emergency में:
📞 108 — Ambulance (FREE)
📞 104 — Health Helpline (FREE)"""
        else:
            return """Type *restart* to start over. 🙏
 
In emergency:
📞 108 — Ambulance (FREE)
📞 104 — Health Helpline (FREE)"""
 
    else:
        reset_session(phone)
        return "Kuch galat hua. *restart* likhein / Type *restart* 🙏"
 
 
# ─── Flask Webhook ────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    if not incoming_msg:
        return "OK"
    reply_text = handle_message(from_number, incoming_msg)
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)
 
@app.route("/", methods=["GET"])
def home():
    return "✅ Sahayak Fever Bot Running | Mediokart | Buxar, Bihar"
 
if __name__ == "__main__":
    print("✅ Sahayak WhatsApp Fever Bot chal raha hai...")
    print("📍 Mediokart | Buxar, Bihar")
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)))
 
