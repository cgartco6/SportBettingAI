import os
import time
from dotenv import load_dotenv
from agents import DataCollectorAgent, ProjectConductor

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Starting Sports Betting AI System...")
    
    # Initialize conductor
    conductor = ProjectConductor(initial_budget=float(os.getenv("INITIAL_BUDGET", 10000)))
    
    # Create initial agent
    data_agent_id = conductor.create_agent(
        "data_collector",
        {"sources": ["Hollywoodbets", "Betway"]}
    )
    
    # Execute workflow
    while conductor.agent_pool:
        current_agent_id = list(conductor.agent_pool.keys())[0]
        agent = conductor.agent_pool[current_agent_id]
        
        print(f"\n=== Executing {current_agent_id} ===")
        result = agent.execute()
        
        # Handle next agent
        if "next_agent" in result:
            print(f"Passing to next agent: {result['next_agent']}")
        else:
            print(f"Completed {current_agent_id}")
        
        # Remove completed agent
        del conductor.agent_pool[current_agent_id]
        
        # Budget check
        if conductor.budget <= 1000:
            print("Budget critically low - pausing operations")
            time.sleep(60 * 60)  # Sleep for 1 hour
            
    print("All tasks completed!")
