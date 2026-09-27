# Digital FIR

## A Blockchain Based Secure First Information Report Management System for the Pakistan Police

**Riphah International University**
**Degree:** BS Computer Science
**Project Type:** Final Year Project
**Academic Year:** 2026/2027
**Development Context:** Islamabad, Pakistan

## Project Overview

Digital FIR is a web based First Information Report management system designed to provide a structured, secure, and traceable process for handling FIR related information.

The project focuses on improving the management of FIR records, investigation related information, evidence records, user access, and audit activities through a centralized application architecture with blockchain based integrity verification.

Sensitive application data will remain off chain in the primary database and protected file storage. Hyperledger Fabric will be used for selected blockchain records such as data hashes, transaction identifiers, workflow events, and relevant evidence metadata.

The project is intended as an academic prototype using synthetic and demonstration data. It will not connect to live police, NADRA, or other government systems.

## Objectives

1. Develop a secure web based Digital FIR management system.
2. Provide controlled access based on user roles and responsibilities.
3. Manage FIR registration and related investigation information digitally.
4. Support structured evidence record management.
5. Maintain an auditable history of important system activities.
6. Use blockchain to provide tamper evident integrity verification for selected records.
7. Separate sensitive operational data from blockchain data through an off chain and on chain architecture.
8. Provide a practical foundation for future extension and deployment.

## Main Users

The system is designed around the following roles:

1. Citizen / Complainant
2. Police Officer
3. Investigation Officer
4. SHO
5. Supervisory Officer
6. Administrator
7. Audit Authority

Each role will have controlled permissions according to its responsibilities within the system.

## Core Modules

The planned system includes:

1. Authentication and Authorization
2. Citizen Portal
3. FIR Management
4. Police Station Management
5. Investigation Management
6. Evidence Management
7. Blockchain Integration
8. Audit Management
9. Notifications
10. Analytics
11. Administration

The exact implementation of each module will be defined during the design and development phases.

## Technology Stack

### Frontend

React
TypeScript
Tailwind CSS
Axios
React Router

### Backend

Python
FastAPI

### Database

PostgreSQL

### Blockchain

Hyperledger Fabric

### Architecture

The project will follow a hybrid off chain and on chain architecture.

Sensitive FIR and operational information will be stored off chain in PostgreSQL and protected file storage.

Blockchain will be used for integrity verification and selected audit related records. SHA 256 hashing will be considered for generating integrity hashes.

## High Level Workflow

```text
Citizen / Complainant
        |
        v
   Digital FIR Portal
        |
        v
 Authentication and Authorization
        |
        v
      FastAPI
        |
        +--------------------+
        |                    |
        v                    v
   PostgreSQL          File Storage
        |
        |
        v
   Application Data
        |
        v
 Hash Generation and
 Blockchain Transactions
        |
        v
 Hyperledger Fabric
        |
        v
 Integrity Verification
 and Audit Trail
```

## Off Chain and On Chain Data

### Off Chain

The following types of information are expected to remain off chain:

1. Sensitive FIR information
2. Citizen information
3. User account information
4. Investigation details
5. Detailed evidence files
6. Application operational data
7. Other information that should not be stored directly on the blockchain

### On Chain

The blockchain layer is expected to contain selected records such as:

1. Record hashes
2. Transaction identifiers
3. Important workflow events
4. Selected evidence metadata
5. Integrity related information required for verification

The exact on chain data model will be finalized during implementation.

## Security Approach

Security will be considered across the application rather than treated as a separate feature.

The planned approach includes:

1. Authentication
2. Role Based Access Control
3. Secure password handling
4. Input validation
5. API authorization
6. Protected database access
7. Secure handling of sensitive files
8. Integrity verification using cryptographic hashes
9. Blockchain based audit related records
10. Environment based configuration for secrets and credentials

Specific security controls will be implemented and tested during development.

## Project Scope

The project focuses on building an academic prototype of a Digital FIR management platform.

The prototype will demonstrate:

1. User authentication and role management
2. FIR creation and management
3. Police and investigation workflows
4. Evidence record management
5. Audit related activities
6. Blockchain integration
7. Data integrity verification
8. Web based interaction between users and the system

## Out of Scope

The following are outside the current project scope:

1. Live integration with Pakistan Police systems
2. Live integration with NADRA
3. Integration with real criminal databases
4. Facial recognition
5. AI based criminal profiling
6. Automated guilt or innocence decisions
7. Production deployment for real government operations

## Team

### Project Members

1. Sharaiz Ahmed
2. Basit Ali
3. Abdul Moiz

### Project Supervisor

**Tabassum Javed**

## Development Status

The project is currently in the initial development stage.

### Completed

1. Project idea and problem definition
2. Technology stack selection
3. Project proposal
4. Project presentation
5. High level system architecture
6. Initial module planning

### In Progress

1. Technical specification
2. System design
3. Database design
4. Backend architecture
5. Blockchain integration design

### Planned

1. Backend foundation
2. PostgreSQL integration
3. Authentication and Role Based Access Control
4. FIR management
5. Investigation management
6. Evidence management
7. Audit system
8. Hyperledger Fabric integration
9. Frontend development
10. Testing
11. Documentation

## Repository Principle

This repository will contain the actual implementation and documentation of the Digital FIR project.

Documentation will be updated as the system is designed and implemented. Features, APIs, database structures, security controls, and blockchain workflows will only be documented as finalized after they are actually designed or implemented.

## Academic Note

This project is developed for academic purposes as a Final Year Project at Riphah International University.

The system uses synthetic and demonstration data and does not represent an operational government or police information system.

## Future Documentation

As development progresses, the repository may include documentation covering:

1. System Requirements
2. Software Architecture
3. Database Design
4. API Documentation
5. Authentication and Authorization
6. Blockchain Architecture
7. Development Setup
8. Testing
9. Deployment
10. User Guide
11. Project Reports

## License

This project is developed as an academic Final Year Project. Licensing and usage terms will be defined separately if required.
