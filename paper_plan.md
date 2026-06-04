# Paper Plan

## Recommended title

**A Software-Defined Low-Cost CAN Testbed for Automotive Cybersecurity Education and Forensic Analysis**

Alternative title:

**A Low-Cost Automotive Cybersecurity and Forensic Testbed for Legacy ECUs in Emerging Markets**

## Central thesis

Academic, forensic, and training environments often lack affordable access to modern vehicles, documented ECUs, commercial HIL platforms, and realistic CAN datasets. A software-defined CAN testbed can support safe, reproducible automotive cybersecurity education and preliminary forensic analysis through controlled attack simulation, structured logging, and evidence-preserving metadata.

## Research questions

RQ1. Can a fully software-defined CAN testbed reproduce basic automotive cybersecurity scenarios in a safe and low-cost way?

RQ2. Which digital evidence artifacts can be collected and preserved during virtual CAN attack experiments?

RQ3. How can spoofing and flooding scenarios be represented and analyzed using structured CAN logs?

RQ4. What are the limitations of software-only CAN simulation compared to hardware-in-the-loop or real vehicle experiments?

## Expected contributions

1. A reproducible software-defined CAN testbed built with open tools.
2. Controlled attack scenarios: baseline, spoofing/fabrication, flooding, and recovery.
3. A forensic logging workflow with manifests and SHA-256 hashes.
4. A small dataset suitable for education, forensic triage, and reproducibility.
5. A discussion of limitations and a path toward hardware-in-the-loop extension.

## Six-page IEEE structure

### 1. Introduction

- Vehicles as distributed cyber-physical systems.
- CAN remains widely used and lacks native authentication/confidentiality.
- Access to real vehicles and ECUs is costly and risky.
- Reproducible education and forensic readiness require safe testbeds.
- Contributions.

### 2. Background and Related Work

- CAN security and attack surfaces.
- Automotive cybersecurity testbeds.
- CAN IDS datasets.
- Automotive digital forensics.
- ISO/SAE 21434 and UNECE R155 as context.

### 3. Software-Defined Testbed Design

- Virtual CAN architecture.
- Simulated ECUs.
- Attack modules.
- Logger and forensic manifest.
- Observer demo.

### 4. Experimental Methodology

- Baseline traffic.
- Spoofing/fabrication.
- Controlled flooding.
- Recovery.
- Data collection and hashing.

### 5. Results and Discussion

- Frame counts per phase.
- Decoded speed before/during/after spoofing.
- Arbitration ID diversity during flooding.
- Evidence artifacts and hash validation.
- Educational and forensic value.
- Limitations of software-only simulation.

### 6. Conclusion and Future Work

- Summary of contribution.
- Hardware-in-the-loop extension with USB-CAN and instrument cluster.
- Larger datasets and additional triage models.

## Draft abstract

Modern vehicles rely on distributed electronic control units interconnected through in-vehicle networks such as CAN, whose legacy design lacks native authentication and confidentiality. Although automotive cybersecurity research has proposed advanced testbeds, datasets, and intrusion detection mechanisms, access to realistic experimentation remains limited for education and forensic analysis in resource-constrained environments. This paper presents a software-defined, low-cost CAN testbed for automotive cybersecurity education and preliminary forensic analysis. The platform supports virtual CAN traffic generation, controlled spoofing and flooding scenarios, structured logging, evidence manifests, and SHA-256 hash preservation. We describe the architecture, experimental workflow, and attack dataset produced by the testbed, and discuss its applicability and limitations. The proposed approach lowers the barrier for reproducible automotive cybersecurity training and provides a safe bridge toward future hardware-in-the-loop experiments with legacy ECUs.
