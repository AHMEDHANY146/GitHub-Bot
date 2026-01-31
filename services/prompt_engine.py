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
- ALL output MUST be in English.
- If the user provides input in Arabic, Egyptian, or any other language, TRANSLATE it to professional English.
- NEVER include non-English text in the JSON values.
- STICK TO PROFESSIONAL ENGLISH terminology for technical roles and descriptions.

Extract following information from user's input and return it as a JSON object:

1. **name**: The person's full name (Convert to English/Latin characters).
2. **summary**: A compelling, professional summary in English (3-4 sentences) that:
   - Starts with their role/title and years of experience
   - Highlights their TOP 2-3 areas of expertise with specific technologies
   - Mentions a notable achievement or passion
   - Ends with what makes them unique or their current focus
   
   GOOD EXAMPLES:
   - "Passionate Full-Stack Developer with 3+ years of experience building scalable web applications. Specialized in React, Node.js, and cloud architecture on AWS. Led development of an e-commerce platform serving 50K+ users. Currently exploring AI integration in web apps."
   - "Data Scientist and ML Engineer with expertise in NLP and computer vision. Built production ML pipelines processing 1M+ records using PyTorch and TensorFlow. Open-source contributor passionate about making AI accessible."

3. **skills**: An array of ALL technical skills mentioned in English.
4. **tools**: An array of development tools and platforms in English.
5. **languages**: An array of programming languages.
6. **currently_working_on**: What they're currently working on (TRANSLATED TO ENGLISH).
7. **currently_learning**: What they're currently learning (TRANSLATED TO ENGLISH).
8. **open_to**: What opportunities they're open to (TRANSLATED TO ENGLISH).
9. **fun_fact**: A personal fun fact or interesting detail (TRANSLATED TO ENGLISH).

Guidelines:
- STRICTLY extract ONLY skills mentioned in the input or explicitly provided.
- DO NOT hallucinate or infer skills that are not clearly stated.
- For languages, focus on programming languages specifically.
- Keep skill names lowercase and standardized.
- If information is missing, use null or empty array.

IMPORTANT: EVERYTHING MUST BE IN ENGLISH. Return ONLY the JSON object. No markdown, no explanations, just the raw JSON.
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
- CRITICAL: STRICTLY FORBIDDEN to include Arabic text or any non-English content in any part of the README.
- CRITICAL: TRANSLATE any provided information to professional English if it is in another language.
- CRITICAL: Never include prefixes like "Here's a personalized 'About Me' section for [Name]'s GitHub README:"
- Generate clean, direct content starting immediately with the header or section.

Generate only the README content, no explanations.
"""