import streamlit as st
from tempfile import NamedTemporaryFile
from PIL import Image
import base64
from jamaibase import JamAI, protocol as p


# Initialize JamAI client
jamai = JamAI(token="API KEY HERE", project_id="PROJECT_ID_KEY_HERE")


# Set up Streamlit app with custom styles
st.markdown(
    """
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        font-family: 'Verdana', sans-serif;
        color: #4B0082;
        text-align: center;
        margin-bottom: 20px;
    }
    .output-card {
        background-color: #333;
        color: #FFF;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
    }
    .output-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    body {
        background-color: #1E1E1E;
        color: #FFFFFF;
        font-family: 'Verdana', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<div class="title">demo fraud template⋆</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a file or image", type=["jpg", "jpeg"]) #to upload files

if uploaded_file is not None:
    # Display uploaded file details
    st.write("Filename:", uploaded_file.name)

    # Store the uploaded file as a temporary file in JPEG format
    with NamedTemporaryFile(delete=False, suffix=".jpeg") as temp_file:
        if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            image = Image.open(uploaded_file)
            image = image.convert("RGB")
            image.save(temp_file, format="JPEG")
        else:
            st.error("Only image files (jpg, jpeg, png) are supported for conversion.")
            st.stop()
        temp_file_path = temp_file.name

    # Upload the file to JamAI action tables
    upload_response = jamai.file.upload_file(temp_file_path)

    # Add file URI to the action table named 'poetry_bot' (non-streaming)
    completion = jamai.table.add_table_rows(
        "action",
        p.RowAddRequest(
            table_id="Dataa",  # action table name
            data=[dict(image=upload_response.uri)],  # make sure to rename the "image" with the input column name in your action table
            stream=False,
        ),
    )

    # Display the uploaded image
    image_bytes = uploaded_file.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode()
    st.image(f"data:image/jpeg;base64,{encoded_image}", width=300, caption="Uploaded Image")

    # Display response
    if completion.rows:
        st.success("File added to the verification table successfully.")
    else:
        st.error("Failed to add the file to the verification table.")

    # Retrieve columns from the action table and display dynamically
    rows = jamai.table.list_table_rows("action", "Dataa")
    if rows.items:
        row = rows.items[0]  # Only display the first set of results to avoid duplication
        llm1 = row.get("text", {}).get("value", "N/A")
        llm2 = row.get("fraud-chances", {}).get("value", "N/A")
        llm3 = row.get("explanation", {}).get("value", "N/A")

        st.subheader("Generated Poetry Output")
        st.markdown(f'<div class="output-card"><div class="output-title">text</div><p>{llm1}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="output-card"><div class="output-title">fraud chances</div><p>{llm2}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="output-card"><div class="output-title">explanation</div><p>{llm3}</p></div>', unsafe_allow_html=True)
else:
    st.write("Please upload a file or image to proceed.")