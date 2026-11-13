"""
TradeShield Localization Module
Supports: English (en), Hindi (hi), and Gujarati (gu).
Provides full translations for Telegram interactions, stock cards, and daily updates.
"""

from typing import Dict, Any, List, Optional


SUPPORTED_LANGUAGES = {
    "en": "English 🇬🇧",
    "hi": "हिंदी 🇮🇳",
    "gu": "ગુજરાતી 🇮🇳"
}


def get_language_inline_keyboard() -> Dict[str, Any]:
    """Returns Telegram InlineKeyboardMarkup for language selection."""
    return {
        "inline_keyboard": [
            [
                {"text": "🇬🇧 English", "callback_data": "set_lang_en"},
                {"text": "🇮🇳 हिंदी", "callback_data": "set_lang_hi"},
                {"text": "🇮🇳 ગુજરાતી", "callback_data": "set_lang_gu"}
            ]
        ]
    }


def get_language_prompt_text() -> str:
    """Returns multilingual prompt asking user to choose their language."""
    return (
        "🌐 *Please select your language / अपनी भाषा चुनें / કૃપા કરીને તમારી ભાષા પસંદ કરો:*\n\n"
        "• 🇬🇧 *English* — Market updates and advice in English\n"
        "• 🇮🇳 *हिंदी* — सभी सलाह और मार्केट अपडेट हिंदी में\n"
        "• 🇮🇳 *ગુજરાતી* — તમામ સલાહ અને માર્કેટ અપડેટ્સ ગુજરાતીમાં\n\n"
        "👇 _Tap a button below:_"
    )


def get_language_set_confirmation(lang: str) -> str:
    """Message sent after a user switches language."""
    if lang == "hi":
        return (
            "✅ *भाषा सफलतापूर्वक हिंदी (हिंदी 🇮🇳) सेट हो गई है!*\n\n"
            "अब आपको सभी शेयर विश्लेषण, सुबह 9:00 बजे और शाम 4:00 बजे के मार्केट अपडेट हिंदी में प्राप्त होंगे।\n\n"
            "👉 किसी भी शेयर का नाम भेजकर अभी देखें (जैसे `TATASTEEL`, `SBIN`, `GOLDBEES`)!"
        )
    elif lang == "gu":
        return (
            "✅ *ભાષા સફળતાપૂર્વક ગુજરાતી (ગુજરાતી 🇮🇳) સેટ થઈ ગઈ છે!*\n\n"
            "હવે તમને તમામ શેર વિશ્લેષણ, સવારે 9:00 વાગ્યે અને સાંજે 4:00 વાગ્યે માર્કેટ અપડેટ્સ ગુજરાતીમાં પ્રાપ્ત થશે.\n\n"
            "👉 કોઈપણ શેરનું નામ મોકલીને હમણાં જ ચકાસો (જેમ કે `TATASTEEL`, `SBIN`, `GOLDBEES`)!"
        )
    else:
        return (
            "✅ *Language successfully set to English 🇬🇧!*\n\n"
            "You will now receive all stock analyses and daily 9:00 AM & 4:00 PM market updates in English.\n\n"
            "👉 Try typing any stock name now (e.g. `TATASTEEL`, `SBIN`, `GOLDBEES`)!"
        )


def get_welcome_message(sender_name: str = "Trader", lang: str = "en") -> str:
    """Returns localized welcome/start message."""
    if lang == "hi":
        return (
            f"👋 नमस्ते *{sender_name}*!\n\n"
            f"मैं आपका *TradeShield असिस्टेंट* हूँ 🛡️\n\n"
            f"मुझे किसी भी **NSE शेयर या कंपनी का नाम** भेजें, और मैं तुरंत आपको बताऊंगा:\n"
            f"1️⃣ क्या अभी **खरीदना सुरक्षित है** (Groww Delivery)?\n"
            f"2️⃣ यदि यह शेयर **पहले से आपके पास है** तो क्या करें (Hold या Sell)?\n"
            f"3️⃣ सख्त **स्टॉप-लॉस और टारगेट** जिससे पूँजी हमेशा सुरक्षित रहे।\n\n"
            f"👉 *अभी कोई भी नाम टाइप करें:*\n"
            f"• `TATASTEEL`\n"
            f"• `SBIN`\n"
            f"• `IRFC`\n"
            f"• `GOLDBEES`\n"
            f"• `Omnitech`\n\n"
            f"🌐 भाषा बदलने के लिए कभी भी **/language** लिखें।"
        )
    elif lang == "gu":
        return (
            f"👋 નમસ્તે *{sender_name}*!\n\n"
            f"હું તમારો *TradeShield આસિસ્ટન્ટ* છું 🛡️\n\n"
            f"મને કોઈપણ **NSE શેર અથવા કંપનીનું નામ** મોકલો, અને હું તરત જ જણાવીશ:\n"
            f"1️⃣ શું અત્યારે **ખરીદવું સુરક્ષિત છે** (Groww Delivery)?\n"
            f"2️⃣ જો તમારી પાસે **પહેલેથી જ આ શેર હોય** તો શું કરવું (Hold કે Sell)?\n"
            f"3️⃣ ચોક્કસ **સ્ટોપ-લોસ અને ટાર્ગેટ** જેથી મૂડી હંમેશા સુરક્ષિત રહે.\n\n"
            f"👉 *હમણાં જ કોઈપણ નામ ટાઇપ કરો:*\n"
            f"• `TATASTEEL`\n"
            f"• `SBIN`\n"
            f"• `IRFC`\n"
            f"• `GOLDBEES`\n"
            f"• `Omnitech`\n\n"
            f"🌐 ભાષા બદલવા માટે ગમે ત્યારે **/language** લખો."
        )
    else:
        return (
            f"👋 Hello *{sender_name}*!\n\n"
            f"I am your *TradeShield Assistant* 🛡️\n\n"
            f"Just send me **any NSE stock or company name**, and I will instantly tell you:\n"
            f"1️⃣ Whether it is safe to **BUY NOW** (Groww Delivery)\n"
            f"2️⃣ What to do if you **ALREADY OWN IT** (Hold/Exit targets)\n"
            f"3️⃣ Strict **Stop-Loss and Target levels** to protect your capital.\n\n"
            f"👉 *Try typing any of these now:*\n"
            f"• `TATASTEEL`\n"
            f"• `SBIN`\n"
            f"• `IRFC`\n"
            f"• `GOLDBEES`\n"
            f"• `Omnitech`\n\n"
            f"🌐 Change language anytime with **/language**."
        )


def get_analyzing_message(query: str, lang: str = "en") -> str:
    """Localized 'analyzing...' transient message."""
    clean = query.upper().strip()
    if lang == "hi":
        return f"🔍 शील्ड द्वारा *{clean}* का विश्लेषण किया जा रहा है... कृपया 3 सेकंड प्रतीक्षा करें।"
    elif lang == "gu":
        return f"🔍 શીલ્ડ દ્વારા *{clean}* નું વિશ્લેષણ થઈ રહ્યું છે... કૃપા કરીને 3 સેકન્ડ રાહ જુઓ."
    else:
        return f"🔍 Analyzing *{clean}* with The Shield... Please wait 3 seconds."


def format_symbol_not_found(query: str, lang: str = "en") -> str:
    """Message when a stock ticker or company name cannot be resolved."""
    if lang == "hi":
        return (
            f"❌ *'{query}' के लिए NSE/BSE पर कोई शेयर नहीं मिला।*\n\n"
            f"👉 *सुझाव:*\n"
            f"• आप कंपनी का नाम लिख सकते हैं: `Tata Motors`, `Omnitech`, `State Bank`, `Reliance`\n"
            f"• या सटीक टिकर: `TATASTEEL`, `SBIN`, `IRFC`, `GOLDBEES`\n"
            f"• कृपया स्पेलिंग जांचें और पुनः प्रयास करें!"
        )
    elif lang == "gu":
        return (
            f"❌ *'{query}' માટે NSE/BSE પર કોઈ શેર મળ્યો નથી.*\n\n"
            f"👉 *ટિપ્સ:*\n"
            f"• તમે કંપનીનું નામ લખી શકો છો: `Tata Motors`, `Omnitech`, `State Bank`, `Reliance`\n"
            f"• અથવા ચોક્કસ ટીકર: `TATASTEEL`, `SBIN`, `IRFC`, `GOLDBEES`\n"
            f"• કૃપા કરીને સ્પેલિંગ તપાસો અને ફરીથી પ્રયાસ કરો!"
        )
    else:
        return (
            f"❌ *Could not find a stock matching '{query}' on NSE/BSE.*\n\n"
            f"👉 *Tips:*\n"
            f"• You can type company names: `Tata Motors`, `Omnitech`, `State Bank`, `Reliance`\n"
            f"• Or exact tickers: `TATASTEEL`, `SBIN`, `IRFC`, `GOLDBEES`\n"
            f"• Please check the spelling and try again!"
        )


def format_stock_analysis_card(
    display_title: str,
    clean_sym: str,
    price: float,
    score: int,
    rsi: float,
    vol: float,
    sh: Dict[str, Any],
    reasons: List[str],
    lang: str = "en"
) -> str:
    """Generates the full interactive stock card in en, hi, or gu."""
    is_approved = sh.get("is_approved", False)
    sl = sh.get("stop_loss_price", 0.0)
    sl_pct = sh.get("sl_percent", 0.0)
    t1 = sh.get("target_1_price", 0.0)
    t1_pct = sh.get("target_1_percent", 0.0)
    t2 = sh.get("target_2_price", 0.0)
    t2_pct = sh.get("target_2_percent", 0.0)
    qty = sh.get("recommended_quantity", 0)
    total_cost = sh.get("total_investment", 0.0)
    max_risk = sh.get("max_possible_loss", 0.0)
    t1_profit = sh.get("target_1_profit", 0.0)
    t2_profit = sh.get("target_2_profit", 0.0)
    rejection_reasons = sh.get("rejection_reasons", [])

    if lang == "hi":
        return _format_card_hindi(
            display_title, clean_sym, price, score, rsi, vol,
            is_approved, sl, sl_pct, t1, t1_pct, t2, t2_pct, qty,
            total_cost, max_risk, t1_profit, t2_profit, reasons, rejection_reasons
        )
    elif lang == "gu":
        return _format_card_gujarati(
            display_title, clean_sym, price, score, rsi, vol,
            is_approved, sl, sl_pct, t1, t1_pct, t2, t2_pct, qty,
            total_cost, max_risk, t1_profit, t2_profit, reasons, rejection_reasons
        )
    else:
        return _format_card_english(
            display_title, clean_sym, price, score, rsi, vol,
            is_approved, sl, sl_pct, t1, t1_pct, t2, t2_pct, qty,
            total_cost, max_risk, t1_profit, t2_profit, reasons, rejection_reasons
        )


def _format_card_english(
    title, sym, price, score, rsi, vol, is_approved, sl, sl_pct,
    t1, t1_pct, t2, t2_pct, qty, cost, risk, p1, p2, reasons, rejections
) -> str:
    if is_approved:
        header = f"🟢 *{title}* (`{sym}`) — HIGH MOMENTUM ({score}% Score)"
        case1 = (
            f"✅ *Safe to Enter in Groww (Delivery)*\n"
            f"• Recommended Buy Price: Around *₹{price:.2f}*\n"
            f"• Recommended Quantity: *{qty} shares* (Cost: ₹{cost:,.0f})\n"
            f"• 🛡️ *Shield Stop-Loss:* ₹{sl:.2f} (-{sl_pct}% | Max risk: ₹{risk:.1f})\n"
            f"• 🎯 *Target 1:* ₹{t1:.2f} (+{t1_pct}%) ➔ Profit: +₹{p1:,.0f}\n"
            f"• 🚀 *Target 2:* ₹{t2:.2f} (+{t2_pct}%) ➔ Profit: +₹{p2:,.0f}"
        )
        case2 = (
            f"📈 *Good Uptrend — Safe to HOLD*\n"
            f"• If you bought earlier, the momentum is strong. Hold towards *₹{t1:.2f}*.\n"
            f"• *Action:* Move your stop-loss up to *₹{sl:.2f}* to lock in your profit!"
        )
    else:
        header = f"⚠️ *{title}* (`{sym}`) — CAUTION / NOT APPROVED BY SHIELD"
        rej_text = "\n".join([f"  ⚠️ {r}" for r in rejections[:2]]) if rejections else "  ⚠️ Technical signals are weak or overbought."
        case1 = (
            f"🚫 *DO NOT BUY NOW (High Risk)*\n"
            f"{rej_text}\n"
            f"• *Advice:* Wait for a proper pullback or breakout before entering."
        )
        case2 = (
            f"🛡️ *If you already own it:*\n"
            f"• Stock is in a downtrend or consolidation.\n"
            f"• If it drops below *₹{sl:.2f}*, exit immediately to protect your capital.\n"
            f"• *Rule:* Never average down on a falling stock!"
        )

    signals_text = "\n".join([f"  • {r}" for r in reasons[:3]]) if reasons else "  • Routine technical scan"
    return (
        f"{header}\n"
        f"💵 *Current Price:* ₹{price:.2f} (RSI: {rsi:.1f} | Vol: {vol:.1f}x)\n"
        f"--------------------------------------\n"
        f"👉 *CASE 1: IF YOU WANT TO BUY NOW*\n"
        f"{case1}\n"
        f"--------------------------------------\n"
        f"👉 *CASE 2: IF YOU ALREADY OWN IT*\n"
        f"{case2}\n"
        f"--------------------------------------\n"
        f"📊 *Key Signals:*\n{signals_text}\n\n"
        f"💡 *TradeShield Rule:* Always trade in Cash Delivery. Respect your Stop-Loss!"
    )


def _format_card_hindi(
    title, sym, price, score, rsi, vol, is_approved, sl, sl_pct,
    t1, t1_pct, t2, t2_pct, qty, cost, risk, p1, p2, reasons, rejections
) -> str:
    if is_approved:
        header = f"🟢 *{title}* (`{sym}`) — मजबूत तेजी (स्कोर: {score}%)"
        case1 = (
            f"✅ *Groww में डिलीवरी में खरीदना सुरक्षित है*\n"
            f"• अनुशंसित खरीद भाव: लगभग *₹{price:.2f}*\n"
            f"• सुझाई गई संख्या: *{qty} शेयर* (कुल लागत: ₹{cost:,.0f})\n"
            f"• 🛡️ *शील्ड स्टॉप-लॉस:* ₹{sl:.2f} (-{sl_pct}% | अधिकतम जोखिम: ₹{risk:.1f})\n"
            f"• 🎯 *टारगेट 1:* ₹{t1:.2f} (+{t1_pct}%) ➔ अनुमानित लाभ: +₹{p1:,.0f}\n"
            f"• 🚀 *टारगेट 2:* ₹{t2:.2f} (+{t2_pct}%) ➔ अनुमानित लाभ: +₹{p2:,.0f}"
        )
        case2 = (
            f"📈 *मजबूत ट्रेंड — होल्ड करना सुरक्षित है*\n"
            f"• यदि आपने पहले खरीदा है, तो ट्रेंड मजबूत है। *₹{t1:.2f}* तक बने रहें।\n"
            f"• *सलाह:* अपना स्टॉप-लॉस बढ़ाकर *₹{sl:.2f}* कर लें ताकि मुनाफा सुरक्षित रहे!"
        )
    else:
        header = f"⚠️ *{title}* (`{sym}`) — सावधानी / शील्ड द्वारा अनुमोदित नहीं"
        rej_text = "\n".join([f"  ⚠️ {r}" for r in rejections[:2]]) if rejections else "  ⚠️ तकनीकी संकेतक कमजोर हैं या शेयर डाउनट्रेंड में है।"
        case1 = (
            f"🚫 *अभी न खरीदें (अधिक जोखिम)*\n"
            f"{rej_text}\n"
            f"• *सलाह:* नए ब्रेकआउट या पुलबैक का इंतजार करें।"
        )
        case2 = (
            f"🛡️ *यदि यह शेयर पहले से आपके पास है:*\n"
            f"• शेयर में गिरावट या कमजोरी के संकेत हैं।\n"
            f"• यदि भाव *₹{sl:.2f}* के नीचे जाए, तो अपनी पूंजी बचाने के लिए तुरंत बाहर निकलें।\n"
            f"• *नियम:* गिरते हुए शेयर में कभी एवरेज न करें!"
        )

    signals_text = "\n".join([f"  • {r}" for r in reasons[:3]]) if reasons else "  • नियमित तकनीकी डेटा"
    return (
        f"{header}\n"
        f"💵 *मौजूदा भाव:* ₹{price:.2f} (RSI: {rsi:.1f} | वॉल्यूम: {vol:.1f}x)\n"
        f"--------------------------------------\n"
        f"👉 *केस 1: यदि आप अभी खरीदना चाहते हैं*\n"
        f"{case1}\n"
        f"--------------------------------------\n"
        f"👉 *केस 2: यदि यह शेयर पहले से आपके पास है*\n"
        f"{case2}\n"
        f"--------------------------------------\n"
        f"📊 *मुख्य संकेत:*\n{signals_text}\n\n"
        f"💡 *शील्ड नियम:* हमेशा कैश डिलीवरी में काम करें। स्टॉप-लॉस का सख्ती से पालन करें!"
    )


def _format_card_gujarati(
    title, sym, price, score, rsi, vol, is_approved, sl, sl_pct,
    t1, t1_pct, t2, t2_pct, qty, cost, risk, p1, p2, reasons, rejections
) -> str:
    if is_approved:
        header = f"🟢 *{title}* (`{sym}`) — ઊંચી તેજી (સ્કોર: {score}%)"
        case1 = (
            f"✅ *Groww માં ડિલિવરીમાં ખરીદવું સુરક્ષિત છે*\n"
            f"• ખરીદીનો ભલામણ કરેલ ભાવ: આશરે *₹{price:.2f}*\n"
            f"• ખરીદવા માટેના શેર: *{qty} શેર* (કુલ ખર્ચ: ₹{cost:,.0f})\n"
            f"• 🛡️ *શીલ્ડ સ્ટોપ-લોસ:* ₹{sl:.2f} (-{sl_pct}% | મહત્તમ જોખમ: ₹{risk:.1f})\n"
            f"• 🎯 *ટાર્ગેટ 1:* ₹{t1:.2f} (+{t1_pct}%) ➔ અંદાજિત નફો: +₹{p1:,.0f}\n"
            f"• 🚀 *ટાર્ગેટ 2:* ₹{t2:.2f} (+{t2_pct}%) ➔ અંદાજિત નફો: +₹{p2:,.0f}"
        )
        case2 = (
            f"📈 *મજબૂત ટ્રેન્ડ — HOLD રાખવું સુરક્ષિત છે*\n"
            f"• જો તમે પહેલાથી ખરીદેલ હોય તો તેજી મજબૂત છે. *₹{t1:.2f}* સુધી પકડી રાખો.\n"
            f"• *સલાહ:* તમારો સ્ટોપ-લોસ વધારીને *₹{sl:.2f}* કરી લો જેથી નફો સુરક્ષિત રહે!"
        )
    else:
        header = f"⚠️ *{title}* (`{sym}`) — સાવચેતી / શીલ્ડ દ્વારા મંજૂર નથી"
        rej_text = "\n".join([f"  ⚠️ {r}" for r in rejections[:2]]) if rejections else "  ⚠️ ટેકનિકલ સંકેત નબળા છે અથવા શેર ડાઉનટ્રેન્ડમાં છે."
        case1 = (
            f"🚫 *અત્યારે ખરીદશો નહીં (વધુ જોખમ)*\n"
            f"{rej_text}\n"
            f"• *સલાહ:* સારા બ્રેકઆઉટ કે પુલબેક સુધી નવી ખરીદી ટાળો."
        )
        case2 = (
            f"🛡️ *જો તમારી પાસે આ શેર પહેલેથી હોય:*\n"
            f"• શેરમાં નબળાઈ કે ઘટાડાના સંકેતો છે.\n"
            f"• જો ભાવ *₹{sl:.2f}* ની નીચે જાય, તો મૂડી બચાવવા તરત એક્ઝિટ કરો.\n"
            f"• *નિયમ:* ઘટતા શેરમાં ક્યારેય નુકસાનમાં એવરેજ ન કરો!"
        )

    signals_text = "\n".join([f"  • {r}" for r in reasons[:3]]) if reasons else "  • ટેકનિકલ સ્કેન વિગતો"
    return (
        f"{header}\n"
        f"💵 *વર્તમાન ભાવ:* ₹{price:.2f} (RSI: {rsi:.1f} | વોલ્યુમ: {vol:.1f}x)\n"
        f"--------------------------------------\n"
        f"👉 *કેસ 1: જો તમે અત્યારે ખરીદવા માંગતા હોવ*\n"
        f"{case1}\n"
        f"--------------------------------------\n"
        f"👉 *કેસ 2: જો તમારી પાસે આ શેર પહેલેથી હોય*\n"
        f"{case2}\n"
        f"--------------------------------------\n"
        f"📊 *મુખ્ય સંકેતો:*\n{signals_text}\n\n"
        f"💡 *શીલ્ડ નિયમ:* હંમેશા કેશ ડિલિવરીમાં જ ટ્રેડ કરો. સ્ટોપ-લોસનું ચુસ્ત પાલન કરો!"
    )


def format_daily_prediction_card(
    gold_data: Dict[str, Any],
    silver_data: Dict[str, Any],
    top_stocks: List[Dict[str, Any]],
    capital_inr: float = 5000.0,
    lang: str = "en",
    timestamp_str: str = ""
) -> str:
    """Formats the daily 9:00 AM / 4:00 PM Telegram update card in en, hi, or gu."""
    if lang == "hi":
        return _format_daily_hindi(gold_data, silver_data, top_stocks, capital_inr, timestamp_str)
    elif lang == "gu":
        return _format_daily_gujarati(gold_data, silver_data, top_stocks, capital_inr, timestamp_str)
    else:
        return _format_daily_english(gold_data, silver_data, top_stocks, capital_inr, timestamp_str)


def _format_daily_english(gold, silver, top_stocks, capital, ts):
    lines = [
        "🛡️ *TRADESHIELD: TODAY'S GROWW PICKS*",
        f"💰 Wallet: ₹{capital:,.0f} | 📅 {ts}",
        "--------------------------------------",
        "🪙 *SAFE ASSETS (GOLD & SILVER DIP-BUYING)*"
    ]
    for m in [gold, silver]:
        if m:
            lines.append(f"• *{m['name']}*: ₹{m['current_price']:.2f} ({m['day_change_pct']:+0.2f}%)")
            lines.append(f"  👉 Buy {m['recommended_units']} units (Cost: ₹{m['total_cost']:,.0f}) | Target: ₹{m['target_1']:.2f}")

    lines.append("--------------------------------------")
    lines.append("🚀 *TOP LOW-VALUE STOCKS (1-2 DAY SWING)*")
    if not top_stocks:
        lines.append("⚠️ *The Shield says:* Market is choppy today. No safe stock triggers.")
        lines.append("   Rule: Keeping cash safe is 100% better than forcing a bad trade!")
    else:
        for s in top_stocks:
            sym = s["symbol"].replace(".NS", "")
            sh = s["shield"]
            lines.append(f"📈 *{sym}* (Confidence: {s['confidence_score']}%)")
            lines.append(f"   • Buy Price: ₹{s['entry_price']:.2f}")
            lines.append(f"   • Qty: *{sh['recommended_quantity']} shares* (Cost: ₹{sh['total_investment']:,.0f})")
            lines.append(f"   • 🛡️ *Stop-Loss*: ₹{sh['stop_loss_price']:.2f} (Max risk: ₹{sh['max_possible_loss']:.1f})")
            lines.append(f"   • 🎯 *Target 1*: ₹{sh['target_1_price']:.2f} (+{sh['target_1_percent']}%) ➔ Profit: +₹{sh['target_1_profit']:,.0f}")

    lines.append("--------------------------------------")
    lines.append("💡 *Shield Rule:* If Stop-Loss hits, exit immediately. Never hold and hope!")
    lines.append("🌐 Change language anytime with /language")
    return "\n".join(lines)


def _format_daily_hindi(gold, silver, top_stocks, capital, ts):
    lines = [
        "🛡️ *ट्रेडशील्ड: आज के ग्रो (GROWW) पिक्स*",
        f"💰 वॉलेट पूंजी: ₹{capital:,.0f} | 📅 {ts}",
        "--------------------------------------",
        "🪙 *सुरक्षित संपत्तियां (सोना और चांदी डिप-बाइंग)*"
    ]
    for m in [gold, silver]:
        if m:
            name_hi = "गोल्ड बीईएस (शुद्ध सोना)" if "Gold" in m['name'] else "सिल्वर बीईएस (शुद्ध चांदी)"
            lines.append(f"• *{name_hi}* ({m['symbol']}): ₹{m['current_price']:.2f} ({m['day_change_pct']:+0.2f}%)")
            lines.append(f"  👉 {m['recommended_units']} यूनिट खरीदें (लागत: ₹{m['total_cost']:,.0f}) | टारगेट: ₹{m['target_1']:.2f}")

    lines.append("--------------------------------------")
    lines.append("🚀 *टॉप मोमेंटम शेयर्स (1-2 दिन का स्विंग ट्रेड)*")
    if not top_stocks:
        lines.append("⚠️ *शील्ड की सलाह:* आज बाजार में कोई सुरक्षित ट्रेड नहीं बना है।")
        lines.append("   नियम: गलत ट्रेड में पैसा फंसाने से बेहतर है नकदी सुरक्षित रखना!")
    else:
        for s in top_stocks:
            sym = s["symbol"].replace(".NS", "")
            sh = s["shield"]
            lines.append(f"📈 *{sym}* (कॉन्फिडेंस: {s['confidence_score']}%)")
            lines.append(f"   • खरीद भाव: ₹{s['entry_price']:.2f}")
            lines.append(f"   • संख्या: *{sh['recommended_quantity']} शेयर* (लागत: ₹{sh['total_investment']:,.0f})")
            lines.append(f"   • 🛡️ *स्टॉप-लॉस*: ₹{sh['stop_loss_price']:.2f} (अधिकतम जोखिम: ₹{sh['max_possible_loss']:.1f})")
            lines.append(f"   • 🎯 *टारगेट 1*: ₹{sh['target_1_price']:.2f} (+{sh['target_1_percent']}%) ➔ लाभ: +₹{sh['target_1_profit']:,.0f}")

    lines.append("--------------------------------------")
    lines.append("💡 *शील्ड नियम:* यदि स्टॉप-लॉस हिट हो, तो तुरंत बाहर निकलें!")
    lines.append("🌐 भाषा बदलने के लिए कभी भी /language लिखें")
    return "\n".join(lines)


def _format_daily_gujarati(gold, silver, top_stocks, capital, ts):
    lines = [
        "🛡️ *ટ્રેડશીલ્ડ: આજના ગ્રો (GROWW) પિક્સ*",
        f"💰 વોલેટ મૂડી: ₹{capital:,.0f} | 📅 {ts}",
        "--------------------------------------",
        "🪙 *સુરક્ષિત રોકાણ (સોનું અને ચાંદી ડીપ-બાયિંગ)*"
    ]
    for m in [gold, silver]:
        if m:
            name_gu = "ગોલ્ડ બીઇએસ (શુદ્ધ સોનું)" if "Gold" in m['name'] else "સિલ્વર બીઇએસ (શુદ્ધ ચાંદી)"
            lines.append(f"• *{name_gu}* ({m['symbol']}): ₹{m['current_price']:.2f} ({m['day_change_pct']:+0.2f}%)")
            lines.append(f"  👉 {m['recommended_units']} યુનિટ ખરીદો (ખર્ચ: ₹{m['total_cost']:,.0f}) | ટાર્ગેટ: ₹{m['target_1']:.2f}")

    lines.append("--------------------------------------")
    lines.append("🚀 *ટોચના મોમેન્ટમ શેર્સ (1-2 દિવસ માટે)*")
    if not top_stocks:
        lines.append("⚠️ *શીલ્ડની સલાહ:* આજે બજાર અનિશ્ચિત છે, કોઈ સુરક્ષિત સ્ટોક મળ્યો નથી.")
        lines.append("   નિયમ: ખોટો ટ્રેડ કરવા કરતા પૈસા કેશમાં રાખવા ૧૦૦% વધુ સારા છે!")
    else:
        for s in top_stocks:
            sym = s["symbol"].replace(".NS", "")
            sh = s["shield"]
            lines.append(f"📈 *{sym}* (વિશ્વાસ: {s['confidence_score']}%)")
            lines.append(f"   • ખરીદ ભાવ: ₹{s['entry_price']:.2f}")
            lines.append(f"   • ખરીદી: *{sh['recommended_quantity']} શેર* (કુલ ખર્ચ: ₹{sh['total_investment']:,.0f})")
            lines.append(f"   • 🛡️ *સ્ટોપ-લોસ*: ₹{sh['stop_loss_price']:.2f} (મહત્તમ જોખમ: ₹{sh['max_possible_loss']:.1f})")
            lines.append(f"   • 🎯 *ટાર્ગેટ 1*: ₹{sh['target_1_price']:.2f} (+{sh['target_1_percent']}%) ➔ નફો: +₹{sh['target_1_profit']:,.0f}")

    lines.append("--------------------------------------")
    lines.append("💡 *શીલ્ડ નિયમ:* જો સ્ટોપ-લોસ હિટ થાય, તો તરત જ એક્ઝિટ કરો!")
    lines.append("🌐 ભાષા બદલવા માટે ગમે ત્યારે /language લખો")
    return "\n".join(lines)

