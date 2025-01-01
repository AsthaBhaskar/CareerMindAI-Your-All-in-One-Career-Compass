## CareerMind-AI
This platform leverages advanced AI technologies to empower users with career planning, skill development, and job market navigation. The system integrates personalized roadmap creation, real-time job market analysis, and intelligent matching mechanisms to address challenges faced by modern professionals and job seekers.

**Key Features** 
1. Personalized Roadmap Creation
* Creates tailored career plans based on user inputs such as skills, learning preferences, and professional aspirations.
* Utilizes GPT-Neo for generating dynamic and context-aware roadmaps.
* Real-time roadmap generation enabled through a Flask-based API and a user-friendly Streamlit interface.

2. Real-Time Job Market Analysis
* Collects data on employment trends, skills demand, and job distributions using web scraping with Selenium.
* Preprocesses data for consistency and quality, including text normalization and handling of missing values.
* Provides interactive visualizations through Streamlit dashboards, offering insights into job market dynamics like geographic trends and skill needs.

3. Customized ATS 
* Uses cutting-edge tools like Gemini 1.5 Pro to generate detailed career development reports and insights along with ATS and HR Manager Perspective.
* Leverages vector databases and semantic similarity algorithms for efficient candidate-job alignment.

**Technology Stack**

* Backend: Flask, Python
* Frontend: Streamlit
* Database: ChromaDB for vector storage
* AI Models: GPT-Neo, Gemini 1.5 Pro
* Data Handling: Selenium for web scraping, data preprocessing pipelines
