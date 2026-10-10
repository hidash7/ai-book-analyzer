import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

# Define schema
class BookReview(BaseModel):
    title:str
    author:str
    rating_out_of_10: int=Field(
        ge=1, le=10,
        description=("A critical rating from 1 to 10 reflecting the general critical reception and reader consensus. "
            "1-3: Widely panned, poorly written, or universally low ratings. "
            "4-5: Below average or deeply flawed. "
            "6-7: Average/decent. "
            "8-10: Acclaimed classic or masterpiece. Do not inflate scores for notoriously poor books."
        ))
    key_takeaways:list[str]
    is_recommended:bool
    critical_flaws: list[str] = Field(
        description="Major criticisms, poor writing decisions, or reasons readers dislike the book."
    )

st.set_page_config(page_title="AI Book Critic", page_icon="📚")
st.title("📚 AI Book Analyzer & Critic")

book_title = st.text_input("Enter a book title:", placeholder="e.g. Atomic Habits")

if st.button("Analyze Book") and book_title:
    with st.spinner("Analyzing critical reception..."):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("API key not found. Please configure GEMINI_API_KEY.")
            st.stop()

        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are an objective, candid literary critic. Evaluate books based on their critical reception "
            "and reader consensus using the full 1-10 rating scale."
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"Analyze the book '{book_title}'.",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": BookReview,
                "temperature": 0.2,
            },
        )

        review: BookReview = BookReview.model_validate_json(response.text)

        st.subheader(f"{review.title} by {review.author}")
        st.metric(label="Critical Score", value=f"{review.rating_out_of_10} / 10")
        
        if review.is_recommended:
            st.success("Recommended Read")
        else:
            st.warning("Not Recommended")

        st.write("### Key Takeaways")
        for point in review.key_takeaways:
            st.markdown(f"- {point}")

        if review.critical_flaws:
            st.write("### Criticisms & Flaws")
            for flaw in review.critical_flaws:
                st.markdown(f"- {flaw}")