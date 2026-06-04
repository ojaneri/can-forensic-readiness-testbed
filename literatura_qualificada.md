# Qualified Literature — Software-Defined and Low-Cost CAN Testbeds

> Status: initial annotated review. PDFs, pages, DOI, and BibTeX metadata still need final validation before submission.

## 1. Core references: automotive testbeds and CAN security

### 1.1 VitroBench: Manipulating in-vehicle networks and COTS ECUs on your table

- **Venue:** *Vehicular Communications*, 2023, vol. 43.
- **URL:** https://www.sciencedirect.com/science/article/pii/S2214209623000797
- **Project page:** https://asset-group.github.io/testbeds/vitrobench/
- **Relevance:** Very high.
- **Use in this paper:** Main baseline for a test platform using real COTS ECUs. Our differentiation is lower cost, software-defined reproducibility, education, and evidence-preserving forensic workflow.

### 1.2 A CAN Bus Security Testbed Framework for Automotive Cyber-Physical Systems

- **DOI:** 10.1155/2022/7176194
- **URL:** https://onlinelibrary.wiley.com/doi/10.1155/2022/7176194
- **Year:** 2022.
- **Relevance:** Very high.
- **Use in this paper:** Supports the argument that controlled CAN testbeds are safer and more reproducible than experiments on operational vehicles.

### 1.3 CANBench — Development and Evaluation of CANBench

- **Source:** BYU ScholarsArchive.
- **URL:** https://scholarsarchive.byu.edu/etd/10732/
- **Relevance:** High.
- **Use in this paper:** Reference for inexpensive, off-the-shelf CAN testbed design and reproducibility criteria.

### 1.4 FAV-NSS — HIL Framework for Automotive Network Security Strategies

- **URL:** https://arxiv.org/html/2505.15393
- **Year:** 2025.
- **Relevance:** High, but more advanced than our scope.
- **Use in this paper:** Represents the HIL/FPGA frontier. Our work is positioned as a lower-cost software-defined entry point.

### 1.5 Adaptive Fuzz Testing for Automotive ECUs: A Modular Testbed

- **Source:** ACM, 2024.
- **URL:** https://dl.acm.org/doi/10.1145/3672202.3673734
- **Relevance:** Medium/high.
- **Use in this paper:** Supports controlled fuzzing and low-cost ECU security experimentation.

### 1.6 CANsec: A Practical In-Vehicle CAN Security Evaluation Tool

- **Source:** *Sensors*, 2020.
- **URL:** https://www.mdpi.com/1424-8220/20/17/4900
- **Relevance:** High.
- **Use in this paper:** Useful for comparing attack/evaluation tooling for CAN security.

## 2. Datasets and IDS evaluation

### 2.1 ROAD Dataset — A comprehensive guide to CAN IDS data and introduction of the ROAD dataset

- **DOI:** 10.1371/journal.pone.0296879
- **URL:** https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296879
- **Dataset:** https://zenodo.org/records/10462796 and https://0xsam.com/road/
- **Year:** 2024.
- **Relevance:** Very high.
- **Use in this paper:** Provides dataset quality criteria and attack taxonomy: fabrication, suspension, masquerade.

### 2.2 can-train-and-test: A Curated CAN Dataset for Automotive Intrusion Detection

- **DOI:** 10.1016/j.cose.2024.103777
- **arXiv:** https://arxiv.org/abs/2308.04972
- **Relevance:** High.
- **Use in this paper:** Reference for replayable CAN logs and labeled/unlabeled files.

### 2.3 can-sleuth: Investigating and Evaluating Automotive Intrusion Detection Datasets

- **Source:** ACM, 2024.
- **URL:** https://dl.acm.org/doi/10.1145/3655693.3655696
- **Relevance:** High.
- **Use in this paper:** Supports the discussion on dataset quality and reproducibility.

### 2.4 CAN-MIRGU

- **Source:** VehicleSec/NDSS 2024.
- **PDF:** https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf
- **Relevance:** Medium/high.
- **Use in this paper:** Real-world moving-vehicle dataset; useful for contrasting software-defined simulation with real vehicle fidelity.

## 3. CAN security foundations

### 3.1 Evaluation of CAN Bus Security Challenges

- **Source:** *Sensors*, 2020; available in PMC.
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7219335/
- **Relevance:** Very high.
- **Use in this paper:** Background on CAN vulnerabilities, lack of native authentication/confidentiality, attack surfaces, and mitigations.

### 3.2 In-Vehicle Communication Cyber Security: Challenges and Solutions

- **DOI:** 10.3390/s22176679
- **Year:** 2022.
- **Relevance:** High.

### 3.3 Survey and Classification of Automotive Security Attacks

- **DOI:** 10.3390/info10040148
- **Year:** 2019.
- **Relevance:** High.

### 3.4 Cyber Threats Facing Autonomous and Connected Vehicles: Future Challenges

- **DOI:** 10.1109/TITS.2017.2665968
- **Year:** 2017.
- **Relevance:** High.

## 4. Classic automotive attack papers

### 4.1 Experimental Security Analysis of a Modern Automobile

- **Known authors:** Koscher et al.
- **Year:** 2010.
- **Relevance:** Classic reference.

### 4.2 Comprehensive Experimental Analyses of Automotive Attack Surfaces

- **Known authors:** Checkoway et al.
- **Year:** 2011.
- **Relevance:** Classic reference.

### 4.3 Remote Exploitation of an Unaltered Passenger Vehicle

- **Known authors:** Miller and Valasek.
- **Year:** 2015.
- **Relevance:** Industry-impact reference.

## 5. Automotive forensics and CAN reverse engineering

### 5.1 On the Feasibility of Carrying Out Live Real-Time Forensics for Modern Intelligent Vehicles

- **DOI:** 10.1007/978-3-642-23602-0_20
- **Year:** 2011.
- **Relevance:** High for forensic framing.

### 5.2 READ: Reverse Engineering of Automotive Data Frames

- **URL:** https://ieeexplore.ieee.org/document/8466914
- **Relevance:** High.
- **Use in this paper:** Supports discussion of proprietary CAN mappings and forensic limitations without DBC/OEM documentation.

## 6. Standards and risk context

### 6.1 ISO/SAE 21434 — Road vehicles — Cybersecurity engineering

- **Relevance:** Required context for cybersecurity engineering lifecycle and TARA.

### 6.2 UNECE R155 — Cyber Security Management System

- **Relevance:** International regulatory context.

### 6.3 UNECE R156 — Software Update Management System

- **Relevance:** Secondary context if OTA/SDV is discussed.

## 7. Positioning our contribution

Existing literature provides:

- advanced COTS ECU testbeds;
- HIL/FPGA validation frameworks;
- CAN IDS datasets;
- CAN security surveys;
- attack tools and evaluation frameworks.

Our target gap:

> A reproducible, low-cost, software-defined CAN testbed with controlled attacks, observer demo, structured dataset, and evidence-preserving forensic workflow.
