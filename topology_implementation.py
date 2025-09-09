#!/usr/bin/env python3
"""
Crisis Management Knowledge Topology Implementation
Integrates leading consultancy, government, and AI insights into the Polycrisis Simulator
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# Knowledge Source Models
class KnowledgeSource(BaseModel):
    name: str
    full_name: str
    type: str
    specialization: List[str]
    url: str
    api_availability: bool
    content_types: List[str]
    update_frequency: str
    credibility_score: float
    merger_history: Optional[Dict] = None

class KnowledgeCategory(BaseModel):
    category: str
    description: str
    priority: str
    access_level: str
    sources: List[KnowledgeSource]

class KnowledgeTopology(BaseModel):
    meta: Dict
    topology: Dict[str, KnowledgeCategory]
    integration_framework: Dict
    implementation_roadmap: Dict

class TopologyManager:
    """Manages the knowledge topology for crisis management insights"""
    
    def __init__(self, topology_file: str = "/app/knowledge_topology.json"):
        self.topology_file = topology_file
        self.topology: Optional[KnowledgeTopology] = None
        self.load_topology()
    
    def load_topology(self):
        """Load the knowledge topology from JSON file"""
        try:
            with open(self.topology_file, 'r') as f:
                data = json.load(f)
                self.topology = KnowledgeTopology(**data['knowledge_topology'])
                print(f"✅ Loaded knowledge topology with {len(self.topology.topology)} categories")
        except Exception as e:
            print(f"❌ Error loading topology: {e}")
    
    def get_sources_by_priority(self, priority: str) -> List[KnowledgeSource]:
        """Get all sources filtered by priority level"""
        sources = []
        for category_name, category in self.topology.topology.items():
            if category.priority == priority:
                sources.extend(category.sources)
        return sources
    
    def get_sources_by_specialization(self, specialization: str) -> List[KnowledgeSource]:
        """Get sources that specialize in a specific area"""
        sources = []
        for category_name, category in self.topology.topology.items():
            for source in category.sources:
                if specialization.lower() in [s.lower() for s in source.specialization]:
                    sources.append(source)
        return sources
    
    def get_api_enabled_sources(self) -> List[KnowledgeSource]:
        """Get sources that have API availability"""
        sources = []
        for category_name, category in self.topology.topology.items():
            for source in category.sources:
                if source.api_availability:
                    sources.append(source)
        return sources
    
    def generate_crisis_insight_strategy(self, crisis_type: str, severity: int) -> Dict:
        """Generate a knowledge sourcing strategy for a specific crisis"""
        
        # Map crisis types to relevant specializations
        crisis_specialization_map = {
            'economic_crisis': ['strategy', 'financial_analytics', 'risk_assessment', 'market_analysis'],
            'natural_disaster': ['crisis_management', 'emergency_response', 'risk_management'],
            'cyber_attack': ['technology_strategy', 'digital_transformation', 'cybersecurity'],
            'pandemic': ['healthcare', 'behavioral_economics', 'policy_design', 'crisis_communication'],
            'geopolitical_crisis': ['geopolitical_risk', 'strategic_forecasting', 'government_relations'],
            'supply_chain_disruption': ['operations', 'logistics', 'risk_management'],
            'climate_change': ['environmental_strategy', 'sustainability', 'adaptation_planning']
        }
        
        relevant_specializations = crisis_specialization_map.get(crisis_type, ['crisis_management', 'strategy'])
        
        # Get recommended sources
        recommended_sources = []
        for spec in relevant_specializations:
            sources = self.get_sources_by_specialization(spec)
            recommended_sources.extend(sources)
        
        # Remove duplicates while preserving order
        unique_sources = []
        seen = set()
        for source in recommended_sources:
            if source.name not in seen:
                unique_sources.append(source)
                seen.add(source.name)
        
        # Sort by credibility score and priority
        priority_weights = {'high': 3, 'medium': 2, 'low': 1}
        
        def source_score(source):
            category = None
            for cat_name, cat in self.topology.topology.items():
                if source in cat.sources:
                    category = cat
                    break
            
            priority_weight = priority_weights.get(category.priority if category else 'medium', 2)
            return source.credibility_score * priority_weight
        
        unique_sources.sort(key=source_score, reverse=True)
        
        # Build strategy based on severity
        if severity >= 8:  # Critical crisis
            strategy_sources = unique_sources[:8]  # Top 8 sources
            access_levels = ['exclusive', 'enterprise', 'premium']
        elif severity >= 6:  # Major crisis
            strategy_sources = unique_sources[:6]  # Top 6 sources
            access_levels = ['enterprise', 'premium', 'subscription']
        elif severity >= 4:  # Moderate crisis
            strategy_sources = unique_sources[:4]  # Top 4 sources
            access_levels = ['premium', 'subscription', 'freemium']
        else:  # Minor crisis
            strategy_sources = unique_sources[:3]  # Top 3 sources
            access_levels = ['subscription', 'freemium', 'public']
        
        return {
            'crisis_type': crisis_type,
            'severity_level': severity,
            'recommended_sources': [
                {
                    'name': source.name,
                    'full_name': source.full_name,
                    'credibility_score': source.credibility_score,
                    'specialization': source.specialization,
                    'api_available': source.api_availability,
                    'url': source.url
                }
                for source in strategy_sources
            ],
            'recommended_access_levels': access_levels,
            'total_sources': len(strategy_sources),
            'api_sources': len([s for s in strategy_sources if s.api_availability]),
            'average_credibility': sum(s.credibility_score for s in strategy_sources) / len(strategy_sources) if strategy_sources else 0
        }
    
    def get_implementation_phase_sources(self, phase: int) -> List[str]:
        """Get sources recommended for a specific implementation phase"""
        phase_key = f"phase_{phase}"
        if phase_key in self.topology.implementation_roadmap:
            return self.topology.implementation_roadmap[phase_key]['sources']
        return []
    
    def generate_topology_summary(self) -> Dict:
        """Generate a comprehensive summary of the topology"""
        total_sources = 0
        api_sources = 0
        avg_credibility = 0
        
        categories_summary = {}
        
        for cat_name, category in self.topology.topology.items():
            cat_api_count = sum(1 for s in category.sources if s.api_availability)
            cat_avg_credibility = sum(s.credibility_score for s in category.sources) / len(category.sources)
            
            categories_summary[cat_name] = {
                'name': category.category,
                'source_count': len(category.sources),
                'api_sources': cat_api_count,
                'average_credibility': round(cat_avg_credibility, 2),
                'priority': category.priority,
                'access_level': category.access_level
            }
            
            total_sources += len(category.sources)
            api_sources += cat_api_count
            avg_credibility += sum(s.credibility_score for s in category.sources)
        
        return {
            'total_categories': len(self.topology.topology),
            'total_sources': total_sources,
            'api_enabled_sources': api_sources,
            'average_credibility': round(avg_credibility / total_sources, 2) if total_sources > 0 else 0,
            'categories': categories_summary,
            'implementation_phases': len(self.topology.implementation_roadmap),
            'access_tiers': list(self.topology.integration_framework['access_tiers'].keys())
        }

def main():
    """Demo the topology manager functionality"""
    print("🧠 Crisis Management Knowledge Topology Demo")
    print("=" * 50)
    
    # Initialize topology manager
    manager = TopologyManager()
    
    if not manager.topology:
        print("❌ Failed to load topology")
        return
    
    # Generate summary
    summary = manager.generate_topology_summary()
    print(f"\n📊 Topology Summary:")
    print(f"   Total Categories: {summary['total_categories']}")
    print(f"   Total Sources: {summary['total_sources']}")
    print(f"   API-Enabled Sources: {summary['api_enabled_sources']}")
    print(f"   Average Credibility: {summary['average_credibility']}/10")
    
    # Show high-priority sources
    high_priority = manager.get_sources_by_priority('high')
    print(f"\n🎯 High Priority Sources ({len(high_priority)}):")
    for source in high_priority[:5]:  # Show top 5
        print(f"   • {source.name} ({source.credibility_score}/10)")
    
    # Show API-enabled sources
    api_sources = manager.get_api_enabled_sources()
    print(f"\n🔌 API-Enabled Sources ({len(api_sources)}):")
    for source in api_sources:
        print(f"   • {source.name} - {source.url}")
    
    # Demo crisis strategy generation
    print(f"\n🚨 Crisis Strategy Demo:")
    crisis_types = ['economic_crisis', 'cyber_attack', 'pandemic']
    
    for crisis_type in crisis_types:
        strategy = manager.generate_crisis_insight_strategy(crisis_type, severity=7)
        print(f"\n   Crisis: {crisis_type.replace('_', ' ').title()}")
        print(f"   Recommended Sources: {strategy['total_sources']}")
        print(f"   API Sources: {strategy['api_sources']}")
        print(f"   Avg Credibility: {strategy['average_credibility']:.1f}/10")
        print(f"   Top Source: {strategy['recommended_sources'][0]['name'] if strategy['recommended_sources'] else 'None'}")

if __name__ == "__main__":
    main()