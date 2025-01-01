import base64
import json
import pandas as pd
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv
import plotly.express as px
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
import requests

# Load API key from environment variable
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("DataScience_jobs.csv", index_col=0)
    df = df.dropna()
    df = df.apply(lambda x: x.astype(str).str.lower())
    df['skills'] = df['skills'].str.split('\n')
    df['locations'] = df['locations'].str.split(',')
    return df
input_prompt1 = """
You are an experienced Human Resource Manager, your task is to review the provided resume against the job description for a {role}.
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
As a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
evaluate the resume against the provided job description for a {role}. Give the percentage match if the resume matches
the job description. First the output should come as a percentage, then keywords missing and last final thoughts.
"""

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            first_page = images[0]

            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }
            ]
            return pdf_parts
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
        return None
    else:
        st.error("No file uploaded")
        return None

# ------------------ Streamlit UI Configuration ------------------ #

st.set_page_config(
    page_title="ATS SYSTEM",
    page_icon=":document:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------ Sidebar ------------------ #

st.sidebar.markdown("<h1 style='text-align: center; text-decoration: underline; font-size: 2.5em;'>CareerMind AI: Your All-in-One Career Compass</h1>", unsafe_allow_html=True)
st.sidebar.markdown("""
### 🎯 Key Features:
- AI-powered Resume Analysis
- Personalized Career Roadmaps
- ATS Optimization Insights
- Skill Gap Analysis

### 💡 Benefits:
- Make informed career decisions
- Create ATS-optimized resumes
- Get tailored learning paths
- Track your career growth
""")

# Add divider
st.sidebar.markdown("---")


# ------------------ Main App UI ------------------ #
# Add custom CSS to style the tabs
st.markdown("""
    <style>
    .big-tabs {
        font-size: 25px;
    }
    button[data-baseweb="tab"] {
        font-size: 20px;
    }
    button[data-baseweb="tab"] p {
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create tabs with custom styling
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "**About**",
    "**ATS**", 
    "**Career Roadmap**",
    "**Job Market Analysis**",
    "**FAQs**"
])

with tab1:
    st.header("Welcome to CareerMind AI!")
    st.subheader("Your all-in-one solution for job search, skill enhancement, and career development.")
    st.markdown(
        "CareerMind AI is an innovative platform designed to empower job seekers, students, and professionals in navigating the complex career landscape with confidence and precision. This unified platform combines the power of advanced AI technologies and real-time data analysis to provide holistic career guidance and support."
    )
    st.subheader("What makes CareerMind AI unique?")
    st.markdown(
        "1. Custom ATS Analysis: Upload your resume, input a job description, and receive a comprehensive ATS report. Our system evaluates your strengths and weaknesses, identifies missing keywords, highlights skill gaps, and provides actionable insights to optimize your resume for the desired role. Side-by-side comparisons of your resume and job descriptions make it easier than ever to align your application with HR expectations."
    )
    st.markdown("2. Personalized Roadmap Generator: Based on your career aspirations, existing skills, and learning preferences, CareerMind AI generates tailored roadmaps. These step-by-step guides outline the skills, resources, and paths you need to achieve your goals. Built on advanced language models, this feature ensures every roadmap is both practical and personalized.")
    st.markdown("3. Real-Time Job Market Insights: Stay ahead of the curve with real-time analysis of emerging job trends, in-demand skills, and salary patterns. Our system uses web scraping, machine learning, and interactive data visualizations to deliver insights that empower you to make data-driven career decisions.")
    
    st.subheader("Why CareerMind AI?")
    st.markdown("Whether you're a student exploring career options, a job seeker aiming to land your dream role, or a professional looking to upskill, CareerMind AI is your ultimate partner. By bridging the gap between individual capabilities and market demands, we help you maximize your potential and stay competitive in an ever-changing job market.")
    st.subheader("Get Started Today:")
    st.markdown("1. Upload your resume: Drag and drop your resume or upload it directly.")
    st.markdown("2. Enter job description: Provide the job description you're targeting for a more tailored analysis. Our system will analyze your resume and provide you with a comprehensive report.")
    st.markdown("3. Enter your preferences: Specify your career goals, skills, or job descriptions for tailored recommendations. Access a detailed analysis and personalized guidance to boost your career prospects.")

    st.subheader("Transform your career journey with CareerMind AI—because your potential deserves the best tools to shine!")

with tab2:
    st.title('ATS Insights')
    st.subheader('Upload the resume below and enter the job description to analyze the input resume and check HR and ATS perspective')

    # Two column layout for the main app content
    col1, col2 = st.columns([1, 1])

    with col1:
        job_roles = ["Software Engineer","GenAI", "Data Scientist", "Product Manager", "Designer", "Marketing Specialist"]
        selected_role = st.selectbox("Select Job Role", job_roles)
        input_text = st.text_area("Job Description", key="input")
        
    uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

    if uploaded_file is not None:
        st.success("PDF Uploaded Successfully")

    analysis_choice = st.selectbox("Select Analysis Type",
                                   ["HR Manager Perspective", "ATS Scanner Perspective"])

    submit_button = st.button("Analyze")

    if submit_button:
        with st.spinner("Processing..."):
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content:
                role = selected_role
                if analysis_choice == "HR Manager Perspective":
                    prompt = input_prompt1.format(role=role)
                else:
                    prompt = input_prompt2.format(role=role)
                response = get_gemini_response(input_text, pdf_content, prompt)
                st.subheader("Analysis Result")
                st.write(response)

    # Layout for displaying job description and resume side by side
    if uploaded_file and input_text:
        st.markdown("## Comparison View")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Job Description")
            st.write(input_text)

        with col2:
            st.markdown("### Resume Preview")
            try:
                images = pdf2image.convert_from_bytes(uploaded_file.read())
                st.image(images[0], use_column_width=True)
            except Exception as e:
                st.error(e)

with tab3:
    st.title('🎯 Career Roadmap Generator')
    st.write("Generate a personalized learning roadmap based on your career goals and preferences.")

    career_goal = st.text_area(
        "What is your career goal?",
        placeholder="E.g., Become a Full Stack Developer, Data Scientist, etc.",
        help="Be specific about the role or position you want to achieve"
    )

    skills_input = st.text_area(
        "What are your current skills? (Enter each skill on a new line)",
        placeholder="Python\nJavaScript\nSQL\nGit",
        help="List your current technical and non-technical skills"
    )
    
    skills = [skill.strip() for skill in skills_input.split("\n") if skill.strip()]

    learning_preference = st.selectbox(
        "What is your preferred learning style?",
        options=[
            "Self-paced online courses",
            "Interactive tutorials",
            "Video lectures",
            "Books and documentation",
            "Project-based learning",
            "Structured bootcamp"
        ],
        help="Select the learning method that works best for you"
    )

    if st.button("Generate Roadmap", type="primary"):
        if not career_goal or not skills or not learning_preference:
            st.error("Please fill in all fields before generating the roadmap.")
        else:
            with st.spinner("Generating your personalized roadmap..."):
                try:
                    data = {
                        "career_goal": career_goal,
                        "skills": skills,
                        "learning_preference": learning_preference
                    }

                    response = requests.post(
                        "http://localhost:5000/generate-roadmap",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        roadmap = response.json()["roadmap"]
                        st.success("🎉 Your roadmap has been generated!")
                        st.markdown("### Your Personalized Learning Roadmap")
                        st.markdown(roadmap)
                        
                        st.download_button(
                            label="Download Roadmap",
                            data=roadmap,
                            file_name="career_roadmap.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error occurred')}")

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend server. Please make sure it's running.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with st.sidebar:
        st.markdown("### 💡 Tips for Better Results")
        st.markdown("""
        1. Be specific about your career goal
        2. List all relevant skills, even basic ones
        3. Choose a learning style that motivates you
        """)

with tab4:
    st.markdown("# 📊 Data Science Job Market Analysis")
    
    try:
        df = load_data()
        
        # Job Overview section with metrics
        st.markdown("## 📈 Job Market Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Jobs", len(df))
        with col2:
            st.metric("Unique Companies", df['companies'].nunique())
        with col3:
            st.metric("Unique Locations", sum(len(locations) for locations in df['locations']))

        # Create two columns for the first row of visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Location-wise Job Distribution")
            location_data = df.locations.explode().str.strip().value_counts().head(10)
            fig_location = px.pie(
                values=location_data.values,
                names=location_data.index,
                title="Top 10 Cities for Data Science Jobs",
                hole=0.4,
            )
            st.plotly_chart(fig_location, use_container_width=True)

        with col2:
            st.subheader("Top Companies Hiring")
            company_data = df['companies'].value_counts().head(10)
            fig_companies = px.bar(
                x=company_data.index,
                y=company_data.values,
                title="Top 10 Companies with Most Job Postings",
                labels={'x': 'Company', 'y': 'Number of Job Postings'}
            )
            fig_companies.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_companies, use_container_width=True)
        # Add Job Listings Section before Skills Analysis
        st.markdown("## 💼 Job Listings")
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            companies_filter = st.multiselect(
                "Filter by Company",
                options=sorted(df['companies'].unique()),
                default=[]
            )
        with col2:
            experience_filter = st.multiselect(
                "Filter by Experience",
                options=sorted(df['experience'].unique()),
                default=[]
            )

        # Filter the dataframe based on filters
        filtered_df = df.copy()
        if companies_filter:
            filtered_df = filtered_df[filtered_df['companies'].isin(companies_filter)]
        if experience_filter:
            filtered_df = filtered_df[filtered_df['experience'].isin(experience_filter)]

        # Display job listings
        st.write(f"Showing {len(filtered_df)} jobs")
        for idx, row in filtered_df.iterrows():
            with st.expander(f"{row['roles']} at {row['companies']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Company:** {row['companies'].title()}")
                    st.markdown(f"**Experience Required:** {row['experience']}")
                with col2:
                    st.markdown(f"**Location(s):** {', '.join(loc.strip().title() for loc in row['locations'])}")
                    st.markdown(f"**Skills Required:** {', '.join(skill.strip().title() for skill in row['skills'])}")


        # Skills Analysis Section
        st.markdown("## 🎯 Skills Analysis")
        
        # Process skills data
        skills_data = df.skills.explode().value_counts()

        # Create tabs for different skill categories
        tab1, tab2, tab3, tab4 = st.tabs(["Core Skills", "Programming Languages", "Frameworks & Tools", "Cloud & Big Data"])

        with tab1:
            core_skills = {
                'Machine Learning': skills_data[skills_data.index.str.contains('machine|ml', case=False)].sum(),
                'Data Mining': skills_data[skills_data.index.str.contains('mining', case=False)].sum(),
                'Statistics': skills_data[skills_data.index.str.contains('stat', case=False)].sum(),
                'NLP': skills_data[skills_data.index.str.contains('nlp|natural', case=False)].sum(),
                'Deep Learning': skills_data[skills_data.index.str.contains('deep learning', case=False)].sum(),
                'Computer Vision': skills_data[skills_data.index.str.contains('computer vision', case=False)].sum()
            }
            fig_core = px.bar(
                x=list(core_skills.keys()),
                y=list(core_skills.values()),
                title="Core Data Science Skills in Demand",
                color=list(core_skills.values()),
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_core, use_container_width=True)

        with tab2:
            programming_langs = {
                'Python': skills_data[skills_data.index.str.contains('python', case=False)].sum(),
                'R': skills_data[skills_data.index.str.contains('^r$', case=False)].sum(),
                'SQL': skills_data[skills_data.index.str.contains('sql', case=False)].sum(),
                'Java': skills_data[skills_data.index.str.contains('java$', case=False)].sum(),
                'C++': skills_data[skills_data.index.str.contains('c\+\+', case=False)].sum()
            }
            fig_lang = px.pie(
                values=list(programming_langs.values()),
                names=list(programming_langs.keys()),
                title="Programming Languages Distribution",
                hole=0.4
            )
            st.plotly_chart(fig_lang, use_container_width=True)

        with tab3:
            frameworks = {
                'TensorFlow': skills_data[skills_data.index.str.contains('tensor', case=False)].sum(),
                'PyTorch': skills_data[skills_data.index.str.contains('torch', case=False)].sum(),
                'Keras': skills_data[skills_data.index.str.contains('keras', case=False)].sum(),
                'Tableau': skills_data[skills_data.index.str.contains('tableau', case=False)].sum(),
                'Power BI': skills_data[skills_data.index.str.contains('power bi', case=False)].sum()
            }
            fig_frameworks = px.bar(
                x=list(frameworks.keys()),
                y=list(frameworks.values()),
                title="Frameworks and Tools Usage",
                color=list(frameworks.values()),
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_frameworks, use_container_width=True)

        with tab4:
            cloud_bigdata = {
                'AWS': skills_data[skills_data.index.str.contains('aws', case=False)].sum(),
                'Azure': skills_data[skills_data.index.str.contains('azure', case=False)].sum(),
                'GCP': skills_data[skills_data.index.str.contains('gcp', case=False)].sum(),
                'Spark': skills_data[skills_data.index.str.contains('spark', case=False)].sum(),
                'Hadoop': skills_data[skills_data.index.str.contains('hadoop', case=False)].sum()
            }
            fig_cloud = px.bar(
                x=list(cloud_bigdata.keys()),
                y=list(cloud_bigdata.values()),
                title="Cloud & Big Data Technologies",
                color=list(cloud_bigdata.values()),
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_cloud, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading or processing data: {str(e)}")
        st.info("Please ensure the 'DataScience_jobs.csv' file is in the same directory as this script.")


with tab5:
    st.title('Frequently Asked Questions(FAQs)')
    st.markdown(""" Q. What is CareerMind AI?""")
    st.markdown("Ans. CareerMind AI is an AI-powered unified platform designed to assist job seekers, students, and professionals by offering ATS resume analysis, personalized learning roadmaps, and real-time job market insights.")
    st.markdown("Q. How does CareerMind AI analyze my resume?")
    st.markdown("Ans. CareerMind AI uses advanced AI models to evaluate your resume against job descriptions and roles. It identifies strengths, weaknesses, missing keywords, skill gaps, and provides a comprehensive ATS percentage score along with actionable feedback to optimize your resume.")
    st.markdown("Q. What is the Personalized Roadmap Generator?")
    st.markdown("Ans. This feature creates a step-by-step learning plan tailored to your career goals, skills, and preferences. It guides you on what skills to learn, resources to use, and the best paths to achieve your objectives.")
    st.markdown("Q. Is CareerMind AI free to use?")
    st.markdown("Ans. Yes! It is absolutely free to use.")
    st.markdown("Q. How do I get started?")
    st.markdown("Ans. Simply upload your resume, enter a job description or career goal, and let CareerMind AI analyze and generate insights for you.")
    st.markdown("""---""")