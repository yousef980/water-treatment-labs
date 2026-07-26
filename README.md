# Water Treatment Laboratory Experiments 

Welcome! This repository serves as a comprehensive digital portfolio of my laboratory work, experiments, and data analysis conducted during my Master's degree in **Environmental Engineering**. 

Leveraging my foundational background in **Chemistry**, these labs focus on practical, data-driven approaches to water quality assessment, chemical dosing, and purification processes.

---

## Repository Structure & Modules

The repository is organized chronologically by experiment type, covering chemical, physical, and microbiological water treatment principles:

* **`01-jar-test`** – Coagulation and flocculation optimization for turbidity removal.
* **`02-breakpoint-chlorination`** – Determining optimum chlorine demand for disinfection.
* **`03-suspended-solids`** – Gravimetric analysis of Total Suspended Solids (TSS) and TDS.
* **`04-iron-manganese-removal`** – Oxidation and filtration methods for groundwater treatment.
* **`05-nitrate-adsorption`** – Evaluating adsorption kinetics for nutrient removal.
* **`06-lime-soda-softening`** – Chemical precipitation for hardness reduction.
* **`07-microbiology-gram-staining`** – Identification and differentiation of bacterial cell walls.
* **`08-microbiology-surface-hygiene`** – Sanitation monitoring and surface swab assessments.
* **`09-microbiology-water-quality`** – Coliform testing and biological contamination tracking.

---

## The AquaLabs Software Journey (v3.0)

Alongside the laboratory modules, this repository hosts **AquaLabs**, a custom-built desktop application designed to act as a computational chemical engineering simulator for water treatment.

### Trial & Error: The Path to v3.0
The development of AquaLabs was an iterative journey to build a perfectly portable, standalone, and visually stunning executable that requires **zero installation** on the host machine:
1. **Initial Prototyping (`v1 / v2`)**: Started with basic data processing scripts and a rudimentary Tkinter GUI.
2. **The Environment Constraint**: The goal was true portability on an external E: drive without touching the C: drive. I initially tried using a minimal embeddable Python zip, but quickly realized it entirely strips out `tkinter` and `tcl/tk` support by default.
3. **The Breakthrough**: Solved the UI rendering failure by downloading and unpacking a full, self-contained Python MSI installation directly onto the E: drive (`portable_python_full`).
4. **Aesthetic Overhaul (`v3`)**: Upgraded from standard Tkinter to `customtkinter`, designing a premium, highly-rounded dark mode UI inspired by modern luxury dashboards (using a bespoke Midnight Ocean palette).
5. **Domain Enhancements**: Completely refactored the Jar Test module to separate Coagulation (Rapid Mix, seconds) from Flocculation (Slow Mix, minutes) and expanded the chemical catalog to 6 industry coagulants with their respective optimal pH tracking.
6. **Final Compilation**: Used the isolated portable environment to compile `aqualabs_v3.py` into a single, massive ~50MB `aqualabs_v3.exe` using PyInstaller, ensuring Matplotlib rendering and Pandas calculations work natively out of the box.

---

## Core Competencies Demonstrated

* **Analytical Techniques:** Titrations, spectrophotometry, gravimetric analysis, and microscopic tracking.
* **Data Processing:** Automating laboratory calculations and plotting chemical curves using **Python (Pandas & Matplotlib)**.
* **HSE Compliance:** Strict adherence to laboratory safety, chemical handling protocols, and quality control.

---

##  Future Enhancements
* Incorporating open-source satellite data pipelines (**Sentinel-5P**) to cross-reference regional environmental air/water quality metrics.
* Expanding interactive Python notebooks (`.ipynb`) for automated kinetic modeling.

---

## Connect With Me
If you are working on similar water treatment research, environmental engineering projects, or chemical automation scripts, let's connect!

* **Email:** Yousefyousef5355@gmail.com
