# app.py
import os
from dotenv import load_dotenv
import streamlit as st
import asyncio
from my_agents import run_structured_output_workflow

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.title("📧 GemReach - Cold Email Generator")

tone = st.selectbox("Select tone", ["Professional", "Casual", "Friendly"])
target = st.text_input("Enter target audience (e.g., CTOs of SaaS startups)")
linkedin_url = st.text_input("Enter LinkedIn profile URL (optional)")
product_details = st.text_area("Enter product details")

if st.button("Generate Emails"):
    with st.spinner("Generating..."):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            emails = loop.run_until_complete(
                run_structured_output_workflow(tone, target, linkedin_url, product_details)
            )

            if not emails:
                st.warning("No emails generated. Check API key or inputs.")
            else:
                for idx, email in enumerate(emails, 1):
                    st.subheader(f"Option {idx}: {email.subject}")
                    st.write(email.body)

                    st.download_button(
                        label="💾 Save this email",
                        data=f"Subject: {email.subject}\n\n{email.body}",
                        file_name=f"email_option_{idx}.txt",
                        mime="text/plain"
                    )
        except Exception as e:
            st.error(f"Error: {e}")
