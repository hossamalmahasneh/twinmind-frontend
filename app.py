import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="TwinMind", page_icon="🧠", layout="wide")
API = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

TEXT = {
    "en": {
        "title": "TwinMind",
        "subtitle": "Your cognitive journal, memory and reflection companion",
        "dashboard": "Dashboard", "new": "New Entry", "timeline": "Timeline", "recall": "Memory Recall", "reflection": "Reflection",
        "language": "Language", "entry_type": "Entry type", "entry_title": "Title (optional)", "content": "What would you like TwinMind to remember?",
        "save": "Save & Analyze", "saved": "Entry saved and analyzed.", "question": "Ask your Twin about your past entries", "ask": "Recall",
        "generate": "Generate 7-day Reflection", "wellbeing": "Well-being suggestion", "negativity": "Constructive response suggestion",
        "sentiment": "Sentiment", "emotion": "Emotions", "summary": "Summary", "recent": "Recent cognitive timeline",
        "notice": "TwinMind supports reflection and decision-making. Sentiment/emotion signals are AI interpretations, not clinical diagnoses.",
        "api_error": "Backend is not reachable. Start the TwinMind API or set API_BASE_URL.",
    },
    "ar": {
        "title": "TwinMind", "subtitle": "دفترك المعرفي وذاكرتك ومساعدك للتأمل",
        "dashboard": "لوحة التحكم", "new": "إضافة مدخل", "timeline": "الخط الزمني", "recall": "استرجاع الذاكرة", "reflection": "التأمل",
        "language": "اللغة", "entry_type": "نوع المدخل", "entry_title": "العنوان (اختياري)", "content": "ما الذي تريد من TwinMind أن يتذكره؟",
        "save": "حفظ وتحليل", "saved": "تم حفظ المدخل وتحليله.", "question": "اسأل TwinMind عن مدخلاتك السابقة", "ask": "استرجاع",
        "generate": "إنشاء تأمل لآخر 7 أيام", "wellbeing": "اقتراح للرفاه", "negativity": "اقتراح لاستجابة بناءة",
        "sentiment": "المشاعر العامة", "emotion": "العواطف", "summary": "الملخص", "recent": "الخط الزمني المعرفي الأخير",
        "notice": "TwinMind أداة للتأمل ودعم القرار. تحليل المشاعر والعواطف هو تفسير بالذكاء الاصطناعي وليس تشخيصاً طبياً.",
        "api_error": "تعذر الاتصال بالخادم. شغّل TwinMind API أو اضبط API_BASE_URL.",
    },
}

ENTRY_LABELS = {
    "en": {"journal":"Journal", "email":"Email", "meeting_minutes":"Meeting minutes", "thought":"Thought", "emotion":"Emotion", "insight":"Insight", "voice_note":"Voice note transcript", "calendar":"Calendar context", "other":"Other"},
    "ar": {"journal":"يوميات", "email":"بريد إلكتروني", "meeting_minutes":"محضر اجتماع", "thought":"فكرة", "emotion":"شعور", "insight":"استنتاج", "voice_note":"ملاحظة صوتية", "calendar":"سياق التقويم", "other":"أخرى"},
}

if "lang" not in st.session_state:
    st.session_state.lang = "en"

with st.sidebar:
    st.markdown("## 🧠 TwinMind")
    selected_lang = st.radio("Language / اللغة", ["English", "العربية"], index=0 if st.session_state.lang == "en" else 1, horizontal=True)
    st.session_state.lang = "ar" if selected_lang == "العربية" else "en"
    lang = st.session_state.lang
    t = TEXT[lang]
    pages = [t["dashboard"], t["new"], t["timeline"], t["recall"], t["reflection"]]
    page = st.radio("Navigation", pages, label_visibility="collapsed")
    st.caption(t["notice"])

t = TEXT[st.session_state.lang]
lang = st.session_state.lang
if lang == "ar":
    st.markdown("<style>div[data-testid='stAppViewContainer']{direction:rtl;} section[data-testid='stSidebar']{direction:rtl;} input,textarea{direction:rtl!important;text-align:right!important;}</style>", unsafe_allow_html=True)

st.title(f"🧠 {t['title']}")
st.caption(t["subtitle"])


def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        st.error(t["api_error"])
        return None


def api_post(path, payload, timeout=60):
    try:
        r = requests.post(f"{API}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as exc:
        st.error(f"{t['api_error']} ({exc})")
        return None


if page == t["dashboard"]:
    entries = api_get("/entries?limit=30") or []
    c1, c2, c3 = st.columns(3)
    c1.metric("Entries" if lang == "en" else "المدخلات", len(entries))
    if entries:
        avg = sum(float(x.get("sentiment_score") or 0) for x in entries) / len(entries)
        negative = sum(1 for x in entries if x.get("sentiment_label") == "negative")
        c2.metric("Avg sentiment" if lang == "en" else "متوسط المشاعر", f"{avg:.2f}")
        c3.metric("Negative signals" if lang == "en" else "الإشارات السلبية", negative)
        st.subheader(t["recent"])
        for e in entries[:6]:
            with st.container(border=True):
                st.markdown(f"**{ENTRY_LABELS[lang].get(e['entry_type'], e['entry_type'])}** · {e['created_at'][:16].replace('T',' ')}")
                st.write(e.get("summary") or e.get("content", "")[:300])
                st.caption(f"{t['sentiment']}: {e.get('sentiment_label','neutral')} ({float(e.get('sentiment_score') or 0):.2f})")
    else:
        c2.metric("Avg sentiment" if lang == "en" else "متوسط المشاعر", "-")
        c3.metric("Negative signals" if lang == "en" else "الإشارات السلبية", 0)
        st.info("Add your first journal, email, meeting minute, thought or emotion." if lang == "en" else "أضف أول يومية أو بريد أو محضر اجتماع أو فكرة أو شعور.")

elif page == t["new"]:
    labels = ENTRY_LABELS[lang]
    reverse = {v:k for k,v in labels.items()}
    label = st.selectbox(t["entry_type"], list(labels.values()))
    title = st.text_input(t["entry_title"])
    content = st.text_area(t["content"], height=260, placeholder="Paste an email or meeting minutes, or write freely..." if lang == "en" else "الصق بريداً إلكترونياً أو محضر اجتماع، أو اكتب بحرية...")
    if st.button(t["save"], type="primary", use_container_width=True, disabled=not content.strip()):
        result = api_post("/entries", {"content":content, "entry_type":reverse[label], "source":"manual", "title":title or None, "preferred_language":lang})
        if result:
            st.success(t["saved"])
            a, b = st.columns(2)
            with a:
                st.markdown(f"**{t['summary']}**")
                st.write(result.get("summary"))
                st.markdown(f"**{t['sentiment']}**: {result.get('sentiment_label')} ({float(result.get('sentiment_score',0)):.2f})")
                st.markdown(f"**{t['emotion']}**: {', '.join(result.get('emotions', []))}")
            with b:
                st.info(f"**{t['wellbeing']}**\n\n{result.get('wellbeing_suggestion','')}")
                st.warning(f"**{t['negativity']}**\n\n{result.get('negativity_suggestion','')}")

elif page == t["timeline"]:
    entries = api_get("/entries?limit=100") or []
    if entries:
        types = ["All"] + list(dict.fromkeys(e["entry_type"] for e in entries))
        selected = st.selectbox("Filter" if lang == "en" else "تصفية", types, format_func=lambda x: ("All" if lang=="en" else "الكل") if x=="All" else ENTRY_LABELS[lang].get(x,x))
        filtered = entries if selected == "All" else [e for e in entries if e["entry_type"] == selected]
        for e in filtered:
            with st.expander(f"{ENTRY_LABELS[lang].get(e['entry_type'],e['entry_type'])} · {e['created_at'][:16].replace('T',' ')} · {e.get('sentiment_label','neutral')}"):
                st.write(e.get("content"))
                st.caption(f"{t['emotion']}: {', '.join(e.get('emotions',[]))}")
    else:
        st.info("No entries yet." if lang == "en" else "لا توجد مدخلات بعد.")

elif page == t["recall"]:
    q = st.text_input(t["question"], placeholder="When was I most concerned about Project X?" if lang == "en" else "متى كنت أكثر قلقاً بشأن المشروع؟")
    if st.button(t["ask"], type="primary", disabled=not q.strip()):
        result = api_post("/recall", {"query":q, "language":lang})
        if result:
            st.markdown(result.get("answer", ""))
            if result.get("matches"):
                st.divider()
                for e in result["matches"][:5]:
                    st.caption(f"{e['created_at'][:10]} · {ENTRY_LABELS[lang].get(e['entry_type'],e['entry_type'])}")
                    st.write(e.get("summary") or e.get("content","")[:300])

elif page == t["reflection"]:
    st.write("Generate a grounded reflection across journals, emails, meeting minutes, thoughts and emotions." if lang == "en" else "أنشئ تأملاً مستنداً إلى اليوميات والبريد ومحاضر الاجتماعات والأفكار والمشاعر.")
    if st.button(t["generate"], type="primary", use_container_width=True):
        result = api_post("/reflection", {"language":lang, "days":7}, timeout=90)
        if result:
            st.markdown(result.get("reflection", ""))
            st.caption(f"Entries analyzed: {result.get('entry_count',0)} · Average sentiment: {result.get('average_sentiment','-')}" if lang == "en" else f"المدخلات المحللة: {result.get('entry_count',0)} · متوسط المشاعر: {result.get('average_sentiment','-')}")
