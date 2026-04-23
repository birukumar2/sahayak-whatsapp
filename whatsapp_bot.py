"""
Sahayak - WhatsApp Fever Specialist Bot
Conversational AI Style - Hindi + English
Mediokart | Buxar, Bihar
Version 2.0 - Bug Fixed
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
    t = text.lower().strip()
    return t in ["yes","haan","ha","haa","ji","bilkul","yeah","yep","han","y","हाँ","हां","ho","ok","okay","theek hai","agree","sahi"]
 
def is_no(text):
    t = text.lower().strip()
    return t in ["no","nahi","nhi","nope","na","nah","n","nai","नहीं","mat","refuse"]
 
def is_restart(text):
    t = text.lower().strip()
    # Exact match only — avoid false triggers like "koi bhi nahi"
    return t in ["restart","reset","start","start over","dobara","firse","phirse","menu","home","back","wapas","shuru"]
 
def is_greeting(text):
    t = text.lower().strip()
    # Exact match only
    return t in ["hi","hello","hey","helo","namaste","sahayak","namaskar","hii","helo","good morning","good evening","good afternoon","hy"]
 
def extract_temp(text):
    match = re.search(r'\b(\d{2,3}(?:\.\d{1,2})?)\b', text)
    if match:
        temp = float(match.group(1))
        # Convert Celsius to Fahrenheit
        if temp < 45:
            temp = round((temp * 9/5) + 32, 1)
        return temp
    return None
 
def temp_category(temp):
    if temp < 99:
        return "normal"
    elif temp < 100.4:
        return "low_grade"
    elif temp < 102:
        return "mild"
    elif temp < 104:
        return "moderate"
    else:
        return "high"
 
# ─── Privacy Policy ───────────────────────────────────────────
PRIVACY_HI = """📋 *Sahayak — Privacy Policy & Terms of Service*
 
*हमारी सेवा:*
Sahayak एक AI-powered health information chatbot है।
Operated by: *Mediokart, Buxar, Bihar* 🇮🇳
 
*⚠️ महत्वपूर्ण Disclaimer:*
• यह सेवा केवल *सामान्य स्वास्थ्य जानकारी* देती है
• यह किसी *डॉक्टर का विकल्प नहीं* है
• जानकारी WHO, MoHFW और Red Cross guidelines पर आधारित है
• गंभीर स्थिति में तुरंत डॉक्टर से मिलें
 
*🔒 आपकी Privacy:*
• आपकी बातचीत सुरक्षित रहती है
• आपका डेटा किसी third party को नहीं दिया जाता
• Session data केवल अस्थायी रूप से store होता है
 
*📞 Emergency हो तो:*
तुरंत *108* call करें — Ambulance FREE है।
 
━━━━━━━━━━━━━━━━━━
क्या आप इन terms से सहमत हैं?
आगे बढ़ने के लिए *हाँ* लिखें।"""
 
PRIVACY_EN = """📋 *Sahayak — Privacy Policy & Terms of Service*
 
*Our Service:*
Sahayak is an AI-powered health information chatbot.
Operated by: *Mediokart, Buxar, Bihar* 🇮🇳
 
*⚠️ Important Disclaimer:*
• This service provides *general health information only*
• It is *NOT a substitute for a doctor*
• Information is based on WHO, MoHFW & Red Cross guidelines
• In any serious condition, consult a doctor immediately
 
*🔒 Your Privacy:*
• Your conversation is secure
• We do not share your data with any third party
• Session data is stored temporarily only
 
*📞 In case of Emergency:*
Call *108* immediately — Ambulance is FREE.
 
━━━━━━━━━━━━━━━━━━
Do you agree to these terms?
Type *Yes* to continue."""
 
# ─── Fever Advice Engine ──────────────────────────────────────
def give_advice(data, lang):
    temp = data.get("temperature", 101)
    temp_unknown = data.get("temp_unknown", False)
    duration = data.get("duration", "")
    symptoms = data.get("symptoms", [])
    danger_signs = data.get("danger_signs", [])
    condition = data.get("condition", "none")
 
    cat = temp_category(temp) if not temp_unknown else "mild"
    has_danger = len(danger_signs) > 0
    has_comorbidity = condition.lower() not in [
        "none","koi nahi","no","nahi","kuch nahi","",
        "koi bhi nahi","koi nhi","nhi","koi nahin","nahin"
    ]
 
    # Possible diagnosis
    possible = []
    symp_str = " ".join([str(s) for s in symptoms]).lower()
    if any(w in symp_str for w in ["cough","khansi","throat","gala","sore"]):
        possible.append("Viral Fever / Flu" if lang == "english" else "वायरल बुखार / फ्लू")
    if any(w in symp_str for w in ["rash","daane","chatte","laal"]):
        possible.append("Dengue / Measles" if lang == "english" else "डेंगू / खसरा")
    if any(w in symp_str for w in ["loose","dast","diarrhea","ulti","vomit","nausea"]):
        possible.append("Typhoid / Gastroenteritis" if lang == "english" else "टाइफाइड / गैस्ट्रोएंटेराइटिस")
    if any(w in symp_str for w in ["joint","jodo","body ache","badan","muscles","muscle"]):
        possible.append("Chikungunya / Dengue" if lang == "english" else "चिकनगुनिया / डेंगू")
    if not possible:
        possible.append("Viral Fever" if lang == "english" else "वायरल बुखार")
 
    # ── HINDI RESPONSE ────────────────────────────────────────
    if lang == "hindi":
 
        # DANGER or HIGH FEVER
        if has_danger or cat == "high":
            resp = "🚨 *तुरंत डॉक्टर के पास जाएं!*\n\n"
            resp += "आपके लक्षण गंभीर हैं।\n"
            if danger_signs:
                resp += "\n*⚠️ खतरे के संकेत मिले:*\n"
                for d in danger_signs:
                    resp += f"• {d}\n"
            resp += """
*अभी करें:*
1. 📞 *108 call करें* — Ambulance FREE है
2. 🏥 नज़दीकी अस्पताल जाएं
3. FREE doctor: esanjeevani.mohfw.gov.in
 
📞 104 — Health Helpline (FREE)
 
_⚠️ Source: WHO Emergency Guidelines, MoHFW_"""
            return resp
 
        # SUMMARY
        temp_display = "पता नहीं" if temp_unknown else f"{temp}°F"
        symp_display = ", ".join([str(s) for s in symptoms]) if symptoms else "कोई नहीं"
 
        resp = f"""📋 *आपकी जानकारी का सारांश:*
• तापमान: {temp_display}
• बुखार कब से: {duration}
• लक्षण: {symp_display}
• संभावित कारण: {", ".join(possible)}
 
━━━━━━━━━━━━━━━━━━
"""
        # MODERATE
        if cat == "moderate":
            resp += f"""⚠️ *यह बुखार ध्यान देने योग्य है।*
 
{temp}°F — थोड़ा ज़्यादा है।
आमतौर पर 3-5 दिन में ठीक होता है।
 
*अभी करें:*
💧 पानी, ORS, नारियल पानी खूब पियें
🧊 माथे और बाहों पर ठंडा गीला कपड़ा रखें
👕 हल्के कपड़े पहनें
🛏️ आराम करें — काम/स्कूल न जाएं
🌡️ हर 4-6 घंटे में temperature check करें
 
*डॉक्टर के पास कब जाएं:*
• 2-3 दिन में बुखार कम न हो
• नए लक्षण आएं
• Temperature 104°F से ऊपर जाए
"""
        # MILD
        elif cat in ["mild","low_grade"]:
            resp += f"""✅ *घबराएं नहीं — हल्का बुखार है।*
 
{temp_display} — सामान्य वायरल बुखार लग रहा है।
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
        # NORMAL
        elif cat == "normal":
            resp += f"""✅ *आपका temperature normal है।*
 
{temp_display} — यह सामान्य है।
लेकिन अगर तकलीफ हो तो डॉक्टर से मिलें।
"""
 
        # COMORBIDITY
        if has_comorbidity:
            resp += f"\n⚠️ *आपको {condition} है — इसलिए जल्द डॉक्टर से मिलें।*\n"
 
        # DO'S AND DON'TS
        resp += """
━━━━━━━━━━━━━━━━━━
*🌡️ Fever में क्या करें — क्या न करें:*
 
✅ *करें:*
• हर 4-6 घंटे में temperature check करें
• ORS पियें — घर पर बनाएं:
  1L पानी + 6 tsp चीनी + ½ tsp नमक
• हल्का खाना — खिचड़ी, दलिया, सूप
• पूरी नींद लें
• गुनगुने पानी से स्नान कर सकते हैं
 
❌ *न करें:*
• बर्फ सीधे शरीर पर न लगाएं
• भूखे न रहें
• बिना डॉक्टर के antibiotics न लें
• ज़्यादा ठंडे पानी से न नहाएं
 
━━━━━━━━━━━━━━━━━━
📞 *Emergency Numbers:*
• 108 — Ambulance (FREE)
• 104 — Health Helpline (FREE)
• eSanjeevani: esanjeevani.mohfw.gov.in
 
_⚠️ यह जानकारी WHO, MoHFW और Indian Red Cross guidelines पर आधारित है। यह डॉक्टर की सलाह का विकल्प नहीं है।_
 
नया सवाल पूछने के लिए *restart* लिखें। 🙏"""
 
    # ── ENGLISH RESPONSE ──────────────────────────────────────
    else:
 
        # DANGER or HIGH FEVER
        if has_danger or cat == "high":
            resp = "🚨 *Go to a doctor IMMEDIATELY!*\n\n"
            resp += "Your symptoms are serious.\n"
            if danger_signs:
                resp += "\n*⚠️ Warning signs detected:*\n"
                for d in danger_signs:
                    resp += f"• {d}\n"
            resp += """
*Do this RIGHT NOW:*
1. 📞 *Call 108* — Ambulance is FREE
2. 🏥 Go to nearest hospital
3. FREE doctor: esanjeevani.mohfw.gov.in
 
📞 104 — Health Helpline (FREE)
 
_⚠️ Source: WHO Emergency Guidelines, MoHFW_"""
            return resp
 
        # SUMMARY
        temp_display = "Unknown" if temp_unknown else f"{temp}°F"
        symp_display = ", ".join([str(s) for s in symptoms]) if symptoms else "None mentioned"
 
        resp = f"""📋 *Here's a summary:*
• Temperature: {temp_display}
• Fever since: {duration}
• Symptoms: {symp_display}
• Most likely: {", ".join(possible)}
 
━━━━━━━━━━━━━━━━━━
"""
        # MODERATE
        if cat == "moderate":
            resp += f"""⚠️ *This fever needs attention.*
 
{temp}°F — that's a notable fever.
Usually resolves in 3-5 days.
 
*What to do now:*
💧 Stay hydrated — water, ORS, coconut water
🧊 Cool compress on forehead & arms
👕 Wear light, comfortable clothing
🛏️ Rest — avoid work/school
🌡️ Check temperature every 4-6 hours
 
*See a doctor if:*
• Fever doesn't improve in 2-3 days
• New symptoms appear
• Temperature crosses 104°F
"""
        # MILD
        elif cat in ["mild","low_grade"]:
            resp += f"""✅ *Don't worry — it's a mild fever.*
 
{temp_display} — looks like a normal viral fever.
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
        # NORMAL
        elif cat == "normal":
            resp += f"""✅ *Your temperature is normal.*
 
{temp_display} — this is within normal range.
But if you feel unwell, consult a doctor.
"""
 
        # COMORBIDITY
        if has_comorbidity:
            resp += f"\n⚠️ *You have {condition} — please consult a doctor sooner.*\n"
 
        # DO'S AND DON'TS
        resp += """
━━━━━━━━━━━━━━━━━━
*🌡️ Fever Do's & Don'ts:*
 
✅ *Do:*
• Check temperature every 4-6 hours
• Drink ORS — make at home:
  1L water + 6 tsp sugar + ½ tsp salt
• Eat light food — porridge, soup, khichdi
• Get full sleep
• Lukewarm bath is okay
 
❌ *Don't:*
• Don't apply ice directly on body
• Don't skip meals
• Don't take antibiotics without doctor's advice
• Don't take very cold baths
 
━━━━━━━━━━━━━━━━━━
📞 *Emergency Numbers:*
• 108 — Ambulance (FREE)
• 104 — Health Helpline (FREE)
• eSanjeevani: esanjeevani.mohfw.gov.in
 
_⚠️ This info is based on WHO, MoHFW & Indian Red Cross guidelines. Not a substitute for medical advice._
 
Type *restart* to ask a new question. 🙏"""
 
    return resp
 
# ─── Main Conversation Handler ────────────────────────────────
def handle_message(phone, text):
    session = get_session(phone)
    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    step = session["step"]
    lang = session["lang"]
 
    # ── RESTART — Exact match only ────────────────────────────
    if is_restart(text_lower):
        reset_session(phone)
        session = get_session(phone)
        session["step"] = "lang_select"
        return """👋 *Namaste! Main Sahayak hoon.*
_Mediokart | Buxar, Bihar_ 🇮🇳
 
Main aapka health companion hoon.
Abhi *sirf Fever* ke baare mein help kar sakta hoon.
 
Bhasha chunein / Choose language:
*1* → हिंदी
*2* → English"""
 
    # ── WELCOME / GREETING ────────────────────────────────────
    if step == "welcome" or is_greeting(text_lower):
        reset_session(phone)
        session = get_session(phone)
        session["step"] = "lang_select"
        return """👋 *Namaste! Main Sahayak hoon.*
_Mediokart | Buxar, Bihar_ 🇮🇳
 
Main aapka health companion hoon.
Abhi *sirf Fever* ke baare mein help kar sakta hoon.
 
Bhasha chunein / Choose language:
*1* → हिंदी
*2* → English"""
 
    # ── LANGUAGE SELECT ───────────────────────────────────────
    elif step == "lang_select":
        if text_lower in ["1","hindi","हिंदी","हिन्दी","h"]:
            session["lang"] = "hindi"
            session["step"] = "privacy"
            return PRIVACY_HI
        elif text_lower in ["2","english","en","e","eng"]:
            session["lang"] = "english"
            session["step"] = "privacy"
            return PRIVACY_EN
        else:
            return """Samajh nahi aaya. Please choose:
*1* → हिंदी
*2* → English"""
 
    # ── PRIVACY AGREEMENT ─────────────────────────────────────
    elif step == "privacy":
        if is_yes(text_lower):
            session["agreed"] = True
            session["step"] = "how_long"
            if lang == "hindi":
                return """धन्यवाद! 🙏
 
मैं आपकी बात ध्यान से सुनूंगा।
 
*बुखार कब से है?*
_(जैसे: आज सुबह से, कल शाम से, 2 दिन से)_"""
            else:
                return """Thank you! 🙏
 
I'm here to help you.
 
*How long have you had this fever?*
_(e.g., since this morning, since yesterday evening, 2 days)_"""
        else:
            if lang == "hindi":
                return "आगे बढ़ने के लिए *हाँ* लिखें।"
            else:
                return "Type *Yes* to continue."
 
    # ── HOW LONG ─────────────────────────────────────────────
    elif step == "how_long":
        session["data"]["duration"] = text_stripped
        session["step"] = "temperature"
 
        # Duration warning
        duration_warning = ""
        if any(w in text_lower for w in ["3 din","4 din","5 din","teen din","3 day","4 day","5 day","week","hafte","ek hafte"]):
            if lang == "hindi":
                duration_warning = "⚠️ 3+ दिन से बुखार है — यह ज़रूर डॉक्टर से दिखाएं।\n\n"
            else:
                duration_warning = "⚠️ Fever for 3+ days — please see a doctor soon.\n\n"
 
        if lang == "hindi":
            return f"""{duration_warning}समझ गया। 👍
 
*अभी temperature कितना है?*
 
Thermometer से check करके बताएं।
_(जैसे: 101, 102.5, 103 — °F या °C दोनों ठीक हैं)_
 
Thermometer नहीं है? → *पता नहीं* लिखें"""
        else:
            return f"""{duration_warning}Got it. 👍
 
*What is your temperature right now?*
 
Check with a thermometer.
_(e.g., 101, 102.5, 103 — °F or °C both fine)_
 
No thermometer? → type *don't know*"""
 
    # ── TEMPERATURE ───────────────────────────────────────────
    elif step == "temperature":
        if any(w in text_lower for w in ["pata nahi","don't know","dont know","nahi pata","unknown","pta nhi","pta nahi"]):
            session["data"]["temperature"] = 101
            session["data"]["temp_unknown"] = True
        else:
            temp = extract_temp(text_stripped)
            if temp:
                session["data"]["temperature"] = temp
                session["data"]["temp_unknown"] = False
            else:
                if lang == "hindi":
                    return "Temperature समझ नहीं आया। सिर्फ number लिखें जैसे *102* या *38.5*"
                else:
                    return "Couldn't understand. Please type just the number like *102* or *38.5*"
 
        session["step"] = "other_symptoms"
        temp_val = session["data"]["temperature"]
        cat = temp_category(temp_val)
        temp_unknown = session["data"].get("temp_unknown", False)
 
        if lang == "hindi":
            comment = ""
            if not temp_unknown:
                if cat == "high":
                    comment = f"⚠️ *{temp_val}°F — यह बहुत ज़्यादा है! ध्यान दें।*\n\n"
                elif cat == "moderate":
                    comment = f"ठीक है, *{temp_val}°F* — थोड़ा ज़्यादा है।\n\n"
                elif cat in ["mild","low_grade"]:
                    comment = f"ठीक है, *{temp_val}°F* — हल्का बुखार है।\n\n"
                elif cat == "normal":
                    comment = f"*{temp_val}°F* — यह सामान्य range में है।\n\n"
 
            return f"""{comment}बुखार के साथ *और क्या लक्षण हैं?*
 
जो भी हो वो लिखें:
• बदन दर्द (body ache)
• सिरदर्द (headache)
• ठंड लगना (chills)
• उल्टी / मतली (vomiting/nausea)
• दस्त (loose motion)
• खांसी (cough)
• गले में दर्द (sore throat)
• भूख न लगना (no appetite)
• कमज़ोरी / थकान (weakness)
• आंखों में दर्द (eye pain)
• शरीर पर दाने (rash)
• कोई नहीं
 
_(एक या ज़्यादा लिख सकते हैं)_"""
 
        else:
            comment = ""
            if not temp_unknown:
                if cat == "high":
                    comment = f"⚠️ *{temp_val}°F — That's quite high! Please pay attention.*\n\n"
                elif cat == "moderate":
                    comment = f"Okay, *{temp_val}°F* — that's a notable fever.\n\n"
                elif cat in ["mild","low_grade"]:
                    comment = f"Okay, *{temp_val}°F* — mild fever.\n\n"
                elif cat == "normal":
                    comment = f"*{temp_val}°F* — that's within normal range.\n\n"
 
            return f"""{comment}*What other symptoms are you experiencing?*
 
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
 
_(Mention one or more)_"""
 
    # ── OTHER SYMPTOMS ────────────────────────────────────────
    elif step == "other_symptoms":
        raw = text_stripped
        symptoms_list = [s.strip() for s in re.split(r'[,،\n•\-/]', raw) if s.strip() and len(s.strip()) > 1]
        session["data"]["symptoms"] = symptoms_list
        session["step"] = "danger_signs"
 
        if lang == "hindi":
            return """समझ गया। 👍
 
अब एक बहुत ज़रूरी सवाल —
 
*क्या इनमें से कुछ हो रहा है?*
 
🚨 *1* → सांस लेने में तकलीफ
🚨 *2* → बहुत तेज़ सिरदर्द (असहनीय)
🚨 *3* → बेहोशी / Confusion / बहुत ज़्यादा चक्कर
🚨 *4* → शरीर पर लाल चकत्ते / rash
🚨 *5* → गर्दन में अकड़न
🚨 *6* → इतनी कमज़ोरी कि उठ नहीं पा रहे
✅ *0* → इनमें से कुछ नहीं
 
_(नंबर लिखें, जैसे: 0 या 1,3)_"""
        else:
            return """Got it. 👍
 
Now one very important question —
 
*Are you experiencing any of these warning signs?*
 
🚨 *1* → Difficulty breathing
🚨 *2* → Severe unbearable headache
🚨 *3* → Confusion / Fainting / Extreme dizziness
🚨 *4* → Skin rash or red spots
🚨 *5* → Stiff neck
🚨 *6* → Extreme weakness — can't get up
✅ *0* → None of the above
 
_(Type the number, e.g., 0 or 1,3)_"""
 
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
        # Only check if NOT "0" or "none"
        if text_stripped != "0" and not is_no(text_lower) and "kuch nahi" not in text_lower and "none" not in text_lower:
            for k, v in danger_map.items():
                if k in text_stripped:
                    danger_signs.append(v[0] if lang == "hindi" else v[1])
 
        session["data"]["danger_signs"] = danger_signs
        session["step"] = "condition"
 
        if lang == "hindi":
            return """एक आखिरी सवाल —
 
*क्या आपको पहले से कोई बीमारी है?*
 
• मधुमेह (Diabetes)
• BP (High/Low)
• दिल की बीमारी
• अस्थमा / सांस की बीमारी
• कोई नहीं
 
_(जो हो वो लिखें, जैसे: diabetes — या लिखें: कोई नहीं)_"""
        else:
            return """One last question —
 
*Do you have any existing medical condition?*
 
• Diabetes
• High/Low BP
• Heart disease
• Asthma / breathing problems
• None
 
_(Type whatever applies, e.g., diabetes — or type: none)_"""
 
    # ── CONDITION → FINAL ADVICE ──────────────────────────────
    elif step == "condition":
        session["data"]["condition"] = text_stripped
        session["step"] = "done"
 
        if lang == "hindi":
            loading = "🔍 *आपके लक्षणों का विश्लेषण हो रहा है...*\n\n"
        else:
            loading = "🔍 *Analyzing your symptoms...*\n\n"
 
        advice = give_advice(session["data"], lang)
        return loading + advice
 
    # ── DONE ─────────────────────────────────────────────────
    elif step == "done":
        if lang == "hindi":
            return """नया सवाल पूछने के लिए *restart* लिखें। 🙏
 
📞 Emergency:
• 108 — Ambulance (FREE)
• 104 — Health Helpline (FREE)"""
        else:
            return """Type *restart* to start a new conversation. 🙏
 
📞 Emergency:
• 108 — Ambulance (FREE)
• 104 — Health Helpline (FREE)"""
 
    # ── FALLBACK ─────────────────────────────────────────────
    else:
        reset_session(phone)
        if lang == "hindi":
            return "Kuch galat hua. *restart* likhein. 🙏"
        else:
            return "Something went wrong. Type *restart* 🙏"
 
 
# ─── Flask Routes ─────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    if not incoming_msg:
        return "OK"
    reply = handle_message(from_number, incoming_msg)
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)
 
@app.route("/", methods=["GET"])
def home():
    return "✅ Sahayak Fever Bot Running | Mediokart | Buxar, Bihar 🇮🇳"
 
 
if __name__ == "__main__":
    print("✅ Sahayak WhatsApp Fever Bot chal raha hai...")
    print("📍 Mediokart | Buxar, Bihar")
    print("🌐 Webhook: /webhook")
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)))
 
