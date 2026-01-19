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
        
        # Contact Info section (LinkedIn, Email) - moved to top
        contact_section = self._generate_contact_section(structured_data)
        if contact_section:
            sections.append(contact_section)
        
        # Features/Flowers section - moved to top
        features_section = self._generate_features_section(structured_data)
        if features_section:
            sections.append(features_section)
        
        # About Me section with gif
        if structured_data.get('summary'):
            sections.append(self._generate_modern_about_section(structured_data))
        
        # Tech Stack sections
        if structured_data.get('languages'):
            sections.append(self._generate_programming_languages_section(structured_data['languages']))
        
        if structured_data.get('skills'):
            sections.append(self._generate_data_science_section(structured_data['skills']))
        
        if structured_data.get('tools'):
            sections.append(self._generate_tools_section(structured_data['tools']))
        
        # GitHub Stats section (GitHub username is now required)
        if structured_data.get('github'):
            sections.append(self._generate_github_stats_section(structured_data))
        
        # Snake animation (GitHub username is now required)
        if structured_data.get('github'):
            sections.append(self._generate_snake_animation(structured_data))
        
        return '\n\n'.join(sections)
    
    def _generate_modern_header(self, structured_data: Dict[str, any]) -> str:
        """Generate modern README header with badges and alignment"""
        name = structured_data.get('name', 'Your Name')
        github_username = structured_data.get('github', '')
        
        # GitHub username is now required for profile generation
        if not github_username:
            github_username = 'yourusername'  # fallback
        
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
        # Use AI to generate personalized subtitle
        ai_subtitle = self._generate_ai_subtitle(structured_data)
        
        if ai_subtitle:
            return ai_subtitle
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
    
    def _generate_contact_section(self, structured_data: Dict[str, any]) -> str:
        """Generate Contact Info section with LinkedIn and Email at the top"""
        linkedin_url = structured_data.get('linkedin', '')
        email = structured_data.get('email', '')
        
        if not linkedin_url and not email:
            return ""
        
        contact_items = []
        
        if linkedin_url:
            contact_items.append(f'  - [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white)]({linkedin_url})')
        
        if email:
            contact_items.append(f'  - [![Email](https://img.shields.io/badge/Email-Contact%20Me-red?style=flat&logo=gmail)](mailto:{email})')
        
        return f"""## 📬 Get In Touch

<div align="left">

{chr(10).join(contact_items)}

</div>"""
    
    def _generate_features_section(self, structured_data: Dict[str, any]) -> str:
        """Generate Features section with AI-powered dynamic content"""
        # Use AI to generate personalized features
        ai_features = self._generate_ai_features(structured_data)
        
        if ai_features:
            return f"""## � Features & Achievements

<div align="left">

{ai_features}

</div>"""
        else:
            # Fallback to basic features if AI is not available
            return ""
    
    def _generate_modern_about_section(self, structured_data: Dict[str, any]) -> str:
        """Generate modern About Me section without images"""
        summary = structured_data.get('summary', '')
        email = structured_data.get('email', '')
        name = structured_data.get('name', 'there')
        skills = structured_data.get('skills', [])
        languages = structured_data.get('languages', [])
        
        # Build the reach me line only if email is provided
        reach_me_line = ""
        if email:
            reach_me_line = f"  - 📫 **Reach me at:** {email}"
        
        # Add personal touch with name
        personal_intro = f"## 👋 About {name.split()[0] if name else 'Me'}" if name else "## 👋 About Me"
        
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
    
    def _generate_data_science_section(self, skills: List[str]) -> str:
        """Generate Data Science & ML section with icons"""
        # Filter for data science related skills
        ds_skills = [skill for skill in skills if any(keyword in skill.lower() 
                   for keyword in ['data', 'machine', 'learning', 'ai', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit'])]
        
        if not ds_skills:
            return ""
        
        valid_skills = self.devicon_resolver.filter_valid_skills(ds_skills)
        skill_icons = self.devicon_resolver.get_skill_icons(valid_skills)
        
        if not skill_icons:
            return "### 📊 Data Science & ML\n" + ', '.join(ds_skills)
        
        # Generate skill entries with icons
        skill_entries = []
        for skill in valid_skills:
            icon_url = skill_icons.get(skill)
            if icon_url:
                skill_entries.append(f'  <img src="{icon_url}" height="40" alt="{skill} logo" title="{skill}" />')
            else:
                skill_entries.append(f'  <strong>{skill.title()}</strong>')
        
        # Add some common data science logos that might not be in devicon
        if 'scikit-learn' in ds_skills or 'sklearn' in ds_skills:
            skill_entries.append('  <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg" height="40" alt="scikit-learn logo" title="scikit-learn" />')
        
        skills_text = '\n'.join(skill_entries)
        return f"""### 📊 Data Science & ML

<div align="left">
{skills_text}
</div>"""
    
    def _generate_tools_section(self, tools: List[str]) -> str:
        """Generate Tools & Technologies section with icons"""
        valid_tools = self.devicon_resolver.filter_valid_skills(tools)
        tool_icons = self.devicon_resolver.get_skill_icons(valid_tools)
        
        if not tool_icons:
            return "### 🛠️ Tools & Technologies\n" + ', '.join(tools)
        
        # Generate tool entries with icons
        tool_entries = []
        for tool in valid_tools:
            icon_url = tool_icons.get(tool)
            if icon_url:
                tool_entries.append(f'  <img src="{icon_url}" height="40" alt="{tool} logo" title="{tool}" />')
            else:
                tool_entries.append(f'  <strong>{tool.title()}</strong>')
        
        # Add some common tool logos that might not be in devicon
        if 'power bi' in [t.lower() for t in tools]:
            tool_entries.append('  <img src="https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg" height="40" alt="Power BI logo" title="Power BI" />')
        
        if 'tableau' in [t.lower() for t in tools]:
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
        """Generate different profile header styles"""
        name = structured_data.get('name', 'Your Name')
        style = structured_data.get('profile_style', 'modern')  # default style
        
        if style == 'minimal':
            return f"""# {name}

<p align="center">Software Developer</p>"""
        
        elif style == 'bold':
            return f"""<h1 align="center"><strong>{name}</strong></h1>

<p align="center">🚀 Full Stack Developer | 💻 Problem Solver</p>"""
        
        elif style == 'creative':
            return f"""<div align="center">
  <h1>{name}</h1>
  <p>💡 Turning ideas into reality, one line of code at a time</p>
</div>"""
        
        else:  # modern (default)
            return f"""<h1 align="center">Hi there, I'm {name} 👋</h1>

<p align="center">Passionate developer building amazing things</p>"""
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def escape_markdown(self, text: str) -> str:
        """Escape special markdown characters"""
        import re
        escape_chars = r'\\*`_{}[]()#+-.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    
    def _generate_dynamic_about_content(self, structured_data: Dict[str, any]) -> str:
        """Generate AI-powered dynamic content for About section"""
        if not self.llm_provider:
            return self._generate_fallback_content(structured_data)
        
        name = structured_data.get('name', 'Developer')
        skills = structured_data.get('skills', [])
        languages = structured_data.get('languages', [])
        summary = structured_data.get('summary', '')
        
        prompt = f"""Generate a personalized "About Me" section for a developer's GitHub README. 

Name: {name}
Skills: {', '.join(skills) if skills else 'Not specified'}
Programming Languages: {', '.join(languages) if languages else 'Not specified'}
Summary: {summary}

Requirements:
- Write in a friendly, professional tone
- Include 2-3 bullet points highlighting their expertise
- Make it unique and personal, not generic
- Keep it concise (under 150 words)
- Use emojis appropriately
- Write in English

Format each bullet point with "  - " at the start."""

        try:
            response = self.llm_provider.generate_text(prompt, [], max_output_tokens=200, temperature=0.7)
            if response and isinstance(response, str):
                return response.strip()
        except Exception as e:
            print(f"Error generating AI content: {e}")
        
        return self._generate_fallback_content(structured_data)
    
    def _generate_fallback_content(self, structured_data: Dict[str, any]) -> str:
        """Fallback content generation when AI is not available"""
        skills = structured_data.get('skills', [])
        content = []
        
        if skills:
            top_skills = skills[:3]
            content.append(f"  - 💡 **Specializing in:** {', '.join(top_skills)}")
        
        if structured_data.get('languages'):
            languages = structured_data.get('languages', [])[:3]
            content.append(f"  - 🚀 **Working with:** {', '.join(languages)}")
        
        return '\n'.join(content) if content else "  - 👨‍💻 **Passionate developer** creating amazing things"
    
    def _generate_ai_features(self, structured_data: Dict[str, any]) -> str:
        """Generate AI-powered features and achievements"""
        if not self.llm_provider:
            return None
        
        name = structured_data.get('name', 'Developer')
        skills = structured_data.get('skills', [])
        languages = structured_data.get('languages', [])
        summary = structured_data.get('summary', '')
        
        prompt = f"""Generate a personalized "Features & Achievements" section for a developer's GitHub README.

Name: {name}
Skills: {', '.join(skills) if skills else 'Not specified'}
Programming Languages: {', '.join(languages) if languages else 'Not specified'}
Summary: {summary}

Requirements:
- Write in a professional yet friendly tone
- Include 3-4 bullet points highlighting their key features and achievements
- Use flower emojis at the beginning of each point
- Make it unique and personal based on their profile
- Keep it concise (under 120 words total)
- Focus on their strengths and expertise
- Write in English

Format each bullet point with "  - " at the start, followed by a flower emoji and bold feature title."""

        try:
            response = self.llm_provider.generate_text(prompt, [], max_output_tokens=200, temperature=0.8)
            if response and isinstance(response, str):
                return response.strip()
        except Exception as e:
            print(f"Error generating AI features: {e}")
        
        return None
    
    def _generate_ai_subtitle(self, structured_data: Dict[str, any]) -> str:
        """Generate AI-powered professional subtitle"""
        if not self.llm_provider:
            return None
        
        name = structured_data.get('name', 'Developer')
        skills = structured_data.get('skills', [])
        languages = structured_data.get('languages', [])
        summary = structured_data.get('summary', '')
        
        prompt = f"""Generate a professional subtitle for a developer's GitHub README header.

Name: {name}
Skills: {', '.join(skills) if skills else 'Not specified'}
Programming Languages: {', '.join(languages) if languages else 'Not specified'}
Summary: {summary}

Requirements:
- Write a single line subtitle (under 80 characters)
- Use 2-3 professional roles/identities separated by " | "
- Include relevant emojis at the beginning of each role
- Make it unique and personal based on their skills
- Focus on their main expertise areas
- Write in English
- Examples: "🔬 Data Analyst | 🤖 AI Enthusiast | 📊 Problem Solver"

Return ONLY the subtitle line, nothing else."""

        try:
            response = self.llm_provider.generate_text(prompt, [], max_output_tokens=100, temperature=0.7)
            if response and isinstance(response, str):
                subtitle = response.strip()
                # Clean up any extra formatting
                if subtitle.startswith('"') and subtitle.endswith('"'):
                    subtitle = subtitle[1:-1]
                return subtitle
        except Exception as e:
            print(f"Error generating AI subtitle: {e}")
        
        return None
