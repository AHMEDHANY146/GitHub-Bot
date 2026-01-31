from typing import Dict, List, Optional
from devicon.resolver import DeviconResolver
from services.llm.LLMProviderFactory import LLMProviderFactory



class MarkdownGenerator:
    """Markdown generation utilities for README files"""
    
    def __init__(self):
        self.devicon_resolver = DeviconResolver()
        try:
            self.llm_provider = LLMProviderFactory.get_default_provider()
        except ValueError:
            self.llm_provider = None
    
    def generate_readme(self, structured_data: Dict[str, any]) -> str:
        """
        Generate a complete README.md file from structured data using modern template
        
        Args:
            structured_data: Dictionary containing user information
            
        Returns:
            Complete README.md content as string
        """
        sections = []
        
        # Header with badges
        sections.append(self._generate_modern_header(structured_data))
        
        # About Me section with gif
        if structured_data.get('summary'):
            sections.append(self._generate_modern_about_section(structured_data))
        
        # Tech Stack sections - combine ALL skills from different sources
        all_skills = []
        
        # Add programming languages
        if structured_data.get('languages'):
            all_skills.extend(structured_data['languages'])
        
        # Add skills/technologies
        if structured_data.get('skills'):
            all_skills.extend(structured_data['skills'])
        
        # Add tools
        if structured_data.get('tools'):
            all_skills.extend(structured_data['tools'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in all_skills:
            skill_lower = skill.lower().strip()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        if unique_skills:
            # Pass languages as exclusion list to avoid duplicates
            excluded_langs = structured_data.get('languages', [])
            sections.append(self._generate_skills_section(unique_skills, exclude=excluded_langs))
        
        # Snake animation (GitHub username is now required)
        if structured_data.get('github'):
            sections.append(self._generate_snake_animation(structured_data))
        
        return '\n\n'.join(sections)
    
    def _generate_modern_header(self, structured_data: Dict[str, any]) -> str:
        """Generate modern README header with badges and alignment"""
        github_username = structured_data.get('github', '')
        
        # Create a professional subtitle based on skills
        subtitle = self._generate_subtitle(structured_data)
        
        # Generate profile header based on style preference
        profile_header = self._generate_profile_header(structured_data, github_username)
        
        badges = self._generate_profile_badges(structured_data)
        
        return f"""{profile_header}

<h3 align="center">{subtitle}</h3>

<div align="center">

{badges}

</div>

---

<div align="left">"""
    
    def _generate_subtitle(self, structured_data: Dict[str, any]) -> str:
        """Generate professional subtitle using AI"""
        # Use AI to generate personalized subtitle and about content together
        subtitle, _ = self._generate_subtitle_and_about(structured_data)
        
        if subtitle:
            return subtitle
        else:
            # Fallback to basic subtitle if AI is not available
            name = structured_data.get('name', 'Developer')
            return f"👨‍💻 Software Developer | 🚀 Tech Enthusiast"
    
    def _generate_profile_badges(self, structured_data: Dict[str, any]) -> str:
        """Generate profile badges - GitHub username is required"""
        github_username = structured_data.get('github', '')
        
        # GitHub username is mandatory for badges
        if not github_username:
            return ""  # Return empty if no GitHub username
        
        badges = []
        
        # GitHub badges (always included if username exists)
        badges.append(f'[![Profile Views](https://komarev.com/ghpvc/?username={github_username}&label=Profile%20views&color=0e75b6&style=flat)](https://github.com/{github_username})')
        badges.append(f'[![GitHub Followers](https://img.shields.io/github/followers/{github_username}?style=social)](https://github.com/{github_username})')
        
        # Only add LinkedIn badge if URL is provided
        linkedin_url = structured_data.get('linkedin', '')
        if linkedin_url:
            badges.append('[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white)](' + linkedin_url + ')')
        
        # Only add Email badge if email is provided
        email = structured_data.get('email', '')
        if email:
            badges.append(f'[![Email](https://img.shields.io/badge/Email-Contact%20Me-red?style=flat&logo=gmail)](mailto:{email})')
        
        return '\n'.join(badges)
    
        
    def _generate_modern_about_section(self, structured_data: Dict[str, any]) -> str:
        """Generate modern About Me section without images"""
        # Validate and clean structured data first
        structured_data = self._validate_structured_data(structured_data)
        
        summary = structured_data.get('summary', '')
        email = structured_data.get('email', '')
        
        # Build the reach me line only if email is provided
        reach_me_line = ""
        if email:
            reach_me_line = f"  - 📫 Reach me at: {email}"
        
        # Use generic About Me title
        personal_intro = "## 👋 About Me"
        
        # Generate dynamic content based on user profile
        dynamic_content = self._generate_dynamic_about_content(structured_data)
        
        return f"""{personal_intro}

<div align="left">
  
  {summary}
  
{dynamic_content}
{reach_me_line}

</div>

---

## 🛠️ Tech Stack"""
    
    def _generate_programming_languages_section(self, languages: List[str]) -> str:
        """Generate Programming Languages section with icons"""
        valid_languages = self.devicon_resolver.filter_valid_skills(languages)
        language_icons = self.devicon_resolver.get_skill_icons(valid_languages)
        
        if not language_icons:
            return "### Programming Languages\n" + ', '.join(languages)
        
        # Generate language entries with icons
        language_entries = []
        for language in valid_languages:
            icon_url = language_icons.get(language)
            if icon_url:
                language_entries.append(f'  <img src="{icon_url}" height="40" alt="{language} logo" title="{language}" />')
            else:
                language_entries.append(f'  <strong>{language.title()}</strong>')
        
        languages_text = '\n'.join(language_entries)
        return f"""### 💻 Programming Languages

<div align="left">
{languages_text}
</div>"""
    
    def _generate_skills_section(self, skills: List[str], exclude: List[str] = None) -> str:
        """Generate unified Tech Stack section with all icons"""
        if not skills:
            return ""
            
        # Filter out excluded skills (like those already shown in languages)
        if exclude:
            exclude_set = {s.lower().strip() for s in exclude}
            skills = [s for s in skills if s.lower().strip() not in exclude_set]
        
        if not skills:
            return ""
        
        # Generate skill entries for ALL skills
        skill_entries = self._generate_skill_entries(skills)
        
        if not skill_entries:
            return ""
            
        skills_text = '\n'.join(skill_entries)
        
        return f"""<div align="left">
{skills_text}
</div>"""
    
    def _generate_skill_entries(self, skills: List[str]) -> List[str]:
        """Generate HTML entries for skills with icons - includes text fallback"""
        skill_entries = []
        
        # Get icons for all skills
        skill_icons = self.devicon_resolver.get_skill_icons(skills)
        
        # Custom icon mappings for popular tools not in standard devicon
        custom_icons = {
            # Data Science
            'scikit': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg',
            'sklearn': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg',
            'scikit-learn': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg',
            'pandas': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg',
            'numpy': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg',
            'matplotlib': 'https://upload.wikimedia.org/wikipedia/commons/8/84/Matplotlib_icon.svg',
            'jupyter': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jupyter/jupyter-original.svg',
            'opencv': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg',
            
            # Concepts/Abstract
            'machine learning': 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Tensorflow_logo.svg', # Using TF as proxy
            'deep learning': 'https://upload.wikimedia.org/wikipedia/commons/1/10/PyTorch_logo_icon.svg', # Using PyTorch as proxy
            'sql': 'https://upload.wikimedia.org/wikipedia/commons/8/87/Sql_data_base_with_logo.png',
            'excel': 'https://upload.wikimedia.org/wikipedia/commons/7/73/Microsoft_Excel_2013-2019_logo.svg',
            
            # AI/ML
            'tensorflow': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tensorflow/tensorflow-original.svg',
            'pytorch': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg',
            'keras': 'https://upload.wikimedia.org/wikipedia/commons/a/ae/Keras_logo.svg',
            'langchain': 'https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/static/img/brand/langchain_logo.svg',
            'huggingface': 'https://huggingface.co/front/assets/huggingface_logo.svg',
            'hugging face': 'https://huggingface.co/front/assets/huggingface_logo.svg',
            'openai': 'https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg',
            'gemini': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg',
            'cohere': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Cohere_logo.png/640px-Cohere_logo.png',
            
            # BI Tools
            'power bi': 'https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg',
            'powerbi': 'https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg',
            'tableau': 'https://cdn.worldvectorlogo.com/logos/tableau-software.svg',
            
            # Backend
            'fastapi': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg',
            'flask': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg',
            'django': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg',
            'express': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/express/express-original.svg',
            'nestjs': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nestjs/nestjs-original.svg',
            'graphql': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/graphql/graphql-plain.svg',
            
            # Frontend
            'next.js': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg',
            'nextjs': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg',
            'nuxt': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nuxtjs/nuxtjs-original.svg',
            'nuxt.js': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nuxtjs/nuxtjs-original.svg',
            'tailwind': 'https://upload.wikimedia.org/wikipedia/commons/d/d5/Tailwind_CSS_Logo.svg',
            'tailwindcss': 'https://upload.wikimedia.org/wikipedia/commons/d/d5/Tailwind_CSS_Logo.svg',
            'vite': 'https://upload.wikimedia.org/wikipedia/commons/f/f1/Vitejs-logo.svg',
            'svelte': 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Svelte_Logo.svg',
            
            # Databases
            'supabase': 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Supabase_logo.svg',
            'firebase': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/firebase/firebase-plain.svg',
            'redis': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg',
            'mongodb': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg',
            'postgresql': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg',
            'mysql': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg',
            'sqlite': 'https://upload.wikimedia.org/wikipedia/commons/3/38/SQLite370.svg',
            
            # DevOps
            'docker': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg',
            'kubernetes': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kubernetes/kubernetes-plain.svg',
            'github actions': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/githubactions/githubactions-original.svg',
            'terraform': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/terraform/terraform-original.svg',
            'ansible': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ansible/ansible-original.svg',
            'jenkins': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jenkins/jenkins-original.svg',
            'nginx': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nginx/nginx-original.svg',
            'linux': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg',
            'bash': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bash/bash-original.svg',
            
            # Cloud
            'aws': 'https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg',
            'azure': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/azure/azure-original.svg',
            'gcp': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg',
            'heroku': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/heroku/heroku-original.svg',
            'vercel': 'https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png',
            
            # Mobile
            'flutter': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flutter/flutter-original.svg',
            'react native': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg',
            'android': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/android/android-original.svg',
            'ios': 'https://upload.wikimedia.org/wikipedia/commons/6/64/Android_logo_2019_%28stacked%29.svg', # Placeholder fallback
            'swift': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/swift/swift-original.svg',
            'kotlin': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kotlin/kotlin-original.svg',
            
            # Languages
            'python': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg',
            'javascript': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg',
            'typescript': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg',
            'java': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg',
            'c': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/c/c-original.svg',
            'c++': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg',
            'c#': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg',
            'go': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg',
            'rust': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rust/rust-original.svg',
            'php': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg',
            'ruby': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ruby/ruby-original.svg',
            'r': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/r/r-original.svg',
            
            # Tools
            'git': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg',
            'github': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg',
            'vscode': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg',
            'figma': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/figma/figma-original.svg',
            'postman': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postman/postman-original.svg',
            'selenium': 'https://upload.wikimedia.org/wikipedia/commons/d/d5/Selenium_Logo.png',
            'streamlit': 'https://streamlit.io/images/brand/streamlit-mark-color.svg',
        }
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            
            # First check if we have an icon from devicon
            icon_url = skill_icons.get(skill)
            
            # If not, check custom icons (try exact match first)
            if not icon_url:
                icon_url = custom_icons.get(skill_lower)
            
            # If still not, try partial match in custom icons
            if not icon_url:
                for key, url in custom_icons.items():
                    if key == skill_lower: # Exact match has priority
                         icon_url = url
                         break
            
            # Final attempt: try to find loose match
            if not icon_url:
                for key, url in custom_icons.items():
                     if key in skill_lower:
                         icon_url = url
                         break

            # Add skill entry (Image if found, formatted text badge if not)
            if icon_url:
                skill_entries.append(f'  <img src="{icon_url}" height="40" alt="{skill} logo" title="{skill.title()}" />')
            else:
                # Fallback to Shields.io badge for missing icons so it's not hidden
                encoded_skill = skill.replace(' ', '%20')
                skill_entries.append(f'  <img src="https://img.shields.io/badge/{encoded_skill}-333333?style=flat&logo=github" height="30" alt="{skill}" />')
        
        return skill_entries
    
    def _generate_tools_section(self, tools: List[str]) -> str:
        """Generate Tools & Technologies section with icons"""
        tool_entries = []
        # Get all tools (both with and without icons)
        valid_tools = self.devicon_resolver.filter_valid_skills(tools)
        tool_icons = self.devicon_resolver.get_skill_icons(valid_tools)
        
        for tool in tools:
            icon_url = tool_icons.get(tool)
            if icon_url:
                tool_entries.append(f'  <img src="{icon_url}" height="40" alt="{tool} logo" title="{tool}" />')
            else:
                tool_entries.append(f'  <strong>{tool.title()}</strong>')
        
        # Add some common tool logos that might not be in devicon
        power_bi_skills = [t for t in tools if 'power bi' in t.lower()]
        for skill in power_bi_skills:
            if skill not in valid_tools or not tool_icons.get(skill):
                tool_entries.append('  <img src="https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg" height="40" alt="Power BI logo" title="Power BI" />')
        
        tableau_skills = [t for t in tools if 'tableau' in t.lower()]
        for skill in tableau_skills:
            if skill not in valid_tools or not tool_icons.get(skill):
                tool_entries.append('  <img src="https://cdn.worldvectorlogo.com/logos/tableau-software.svg" height="40" alt="tableau logo" title="Tableau" />')
        
        tools_text = '\n'.join(tool_entries)
        return f"""### 🛠️ Tools & Technologies

<div align="left">
{tools_text}
</div>"""
    

    
    def _generate_snake_animation(self, structured_data: Dict[str, any]) -> str:
        """Generate snake animation section from template"""
        github_username = structured_data.get('github', '')
        
        if not github_username:
            return ""
            
        import os
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     'resources', 'templates', 'snake_section.md')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return template.format(github_username=github_username)
        except Exception as e:
            # Fallback to hardcoded if template fails
            return f"\n---\n\n## 🐍 Contribution Graph\n\n<div align=\"center\">\n  <img src=\"https://github.com/{github_username}/{github_username}/blob/output/snake-dark.svg\" alt=\"Snake animation\" />\n</div>"
    
    def _generate_profile_header(self, structured_data: Dict[str, any], github_username: str) -> str:
        """Generate standardized modern profile header"""
        name = structured_data.get('name', 'Your Name')
        
        return f"""<h1 align="center">Hi there, I'm {name} 👋</h1>"""
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def escape_markdown(self, text: str) -> str:
        """Escape special markdown characters"""
        import re
        escape_chars = r'\\*`_{}[]()#+-.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    
    def _validate_structured_data(self, structured_data: Dict[str, any]) -> Dict[str, any]:
        """Clean structured data"""
        return structured_data.copy()

    def _validate_english_response(self, response: str) -> str:
        """Deprecated: Validation removed to allow multi-language support"""
        return response

    def _generate_dynamic_about_content(self, structured_data: Dict[str, any]) -> str:
        """Generate AI-powered dynamic content for About section"""
        # Use consolidated function to generate both subtitle and about content together
        _, about_content = self._generate_subtitle_and_about(structured_data)
        
        return about_content
    
    def _generate_fallback_content(self, structured_data: Dict[str, any]) -> str:
        """Fallback content generation when AI is not available"""
        skills = structured_data.get('skills', [])
        content = []
        
        if skills:
            top_skills = skills[:3]
            content.append(f"  - 💡 Specializing in: {', '.join(top_skills)}")
        
        if structured_data.get('languages'):
            languages = structured_data.get('languages', [])[:3]
            content.append(f"  - 🚀 Working with: {', '.join(languages)}")
        
        return '\n'.join(content) if content else "  - 👨‍💻 Passionate developer creating amazing things"
    
        
    def _generate_subtitle_and_about(self, structured_data: Dict[str, any]) -> tuple[str, str]:
        """Generate AI-powered subtitle and About Me content in single request"""
        # Validate and clean structured data first
        structured_data = self._validate_structured_data(structured_data)
        
        if not self.llm_provider:
            return None, self._generate_fallback_content(structured_data)
        
        name = structured_data.get('name', 'Developer')
        skills = structured_data.get('skills', [])
        languages = structured_data.get('languages', [])
        summary = structured_data.get('summary', '')
        
        prompt = f"""Generate subtitle and About Me content for a developer's GitHub README.

CRITICAL LANGUAGE INSTRUCTIONS:
- NEVER write Arabic text or any non-English content
- ALWAYS respond in English only
- DO NOT include any Arabic introductions, greetings, or explanations
- ALL output must be in English language exclusively

Developer Info:
Name: {name}
Skills: {', '.join(skills) if skills else 'Not specified'}
Programming Languages: {', '.join(languages) if languages else 'Not specified'}
Background/Summary: {summary}

Requirements:
1. SUBTITLE: Generate a professional subtitle (under 80 characters, 2-3 roles separated by " | ", with emojis)
   - Should reflect their main role and expertise
   - Example: " Data Scientist | ML Engineer | Analytics Expert"

2. ABOUT ME: Generate 3-4 bullet points that tell their PROFESSIONAL STORY:
   - STRICTLY use the provided 'Background/Summary' information.
   - DO NOT hallucinate or invent new experiences, companies, or skills not mentioned.
   - DO NOT mention any skills/tools that are not listed in the 'Developer Info' above.
   - You can rephrase and polish the English to make it professional, but keep the FACTS unchanged.
   - Focus on EXPERIENCE and ACHIEVEMENTS mentioned by the user.
   - Under 180 words total.

Format your response exactly like this:
SUBTITLE: [your subtitle here]
ABOUT:
  - 🎯 [Experience bullet based on input]
  - 💼 [Work/Domain bullet based on input]  
  - 🚀 [Achievement/Current focus bullet based on input]

CRITICAL: Start directly with "SUBTITLE:", no introduction. STAY FAITHFUL TO THE INPUT."""

        try:
            response = self.llm_provider.generate_text(prompt, [], max_output_tokens=300, temperature=0.7)
            if response and isinstance(response, str):
                validated_response = self._validate_english_response(response.strip())
                if validated_response:
                    # Parse the response
                    lines = validated_response.split('\n')
                    subtitle = None
                    about_lines = []
                    
                    current_section = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith('SUBTITLE:'):
                            subtitle = line.replace('SUBTITLE:', '').strip()
                            # Clean up quotes if present
                            if subtitle.startswith('"') and subtitle.endswith('"'):
                                subtitle = subtitle[1:-1]
                        elif line.startswith('ABOUT:'):
                            current_section = 'about'
                        elif line.startswith('- ') and current_section == 'about':
                            about_lines.append(line)
                    
                    # Validate subtitle
                    if subtitle and len(subtitle) > 0:
                        return subtitle, '\n'.join(about_lines) if about_lines else self._generate_fallback_content(structured_data)
        except Exception as e:
            print(f"Error generating AI content: {e}")
        
        return None, self._generate_fallback_content(structured_data)
