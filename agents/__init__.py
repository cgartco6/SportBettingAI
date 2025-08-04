"""
agents package - Contains all specialized AI agents for the sports betting prediction system
"""

from .base_agent import BaseAgent
from .data_collector import DataCollectorAgent
from .feature_engineer import FeatureEngineerAgent
from .model_trainer import ModelTrainerAgent
from .prediction_engine import PredictionEngineAgent
from .value_identifier import ValueIdentifierAgent
from .reporting_agent import ReportingAgent
from .qa_agent import QAAgent

# Define public interface for the agents module
__all__ = [
    'BaseAgent',
    'DataCollectorAgent',
    'FeatureEngineerAgent',
    'ModelTrainerAgent',
    'PredictionEngineAgent',
    'ValueIdentifierAgent',
    'ReportingAgent',
    'QAAgent'
]

# Agent registry for dynamic creation
AGENT_REGISTRY = {
    'base': BaseAgent,
    'data_collector': DataCollectorAgent,
    'feature_engineer': FeatureEngineerAgent,
    'model_trainer': ModelTrainerAgent,
    'prediction_engine': PredictionEngineAgent,
    'value_identifier': ValueIdentifierAgent,
    'reporting_agent': ReportingAgent,
    'qa_agent': QAAgent
}

def create_agent(agent_type, agent_id, conductor, task_spec=None):
    """
    Factory function for creating agent instances
    
    Args:
        agent_type (str): Type of agent to create
        agent_id (str): Unique identifier for the agent
        conductor (ProjectConductor): Reference to the main conductor
        task_spec (dict): Task specification for the agent
    
    Returns:
        Agent: Instance of the requested agent type
    """
    agent_class = AGENT_REGISTRY.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    agent = agent_class(agent_id, conductor)
    if task_spec:
        agent.initialize(task_spec)
    return agent
