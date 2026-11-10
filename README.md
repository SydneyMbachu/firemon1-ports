# Northwind: one connection, two controls

**Situation:** The web server needs the application's new port, 8443. The firewall still allows only the old port, 8080. The AWS security group allows 8443 and a legacy administrative port, 22.

**Request:** Open all TCP ports at the firewall. That restores application access but also opens SSH.

**Recommendation:** Add only 8443. Required access works; SSH stays blocked.

From this folder, run one command at a time:

```bash
python3 northwind.py current
```

```bash
python3 northwind.py broad
```

```bash
python3 northwind.py scoped
```

| Scenario | API 8443 | SSH 22 |
|---|---|---|
| Current | Blocked — FAIL | Blocked — PASS |
| Broad request | Allowed — PASS | Allowed — FAIL |
| Scoped change | Allowed — PASS | Blocked — PASS |

**Read each row left to right:** firewall permission → security-group permission → combined result → whether it meets the customer's goal. Both controls must allow a connection. Blocked SSH is a PASS because the customer wants SSH blocked.

## How it works

`case.json` supplies the permissions, proposals and goals. `assess()` calculates the two checks; `main()` prints the results. Proposals add permissions to an in-memory list. Neither proposal changes the JSON file or a live device. Rerunning starts from the same baseline; no reset required.

Python 3.10+ only. No installation, API keys, internet or cloud accounts needed. Verify with `python3 -m unittest -v`.

## Scope

This is a custom offline simulation, not FireMon software or a vendor configuration parser. It assumes one fixed web-to-application path with two mandatory allow-list controls and implicit deny. Source/destination scope is fixed and assumed correct. Only new TCP connections on the two listed ports are assessed; no CIDRs, zones, rule ordering, routing, NAT, egress checks or Unknown-state engine. Input is a trusted, complete fixture—not production configuration. Real changes require approval and live validation.

The script calculates decisions from the inputs; it does not hard-code the result table. The two checks here are narrower than the seven-check case in `firemon`. The original `firemon` folder has been removed.

## Live AWS firewall lab

See [lab/README.md](lab/README.md) for the VM-Series Terraform draft, Marketplace checklist, deployment stages, and teardown. The live lab has not been deployed.
