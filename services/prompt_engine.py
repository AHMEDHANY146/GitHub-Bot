from typing import Dict, Any


class PromptEngine:
    """Centralized prompt management for LLM interactions"""
    
    @staticmethod
    def get_personal_info_extraction_prompt() -> str:
        """
        System prompt for extracting personal information from voice messages
        to generate a comprehensive README file
        """
        return """
You are an intelligent assistant specialized in extracting personal information from voice recordings and organizing them into a professional README file.

CRITICAL LANGUAGE INSTRUCTIONS:
- NEVER write Arabic text or any non-English content
- ALWAYS respond in English only
- DO NOT include any Arabic introductions, greetings, or explanations
- ALL output must be in English language exclusively

Your task: Listen to the voice recording and extract all the following personal information:
- Full name
- Age
- Profession/Job
- Location of residence
- Interests and hobbies
- Skills and experience
- Education
- Contact information (if mentioned)
- Any other relevant personal information

Organize this information into a README file with the following format:

# My Personal Profile

## Basic Information
- **Name:** [Extracted name]
- **Age:** [Extracted age]
- **Profession:** [Extracted profession]
- **Location:** [Extracted location]

## Education
[Extracted education information]

## Skills and Experience
[Extracted skills and experience]

## Interests and Hobbies
[Extracted interests and hobbies]

## Contact Information
[Extracted contact information]

## Additional Information
[Any other extracted personal information]

Use English for the entire file. If you cannot extract certain information, leave it empty or write "Not available".
"""

    @staticmethod
    def get_structured_data_schema() -> Dict[str, Any]:
        """
        Schema for structured data extraction from user input
        """
        return {
            "name": "string",
            "summary": "string", 
            "skills": ["python", "react", "docker"],
            "tools": ["git", "github"],
            "languages": ["python", "javascript"],
            "currently_working_on": "string",
            "currently_learning": "string",
            "open_to": "string",
            "fun_fact": "string"
        }

    @staticmethod
    def get_structured_extraction_prompt() -> str:
        """
        Prompt for extracting structured data from user text/voice for modern README template
        """
        return """
You are a professional resume analyzer and GitHub profile optimizer. 

CRITICAL LANGUAGE INSTRUCTIONS:
- NEVER write Arabic text or any non-English content
- ALWAYS respond in English only
- ALL JSON values must be in English
- DO NOT include any Arabic text in extracted data

Extract following information from user's input and return it as a JSON object:

1. **name**: The person's full name
2. **summary**: A brief professional summary (2-3 sentences) about their background and expertise
3. **skills**: An array of ALL technical skills mentioned including:
   - Programming languages (python, javascript, c++, typescript, go, rust, php, swift, kotlin, ruby, scala, r, matlab, etc.)
   - Data science tools (pandas, numpy, tensorflow, pytorch, scikit-learn, jupyter, etc.)
   - Frameworks and libraries (react, vue, angular, django, flask, spring, laravel, express, next, tailwind, bootstrap, etc.)
   - Development methodologies (agile, scrum, devops, etc.)
   - Cloud platforms (aws, azure, gcp, firebase, etc.)
   - Databases (mysql, postgresql, mongodb, sqlite, redis, etc.)
   - DevOps tools (docker, kubernetes, jenkins, git, github, gitlab, etc.)
   - Frontend technologies (html, css, javascript, typescript, etc.)
   - Backend technologies (nodejs, express, django, flask, etc.)
   - Mobile development (react native, flutter, swift, kotlin, etc.)
   - Business intelligence tools (power bi, tableau, etc.)
4. **tools**: An array of development tools and platforms they use (git, github, docker, kubernetes, aws, azure, power bi, tableau, etc.)
5. **languages**: An array of programming languages they know (focus on core languages: python, javascript, c++, typescript, go, rust, php, swift, kotlin, ruby, scala, r, matlab, etc.)
6. **currently_working_on**: What they're currently working on (extract from their description)
7. **currently_learning**: What they're currently learning (extract from their description)
8. **open_to**: What opportunities they're open to (extract from their description)
9. **fun_fact**: A personal fun fact or interesting detail about them (extract from their description)

Guidelines:
- BE COMPREHENSIVE: Extract ALL mentioned technologies, skills, and tools
- Include both hard skills (technologies) and domain-specific skills
- For skills, include ANY technical term mentioned (even if you're not sure about the category)
- For tools, include development tools, platforms, and services
- For languages, focus on programming languages specifically
- Separate different types of technologies appropriately but don't miss any
- If information is missing, use null or empty array
- Keep skill names lowercase and standardized (e.g., "javascript" not "JavaScript", "python" not "Python")
- Be comprehensive but accurate - extract what's mentioned, don't invent completely new information
- Look for indicators of data science, machine learning, web development, mobile development, etc.
- For currently_working_on, look for phrases like "I'm working on", "Currently building", "My current project"
- For currently_learning, look for phrases like "I'm learning", "Studying", "Currently exploring"
- For open_to, look for phrases like "Looking for", "Open to", "Interested in"
- For fun_fact, look for personal details, hobbies, or interesting facts they mention

Examples of good extraction:
- "I work with python, tensorflow, and react" → skills: ["python", "tensorflow", "react"], languages: ["python"]
- "I use Power BI, Tableau, and Git for my projects" → skills: ["power bi", "tableau", "git"], tools: ["power bi", "tableau", "git"]
- "I develop web apps with react, javascript, and next.js" → skills: ["react", "javascript", "next.js"], languages: ["javascript"]
- "I'm experienced in docker, kubernetes, and aws deployment" → skills: ["docker", "kubernetes", "aws"], tools: ["docker", "kubernetes", "aws"]
- "I'm currently working on a machine learning project for healthcare" → currently_working_on: "a machine learning project for healthcare"
- "I'm learning Kubernetes and advanced React patterns" → currently_learning: "Kubernetes and advanced React patterns"
- "I'm open to freelance opportunities and collaborations" → open_to: "freelance opportunities and collaborations"

IMPORTANT: Extract as many relevant skills, tools, and languages as possible. Don't limit the extraction - be thorough.

Return ONLY the JSON object. No markdown, no explanations, just the raw JSON.
"""

    @staticmethod
    def get_readme_generation_prompt(structured_data: Dict[str, Any]) -> str:
        """
        Generate a modern README based on structured data using the new template
        """
        return f"""
Generate a modern, professional GitHub README.md file based on the following structured data:

{structured_data}

Requirements:
1. Use the modern template format with HTML alignment and proper structure
2. Include centered header with professional subtitle based on skills
3. Add profile badges (views, followers, LinkedIn, Email)
4. Create About Me section with right-aligned gif and bullet points
5. Organize Tech Stack into sections: Programming Languages, Data Science & ML, Tools & Technologies
6. Use Devicon icons for all technologies where available
7. Include GitHub Stats section with dark theme
8. Add snake animation at the end
9. Use proper HTML alignment (align="center", align="left", align="right")
10. Include proper spacing and visual hierarchy

Template Structure:
- Centered H1 header with "Hello, I'm [Name]"
- H3 subtitle based on professional focus
- Centered badges div
- About Me section with gif and bullet points
- Tech Stack sections with icon grids
- GitHub Stats with three cards
- Snake animation

Special Instructions:
- Use "yourusername" as GitHub username placeholder
- Use "your.email@example.com" as email placeholder
- For data science profiles, emphasize ML/AI focus
- Use dark theme for GitHub stats
- Include proper HTML div structure
- CRITICAL: Never include Arabic text or any non-English introductions in the About Me section
- CRITICAL: Never include prefixes like "Here's a personalized 'About Me' section for [Name]'s GitHub README:"
- Generate clean, direct About Me content starting immediately with the introduction

Generate only the README content, no explanations.
"""