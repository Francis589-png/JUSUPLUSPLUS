"""Small runner script for the Automation Agent demo."""
from projects.automation_agent.agent import Agent
import json

if __name__ == '__main__':
    a = Agent()
    a.discover()
    print('Discovered plugins:', list(a.plugins.keys()))
    results = a.run_all({'trigger': 'manual'})
    print('Results:')
    print(json.dumps(results, indent=2))
