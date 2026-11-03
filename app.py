
"""ISA 414 Assignment 4: Fleet Feet Cincinnati student demonstration chatbot.
Based on the RX Pizzeria example from Dr. Rayna Xu's course.
"""
import httpx
import streamlit as st
from openai import OpenAI
from PIL import Image

st.set_page_config(page_title="Cincy Run Guide", page_icon="👟", layout="centered")
st.title("👟 Cincy Run Guide")
st.caption("Student-built Fleet Feet Cincinnati customer-service chatbot prototype. Not an official Fleet Feet service.")

@st.cache_resource
def get_openai_client(api_key):
    return OpenAI(api_key=api_key, http_client=httpx.Client(timeout=60.0))

try:
    client = get_openai_client(st.secrets["OPENAI_API_KEY"])
    grounding = st.secrets["GROUNDING"]
except KeyError:
    st.error("Missing OPENAI_API_KEY or GROUNDING in Streamlit secrets. Add both under App settings > Secrets.")
    st.stop()

st.image(Image.open("logo.png"), width=390)
st.markdown("**Ask about:** free shoe fittings, Cincinnati-area locations, walk-ins, appointments, and picking the right kind of shoes.")
with st.expander("Important information"):
    st.write("This is an educational prototype; it cannot access orders, real-time prices, availability, or appointment bookings. Confirm details with your local store.")
    st.markdown("[Fleet Feet Cincinnati](https://www.fleetfeet.com/s/cincy) · [Appointments](https://www.fleetfeet.com/s/cincy/shop/appointments)")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I help you with today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        slot = st.empty()
        reply = ""
        try:
            events = client.responses.create(
                model="gpt-5-mini",
                instructions=grounding,
                input=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            for event in events:
                if event.type == "response.output_text.delta":
                    reply += event.delta
                    slot.markdown(reply + "▌")
            slot.markdown(reply or "I couldn't produce an answer. Please try again.")
            if reply:
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.session_state.messages.pop()
        except Exception as exc:
            st.session_state.messages.pop()
            st.error(f"The model request could not be completed: {exc}")
