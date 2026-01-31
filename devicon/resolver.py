import json
import os
import logging
from typing import Dict, List, Optional, Set
from functools import lru_cache


class DeviconResolver:
    """Resolver for Devicon icons with caching and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devicon_data = {}
        self.skill_cache = {}
        self._load_devicon_data()
        self._setup_skill_mappings()
    
    def _setup_skill_mappings(self):
        """Setup common skill name mappings - ONLY for skills with correct icons"""
        self.skill_mappings = {
            # HTML/CSS variations
            'html': 'html5',
            'html5': 'html5',
            'css': 'css3',
            'css3': 'css3',
            
            # JavaScript variations
            'javascript': 'javascript',
            'js': 'javascript',
            'typescript': 'typescript',
            'ts': 'typescript',
            'node': 'nodejs',
            'node.js': 'nodejs',
            'nodejs': 'nodejs',
            
            # Data Science tools with CORRECT icons
            'tensorflow': 'tensorflow',
            'pytorch': 'pytorch',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'matplotlib': 'matplotlib',
            'jupyter': 'jupyter',
            'anaconda': 'anaconda',
            
            # Web frameworks
            'react': 'react',
            'reactjs': 'react',
            'vue': 'vuejs',
            'vuejs': 'vuejs',
            'vue.js': 'vuejs',
            'angular': 'angularjs',
            'angularjs': 'angularjs',
            'next.js': 'nextjs',
            'nextjs': 'nextjs',
            'nuxt': 'nuxtjs',
            'nuxt.js': 'nuxtjs',
            'svelte': 'svelte',
            'gatsby': 'gatsby',
            
            # Backend technologies
            'express': 'express',
            'express.js': 'express',
            'expressjs': 'express',
            'django': 'django',
            'flask': 'flask',
            'fastapi': 'fastapi',
            'spring': 'spring',
            'laravel': 'laravel',
            'rails': 'rails',
            'ruby on rails': 'rails',
            
            # Database - each has its OWN icon
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'postgres': 'postgresql',
            'mongodb': 'mongodb',
            'sqlite': 'sqlite',
            'redis': 'redis',
            'oracle': 'oracle',
            'mariadb': 'mariadb',
            'cassandra': 'cassandra',
            'neo4j': 'neo4j',
            'graphql': 'graphql',
            'sql server': 'microsoftsqlserver',
            'mssql': 'microsoftsqlserver',
            
            # Cloud platforms
            'aws': 'amazonwebservices',
            'amazon web services': 'amazonwebservices',
            'azure': 'azure',
            'google cloud': 'googlecloud',
            'gcp': 'googlecloud',
            'firebase': 'firebase',
            'heroku': 'heroku',
            'digitalocean': 'digitalocean',
            
            # DevOps tools
            'docker': 'docker',
            'kubernetes': 'kubernetes',
            'k8s': 'kubernetes',
            'jenkins': 'jenkins',
            'git': 'git',
            'github': 'github',
            'gitlab': 'gitlab',
            'bitbucket': 'bitbucket',
            'terraform': 'terraform',
            'ansible': 'ansible',
            'nginx': 'nginx',
            'apache': 'apache',
            
            # Programming languages
            'python': 'python',
            'c++': 'cplusplus',
            'cpp': 'cplusplus',
            'c#': 'csharp',
            'csharp': 'csharp',
            '.net': 'dotnetcore',
            'dotnet': 'dotnetcore',
            'java': 'java',
            'go': 'go',
            'golang': 'go',
            'rust': 'rust',
            'swift': 'swift',
            'kotlin': 'kotlin',
            'php': 'php',
            'ruby': 'ruby',
            'scala': 'scala',
            'perl': 'perl',
            'lua': 'lua',
            'dart': 'dart',
            'r': 'r',
            'matlab': 'matlab',
            'haskell': 'haskell',
            'elixir': 'elixir',
            'clojure': 'clojure',
            'groovy': 'groovy',
            
            # Mobile development
            'android': 'android',
            'flutter': 'flutter',
            'react native': 'react',
            
            # Other tools with CORRECT icons
            'linux': 'linux',
            'ubuntu': 'ubuntu',
            'debian': 'debian',
            'centos': 'centos',
            'bash': 'bash',
            'vim': 'vim',
            'vs code': 'vscode',
            'vscode': 'vscode',
            'visual studio': 'visualstudio',
            'intellij': 'intellij',
            'pycharm': 'pycharm',
            'webstorm': 'webstorm',
            'atom': 'atom',
            'figma': 'figma',
            'photoshop': 'photoshop',
            'illustrator': 'illustrator',
            'blender': 'blender',
            'unity': 'unity',
            'unreal': 'unrealengine',
            'excel': 'google', # Using google sheets as proxy or handled by custom icon
            
            # Typo fixes and variations
            'superbase': 'supabase',
            'versel': 'vercel',
            'machine learning': 'tensorflow', # Fallback
            'deep learning': 'pytorch', # Fallback
            'sql': 'mysql', # Generic SQL fallback
            'postgres': 'postgresql',
            'html': 'html5',
            'css': 'css3',
        }
    
    def _normalize_skill_name(self, skill: str) -> str:
        """Normalize skill name using mappings"""
        skill_lower = skill.lower().strip()
        return self.skill_mappings.get(skill_lower, skill)
    
    def _load_devicon_data(self):
        try:
            devicon_path = os.path.join(os.path.dirname(__file__), 'devicon.json')
            with open(devicon_path, 'r', encoding='utf-8') as f:
                self.devicon_data = json.load(f)
            self.logger.info(f"Loaded {len(self.devicon_data)} devicon entries")
        except Exception as e:
            self.logger.error(f"Failed to load devicon.json: {e}")
            self.devicon_data = {}
    
    @lru_cache(maxsize=1000)
    def validate_skill(self, skill: str) -> bool:
        """Check if a skill exists in devicon data"""
        if not self.devicon_data:
            return False
        
        # First try to normalize the skill name
        normalized_skill = self._normalize_skill_name(skill)
        skill_lower = normalized_skill.lower().strip()
        
        for entry in self.devicon_data:
            # Check main name
            if entry['name'].lower() == skill_lower:
                return True
            
            # Check alternative names
            if 'altnames' in entry:
                for altname in entry['altnames']:
                    if altname.lower() == skill_lower:
                        return True
        
        return False
    
    @lru_cache(maxsize=1000)
    def get_icon_url(self, skill: str, version: str = "original") -> Optional[str]:
        """
        Get the CDN URL for a skill's icon
        
        Args:
            skill: The skill name
            version: Icon version (original, plain, line, etc.)
        
        Returns:
            CDN URL or None if skill not found
        """
        if not self.devicon_data:
            return None
        
        # First try to normalize the skill name
        normalized_skill = self._normalize_skill_name(skill)
        skill_lower = normalized_skill.lower().strip()
        
        for entry in self.devicon_data:
            # Check main name
            if entry['name'].lower() == skill_lower:
                return self._build_icon_url(entry['name'], version)
            
            # Check alternative names
            if 'altnames' in entry:
                for altname in entry['altnames']:
                    if altname.lower() == skill_lower:
                        return self._build_icon_url(entry['name'], version)
        
        return None
    
    def _build_icon_url(self, icon_name: str, version: str) -> str:
        """Build the CDN URL for an icon"""
        return f"https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{icon_name}/{icon_name}-{version}.svg"
    
    def get_available_versions(self, skill: str) -> List[str]:
        """Get available versions for a skill"""
        if not self.devicon_data:
            return []
        
        skill_lower = skill.lower().strip()
        
        for entry in self.devicon_data:
            if entry['name'].lower() == skill_lower:
                if 'versions' in entry and 'svg' in entry['versions']:
                    return entry['versions']['svg']
            
            # Check alternative names
            if 'altnames' in entry:
                for altname in entry['altnames']:
                    if altname.lower() == skill_lower:
                        if 'versions' in entry and 'svg' in entry['versions']:
                            return entry['versions']['svg']
        
        return []
    
    def filter_valid_skills(self, skills: List[str]) -> List[str]:
        """Filter list to only include valid skills"""
        valid_skills = []
        for skill in skills:
            if self.validate_skill(skill):
                valid_skills.append(skill)
            else:
                self.logger.warning(f"Skill not found in devicon: {skill}")
        
        return valid_skills
    
    def get_skill_icons(self, skills: List[str]) -> Dict[str, str]:
        """Get icon URLs for a list of skills"""
        icons = {}
        for skill in skills:
            url = self.get_icon_url(skill)
            if url:
                icons[skill] = url
        return icons
    
    def search_skills(self, query: str, limit: int = 10) -> List[str]:
        """Search for skills by name or tags"""
        if not self.devicon_data:
            return []
        
        query_lower = query.lower().strip()
        matches = []
        
        for entry in self.devicon_data:
            # Check name match
            if query_lower in entry['name'].lower():
                matches.append(entry['name'])
                continue
            
            # Check alternative names
            if 'altnames' in entry:
                for altname in entry['altnames']:
                    if query_lower in altname.lower():
                        matches.append(entry['name'])
                        break
            
            # Check tags
            if 'tags' in entry:
                for tag in entry['tags']:
                    if query_lower in tag.lower():
                        matches.append(entry['name'])
                        break
            
            if len(matches) >= limit:
                break
        
        return matches[:limit]
    
    def get_all_skills(self) -> Set[str]:
        """Get all available skill names"""
        if not self.devicon_data:
            return set()
        
        skills = set()
        for entry in self.devicon_data:
            skills.add(entry['name'])
            if 'altnames' in entry:
                skills.update(entry['altnames'])
        
        return skills
    
    def clear_cache(self):
        """Clear the LRU cache"""
        self.validate_skill.cache_clear()
        self.get_icon_url.cache_clear()
        self.logger.info("Devicon resolver cache cleared")