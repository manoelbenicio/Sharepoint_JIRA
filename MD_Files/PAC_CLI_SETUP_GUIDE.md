# Power Platform CLI (PAC) Setup Guide

## Installation (Windows)

```powershell
# Option 1: winget
winget install Microsoft.PowerAppsCLI

# Option 2: dotnet tool
dotnet tool install --global Microsoft.PowerApps.CLI.Tool
```

## Authentication

```powershell
# Create auth profile (opens browser)
pac auth create
```

### Active Profile (2025-12-28)

| Property | Value |
|----------|-------|
| User | mbenicios@minsait.com |
| Cloud | Public |
| Organization | Default |
| Environment URL | https://orgd32f66fd.crm4.dynamics.com/ |

## Common Commands

```powershell
# List auth profiles
pac auth list

# List organizations/environments  
pac org list

# Select environment interactively
pac org select

# List solutions
pac solution list

# Export solution (includes flows)
pac solution export --name "SolutionName" --path "./solution.zip"

# Import solution
pac solution import --path "./solution.zip"
```

## Flow Management via Solutions

Power Automate flows must be in a **Solution** to be managed via CLI:

1. In Power Automate portal: Create flow inside a Solution
2. Export: `pac solution export --name "MySolution" --path ./flows.zip`
3. Import to another env: `pac solution import --path ./flows.zip`

## References

- [PAC CLI Documentation](https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction)
- [Solution Management](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm)
