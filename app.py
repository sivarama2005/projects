import streamlit as st
import google.generativeai as genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import os

# Set up Gemini API
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCv6jdoUC3YslqkNj42YNZEhjtWmbBkYEM'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def generate_recipe(ingredients, meal_type, cuisine, cooking_time, complexity):
    prompt = f"""Create a recipe using these ingredients: {ingredients}
    Meal type: {meal_type}
    Cuisine: {cuisine}
    Cooking time: {cooking_time}
    Complexity: {complexity}
    
    Format the recipe as follows:
    Title:
    Ingredients:
    - item 1
    - item 2
    ...
    
    Instructions:
    1. Step 1
    2. Step 2
    ...
    """
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def create_pdf(recipe):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    
    # Set up the document
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.2, 0.4, 0.6)
    c.drawString(margin, height - margin, "AI Generated Recipe")
    
    # Add recipe content
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0, 0, 0)
    y = height - margin - 30
    max_width = width - 2 * margin
    
    def draw_wrapped_text(c, text, x, y, max_width, font_name="Helvetica", font_size=12):
        lines = simpleSplit(text, font_name, font_size, max_width)
        for line in lines:
            if y < margin:
                c.showPage()
                c.setFont(font_name, font_size)
                y = height - margin
            c.drawString(x, y, line)
            y -= font_size + 2
        return y

    for line in recipe.split('\n'):
        if line.strip():
            if line.startswith('Title:'):
                c.setFont("Helvetica-Bold", 18)
                c.setFillColorRGB(0.2, 0.4, 0.6)
                y = draw_wrapped_text(c, line[7:].strip(), margin, y, max_width, "Helvetica-Bold", 18)
                c.setFont("Helvetica", 12)
                c.setFillColorRGB(0, 0, 0)
            elif line == 'Ingredients:':
                c.setFont("Helvetica-Bold", 16)
                c.setFillColorRGB(0.4, 0.6, 0.8)
                y = draw_wrapped_text(c, line, margin, y, max_width, "Helvetica-Bold", 16)
                c.setFont("Helvetica", 12)
                c.setFillColorRGB(0, 0, 0)
            elif line == 'Instructions:':
                c.setFont("Helvetica-Bold", 16)
                c.setFillColorRGB(0.4, 0.6, 0.8)
                y = draw_wrapped_text(c, line, margin, y, max_width, "Helvetica-Bold", 16)
                c.setFont("Helvetica", 12)
                c.setFillColorRGB(0, 0, 0)
            else:
                y = draw_wrapped_text(c, line, margin + 20, y, max_width - 20)
    
    c.save()
    buffer.seek(0)
    return buffer

st.title("AI Recipe Generator")

ingredients = st.text_input("Dish Name", "")
meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
cuisine = st.text_input("Cuisine Preference", "")
cooking_time = st.selectbox("Cooking Time", ["15-30 minutes", "30-60 minutes", "60+ minutes"])
complexity = st.selectbox("Complexity", ["Easy", "Intermediate", "Advanced"])

if st.button("Generate Recipe"):
    with st.spinner("Generating your recipe..."):
        recipe = generate_recipe(ingredients, meal_type, cuisine, cooking_time, complexity)
    
    st.subheader("Generated Recipe")
    st.write(recipe)
    
    pdf = create_pdf(recipe)
    st.download_button(
        label="Download Recipe as PDF",
        data=pdf,
        file_name="recipe.pdf",
        mime="application/pdf"
    )

st.sidebar.markdown("""
## How to use:
1. Enter your ingredients
2. Select meal type
3. Enter cuisine preference
4. Choose cooking time
5. Select complexity level
6. Click 'Generate Recipe'
7. Download the recipe as PDF if desired
""")
