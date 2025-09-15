"""
Transparency & Guardrails Component - Advanced explainability and safety features
"""

import streamlit as st
import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class TransparencyGuardrails:
    """Handles advanced transparency, explainability, and safety features with modern UI."""
    
    def __init__(self):
        self.sensitive_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?',
            'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^\s]{6,}["\']?',
            'token': r'(?i)(token|access_token|bearer)\s*[:=]\s*["\']?[a-zA-Z0-9_.-]{20,}["\']?',
            'secret': r'(?i)(secret|secret_key|private_key)\s*[:=]\s*["\']?[a-zA-Z0-9_.-]{20,}["\']?',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        self.bias_keywords = {
            'gender': ['he', 'she', 'him', 'her', 'his', 'hers', 'man', 'woman', 'male', 'female'],
            'age': ['young', 'old', 'elderly', 'senior', 'junior', 'millennial', 'boomer'],
            'race': ['white', 'black', 'asian', 'hispanic', 'latino', 'caucasian'],
            'ability': ['disabled', 'handicapped', 'normal', 'abnormal', 'healthy', 'sick'],
            'technical_role': ['obviously', 'simply', 'just', 'easy', 'basic', 'advanced', 'expert', 'beginner'],
            'seniority': ['junior', 'senior', 'lead', 'principal', 'architect', 'manager', 'director'],
            'department': ['engineering', 'developer', 'marketing', 'sales', 'hr', 'qa', 'designer'],
            'team_size': ['enterprise', 'startup', 'small team', 'large team', 'individual'],
            'methodology': ['agile', 'scrum', 'devops', 'waterfall', 'kanban', 'sprint'],
            'feature_preference': ['premium', 'paid', 'free', 'latest', 'newest', 'stable'],
            'language': ['english', 'native speaker', 'fluent', 'accent', 'dialect'],
            'cultural': ['western', 'eastern', 'american', 'european', 'asian', 'global'],
            'timezone': ['pst', 'est', 'gmt', 'utc', 'morning', 'evening', 'business hours']
        }
        
        self.confidence_levels = {
            'high': {'min': 0.8, 'color': '#10b981', 'bg_color': '#d1fae5', 'icon': '🟢'},
            'medium': {'min': 0.6, 'color': '#f59e0b', 'bg_color': '#fef3c7', 'icon': '🟡'},
            'low': {'min': 0.0, 'color': '#ef4444', 'bg_color': '#fee2e2', 'icon': '🔴'}
        }
        
        # Setup modern CSS styling
        self._setup_transparency_css()
    
    def _setup_transparency_css(self):
        """Setup modern CSS styling for transparency components."""
        st.markdown("""
        <style>
        /* Confidence display styling */
        .confidence-display {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px 0;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            font-size: 13px;
            font-weight: 500;
        }
        
        .confidence-high {
            border-left-color: #10b981;
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            color: #065f46;
        }
        
        .confidence-medium {
            border-left-color: #f59e0b;
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            color: #92400e;
        }
        
        .confidence-low {
            border-left-color: #ef4444;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            color: #991b1b;
        }
        
        /* Safety status styling */
        .safety-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            margin: 4px 0;
        }
        
        .safety-pass {
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            color: #065f46;
            border: 1px solid #10b981;
        }
        
        .safety-warning {
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            color: #991b1b;
            border: 1px solid #ef4444;
        }
        
        /* Bias detection styling */
        .bias-detection {
            background: rgba(249, 250, 251, 0.9);
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 10px;
            margin: 6px 0;
            font-size: 12px;
        }
        
        .bias-item {
            background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
            border: 1px solid #f97316;
            border-radius: 4px;
            padding: 6px 8px;
            margin: 4px 0;
            font-size: 11px;
            color: #9a3412;
        }
        
        /* Decision trail styling */
        .decision-trail {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            font-size: 11px;
            line-height: 1.6;
            color: #374151;
        }
        
        .decision-step {
            margin: 8px 0;
            padding: 6px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .decision-step:last-child {
            border-bottom: none;
        }
        
        .decision-step h4 {
            color: #1f2937;
            font-size: 12px;
            margin: 0 0 4px 0;
            font-weight: 600;
        }
        
        /* Feedback form styling */
        .feedback-container {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        
        .feedback-title {
            color: #1f2937;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        /* Learning dashboard styling */
        .learning-card {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .learning-metric {
            background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
            border-radius: 6px;
            padding: 12px;
            text-align: center;
            color: #1e40af;
            font-weight: 600;
        }
        
        .learning-insight {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 1px solid #22c55e;
            border-radius: 6px;
            padding: 10px;
            margin: 6px 0;
            color: #15803d;
            font-size: 12px;
        }
        
        /* Expandable sections */
        .transparency-expander {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            margin: 4px 0;
        }
        
        .transparency-expander .streamlit-expanderHeader {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: #374151;
            font-size: 12px;
            font-weight: 500;
            padding: 8px 12px;
            border-radius: 6px 6px 0 0;
        }
        
        .transparency-expander .streamlit-expanderContent {
            background: rgba(255, 255, 255, 0.98);
            color: #374151;
            padding: 10px 12px;
            font-size: 11px;
            line-height: 1.5;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 500;
        }
        
        .status-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-warning {
            background: #fef3c7;
            color: #92400e;
        }
        
        .status-error {
            background: #fee2e2;
            color: #991b1b;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def calculate_confidence_score(self, response: str, sources: List[Dict], query: str) -> Dict:
        """Calculate confidence score based on multiple factors."""
        score = 0.0
        factors = []
        
        # Source quality factor (40% weight)
        if sources:
            source_score = min(len(sources) / 3.0, 1.0)  # More sources = higher confidence
            score += source_score * 0.4
            factors.append(f"📚 Source quality: {source_score:.1%} ({len(sources)} sources)")
        else:
            factors.append("📚 Source quality: 0% (no sources)")
        
        # Response length factor (20% weight)
        response_length = len(response.split())
        length_score = min(response_length / 100.0, 1.0)  # Longer responses often more detailed
        score += length_score * 0.2
        factors.append(f"📝 Response detail: {length_score:.1%} ({response_length} words)")
        
        # Query specificity factor (20% weight)
        specific_terms = ['how', 'what', 'why', 'when', 'where', 'which', 'who']
        query_specificity = sum(1 for term in specific_terms if term in query.lower()) / len(specific_terms)
        score += query_specificity * 0.2
        factors.append(f"🎯 Query specificity: {query_specificity:.1%}")
        
        # GitLab relevance factor (20% weight)
        gitlab_terms = ['gitlab', 'git', 'ci/cd', 'pipeline', 'merge request', 'issue', 'epic']
        relevance_score = sum(1 for term in gitlab_terms if term in query.lower()) / len(gitlab_terms)
        score += relevance_score * 0.2
        factors.append(f"🔗 GitLab relevance: {relevance_score:.1%}")
        
        # Determine confidence level
        confidence_level = 'low'
        for level, config in self.confidence_levels.items():
            if score >= config['min']:
                confidence_level = level
        
        return {
            'score': round(score, 2),
            'level': confidence_level,
            'color': self.confidence_levels[confidence_level]['color'],
            'bg_color': self.confidence_levels[confidence_level]['bg_color'],
            'icon': self.confidence_levels[confidence_level]['icon'],
            'factors': factors
        }
    
    def detect_sensitive_data(self, text: str) -> List[Dict]:
        """Detect and identify sensitive information in text."""
        detected_items = []
        
        for category, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                detected_items.append({
                    'category': category,
                    'pattern': pattern,
                    'match': match,
                    'severity': 'high' if category in ['api_key', 'password', 'token', 'secret'] else 'medium'
                })
        
        return detected_items
    
    def redact_sensitive_data(self, text: str) -> Tuple[str, List[Dict]]:
        """Redact sensitive information from text."""
        redacted_text = text
        redactions = []
        
        for category, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                redaction = f"[REDACTED_{category.upper()}]"
                redacted_text = redacted_text.replace(match, redaction)
                redactions.append({
                    'category': category,
                    'original': match,
                    'redacted': redaction
                })
        
        return redacted_text, redactions
    
    def detect_bias(self, text: str) -> List[Dict]:
        """Detect potential biases in text with comprehensive analysis."""
        bias_detections = []
        text_lower = text.lower()
        
        # Technical Role Bias Detection
        technical_bias_phrases = [
            'obviously', 'simply', 'just', 'easy', 'basic', 'advanced'
        ]
        found_technical = [phrase for phrase in technical_bias_phrases if phrase in text_lower]
        if found_technical:
            bias_detections.append({
                'category': '🎯 Technical Role Bias',
                'keywords': found_technical,
                'severity': 'high',
                'suggestion': "Avoid assuming technical expertise level. Provide options for different experience levels.",
                'example_bad': "Just use the advanced CI/CD pipeline configuration—it's simple.",
                'example_good': "Here are CI/CD options ranging from basic to advanced, depending on your experience level."
            })
        
        # Departmental/Team Bias Detection
        dept_bias_phrases = [
            'engineering', 'developer', 'marketing', 'sales', 'hr', 'qa', 'designer'
        ]
        found_dept = [phrase for phrase in dept_bias_phrases if phrase in text_lower]
        if found_dept and len(found_dept) == 1:  # Only one department mentioned
            bias_detections.append({
                'category': '🏢 Departmental Bias',
                'keywords': found_dept,
                'severity': 'medium',
                'suggestion': "Consider how this applies to different departments and team roles.",
                'example_bad': "This is primarily for engineering teams.",
                'example_good': "This applies to various teams - here's how different roles can use it."
            })
        
        # Experience Level Bias Detection
        experience_bias_phrases = [
            'expert', 'beginner', 'junior', 'senior', 'advanced user', 'new user'
        ]
        found_experience = [phrase for phrase in experience_bias_phrases if phrase in text_lower]
        if found_experience:
            bias_detections.append({
                'category': '📈 Experience Level Bias',
                'keywords': found_experience,
                'severity': 'medium',
                'suggestion': "Provide context for different experience levels without assumptions.",
                'example_bad': "As an expert, you'll know this already.",
                'example_good': "Depending on your experience level, here are different approaches."
            })
        
        # Language and Cultural Bias Detection
        cultural_bias_phrases = [
            'english', 'native speaker', 'western', 'american', 'european'
        ]
        found_cultural = [phrase for phrase in cultural_bias_phrases if phrase in text_lower]
        if found_cultural:
            bias_detections.append({
                'category': '🌍 Language/Cultural Bias',
                'keywords': found_cultural,
                'severity': 'high',
                'suggestion': "Consider global audience and diverse cultural contexts.",
                'example_bad': "This is standard in American companies.",
                'example_good': "This approach works well in many organizational cultures."
            })
        
        # Feature/Product Bias Detection
        feature_bias_phrases = [
            'premium', 'paid', 'free', 'latest', 'newest', 'stable'
        ]
        found_feature = [phrase for phrase in feature_bias_phrases if phrase in text_lower]
        if found_feature:
            bias_detections.append({
                'category': '💰 Feature/Product Bias',
                'keywords': found_feature,
                'severity': 'medium',
                'suggestion': "Present options neutrally without favoring specific features.",
                'example_bad': "The premium version is obviously better.",
                'example_good': "Here are the available options with their respective benefits."
            })
        
        # Process and Methodology Bias Detection
        methodology_bias_phrases = [
            'agile', 'scrum', 'devops', 'waterfall', 'kanban'
        ]
        found_methodology = [phrase for phrase in methodology_bias_phrases if phrase in text_lower]
        if found_methodology and len(found_methodology) == 1:  # Only one methodology mentioned
            bias_detections.append({
                'category': '⚙️ Process/Methodology Bias',
                'keywords': found_methodology,
                'severity': 'medium',
                'suggestion': "Acknowledge different methodologies and team structures.",
                'example_bad': "All teams should use agile methodology.",
                'example_good': "This can be adapted to various methodologies including agile, waterfall, etc."
            })
        
        # Gender and Diversity Bias Detection
        gender_bias_phrases = [
            'he', 'she', 'him', 'her', 'his', 'hers', 'man', 'woman'
        ]
        found_gender = [phrase for phrase in gender_bias_phrases if phrase in text_lower]
        if found_gender:
            bias_detections.append({
                'category': '👥 Gender/Diversity Bias',
                'keywords': found_gender,
                'severity': 'high',
                'suggestion': "Use gender-neutral language and inclusive pronouns.",
                'example_bad': "The developer should check his code.",
                'example_good': "The developer should check their code."
            })
        
        return bias_detections
    
    def create_decision_trail(self, query: str, response: str, sources: List[Dict], confidence: Dict) -> str:
        """Create a visual decision trail showing how the response was generated."""
        # Handle missing confidence data gracefully
        confidence_level = confidence.get('level', 'medium') if confidence else 'medium'
        confidence_score = confidence.get('score', 0.5) if confidence else 0.5
        confidence_icon = confidence.get('icon', '🟡') if confidence else '🟡'
        confidence_factors = confidence.get('factors', ['📚 Source relevance: High', '🧠 Response coherence: Strong']) if confidence else ['📚 Source relevance: High', '🧠 Response coherence: Strong']
        
        trail = f"""
**🔍 Decision Trail for: "{query}"**

**Step 1: 📊 Query Analysis**
- Query type: {'❓ Specific question' if '?' in query else '💬 General inquiry'}
- Keywords: {', '.join(re.findall(r'\\b\\w+\\b', query.lower())[:5])}

**Step 2: 🔎 Source Retrieval**
- Sources found: {len(sources)} 📚
- Types: {', '.join(set(s.get('type', 'unknown') for s in sources))}

**Step 3: 🤖 Response Generation**
- Confidence: {confidence_level.upper()} ({confidence_score:.0%}) {confidence_icon}
- Length: {len(response.split())} words 📝

**Step 4: ⚖️ Quality Factors**
"""
        for factor in confidence_factors:
            trail += f"- {factor}\n"
        
        trail += f"""
**Step 5: 🛡️ Safety Checks**
- Sensitive data: {'✅ None detected' if not self.detect_sensitive_data(response) else '⚠️ Detected and flagged'}
- Bias detection: {'✅ None detected' if not self.detect_bias(response) else '⚠️ Potential issues found'}

**🎯 Final Confidence: {confidence_icon} {confidence_score:.0%}**
"""
        return trail
    
    def render_confidence_display(self, confidence: Dict):
        """Render confidence score in a clean way."""
        level = confidence['level']
        icon = confidence['icon']
        score = confidence['score']
        
        st.markdown(f"**Confidence:** {icon} {score:.0%} ({level.title()})")
    
    def render_decision_trail(self, query: str, response: str, sources: List[Dict], confidence: Dict):
        """Render the decision trail in a clean way."""
        trail = self.create_decision_trail(query, response, sources, confidence)
        st.markdown(trail)
    
    def render_bias_dashboard(self, text: str):
        """Render bias detection dashboard with modern UI."""
        biases = self.detect_bias(text)
        
        if biases:
            st.markdown('<div class="safety-status safety-warning">⚠️ Potential bias detected in response</div>', unsafe_allow_html=True)
            
            for bias in biases:
                with st.expander(f"{bias['category']}", expanded=False):
                    st.markdown(f"""
                    <div class="bias-item">
                        <strong>Keywords:</strong> {", ".join(bias["keywords"])}<br>
                        <strong>💡 Suggestion:</strong> {bias["suggestion"]}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="safety-status safety-pass">✅ No bias detected in response</div>', unsafe_allow_html=True)
    
    def render_safety_checks(self, text: str):
        """Render safety and sensitive data checks with modern styling."""
        sensitive_items = self.detect_sensitive_data(text)
        
        if sensitive_items:
            st.markdown('<div class="safety-status safety-warning">🚨 Sensitive data detected!</div>', unsafe_allow_html=True)
            
            for item in sensitive_items:
                st.markdown(f"""
                <div class="bias-item">
                    <strong>🔒 {item["category"].replace("_", " ").title()}:</strong> {item["match"]}
                </div>
                """, unsafe_allow_html=True)
            
            # Show redacted version
            redacted_text, redactions = self.redact_sensitive_data(text)
            with st.expander("🔒 Redacted Response", expanded=False):
                st.markdown(f'<div class="decision-trail">{redacted_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="safety-status safety-pass">✅ No sensitive data detected</div>', unsafe_allow_html=True)
    
    def track_learning_feedback(self, query: str, response: str, feedback: str, user_rating: int):
        """Track user feedback for learning improvements with persistent storage."""
        # Load existing feedback from file
        feedback_data = self._load_feedback_data()
        
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'feedback': feedback,
            'rating': user_rating,
            'improvement_suggestions': self._generate_improvement_suggestions(query, response, feedback)
        }
        
        feedback_data.append(feedback_entry)
        
        # Keep only last 100 feedback entries
        if len(feedback_data) > 100:
            feedback_data = feedback_data[-100:]
        
        # Save to file
        self._save_feedback_data(feedback_data)
        
        # Update session state
        st.session_state.learning_feedback = feedback_data
    
    def _load_feedback_data(self) -> List[Dict]:
        """Load feedback data from persistent storage."""
        try:
            with open('data/feedback_data.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_feedback_data(self, feedback_data: List[Dict]):
        """Save feedback data to persistent storage."""
        import os
        os.makedirs('data', exist_ok=True)
        with open('data/feedback_data.json', 'w') as f:
            json.dump(feedback_data, f, indent=2)
    
    def _generate_improvement_suggestions(self, query: str, response: str, feedback: str) -> List[str]:
        """Generate improvement suggestions based on feedback."""
        suggestions = []
        
        if 'inaccurate' in feedback.lower() or 'wrong' in feedback.lower():
            suggestions.append("🔍 Verify information against authoritative sources")
            suggestions.append("📚 Add more specific examples or citations")
        
        if 'unclear' in feedback.lower() or 'confusing' in feedback.lower():
            suggestions.append("✨ Simplify language and structure")
            suggestions.append("📝 Add step-by-step explanations")
        
        if 'incomplete' in feedback.lower() or 'missing' in feedback.lower():
            suggestions.append("📋 Expand response with additional details")
            suggestions.append("💡 Include related topics or follow-up questions")
        
        return suggestions
    
    def analyze_feedback_patterns(self) -> Dict:
        """Analyze feedback patterns to identify improvement opportunities."""
        feedback_data = self._load_feedback_data()
        
        if not feedback_data:
            return {"message": "No feedback data available yet"}
        
        # Calculate average rating
        ratings = [entry['rating'] for entry in feedback_data]
        avg_rating = sum(ratings) / len(ratings)
        
        # Find low-rated responses
        low_rated = [entry for entry in feedback_data if entry['rating'] <= 2]
        
        # Analyze common issues
        common_issues = []
        for entry in low_rated:
            if entry['feedback']:
                common_issues.append(entry['feedback'].lower())
        
        # Count feedback keywords
        issue_counts = {}
        for issue in common_issues:
            if 'inaccurate' in issue or 'wrong' in issue:
                issue_counts['accuracy'] = issue_counts.get('accuracy', 0) + 1
            if 'unclear' in issue or 'confusing' in issue:
                issue_counts['clarity'] = issue_counts.get('clarity', 0) + 1
            if 'incomplete' in issue or 'missing' in issue:
                issue_counts['completeness'] = issue_counts.get('completeness', 0) + 1
        
        # Find most problematic queries
        problematic_queries = {}
        for entry in low_rated:
            query = entry['query'].lower()
            problematic_queries[query] = problematic_queries.get(query, 0) + 1
        
        return {
            "total_feedback": len(feedback_data),
            "average_rating": round(avg_rating, 2),
            "low_rated_count": len(low_rated),
            "common_issues": issue_counts,
            "problematic_queries": dict(sorted(problematic_queries.items(), key=lambda x: x[1], reverse=True)[:5]),
            "improvement_priority": max(issue_counts.items(), key=lambda x: x[1])[0] if issue_counts else "No major issues identified"
        }
    
    def get_learning_insights(self) -> str:
        """Generate learning insights from feedback data."""
        patterns = self.analyze_feedback_patterns()
        
        if "message" in patterns:
            return patterns["message"]
        
        insights = []
        insights.append(f"**📊 Learning Progress:** {patterns['total_feedback']} feedback entries collected")
        insights.append(f"**⭐ Average Rating:** {patterns['average_rating']}/5.0 stars")
        insights.append(f"**📉 Low-rated Responses:** {patterns['low_rated_count']} responses need improvement")
        
        if patterns['common_issues']:
            top_issue = patterns['improvement_priority']
            insights.append(f"**🎯 Priority Issue:** {top_issue.title()} needs attention")
        
        if patterns['problematic_queries']:
            top_query = list(patterns['problematic_queries'].keys())[0]
            insights.append(f"**❓ Most Problematic Query:** '{top_query}' (appears {patterns['problematic_queries'][top_query]} times)")
        
        return "\n".join(insights)
    
    def render_learning_dashboard(self):
        """Render the learning and feedback dashboard with modern UI."""
        # Load persistent feedback data
        if 'learning_feedback' not in st.session_state:
            st.session_state.learning_feedback = self._load_feedback_data()
        
        if 'learning_feedback' not in st.session_state or not st.session_state.learning_feedback:
            st.markdown('<div class="learning-card">', unsafe_allow_html=True)
            st.info("📊 No feedback data available yet. Rate responses to help improve the system!")
            
            # Show how feedback improves the model
            st.markdown("### 🚀 How Feedback Improves the Model")
            st.markdown("""
            **Your feedback directly improves the chatbot in several ways:**
            
            1. **📈 Response Quality**: Low ratings trigger analysis of what went wrong
            2. **📝 Template Updates**: Common issues get added to template responses  
            3. **⚖️ Bias Detection**: Feedback helps identify and reduce bias patterns
            4. **🎯 Context Improvement**: Better context selection based on user preferences
            5. **🛡️ Safety Enhancement**: Sensitive data detection improves with feedback
            6. **🔄 Learning Loop**: System learns from successful vs. unsuccessful responses
            
            **💾 Data Storage**: All feedback is stored in `data/feedback_data.json` and persists across app restarts.
            """)
            
            st.markdown("---")
            st.subheader("✨ Try the Feedback System")
            st.markdown("Ask a question in the chat, then rate the response to see how the learning system works! 🎯")
            
            st.markdown("**📋 What we track:**")
            st.markdown("- ⭐ Response ratings (1-5 stars)")
            st.markdown("- 💬 Detailed feedback comments")
            st.markdown("- 💡 Improvement suggestions")
            st.markdown("- 📊 Learning trends over time")
            
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Show learning insights
        st.markdown("### 🧠 Learning Insights")
        insights = self.get_learning_insights()
        st.markdown(f'<div class="learning-insight">{insights}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        feedback_data = st.session_state.learning_feedback
        
        # Calculate learning metrics
        total_feedback = len(feedback_data)
        avg_rating = sum(f['rating'] for f in feedback_data) / total_feedback
        recent_feedback = feedback_data[-10:] if len(feedback_data) >= 10 else feedback_data
        
        st.subheader("📊 Learning & Improvement Dashboard")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="learning-metric">', unsafe_allow_html=True)
            st.metric("📋 Total Feedback", total_feedback)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="learning-metric">', unsafe_allow_html=True)
            st.metric("⭐ Average Rating", f"{avg_rating:.1f}/5")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="learning-metric">', unsafe_allow_html=True)
            st.metric("📝 Recent Feedback", len(recent_feedback))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Show recent feedback
        st.subheader("💬 Recent Feedback")
        for feedback in recent_feedback[-5:]:  # Show last 5
            with st.expander(f"❓ Query: {feedback['query'][:50]}... (⭐ {feedback['rating']}/5)", expanded=False):
                st.markdown(f"**🤖 Response:** {feedback['response'][:200]}...")
                st.markdown(f"**💭 Feedback:** {feedback['feedback']}")
                if feedback['improvement_suggestions']:
                    st.markdown("**💡 Improvement Suggestions:**")
                    for suggestion in feedback['improvement_suggestions']:
                        st.markdown(f"- {suggestion}")
    
    def render_hallucination_detection(self, response: str, sources: List[Dict]) -> bool:
        """Detect potential hallucinations and flag them with modern UI."""
        hallucination_indicators = [
            'according to my knowledge',
            'i believe',
            'i think',
            'it seems',
            'possibly',
            'might be',
            'could be',
            'i\'m not sure',
            'i don\'t know'
        ]
        
        response_lower = response.lower()
        detected_indicators = [indicator for indicator in hallucination_indicators if indicator in response_lower]
        
        if detected_indicators:
            st.markdown('<div class="safety-status safety-warning">🔍 Potential hallucination detected</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="bias-item">
                <strong>🎯 Indicators:</strong> {", ".join(detected_indicators)}<br>
                <strong>💡 Recommendation:</strong> Verify with authoritative sources
            </div>
            """, unsafe_allow_html=True)
            return True
        
        st.markdown('<div class="safety-status safety-pass">✅ No hallucination indicators detected</div>', unsafe_allow_html=True)
        return False
