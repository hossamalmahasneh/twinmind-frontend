
import streamlit as st

st.title("TwinMind - Your Cognitive Twin")

menu = ["Home", "New Journal Entry", "Memory Recall", "Smart Suggestions"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome to your dashboard!")
elif choice == "New Journal Entry":
    st.subheader("Add a new entry:")
    journal_text = st.text_area("What's on your mind today?")
    if st.button("Save Entry"):
        st.success("Entry saved (to be connected to backend)")
elif choice == "Memory Recall":
    st.subheader("Ask your Twin:")
    query = st.text_input("Type your question...")
    if st.button("Recall Memory"):
        st.info("Memory recall will be shown here (to be connected).")
elif choice == "Smart Suggestions":
    st.subheader("Your Smart Behavior Insights")
    st.info("Suggestions based on your data (to be connected).")
