import abc
import json
import git
from datetime import datetime
from config import Config

class BaseAgent(abc.ABC):
    def __init__(self, agent_id, conductor):
        self.agent_id = agent_id
        self.conductor = conductor
        self.long_term_memory = []
        self.context = []
        self.sub_agents = []
        self.cost = 0
        
    def initialize(self, task_spec):
        self.task_spec = task_spec
        self.create_version_snapshot(f"{self.agent_id}_init")
        
    @abc.abstractmethod
    def execute(self):
        pass
    
    def create_sub_agent(self, agent_type, task_spec):
        sub_agent_id = f"sub_{agent_type}_{datetime.now().strftime('%H%M%S')}"
        self.sub_agents.append({
            "id": sub_agent_id,
            "type": agent_type,
            "spec": task_spec,
            "status": "pending"
        })
        return self.conductor.create_agent(agent_type, task_spec)
    
    def create_version_snapshot(self, message):
        try:
            repo = git.Repo('sports_betting_ai')
            repo.git.add('--all')
            commit = repo.index.commit(message)
            self.conductor.version_snapshots[commit.hexsha] = {
                "timestamp": datetime.now(),
                "agent": self.agent_id,
                "message": message
            }
            return True
        except Exception as e:
            print(f"Version control error: {str(e)}")
            return False
    
    def log_performance(self, result, confidence):
        self.conductor.performance_log.append({
            "agent": self.agent_id,
            "timestamp": datetime.now(),
            "result": result,
            "confidence": confidence,
            "cost": self.cost
        })
    
    def request_human_approval(self, reason):
        # In production, would trigger notification
        print(f"ACTION REQUIRED: {reason}")
        return False
