import os
import requests
import streamlit as st

st.set_page_config(page_title="TwinMind",page_icon="🧠",layout="wide")
API=os.getenv("API_BASE_URL","http://localhost:8000").rstrip("/")
if "lang" not in st.session_state: st.session_state.lang="en"
if "openai_api_key" not in st.session_state: st.session_state.openai_api_key=""

T={"en":{"dash":"Dashboard","new":"New Entry","timeline":"Timeline","recall":"Memory Recall","reflect":"Reflection","secret":"Secrets","subtitle":"Your cognitive journal, memory and reflection companion"},"ar":{"dash":"لوحة التحكم","new":"إضافة مدخل","timeline":"الخط الزمني","recall":"استرجاع الذاكرة","reflect":"التأمل","secret":"المفاتيح السرية","subtitle":"دفترك المعرفي وذاكرتك ومساعدك للتأمل"}}
LABELS={"en":{"journal":"Journal","email":"Email","meeting_minutes":"Meeting minutes","thought":"Thought","emotion":"Emotion","insight":"Insight","voice_note":"Voice note transcript","calendar":"Calendar context","other":"Other"},"ar":{"journal":"يوميات","email":"بريد إلكتروني","meeting_minutes":"محضر اجتماع","thought":"فكرة","emotion":"شعور","insight":"استنتاج","voice_note":"ملاحظة صوتية","calendar":"سياق التقويم","other":"أخرى"}}

with st.sidebar:
    st.markdown("## 🧠 TwinMind")
    choice=st.radio("Language / اللغة",["English","العربية"],horizontal=True,index=0 if st.session_state.lang=="en" else 1)
    st.session_state.lang="ar" if choice=="العربية" else "en"; lang=st.session_state.lang; t=T[lang]
    page=st.radio("Navigation",[t["dash"],t["new"],t["timeline"],t["recall"],t["reflect"],"🔐 "+t["secret"]],label_visibility="collapsed")

lang=st.session_state.lang; t=T[lang]
if lang=="ar": st.markdown("<style>div[data-testid='stAppViewContainer'],section[data-testid='stSidebar']{direction:rtl} input,textarea{direction:rtl!important;text-align:right!important}</style>",unsafe_allow_html=True)
st.title("🧠 TwinMind"); st.caption(t["subtitle"])

def get(path):
    try: r=requests.get(API+path,timeout=20); r.raise_for_status(); return r.json()
    except Exception as e: st.error(f"Backend error: {e}")

def post(path,payload,timeout=90):
    key=st.session_state.get("openai_api_key","").strip()
    if key: payload={**payload,"openai_api_key":key}
    try: r=requests.post(API+path,json=payload,timeout=timeout); r.raise_for_status(); return r.json()
    except Exception as e: st.error(f"Backend error: {e}")

if page=="🔐 "+t["secret"]:
    st.subheader("🔐 OpenAI API Key")
    st.info("The key is kept only in this Streamlit session and is sent over HTTPS to TwinMind when AI analysis is requested. It is not written to the journal database or GitHub." if lang=="en" else "يُحتفظ بالمفتاح داخل جلسة Streamlit الحالية فقط، ويُرسل عبر HTTPS إلى TwinMind عند طلب التحليل. لا يتم حفظه في قاعدة بيانات اليوميات أو GitHub.")
    key=st.text_input("OPENAI_API_KEY",value=st.session_state.openai_api_key,type="password",placeholder="sk-...")
    c1,c2=st.columns(2)
    if c1.button("Save for this session" if lang=="en" else "حفظ لهذه الجلسة",type="primary",use_container_width=True):
        st.session_state.openai_api_key=key.strip(); st.success("API key saved for this session." if lang=="en" else "تم حفظ المفتاح لهذه الجلسة.")
    if c2.button("Clear key" if lang=="en" else "مسح المفتاح",use_container_width=True):
        st.session_state.openai_api_key=""; st.rerun()
    st.caption(("Status: AI key loaded" if st.session_state.openai_api_key else "Status: no session key; fallback analysis will be used") if lang=="en" else ("الحالة: تم تحميل مفتاح الذكاء الاصطناعي" if st.session_state.openai_api_key else "الحالة: لا يوجد مفتاح؛ سيتم استخدام التحليل الاحتياطي"))

elif page==t["dash"]:
    entries=get("/entries?limit=30") or []; c1,c2,c3=st.columns(3); c1.metric("Entries" if lang=="en" else "المدخلات",len(entries))
    avg=sum(float(x.get("sentiment_score") or 0) for x in entries)/len(entries) if entries else 0; neg=sum(x.get("sentiment_label")=="negative" for x in entries)
    c2.metric("Avg sentiment" if lang=="en" else "متوسط المشاعر",f"{avg:.2f}" if entries else "-"); c3.metric("Negative signals" if lang=="en" else "الإشارات السلبية",neg)
    for e in entries[:8]:
        with st.container(border=True): st.markdown(f"**{LABELS[lang].get(e['entry_type'],e['entry_type'])}** · {e['created_at'][:16].replace('T',' ')}"); st.write(e.get("summary") or e.get("content","")[:300]); st.caption(f"Sentiment: {e.get('sentiment_label','neutral')}")

elif page==t["new"]:
    rev={v:k for k,v in LABELS[lang].items()}; label=st.selectbox("Entry type" if lang=="en" else "نوع المدخل",list(rev)); title=st.text_input("Title (optional)" if lang=="en" else "العنوان (اختياري)"); content=st.text_area("What would you like TwinMind to remember?" if lang=="en" else "ما الذي تريد من TwinMind أن يتذكره؟",height=260)
    if st.button("Save & Analyze" if lang=="en" else "حفظ وتحليل",type="primary",use_container_width=True,disabled=not content.strip()):
        r=post("/entries",{"content":content,"entry_type":rev[label],"source":"manual","title":title or None,"preferred_language":lang})
        if r: st.success("Saved and analyzed." if lang=="en" else "تم الحفظ والتحليل."); st.markdown("### "+("Analysis" if lang=="en" else "التحليل")); st.write(r.get("summary")); st.write(f"**Sentiment:** {r.get('sentiment_label')} ({float(r.get('sentiment_score',0)):.2f})"); st.write(f"**Emotions:** {', '.join(r.get('emotions',[]))}"); st.info(r.get("wellbeing_suggestion","")); st.warning(r.get("negativity_suggestion",""))

elif page==t["timeline"]:
    entries=get("/entries?limit=100") or []
    for e in entries:
        with st.expander(f"{LABELS[lang].get(e['entry_type'],e['entry_type'])} · {e['created_at'][:16].replace('T',' ')} · {e.get('sentiment_label','neutral')}"): st.write(e.get("content")); st.caption(", ".join(e.get("emotions",[])))

elif page==t["recall"]:
    q=st.text_input("Ask your Twin about your past entries" if lang=="en" else "اسأل TwinMind عن مدخلاتك السابقة")
    if st.button("Recall" if lang=="en" else "استرجاع",type="primary",disabled=not q.strip()):
        r=post("/recall",{"query":q,"language":lang})
        if r: st.markdown(r.get("answer","")); st.divider(); [st.write(f"**{e['created_at'][:10]}** — {e.get('summary') or e.get('content','')[:300]}") for e in r.get("matches",[])[:5]]

elif page==t["reflect"]:
    st.write("Generate a grounded reflection across your recent entries." if lang=="en" else "أنشئ تأملاً مستنداً إلى مدخلاتك الأخيرة.")
    if st.button("Generate 7-day Reflection" if lang=="en" else "إنشاء تأمل لآخر 7 أيام",type="primary",use_container_width=True):
        r=post("/reflection",{"language":lang,"days":7})
        if r: st.markdown(r.get("reflection","")); st.caption(f"Entries analyzed: {r.get('entry_count',0)} · Average sentiment: {r.get('average_sentiment','-')}")
