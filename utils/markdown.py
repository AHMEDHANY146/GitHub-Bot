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
            sections.append(self._generate_skills_section(unique_skills))
        
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
    
    def _generate_skills_section(self, skills: List[str]) -> str:
        """Generate Skills section with proper categorization and icons - shows ALL skills with icons"""
        if not skills:
            return ""
        
        # Extended keyword lists for better categorization
        programming_keywords = [
            'python', 'javascript', 'java', 'c++', 'c#', 'typescript', 'go', 'golang',
            'rust', 'php', 'swift', 'kotlin', 'ruby', 'scala', 'r', 'matlab', 'html', 
            'css', 'sass', 'less', 'perl', 'lua', 'dart', 'objective-c', 'shell', 'bash',
            'powershell', 'haskell', 'elixir', 'clojure', 'f#', 'groovy', 'julia'
        ]
        
        frameworks_keywords = [
            # AI/ML
            'tensorflow', 'pytorch', 'keras', 'scikit', 'sklearn', 'pandas', 'numpy', 
            'matplotlib', 'seaborn', 'opencv', 'nltk', 'spacy', 'huggingface', 'langchain',
            # Web frameworks
            'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'spring', 'laravel', 
            'express', 'next', 'nuxt', 'svelte', 'gatsby', 'tailwind', 'bootstrap', 'node',
            'nestjs', 'rails', 'asp.net', 'blazor', 'jquery', 'backbone', 'ember',
            # Cloud and DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'jenkins',
            'git', 'github', 'gitlab', 'bitbucket', 'terraform', 'ansible', 'puppet', 'chef',
            'circleci', 'travis', 'nginx', 'apache', 'heroku', 'vercel', 'netlify',
            # Databases
            'power bi', 'tableau', 'excel', 'sql', 'mongodb', 'postgresql', 'postgres',
            'mysql', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'firebase', 'supabase',
            'sqlite', 'oracle', 'mariadb', 'neo4j', 'graphql',
            # AI/ML concepts
            'rag', 'chatbot', 'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data science', 'ai', 'artificial intelligence', 'llm', 'generative ai',
            # Mobile
            'android', 'ios', 'flutter', 'react native', 'xamarin', 'ionic',
            # Other tools
            'figma', 'photoshop', 'illustrator', 'sketch', 'xd', 'blender', 'unity', 'unreal',
            'postman', 'insomnia', 'swagger', 'linux', 'ubuntu', 'debian', 'centos', 'vim',
            'vscode', 'visual studio', 'intellij', 'pycharm', 'webstorm', 'atom', 'sublime'
        ]
        
        # Categorize skills into 3 main sections
        programming_skills = []
        frameworks_tools = []
        other_skills = []
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            
            # Check if it's a programming language
            if any(keyword in skill_lower for keyword in programming_keywords):
                programming_skills.append(skill)
            # Check if it's a framework/tool
            elif any(keyword in skill_lower for keyword in frameworks_keywords):
                frameworks_tools.append(skill)
            # Check if devicon has this skill - if yes, add to frameworks
            elif self.devicon_resolver.validate_skill(skill):
                frameworks_tools.append(skill)
            # Other skills
            else:
                other_skills.append(skill)
        
        sections = []
        
        # Programming Languages section
        if programming_skills:
            skill_entries = self._generate_skill_entries(programming_skills)
            if skill_entries:
                skills_text = '\n'.join(skill_entries)
                sections.append(f"""### 💻 Programming Languages

<div align="left">
{skills_text}
</div>""")
        
        # Frameworks & Tools section
        if frameworks_tools:
            skill_entries = self._generate_skill_entries(frameworks_tools)
            if skill_entries:
                skills_text = '\n'.join(skill_entries)
                sections.append(f"""### 🤖 Frameworks & Tools

<div align="left">
{skills_text}
</div>""")
        
        # Other Skills section - only show if there are valid skills with icons
        if other_skills:
            skill_entries = self._generate_skill_entries(other_skills)
            if skill_entries:
                skills_text = '\n'.join(skill_entries)
                sections.append(f"""### 🎯 Other Technologies

<div align="left">
{skills_text}
</div>""")
        
        return '\n\n'.join(sections) if sections else ""
    
    def _generate_skill_entries(self, skills: List[str]) -> List[str]:
        """Generate HTML entries for skills with icons - only includes skills with valid icons"""
        skill_entries = []
        
        # Get icons for all skills
        skill_icons = self.devicon_resolver.get_skill_icons(skills)
        
        # Custom icon mappings for popular tools not in standard devicon
        custom_icons = {
            'scikit': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg',
            'sklearn': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg',
            'scikit-learn': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg',
            'power bi': 'https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg',
            'powerbi': 'https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg',
            'tableau': 'https://cdn.worldvectorlogo.com/logos/tableau-software.svg',
            'langchain': 'https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/static/img/brand/langchain_logo.svg',
            'huggingface': 'https://huggingface.co/front/assets/huggingface_logo.svg',
            'fastapi': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg',
        }
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            
            # First check if we have an icon from devicon
            icon_url = skill_icons.get(skill)
            
            # If not, check custom icons
            if not icon_url:
                for key, url in custom_icons.items():
                    if key in skill_lower:
                        icon_url = url
                        break
            
            # Only add skills that have icons
            if icon_url:
                skill_entries.append(f'  <img src="{icon_url}" height="40" alt="{skill} logo" title="{skill.title()}" />')
        
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
    
    def _generate_github_stats_section(self, structured_data: Dict[str, any]) -> str:
        """Generate GitHub Stats section"""
        github_username = structured_data.get('github', '')
        
        # Only generate GitHub stats section if username is provided
        if not github_username:
            return ""
        
        return f"""---

## 📊 GitHub Activity

<div align="center">
  
  <img src="https://github-readme-stats.vercel.app/api?username={github_username}&hide_title=false&hide_rank=false&show_icons=true&include_all_commits=true&count_private=true&disable_animations=false&theme=dark&locale=en&hide_border=true&bg_color=0D1117" height="150" alt="stats graph"  />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={github_username}&locale=en&hide_title=false&layout=compact&card_width=320&langs_count=5&theme=dark&hide_border=true&bg_color=0D1117" height="150" alt="languages graph"  />
  
</div>

<div align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user={github_username}&theme=dark&hide_border=true&background=0D1117" alt="streak stats" />
</div>"""
    
    def _generate_snake_animation(self, structured_data: Dict[str, any]) -> str:
        """Generate snake animation section"""
        github_username = structured_data.get('github', '')
        
        # Only generate snake animation if username is provided
        if not github_username:
            return ""
        
        return f"""
---

## 🐍 Contribution Graph

<div align="center">
  <img src="https://github.com/{github_username}/{github_username}/blob/output/snake-dark.svg" alt="Snake animation" />
</div>

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={github_username}&theme=dark&hide_border=true&bg_color=0D1117" alt="Activity graph" />
</div>"""
    
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
        """Validate and clean structured data to ensure English-only content"""
        cleaned_data = structured_data.copy()
        
        # Clean summary
        if 'summary' in cleaned_data and cleaned_data['summary']:
            summary = cleaned_data['summary']
            if self._validate_english_response(summary) is None:
                # Replace Arabic summary with English fallback
                cleaned_data['summary'] = f"Passionate developer with expertise in {', '.join(cleaned_data.get('skills', ['software development'])[:3])}"
        
        # Clean skills list
        if 'skills' in cleaned_data and cleaned_data['skills']:
            cleaned_skills = []
            for skill in cleaned_data['skills']:
                if self._validate_english_response(skill) is not None:
                    cleaned_skills.append(skill)
            cleaned_data['skills'] = cleaned_skills
        
        # Clean languages list
        if 'languages' in cleaned_data and cleaned_data['languages']:
            cleaned_languages = []
            for lang in cleaned_data['languages']:
                if self._validate_english_response(lang) is not None:
                    cleaned_languages.append(lang)
            cleaned_data['languages'] = cleaned_languages
        
        return cleaned_data

    def _validate_english_response(self, response: str) -> str:
        """Validate and clean AI response to ensure it's English only"""
        if not response:
            return response
        
        # Check for Arabic characters
        arabic_chars = any('\u0600' <= char <= '\u06FF' for char in response)
        
        if arabic_chars:
            # If Arabic detected, return fallback content
            print("Arabic text detected in AI response, using fallback")
            return None
        
        # Additional validation for common Arabic words
        arabic_words = ['في', 'من', 'إلى', 'على', 'مع', 'خلال', 'بعد', 'قبل', 'حول', 'هذا', 'هذه', 'ذلك', 
                        'تطوير', 'مطور', 'برمجة', 'مشاريع', 'خبرة', 'مهارات', 'لغات', 'أدوات']
        
        response_lower = response.lower()
        if any(word in response_lower for word in arabic_words):
            print("Arabic words detected in AI response, using fallback")
            return None
        
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

Name: {name}
Skills: {', '.join(skills) if skills else 'Not specified'}
Programming Languages: {', '.join(languages) if languages else 'Not specified'}
Summary: {summary}

Requirements:
1. SUBTITLE: Generate a professional subtitle (under 80 characters, 2-3 roles separated by " | ", with emojis)
2. ABOUT ME: Generate 2-3 bullet points highlighting expertise (friendly, professional tone, under 150 words total)

Format your response exactly like this:
SUBTITLE: [your subtitle here]
ABOUT:
  - [first bullet point]
  - [second bullet point]
  - [third bullet point if applicable]

Examples:
SUBTITLE: 🔬 Data Analyst | 🤖 AI Enthusiast | 📊 Problem Solver
ABOUT:
  - 💡 Specializing in data analysis and machine learning with Python
  - 🚀 Experienced in creating insights from complex datasets
  - 🎯 Passionate about solving real-world problems with data

CRITICAL: Start directly with "SUBTITLE:", no introduction."""

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
