import argparse
import json
from pathlib import Path


def assess(case, scenario):
    firewall_ports = case['firewall']['allowed_tcp_ports']
    if scenario != 'current':
        added_ports = case['changes'][scenario]['add_tcp_ports']
        if added_ports == 'any':
            firewall_ports = 'any'
        else:
            firewall_ports = firewall_ports + added_ports
    security_group_ports = case['security_group']['allowed_tcp_ports']
    results = []
    for check in case['checks']:
        port = check['port']
        firewall_allows = firewall_ports == 'any' or port in firewall_ports
        security_group_allows = port in security_group_ports
        allowed = firewall_allows and security_group_allows
        results.append((check, firewall_allows, security_group_allows, allowed))
    return results


def main():
    parser = argparse.ArgumentParser(description='Web-to-app access case study')
    parser.add_argument('scenario', choices=['current', 'broad', 'scoped'])
    args = parser.parse_args()
    case_path = Path(__file__).with_name('case.json')
    case = json.loads(case_path.read_text())
    print(f"\n{case['scenarios'][args.scenario]}\n")
    print(f"{'Connection':24} {'Firewall':10} {'AWS SG':10} {'Result':10} Goal")
    for check, firewall_allows, security_group_allows, allowed in assess(case, args.scenario):
        firewall = 'ALLOW' if firewall_allows else 'BLOCK'
        security_group = 'ALLOW' if security_group_allows else 'BLOCK'
        result = 'ALLOWED' if allowed else 'BLOCKED'
        goal = 'PASS' if allowed == check['should_allow'] else 'FAIL'
        label = f"{check['name']} :{check['port']}"
        print(f'{label:24} {firewall:10} {security_group:10} {result:10} {goal}')
    print('\nSimulation only. Both controls must allow. No live changes.')


if __name__ == '__main__':
    main()

# python3 northwind.py current
# python3 northwind.py broad
# python3 northwind.py scoped
