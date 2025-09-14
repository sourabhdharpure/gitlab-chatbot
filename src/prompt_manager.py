#!/usr/bin/env python3
"""
Prompt Manager for the GitLab AI Chatbot.
Manages both static and data-driven prompts.
"""

import json
import os
import random
from typing import Dict, List, Optional

class PromptManager:
    def __init__(self, data_driven_file: str = "data_driven_prompts_simplified.json"):
        self.data_driven_file = data_driven_file
        self.data_driven_prompts = {}
        self.load_data_driven_prompts()
        
        # Fallback static prompts if data-driven ones aren't available
        self.static_prompts = {
            "company_basics": [
                "What is GitLab?",
                "What does GitLab do as a company?",
                "What are GitLab's core values?",
                "What is GitLab's mission?"
            ],
            "remote_culture": [
                "How does GitLab handle remote work?",
                "What is GitLab's remote work policy?",
                "How does GitLab manage distributed teams?",
                "What tools does GitLab use for collaboration?"
            ],
            "hiring_careers": [
                "What is GitLab's hiring process?",
                "How does GitLab interview candidates?",
                "What does GitLab look for in employees?",
                "How does GitLab onboard new employees?"
            ],
            "development_engineering": [
                "How does GitLab's development process work?",
                "What is GitLab's merge request process?",
                "How does GitLab handle code reviews?",
                "How does GitLab ensure code quality?"
            ],
            "management_leadership": [
                "What is GitLab's management philosophy?",
                "How does GitLab train managers?",
                "How does GitLab make decisions?",
                "How does GitLab handle performance reviews?"
            ]
        }
    
    def load_data_driven_prompts(self):
        """Load data-driven prompts from JSON file."""
        try:
            if os.path.exists(self.data_driven_file):
                with open(self.data_driven_file, 'r', encoding='utf-8') as f:
                    self.data_driven_prompts = json.load(f)
                
                # Clean up malformed prompts in specific_gitlab_features
                if 'specific_gitlab_features' in self.data_driven_prompts:
                    cleaned_features = []
                    for prompt in self.data_driven_prompts['specific_gitlab_features']:
                        # Only keep well-formed questions
                        if (len(prompt) < 100 and 
                            not prompt.startswith('What is handle') and
                            not prompt.startswith('What is Note') and
                            not prompt.startswith('What is day') and
                            not prompt.startswith('What is our legal') and
                            not prompt.startswith('What is configure')):
                            cleaned_features.append(prompt)
                    
                    # Add some better specific feature prompts
                    cleaned_features.extend([
                        "How does GitLab's CI/CD pipeline work?",
                        "What is GitLab's approach to DevOps?",
                        "How does GitLab handle container registries?",
                        "What security scanning features does GitLab offer?",
                        "How does GitLab integrate with other tools?"
                    ])
                    
                    self.data_driven_prompts['specific_gitlab_features'] = cleaned_features
                    
        except Exception as e:
            print(f"Warning: Could not load data-driven prompts: {e}")
            self.data_driven_prompts = {}
    
    def get_prompts(self) -> Dict[str, List[str]]:
        """Get the best available prompts (data-driven if available, otherwise static)."""
        if self.data_driven_prompts:
            return self.data_driven_prompts
        return self.static_prompts
    
    def get_category_prompts(self, category: str) -> List[str]:
        """Get prompts for a specific category."""
        prompts = self.get_prompts()
        return prompts.get(category, [])
    
    def get_quick_start_prompts(self) -> List[str]:
        """Get a curated list of quick start prompts."""
        prompts = self.get_prompts()
        
        quick_start = []
        
        # Get top prompts from each major category
        categories_for_quick_start = [
            'company_basics',
            'values_and_culture', 
            'hiring_and_careers',
            'development_and_engineering'
        ]
        
        for category in categories_for_quick_start:
            category_prompts = prompts.get(category, [])
            if category_prompts:
                quick_start.extend(category_prompts[:2])  # Top 2 from each
        
        return quick_start[:8]  # Limit to 8 total
    
    def get_random_prompts(self, count: int = 6) -> List[str]:
        """Get random prompts from all categories."""
        all_prompts = []
        prompts = self.get_prompts()
        
        for category_prompts in prompts.values():
            all_prompts.extend(category_prompts)
        
        if len(all_prompts) <= count:
            return all_prompts
        
        return random.sample(all_prompts, count)
    
    def get_category_titles(self) -> Dict[str, str]:
        """Get user-friendly titles for categories."""
        return {
            'company_basics': '🏢 Company Basics',
            'values_and_culture': '🌟 Values & Culture',
            'processes_and_workflows': '⚙️ Processes & Workflows',
            'hiring_and_careers': '💼 Hiring & Careers',
            'development_and_engineering': '💻 Development & Engineering',
            'management_and_leadership': '👥 Management & Leadership',
            'security_and_compliance': '🔒 Security & Compliance',
            'specific_gitlab_features': '🛠️ GitLab Features',
            'remote_culture': '🌍 Remote Culture',
            'hiring_careers': '💼 Hiring & Careers',
            'development_engineering': '💻 Development',
            'management_leadership': '👥 Management'
        }
    
    def search_prompts(self, search_term: str) -> List[str]:
        """Search for prompts containing a specific term."""
        search_term = search_term.lower()
        matching_prompts = []
        prompts = self.get_prompts()
        
        for category_prompts in prompts.values():
            for prompt in category_prompts:
                if search_term in prompt.lower():
                    matching_prompts.append(prompt)
        
        return matching_prompts
    
    def get_prompts_for_role(self, role: str) -> List[str]:
        """Get prompts tailored for specific roles."""
        prompts = self.get_prompts()
        
        role_mapping = {
            'candidate': [
                'hiring_and_careers',
                'values_and_culture',
                'company_basics'
            ],
            'developer': [
                'development_and_engineering',
                'specific_gitlab_features',
                'processes_and_workflows'
            ],
            'manager': [
                'management_and_leadership',
                'processes_and_workflows',
                'values_and_culture'
            ],
            'security': [
                'security_and_compliance',
                'development_and_engineering',
                'processes_and_workflows'
            ]
        }
        
        relevant_categories = role_mapping.get(role.lower(), [])
        role_prompts = []
        
        for category in relevant_categories:
            role_prompts.extend(prompts.get(category, []))
        
        return role_prompts[:10]  # Limit to 10 prompts
    
    def is_data_driven(self) -> bool:
        """Check if we're using data-driven prompts."""
        return bool(self.data_driven_prompts)
    
    def get_prompt_stats(self) -> Dict[str, int]:
        """Get statistics about available prompts."""
        prompts = self.get_prompts()
        stats = {}
        
        total = 0
        for category, category_prompts in prompts.items():
            count = len(category_prompts)
            stats[category] = count
            total += count
        
        stats['total'] = total
        return stats
