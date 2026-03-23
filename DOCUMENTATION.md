## VM Creation with Vagrant

The experiment starts with creating the four VMs using Vagrant (SSI cloud + two edge nodes + ground node):

```bash
cd infra/nodes
vagrant plugin install vagrant-hostmanager
vagrant up
vagrant status
```

If enabled, `vagrant-hostmanager` automatically updates `/etc/hosts` for the host. Manual edits are optional if plugin does the job.

Now configure bridged networking and static IPs (see below).

## Network Setup (Bridge + Host Interface)

The VMs are connected via a bridge interface that uses the host network interface. To ensure communication among VMs and from the control host, configure the host with a static IP in the same subnet as the VMs.

Required hostnames (in Vagrant and /etc/hosts):
 - `ssi-cloud`
 - `ssi-edge-alpha`
 - `ssi-edge-beta`
 - `ssi-ground`

Vagrant should use a bridge adapter and bind to the host interface explicitly. Example Vagrantfile snippet:

```ruby
config.vm.network "public_network", bridge: "enp3s0", ip: "192.168.0.2"
config.vm.hostname = "ssi-cloud"
```

Repeat for all nodes with corresponding hostnames and VM IPs:
 - `ssi-cloud`: 192.168.0.2
 - `ssi-edge-alpha`: 192.168.0.3
 - `ssi-edge-beta`: 192.168.0.4
 - `ssi-ground`: 192.168.0.5

On the host machine, set a static IP on the same subnet (e.g., `192.168.0.1`) and ensure router/DHCP does not conflict.

Add entries in `/etc/hosts`:
```
192.168.0.2 ssi-cloud
192.168.0.3 ssi-edge-alpha
192.168.0.4 ssi-edge-beta
192.168.0.5 ssi-ground
```

# SSI Mobile Edge Computing Experiment: Digital Twin Migration & Capability Delegation

## Overview

This experiment demonstrates two key capabilities of Self-Sovereign Identity (SSI) in Mobile Edge Computing:

1. **Digital Twin Application Migration**: Migrating an application between two edge nodes while maintaining agent identity
2. **Capability Delegation Verification**: Using Verifiable Credentials (VCs) to delegate capabilities, allowing one agent to access another's data only with proper authorization

## Experiment Architecture

### Network Setup

The experiment requires four nodes communicating over a network:

- **ssi-cloud**: Central cloud node (IP: 192.168.0.2)
  - Runs the Indy distributed ledger
  - Hosts the credential authority
  
- **ssi-edge-alpha**: First edge computing node (IP: 192.168.0.3)
  - Hosts the digital twin applications
  
- **ssi-edge-beta**: Second edge computing node (IP: 192.168.0.4)
  - Hosts the digital twin applications
  
- **ssi-ground**: Ground control/vehicle node (IP: 192.168.0.5)
  - Hosts the physical twin applications

## Repository Structure

```
.
├── app/                                  # Main application services
│   ├── global_config.py                 # Global configuration
│   ├── app_authorities/                 # Credential authority service
│   │   ├── main.py                      # Application entry point
│   │   ├── env_config.py                # Environment configuration
│   │   ├── routes/                      # API endpoints
│   │   ├── dependencies/                # Dependency injection
│   │   ├── utils/                       # Service utilities
│   │   └── data/                        # Configuration data
│   ├── app_car/                         # Car entity service
│   ├── app_drone/                       # Drone entity service
│   ├── app_digital_twin_car/            # Digital twin for car
│   ├── app_digital_twin_drone/          # Digital twin for drone
│   ├── app_edge/                        # Edge node coordinator
│   └── utils/                           # Shared infrastructure
│       ├── agent.py                     # ACA-Py agent management
│       ├── logger.py                    # Centralized logging
│       ├── utils.py                     # Helper utilities
│       ├── bootstrap_data/              # Ledger bootstrap files
│       ├── models/                      # Data models
│       ├── ssi/                         # SSI utilities
│       ├── vdr/                         # VDR interactions
│       └── web/                         # Web service utilities
│
├── acapy-plugins/                      # Custom ACA-Py extensions
│   └── ShortTTLForDIDDocCache/         # DID document cache plugin
│
├── bootstrap/                           # Ledger and actor setup
│   ├── 00_register-actors.py            # Actor registration script
│   ├── actors.json                      # Actor DIDs and seeds
│   └── genesis.txt                      # Ledger genesis block
│
├── deployment/                          # Ansible deployment automation
│   ├── 01-install-basic-software.yaml
│   ├── 02-00-cloud-install-von-network.yaml
│   ├── 02-01-setup-von-network-clean.yaml
│   ├── 03-deploy-universal-resolver-custom-indy.yaml
│   ├── 04-01-clear-ssi-apps.yaml
│   ├── 04-02-prune-unused-images.yaml
│   ├── 04-03-deploy-ssi-apps.yaml
│   ├── ansible.cfg
│   ├── inventory                        # Target hosts
│   ├── group_vars/                      # Shared variables
│   ├── host_vars/                       # Host-specific variables
│   └── roles/                           # Ansible role definitions
│
├── dockerfiles/                         # Container configurations
│   ├── apps.dockerfile                  # Application image
│   └── custom_indy_resolver_driver.dockerfile
│
├── build-scripts/                       # Build automation
│
├── infra/                               # Local infrastructure setup
│   ├── README.MD
│   └── nodes/
│       ├── config.yaml
│       └── Vagrantfile
│
└── Configuration files
    ├── requirements.txt                 # Python dependencies
    ├── aca-py_cmdline_args.txt         # ACA-Py arguments template
    ├── example_docker_cmd.txt          # Docker command examples
    └── start_apps_local.txt            # Local startup guide
```

## Prerequisites & System Requirements

Before starting the experiment, ensure you have:

### Hardware & OS
- **OS**: Linux (Ubuntu 20.04+ recommended) for VMs and control machine
- **CPU**: 12+ cores recommended
- **RAM**: 16GB+ for running 4 VMs simultaneously

### Required Software (on control machine)

1. **Vagrant** v2.4.7+
   - Install: https://www.vagrantup.com/downloads
   - Verify: `vagrant --version`
   - Install plugin: `vagrant plugin install vagrant-hostmanager`

2. **Ansible** 2.12+
   - Install: `pip install ansible>=2.12`
   - Verify: `ansible --version`

3. **Python** 3.10+
   - Verify: `python --version`


## Deployment with Ansible

After Vagrant VM creation and network setup, deploy the applications to all nodes using Ansible.

```bash
cd deployment

# 1) Install base dependencies on all nodes
ansible-playbook -i inventory 01-install-basic-software.yaml

# 2) Set up the VON/Indy ledger on the cloud node
ansible-playbook -i inventory 02-00-cloud-install-von-network.yaml

# 3) Register actors on the ledger
cd ..
python bootstrap/00_register-actors.py

# 4) Deploy SSI application containers to all nodes
ansible-playbook -i inventory 04-03-deploy-ssi-apps.yaml
```

`vagrant-hostmanager` should update host entries automatically so the ansible inventory names are resolvable.

If you need to reset or cleanup before retrying:

```bash
ansible-playbook -i inventory 04-01-clear-ssi-apps.yaml
ansible-playbook -i inventory 04-02-prune-unused-images.yaml
```

## Running the Experiment Scenarios

Once infrastructure is deployed, the experiment has two main scenarios triggered by HTTP requests.

### Scenario 1: Digital Twin Application Migration

**Goal**: Migrate the digital twin car application from edge-alpha to edge-beta while maintaining its identity.

**Trigger**: Send HTTP POST request to the digital twin car's `/triggers/app_migration/` endpoint

```bash
# Execute from control machine (or any machine with network access)
curl -X POST http://ssi-edge-alpha:5002/triggers/app_migration/
```

**What happens**:
1. Digital twin car (currently on edge-alpha) initiates migration
2. Creates a new container on edge-beta with same application image
3. Starts a new ACA-Py agent on edge-beta with migration flag
4. Rotates verification key on the ledger (changes verkey)
5. Old application container terminates
6. Digital twin car now runs on edge-beta with new agent

### Scenario 2: Capability Delegation & Conditional Access

**Goal**: Demonstrate that the digital twin drone can only access car data if it has a capability delegation credential from the car.

**Step 1 - Request Capability Delegation**:
```bash
# Digital twin car requests capability delegation VC from the physical car
curl -X POST http://ssi-edge-alpha:5002/triggers/request_capability_delegation/
```

**What happens**:
1. Digital twin car agent creates invitation for the car agent
2. Car agent receives invitation and establishes connection
3. Car agent issues a capability delegation VC to digital twin car
4. Digital twin car stores the credential

**Step 2 - Digital Twin Drone Requests Car Data**:
```bash
# Digital twin drone requests car information
curl -X POST http://ssi-edge-alpha:5003/triggers/request_car_position/
```

**What happens**:
1. Digital twin drone agent creates invitation for digital twin car
2. Digital twin car receives invitation and establishes connection
5. Only if VC is valid, digital twin drone reveals car's position

**Without Valid VC**:
- If digital twin car hasn't received capability delegation VC from car agent
- Or if credential verification fails
- Digital twin drone denies the request from digital twin car
