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
        """Setup common skill name mappings"""
        self.skill_mappings = {
            # Data Science variations
            'data science': 'python',
            'data-science': 'python',
            'datascience': 'python',
            'machine learning': 'python',
            'ml': 'python',
            'artificial intelligence': 'python',
            'ai': 'python',
            'deep learning': 'python',
            'tensorflow': 'tensorflow',
            'pytorch': 'pytorch',
            'pandas': 'python',
            'numpy': 'python',
            'scikit-learn': 'python',
            'sklearn': 'python',
            
            # Dashboard variations
            'dashboard development': 'react',
            'dashboard dev': 'react',
            'dashboards': 'react',
            'dashboard': 'react',
            'power bi': 'microsoftsqlserver',
            'tableau': 'tableau',
            
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
            
            # Web frameworks
            'react': 'react',
            'reactjs': 'react',
            'vue': 'vuejs',
            'vuejs': 'vuejs',
            'angular': 'angularjs',
            'next.js': 'nextjs',
            'nextjs': 'nextjs',
            
            # Backend technologies
            'express': 'express',
            'express.js': 'express',
            'expressjs': 'express',
            'django': 'django',
            'flask': 'flask',
            'fastapi': 'fastapi',
            
            # Database variations
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'postgres': 'postgresql',
            'mongodb': 'mongodb',
            'sqlite': 'sqlite',
            'redis': 'redis',
            
            # Cloud platforms
            'aws': 'amazonwebservices',
            'azure': 'azure',
            'google cloud': 'googlecloud',
            'gcp': 'googlecloud',
            'firebase': 'firebase',
            
            # DevOps tools
            'docker': 'docker',
            'kubernetes': 'kubernetes',
            'k8s': 'kubernetes',
            'jenkins': 'jenkins',
            'git': 'git',
            'github': 'github',
            'gitlab': 'gitlab',
            
            # Programming languages
            'c++': 'cplusplus',
            'c#': 'csharp',
            'csharp': 'csharp',
            '.net': 'dotnet',
            'dotnet': 'dotnet',
            'java': 'java',
            'go': 'go',
            'golang': 'go',
            'rust': 'rust',
            'swift': 'swift',
            'kotlin': 'kotlin',
            'php': 'php',
            'ruby': 'ruby',
            'ruby on rails': 'ruby',
            'rails': 'ruby',
            
            # Mobile development
            'android': 'android',
            'ios': 'apple',
            'swift': 'swift',
            'kotlin': 'kotlin',
            'react native': 'react',
            'flutter': 'flutter',
            
            # Business process variations
            'business process improvement': 'flow',
            'process improvement': 'flow',
            'business process': 'flow',
            
            # Other common tools
            'linux': 'linux',
            'ubuntu': 'ubuntu',
            'windows': 'windows',
            'macos': 'apple',
            'vs code': 'visualstudiocode',
            'vscode': 'visualstudiocode',
            'visual studio': 'visualstudio',
            'sql': 'mysql',
            'data analysis': 'python',
            'tableau': 'tableau',
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