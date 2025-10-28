# MSP430 Development Environment and Hardware Integration

Comprehensive assembly language development environment for the MSP430 microcontroller, featuring a custom assembler, visual simulator, and direct hardware integration.

## 📑 Table of Contents

* [About the Project](#-about-the-project)

* [Features](#-features)

* [Installation](#installation)

* [Usage](#-usage)

* [File Structure](#-file-structure)

* [Contributors](#-contributors)

## 🚀 About the Project

This project provides a sophisticated toolset designed to facilitate assembly language programming on the MSP430 microcontroller. Developers can write, assemble, simulate, and directly upload assembly code to physical MSP430 hardware.

A user-friendly Graphical User Interface (GUI) simplifies debugging and provides visual insights into microcontroller behavior.

## ✨ Features

- **✅ Custom Assembler:** Converts MSP430 assembly code into machine-readable executable code.
- **✅ Visual Simulator:** Interactive simulator built with Tkinter, visualizing LED states, registers, and memory operations.
- **✅ Hardware Bridge:** Python-based bridge `(msp430_bridge.py)` enabling communication between simulator and physical MSP430 devices.
- **✅ Hardware Integration Module:** Handles serial communication with MSP430 boards via `msp430_hardware.py`.
- **✅ User-Friendly GUI:** GUI (`MSP430v1.9.py`, `hardware_integration_test.py`) for code input, compilation, simulation, and hardware testing.
- **✅ Advanced Directive Support:** Supports `.bss`, `.data`, `.text`, `.wordv`,`.byte` for efficient memory and section management.
- **✅ Conditional Assembly & Macros:** Allows flexible, modular code with conditional assembly and macro definitions.

## Installation

**Prerequisites**

* **Python 3.x**

* **pyserial library for hardware integration**

### Setup Steps
  ```python
   git clone [https://github.com/YusufTahaKasdemir/MSP430-Assembler.git]
   cd MSP430-Assembler
   pip install pyserial
```

⚠️ Ensure you have the necessary drivers installed for your MSP430 board (e.g., Texas Instruments USB UART drivers).

## 💡 Usage

To launch the development environment, run:
```python
python MSP430v1.9.py
```

### Capabilities via GUI

* **Assembly Code Input:** Write MSP430 assembly code in the left panel.

* **Assemble & Convert:** Compile to machine code (Hex and Binary outputs displayed).

* **Simulation:** Run code on the visual simulator, observe LEDs, registers, and memory in real-time.

* **Hardware Integration:** Access from the "Hardware" menu to scan devices, upload code, and establish serial communication.

* **Save/Load:** Save or open assembly code files for future editing.

## 📁 File Structure
```
MSP430-Assembler/
├── MSP430v1.9.py                 # Main GUI application
├── msp430_simulator.py           # Visual MSP430 simulator
├── msp430_bridge.py              # Bridge for simulator-hardware communication
├── msp430_hardware.py            # Serial communication and hardware programming
├── msp430_integration.py         # Hardware interface integration logic
├── hardware_integration_test.py  # GUI for hardware communication testing
├── mS-P_430_directives.txt       # Supported assembler directives
├── patch_instructions.txt        # Developer notes and patching guidelines
└── README.md                     # Project documentation (this file)
```

## 👥 Contributors

[Yusuf Taha Kaşdemir]

[Murat Semih Esmeray]

[Umut Kuzey Görgeç]

[Taha Melih Öztaş]

[Faruk Musa]
