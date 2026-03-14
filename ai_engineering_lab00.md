---
title: "Sovereign AI Lab: Post-Mortem & Closure Report"
date: 2026-03-14
author: AI Systems Engineering Lead
status: Closed / Pivoting to V2 Architecture
tags: [infrastructure, wsl, cuda, flash-attention, troubleshooting, bottleneck-analysis]
---

# Executive Summary
This report documents the architectural attempts, environmental debugging, and ultimate hardware constraints discovered during the Phase 1 build of a local "Sovereign AI Node." The primary objective was to deploy a mission-critical AI environment—capable of legacy code translation (RPG/C# to Neo4j) via OpenViking, evaluated deterministically by Promptfoo, and optimized by Flash Attention 2.

Ultimately, the lab exposed a critical physical bottleneck between the compute engine (RTX 4070) and the host processor (Intel Core i3-6006U). This document serves as the formal closure of the "Heavy Stack" iteration and provides the blueprint for the upcoming "Lean Stack" (V2) architecture.

---

## Page 1: Lab Objectives & Initial Architecture

### 1.1 The "Sovereign Node" Philosophy
The goal was to build an enterprise-grade AI infrastructure locally, bypassing cloud APIs to ensure absolute data privacy (zero PII leakage) and zero recurring inference costs. The stack was designed to separate the engineer from the "wrapper" developers by implementing rigorous evaluation and hardware-level optimization.

### 1.2 Target Software Stack
* **Host OS:** Windows 11 Pro with WSL2 (Ubuntu 22.04)
* **Orchestration & Context:** OpenViking, OpenClaw
* **Evaluation & Safety:** Promptfoo (via Node.js v22), Guardrails AI
* **Compute Engine:** PyTorch (CUDA 12.x) accelerated by Flash Attention 2

### 1.3 The Hardware Profile (The Discovery)
* **GPU (The T-Rex):** NVIDIA RTX 4070 (12GB VRAM) - Capable of massive parallel processing.
* **CPU (The Puppy):** Intel Core i3-6006U (Skylake, 2.0GHz, 2 Cores) - A low-voltage 2016 architecture.
* **System RAM:** 12GB Host RAM, rigorously managed via `.wslconfig` (8GB limit, 16GB Swap).

---

## Page 2: Phase 1 - The Build & The Compilation Bottleneck

### 2.1 The "Eons" of Compilation
The initial attempt to optimize the RTX 4070 involved compiling `flash-attn` from source code. This is a highly intensive C++ template metaprogramming task.
* **The Issue:** The build stalled at job `2/73` using the Ninja build system.
* **Resource Monitoring:** RAM usage stabilized at exactly 7.7GB, successfully avoiding "Swap Death" (where Windows pages memory to the SSD, crashing the socket).
* **The Root Cause:** The dual-core i3 processor was completely overwhelmed by the C++ template expansion required to generate thousands of mathematical kernels for the Ada Lovelace GPU architecture.

### 2.2 Pivot 1: Bypassing the Nightmare (Pre-Built Wheels)
To bypass the CPU compilation bottleneck, the lab pivoted from a source build to utilizing pre-compiled Python wheels (`.whl`).
* **Action:** Aborted the 73-job compilation.
* **Implementation:** Downloaded official `Dao-AILab` releases directly, reducing a multi-hour compilation to a 5-second installation.
* **Result:** Successfully bypassed the CPU limitation for the installation phase, but immediately encountered deep-system library conflicts.

---

## Page 3: Phase 2 - The ABI Wars (C++ Symbol Mismatches)

### 3.1 The First Collision (`cxx11abiTRUE`)
Upon installing the pre-built wheel for PyTorch 2.6.0, the system threw a fatal import error:
`undefined symbol: _ZN3c104cuda29c10_cuda_check_implementation...`
* **Diagnosis:** Application Binary Interface (ABI) mismatch. The installed Flash Attention binary was looking for modern C++ standards, but the Python environment was not aligned.
* **Action:** Executed a "Clean Sweep," wiping the `.venv`, clearing pip caches, and removing zombie directories (e.g., `-nvidia-cublas-cu12`).

### 3.2 The Second Collision (The `ErrorC2` Symbol)
After locking versions, a new error emerged:
`undefined symbol: _ZN3c105ErrorC2...`
* **Diagnosis:** This confirmed a fundamental disconnect in how the underlying Linux environment and PyTorch were handling C++ strings.
* **The Probe:** Ran `torch._C._GLIBCXX_USE_CXX11_ABI` to interrogate the system's actual C++ dialect.
* **The Result:** The system returned `False`. The environment was strictly bound to pre-2015 C++ string handling.

### 3.3 Pivot 2: The "Golden Pair" Version Lock
To achieve stability, the stack was downgraded and locked to the exact ABI standard of the host machine:
* **PyTorch:** Rolled back to `v2.4.0` (cu124).
* **Flash Attention:** Matched to `v2.7.4.post1` explicitly built with the `cxx11abiFALSE` flag.
* **Result:** Software alignment was achieved, but the execution still failed, leading to the final hardware audit.

---

## Page 4: Phase 3 - The Hardware Reality Check

### 4.1 Uncovering the Physical Limit
The final investigation required a hard look at the `sysinfo` data. The host machine was identified as an HP Laptop 15-bs0xx running an Intel Core i3-6006U.

### 4.2 The Physics of the Bottleneck (Puppy vs. T-Rex)
The errors and timeouts were not merely software bugs; they were symptoms of physical silicon limitations.
1.  **Instruction Set Deficits:** The i3-6006U lacks modern AVX-512 (Advanced Vector Extensions) instructions. Modern AI libraries expect these high-bandwidth instructions to feed data to the GPU.
2.  **PCIe / Data Starvation:** Even with a powerful RTX 4070 bridged to the system, the dual-core CPU could not process the execution graphs fast enough to keep the GPU fed. The GPU was starving while the CPU was perpetually at 100% load.
3.  **The Verdict:** Attempting to run a heavy, enterprise-grade PyTorch/CUDA stack on this specific CPU is architecturally unviable. The host cannot sustain the overhead of the Python orchestration layer alongside the C++ bindings.

---

## Page 5: Strategic Conclusion & The "Lean Lab" Blueprint

### 5.1 Lab Closure Status
The current iteration of the Sovereign AI Lab is officially **closed**. The attempts to force high-end PyTorch libraries onto a legacy mobile CPU provided immense educational value in debugging, ABI compilation, and environment isolation. This "Proof of Work" is highly valuable for an AI Systems Engineering portfolio, demonstrating the ability to diagnose issues down to the compiler level.

### 5.2 The V2 Blueprint (The Simpler Lab)
To successfully utilize the RTX 4070 without melting the i3 host, the architecture must pivot from a "Heavy Stack" to a "Lean Stack." 

**Upcoming V2 Directives:**
1.  **Abandon PyTorch/Flash-Attention Locally:** These libraries carry too much C++ overhead for the host CPU.
2.  **Adopt Llama.cpp (GGUF):** Transition to pure C/C++ inference. `llama-cpp-python` can offload 100% of the transformer layers directly to the RTX 4070's VRAM, completely bypassing the i3's processing bottleneck.
3.  **Headless Orchestration:** Cease running UI-heavy tools or web views on the laptop. The HP laptop will transition into a "Thin Client," focusing solely on sending text streams to the GPU via the CLI.
4.  **Decoupled Evaluation:** Promptfoo will be configured to run sequentially (`--max-concurrency 1`) to ensure the Node.js overhead does not trigger an Out-Of-Memory kernel panic on the 12GB host.

**Final Note:** The constraints of the hardware have dictated the architecture. The next lab will prioritize mechanical sympathy—building a system that respects the physical limits of the silicon while still achieving the mission-critical output.
