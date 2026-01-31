"""
Common Skills List for Skill Selection Feature
Organized by category for easy navigation
"""

# Programming Languages
LANGUAGES = [
    "python", "javascript", "typescript", "java", "c", "c++", "c#", "go", "rust",
    "php", "swift", "kotlin", "ruby", "scala", "r", "matlab", "dart", "lua",
    "objective-c", "perl", "haskell", "elixir", "clojure", "f#", "assembly"
]

# Frontend Technologies
FRONTEND = [
    "react", "vue", "angular", "next.js", "nuxt.js", "svelte", "html", "css",
    "sass", "tailwind", "bootstrap", "jquery", "redux", "webpack", "vite",
    "material ui", "chakra ui", "ant design", "styled-components", "emotion"
]

# Backend Technologies
BACKEND = [
    "node.js", "express", "django", "flask", "fastapi", "spring", "laravel",
    "rails", "asp.net", "graphql", "rest api", "microservices", "nestjs",
    "koa", "hapi", "gin", "fiber", "actix", "rocket"
]

# Data Science & AI
DATA_SCIENCE = [
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "jupyter", "opencv", "nltk", "spacy",
    "machine learning", "deep learning", "nlp", "computer vision", "rag",
    "langchain", "llamaindex", "hugging face", "transformers", "stable diffusion",
    "generative ai", "llm", "openai", "anthropic", "gemini", "cohere"
]

# Databases
DATABASES = [
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "firebase",
    "supabase", "dynamodb", "elasticsearch", "cassandra", "neo4j",
    "mariadb", "oracle", "sql server", "couchdb", "influxdb", "pinecone", "qdrant"
]

# DevOps & Cloud
DEVOPS = [
    "docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "github actions",
    "gitlab ci", "terraform", "ansible", "nginx", "linux", "bash",
    "circleci", "travis ci", "prometheus", "grafana", "datadog", "heroku", "vercel", "netlify"
]

# Mobile Development
MOBILE = [
    "react native", "flutter", "android", "ios", "xamarin", "ionic",
    "swift ui", "jetpack compose", "expo", "capacitor"
]

# Tools & Platforms
TOOLS = [
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
    "figma", "postman", "vscode", "intellij", "power bi", "tableau", "excel",
    "notion", "trello", "asana", "selenium", "playwright", "cypress",
    "streamlit", "gradio", "airflow", "celery", "rabbitmq", "kafka"
]

# All skills combined (for easy iteration)
ALL_SKILLS = {
    "languages": LANGUAGES,
    "frontend": FRONTEND,
    "backend": BACKEND,
    "data_science": DATA_SCIENCE,
    "databases": DATABASES,
    "devops": DEVOPS,
    "mobile": MOBILE,
    "tools": TOOLS
}

# Flat list of all skills
ALL_SKILLS_FLAT = (
    LANGUAGES + FRONTEND + BACKEND + DATA_SCIENCE + 
    DATABASES + DEVOPS + MOBILE + TOOLS
)

def get_skill_category(skill: str) -> str:
    """Get the category of a skill"""
    skill_lower = skill.lower()
    for category, skills in ALL_SKILLS.items():
        if skill_lower in skills:
            return category
    return "other"

def get_all_skills_by_category() -> dict:
    """Get all skills organized by category"""
    return ALL_SKILLS.copy()

def get_popular_skills(limit: int = 50) -> list:
    """Get most popular/common skills for quick selection"""
    popular = [
        # Top languages
        "python", "javascript", "typescript", "java", "c", "c++", "go",
        # Top frontend
        "react", "vue", "next.js", "html", "css", "tailwind", "angular",
        # Top backend
        "node.js", "django", "flask", "fastapi", "express", "spring",
        # Top data science/AI
        "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
        "machine learning", "deep learning", "langchain", "openai", "llm",
        # Top databases
        "mysql", "postgresql", "mongodb", "redis", "sqlite", "supabase",
        # Top devops
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
        "github actions", "vercel", "heroku",
        # Top mobile
        "react native", "flutter", "android", "ios",
        # Top tools
        "github", "vscode", "figma", "postman", "selenium", "streamlit"
    ]
    return popular[:limit]
