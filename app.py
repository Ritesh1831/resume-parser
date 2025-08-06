import streamlit as st
from parser import ResumeParser

st.set_page_config(page_title="Resume Parser", layout="centered")
st.title("📄 Resume Parser")
st.markdown("Upload your **PDF** or **DOCX** resume to auto-fill your details. You can manually edit any field.")

uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    try:
        file_content = uploaded_file.read()
        file_extension = uploaded_file.name[uploaded_file.name.rfind('.'):]

        with st.spinner("🔍 Parsing resume..."):
            parser = ResumeParser(file_content, file_extension)
            extracted_data = parser.parse()

        st.success("✅ Resume parsed successfully!")
        
        name = st.text_input("👤 Name", extracted_data.get("name", ""))
        email = st.text_input("📧 Email", extracted_data.get("email", ""))
        contact_number = st.text_input("📞 Contact Number", extracted_data.get("contact_number", ""))
        education = st.text_area("🎓 Education (Separate each degree with a new line)", "\n".join(extracted_data.get("education", [])))
        skills = st.text_area("🛠️ Skills (Separate with commas)", ", ".join(extracted_data.get("skills", [])))

        st.markdown("---")
        if st.button("📦 Save / Submit"):
            st.success("📝 Final Extracted & Edited Data")
            st.json({
                "name": name,
                "email": email,
                "contact_number": contact_number,
                "education": [line.strip() for line in education.split('\n') if line.strip()],
                "skills": [skill.strip() for skill in skills.split(',') if skill.strip()]
            })

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.info("Please make sure your file is a valid `.pdf` or `.docx` resume.")
