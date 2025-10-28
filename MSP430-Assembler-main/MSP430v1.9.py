import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import messagebox, filedialog, Toplevel, ttk
import re
import os
import time
import datetime
from tkinter.font import Font
import traceback

# Donanım entegrasyonu için import
import msp430_integration
import msp430_simulator

# Donanım kullanılabilirliğini kontrol için global değişken
HARDWARE_AVAILABLE = False

# Global variables
root = None
input_text = None
hex_text = None
binary_text = None
convert_button = None
clear_button = None
load_button = None
save_button = None
status_var = None
status_bar = None
title_label = None
input_label = None
info_panel = None
info_label = None
hex_label = None
binary_label = None
section_output_data = {
    ".TEXT": [],
    ".DATA": [],
    ".BSS": []
}

# Renk tanımlamaları - Koyu tema (Dark theme colors)
BG_COLOR = "#1e1e1e"          # Background color (dark black)
TEXT_COLOR = "#ffffff"        # Main text color (white)
BUTTON_COLOR = "#ff5722"      # Orange button color
BUTTON_TEXT = "#ffffff"       # Button text color (white)
TEXTBOX_BG = "#121212"        # Textbox background (pure black)
HEADER_COLOR = "#ffffff"      # Header color (white)
KEYWORD_COLOR = "#007ACC"     # Navy blue (for commands)
REGISTER_COLOR = "#FF8C00"    # Orange (for registers)
NUMBER_COLOR = "#56DB40"      # Bright green (for numbers)
COMMENT_COLOR = "#898989"     # Gray (for comments)
ADDRESSING_COLOR = "#DB70DB"  # Candy pink (for addressing modes)
BYTE_WORD_COLOR = "#FFC300"   # Bright yellow (for .W/.B markers)
LABEL_COLOR = "#00B7C3"       # Turquoise (for labels)
BRANCH_LABEL_COLOR = "#E74C3C"# Red (for branch target labels)
ERROR_COLOR = "#FF1493"       # Pink red (for invalid commands)
ERROR_BG = "#3a1212"          # Error background color (dark pink)
SUGGESTION_COLOR = "#4CAF50"  # Green (for suggestions)
INFO_BG = "#3E3E3E"           # Info panel background (dark gray)
HOVER_COLOR = "#ff8a65"       # Hover effect color

# Modification record system
modification_records = []
# Initial value for program relocation address
program_relocation_address = 0x0000

memory_values = {}
current_format = "HEX"
register_values = {}
status_flags_label = None

# Current MSP430 opcode table - All core commands
opcode_table = {
    # Double Operand Format (Format I)
    "MOV": "0100", "ADD": "0101", "ADDC": "0110", "SUBC": "0111", "SUB": "1000",
    "CMP": "1001", "DADD": "1010", "BIT": "1011", "BIC": "1100", "BIS": "1101",
    "XOR": "1110", "AND": "1111",
    
    # Byte versions (.B)
    "MOV.B": "0100", "ADD.B": "0101", "ADDC.B": "0110", "SUBC.B": "0111", "SUB.B": "1000",
    "CMP.B": "1001", "DADD.B": "1010", "BIT.B": "1011", "BIC.B": "1100", "BIS.B": "1101",
    "XOR.B": "1110", "AND.B": "1111",
    
    # Word versions (.W)
    "MOV.W": "0100", "ADD.W": "0101", "ADDC.W": "0110", "SUBC.W": "0111", "SUB.W": "1000",
    "CMP.W": "1001", "DADD.W": "1010", "BIT.W": "1011", "BIC.W": "1100", "BIS.W": "1101",
    "XOR.W": "1110", "AND.W": "1111",
    
    # Branch Commands (Format II)
    "JNE": "001000", "JNZ": "001000",  # JNZ = JNE
    "JEQ": "001001", "JZ": "001001",   # JZ = JEQ
    "JNC": "001010", "JLO": "001010",  # JLO = JNC
    "JC": "001011", "JHS": "001011",   # JHS = JC
    "JN": "001100",
    "JGE": "001101",
    "JL": "001110",
    "JMP": "001111",
    
    # Single Operand Format (Format III)
    "RRC": "000", "SWPB": "001", "RRA": "010", "SXT": "011",
    "PUSH": "100", "CALL": "101", "RETI": "110",
    
    # Byte versions (.B)
    "RRC.B": "000", "RRA.B": "010", "PUSH.B": "100",
    
    # Word versions (.W)
    "RRC.W": "000", "SWPB.W": "001", "RRA.W": "010", "SXT.W": "011",
    "PUSH.W": "100", "CALL.W": "101"
}
# Initialize sets for directives and keywords
directives = {
        # Section Control
        "TEXT", "DATA", "BSS", "INTVEC", "SECT", "USECT",
        # Group Control
        "GROUP", "GMEMBER", "ENDGROUP",
        # Unused Section Elimination
        "RETAIN", "RETAINREFS",
        # Value Initialization
        "BITS", "BYTE", "CHAR", "CSTRING", "DOUBLE", "FIELD",
        "FLOAT", "HALF", "INT", "LONG", "SHORT", "STRING",
        "UBYTE", "UCHAR", "UHALF", "UINT", "ULONG", "USHORT",
        "UWORD", "WORD",
        # Alignment and Space
        "ALIGN", "BES", "SPACE",
        # Output Formatting
        "DRLIST", "DRNOLIST", "FCLIST", "FCNOLIST", "LENGTH",
        "LIST", "MLIST", "MNOLIST", "NOLIST", "OPTION", "PAGE",
        "SSLIST", "SSNOLIST", "TAB", "TITLE", "WIDTH",
        # File Reference
        "COPY", "INCLUDE", "MLIB",
        # Symbol Visibility
        "COMMON", "DEF", "GLOBAL", "REF", "WEAK",
        # Conditional Assembly
        "IF", "ELSE", "ELSEIF", "ENDIF",
        # Structures
        "STRUCT", "ENDSTRUCT", "TAG",
        # Enumerated Types
        "ENUM", "EMEMBER", "ENDENUM",
        # Assembly-Time Symbols
        "ASG", "DEFINE", "ELFSYM", "EVAL", "LABEL",
        "NEWBLOCK", "SET", "UNASG", "UNDEFINE",
        # Macro Support
        "MACRO", "ENDM", "MEXIT", "VAR",
        # Diagnostics
        "EMSG", "MMSG", "WMSG",
        # Debug Support
        "LINE", "FUNC", "ENDFUNC", "ASMFUNC", "ENDASMFUNC", "LOC",
        # Absolute Lister
        "ENDLN", "LN", "MN", "NREF", "XLIST",
        # Miscellaneous
        "VERSION", "END", "EXIT", "TITLE", "SBTTL", "SUBTITLE",
        # Legacy directives
        "DW", "DB", "INT"
    }

# Non-dot-prefixed directives (only EQU and ORG)
non_dot_directives = {"EQU", "ORG", "INT"}

# Emulated instruction map - All emulated commands
emulated_map = {
    # R/W and B/W modes
    "ADC": "ADDC #0, dst",
    "ADC.W": "ADDC.W #0, dst", "ADC.B": "ADDC.B #0, dst",
    
    "BR": "MOV dst, PC",
    
    "CLR": "MOV #0, dst",
    "CLR.W": "MOV.W #0, dst", "CLR.B": "MOV.B #0, dst",
    
    "CLRC": "BIC #1, SR", "CLRN": "BIC #4, SR", "CLRZ": "BIC #2, SR", "CLRV": "BIC #0100, SR",
    
    "DADC": "DADD #0, dst",
    "DADC.W": "DADD.W #0, dst", "DADC.B": "DADD.B #0, dst",
    
    "DEC": "SUB #1, dst",
    "DEC.W": "SUB.W #1, dst", "DEC.B": "SUB.B #1, dst",
    
    "DECD": "SUB #2, dst",
    "DECD.W": "SUB.W #2, dst", "DECD.B": "SUB.B #2, dst",
    
    "DINT": "BIC #8, SR", "EINT": "BIS #8, SR",
    
    "INC": "ADD #1, dst",
    "INC.W": "ADD.W #1, dst", "INC.B": "ADD.B #1, dst",
    
    "INCD": "ADD #2, dst",
    "INCD.W": "ADD.W #2, dst", "INCD.B": "ADD.B #2, dst",
    
    "INV": "XOR #-1, dst",
    "INV.W": "XOR.W #-1, dst", "INV.B": "XOR.B #-1, dst",
    
    "NOP": "MOV #0, R3",
    
    "POP": "MOV @SP+, dst",
    
    "RET": "MOV @SP+, PC",
    
    "RLA": "ADD dst, dst",
    "RLA.W": "ADD.W dst, dst", "RLA.B": "ADD.B dst, dst",
    
    "RLC": "ADDC dst, dst",
    "RLC.W": "ADDC.W dst, dst", "RLC.B": "ADDC.B dst, dst",
    
    "SBC": "SUBC #0, dst",
    "SBC.W": "SUBC.W #0, dst", "SBC.B": "SUBC.B #0, dst",
    
    "SETC": "BIS #1, SR", "SETN": "BIS #4, SR", "SETZ": "BIS #2, SR", "SETV": "BIS #0100, SR",
    
    "TST": "CMP #0, dst",
    "TST.W": "CMP.W #0, dst", "TST.B": "CMP.B #0, dst"
}

# Some directly defined commands (as alternative to emulation)
hardcoded_commands = {
    "RET": "4130"  # MOV @SP+, PC - Direct hex value
}

register_table = {f"R{i}": i for i in range(16)}
register_table["PC"] = 0  # PC = R0
register_table["SP"] = 1  # SP = R1
register_table["SR"] = 2  # SR = R2
register_table["CG"] = 3  # CG = R3
labels = {}
start_address = 0x0000

##########################################
# Symbol Table (symtab)
##########################################

# This structure contains all defined instructions,
# registers, labels, and constants for MSP430.

symtab = {
    "registers": register_table.copy(),
    "opcodes": opcode_table.copy(),
    "emulated": emulated_map.copy(),
    "labels": {},   # Will be filled after first pass
    "equ": {}       # EQU constants, will be filled after first pass
}

def show_symtab_window():
    """Shows the MSP430 symbol table"""
    window = Toplevel()
    window.title("MSP430 Symbol Table")
    window.geometry("800x600")
    window.configure(bg=BG_COLOR)

    # Title
    title = tk.Label(window, text="MSP430 Symbol Table", font=("Impact", 16), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=10)

    # Main frame
    main_frame = tk.Frame(window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    # Left panel (categories)
    left_frame = tk.Frame(main_frame, bg=INFO_BG, width=200)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    left_frame.pack_propagate(False)

    # Category title
    category_title = tk.Label(left_frame, text="Symbol Categories", 
                            font=("Arial", 11, "bold"), bg=INFO_BG, fg=TEXT_COLOR)
    category_title.pack(pady=10, padx=5, anchor=tk.W)

    # Categories
    categories = [
        "Labels",
        "Constants (EQU)",
        
        "Literal Table (LITTAB)",
        "Block Table (BLOCKTAB)",
        "Show All"
    ]

    # Category buttons
    buttons_frame = tk.Frame(left_frame, bg=INFO_BG)
    buttons_frame.pack(fill=tk.X, padx=5)

    text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                          font=("Courier New", 11),
                                          bg=TEXTBOX_BG, fg=TEXT_COLOR)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_category(category):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)

        if category == "Labels" or category == "Show All":
            text_widget.insert(tk.END, "Labels:\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            for label, addr in symtab["labels"].items():
                text_widget.insert(tk.END, f"{label:<20} : 0x{addr:04X}\n", "symbol")

        if category == "Constants (EQU)" or category == "Show All":
            text_widget.insert(tk.END, "\nConstants (EQU):\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            for const, value in symtab["equ"].items():
                text_widget.insert(tk.END, f"{const:<20} : 0x{value:04X}\n", "symbol")

        if category == "Registers" or category == "Show All":
            text_widget.insert(tk.END, "\nRegisters:\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            for reg, desc in symtab["registers"].items():
                text_widget.insert(tk.END, f"{reg:<20} : {desc}\n", "symbol")

        if category == "Instructions" or category == "Show All":
            text_widget.insert(tk.END, "\nInstructions:\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            for opcode, info in symtab["opcodes"].items():
                text_widget.insert(tk.END, f"{opcode:<20} : {info}\n", "symbol")

        if category == "Emulated Instructions" or category == "Show All":
            text_widget.insert(tk.END, "\nEmulated Instructions:\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            for cmd, impl in symtab["emulated"].items():
                text_widget.insert(tk.END, f"{cmd:<20} : {impl}\n", "symbol")

        if category == "Literal Table (LITTAB)" or category == "Show All":
            text_widget.insert(tk.END, "\nLiteral Table (LITTAB):\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            
            # Pool information
            text_widget.insert(tk.END, "Pool Information:\n", "subheader")
            text_widget.insert(tk.END, f"Pool Address: {symtab['littab']['pool_address'] if symtab['littab']['pool_address'] is not None else 'Not set'}\n", "symbol")
            text_widget.insert(tk.END, f"Pool Size: {symtab['littab']['pool_size']} bytes\n\n", "symbol")
            
            # Literals
            text_widget.insert(tk.END, "Literals:\n", "subheader")
            for i, literal in enumerate(symtab['littab']['literals']):
                value_str = str(literal['value'])
                if literal['type'] == 'IMM':
                    if isinstance(literal['value'], int):
                        value_str = f"#{literal['value']:04X}h"
                    else:
                        value_str = f"#'{literal['value']}'"
                elif literal['type'] == 'STR':
                    value_str = f'"{literal["value"]}"'
                elif literal['type'] == 'CHAR':
                    value_str = f"'{literal['value']}'"
                
                text_widget.insert(tk.END, f"Literal {i+1}:\n", "symbol")
                text_widget.insert(tk.END, f"  Type    : {literal['type']}\n", "symbol")
                text_widget.insert(tk.END, f"  Value   : {value_str}\n", "symbol")
                text_widget.insert(tk.END, f"  Size    : {literal['size']} bytes\n", "symbol")
                if literal['address'] is not None:
                    text_widget.insert(tk.END, f"  Address : 0x{literal['address']:04X}\n", "symbol")
                text_widget.insert(tk.END, "\n", "symbol")

        if category == "Block Table (BLOCKTAB)" or category == "Show All":
            text_widget.insert(tk.END, "\nBlock Table (BLOCKTAB):\n", "header")
            text_widget.insert(tk.END, "-"*35 + "\n\n", "header")
            
            # Current block
            current_block = symtab["blocktab"]["current_block"]
            text_widget.insert(tk.END, "Current Block:\n", "subheader")
            if current_block:
                text_widget.insert(tk.END, f"  Name    : {current_block['name']}\n", "symbol")
                text_widget.insert(tk.END, f"  Type    : {current_block['type']}\n", "symbol")
                text_widget.insert(tk.END, f"  Address : 0x{current_block['start_address']:04X}\n", "symbol")
                text_widget.insert(tk.END, f"  Size    : {current_block['size']} bytes\n", "symbol")
            else:
                text_widget.insert(tk.END, "  No active block\n", "symbol")
            text_widget.insert(tk.END, "\n", "symbol")
            
            # All blocks
            text_widget.insert(tk.END, "All Blocks:\n", "subheader")
            for block in symtab["blocktab"]["blocks"]:
                text_widget.insert(tk.END, f"Block: {block['name']}\n", "symbol")
                text_widget.insert(tk.END, f"  Type    : {block['type']}\n", "symbol")
                text_widget.insert(tk.END, f"  Start   : 0x{block['start_address']:04X}\n", "symbol")
                text_widget.insert(tk.END, f"  Size    : {block['size']} bytes\n", "symbol")
                if block['end_address'] is not None:
                    text_widget.insert(tk.END, f"  End     : 0x{block['end_address']:04X}\n", "symbol")
                text_widget.insert(tk.END, "\n", "symbol")

        # Apply styles
        text_widget.tag_configure("header", foreground=HEADER_COLOR, font=("Courier New", 12, "bold"))
        text_widget.tag_configure("subheader", foreground=HEADER_COLOR, font=("Courier New", 11, "bold"))
        text_widget.tag_configure("symbol", foreground=TEXT_COLOR, font=("Courier New", 11))
        text_widget.config(state=tk.DISABLED)

    # Create category buttons
    for cat in categories:
        btn = tk.Button(buttons_frame, text=cat, bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                       font=("Arial", 10), width=20, anchor="w",
                       command=lambda c=cat: show_category(c))
        btn.pack(pady=2, padx=5, fill=tk.X)

    # Show first category
    show_category("Show All")

    # Refresh button
    refresh_button = tk.Button(window, text="Refresh", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                             font=("Arial", 10), command=lambda: show_category("Show All"))
    refresh_button.pack(pady=10)

def apply_emulated_instructions(parts):
    try:
        # Eğer komut emüle edilmiş bir komutsa, gerçek komutu döndür
        mnemonic = parts[0].upper()
        if mnemonic in emulated_map:
            # Orijinal komutu al
            replacement = emulated_map[mnemonic]
            # Virgülleri ve boşlukları temizle
            replacement = replacement.replace(",", " ").split()
            # Hedef operandı değiştir (varsa)
            if "dst" in replacement and len(parts) >= 2:
                dst_index = replacement.index("dst")
                replacement[dst_index] = parts[1]
            return replacement
        return parts
    except Exception as e:
        print(f"apply_emulated_instructions error: {str(e)}")
        return parts

def get_addressing_mode(operand):
    try:
        # Register direct (Rn) - 00
        if operand in register_table:
            return 0, register_table[operand], None
            
        # Immediate value: #constant - 11
        elif operand.startswith('#'):
            value_str = operand[1:]
            
            # Register number
            if value_str.startswith('R') and value_str[1:].isdigit():
                reg_num = int(value_str[1:])
                return 0, reg_num, None
                
            # Constant (EQU) value
            if value_str in labels:
                value = labels[value_str]
                print(f"Immediate constant: {value_str} -> {value:04X}")
                return 3, 0, f"{value & 0xFFFF:04X}"
                
            # Hex value check
            if value_str.endswith('h'):
                value_str = "0x" + value_str[:-1]
            
            # Parse the value
            try:
                # First try as hex
                if value_str.startswith("0x") or value_str.endswith("h"):
                    if value_str.endswith("h"):
                        value_str = "0x" + value_str[:-1]
                    value = int(value_str, 16)
                # Then try as decimal
                elif value_str.isdigit():
                    value = int(value_str, 10)
                else:
                    # Auto-detect base
                    value = int(value_str, 0)
                
                print(f"Immediate value: {value_str} -> {value}")
                return 3, 0, f"{value & 0xFFFF:04X}"
            except ValueError:
                print(f"Invalid number format: {value_str}")
                return -1, -1, "????"
            
        # Indexed mode: offset(Rn) - 01
        elif "(" in operand and ")" in operand:
            offset, reg = operand.split("(")
            reg = reg.rstrip(")")
            
            if offset == "":
                offset = "0"
                
            if offset.endswith('h'):
                offset = "0x" + offset[:-1]
                
            if reg not in register_table:
                print(f"Invalid register: {reg}")
                return -1, -1, "????"
                
            try:
                # Parse offset value
                if offset.startswith("0x") or offset.endswith("h"):
                    if offset.endswith("h"):
                        offset = "0x" + offset[:-1]
                    offset_value = int(offset, 16)
                elif offset.isdigit():
                    offset_value = int(offset, 10)
                else:
                    offset_value = int(offset, 0)
                    
                return 1, register_table.get(reg, 0), f"{offset_value & 0xFFFF:04X}"
            except ValueError:
                print(f"Invalid offset format: {offset}")
                return -1, -1, "????"
            
        # Indirect mode: @Rn - 10
        elif operand.startswith('@'):
            reg = operand[1:]
            
            if reg.endswith('+'):
                reg = reg[:-1]
                
            if reg not in register_table:
                print(f"Invalid register: {reg}")
                return -1, -1, "????"
                
            return 2, register_table.get(reg, 0), None
            
        # Indirect memory (not with @register, in the form of &symbol) - 01
        elif operand.startswith('&'):
            addr = operand[1:]
            reg = 2  # SR register
            
            if addr.endswith('h'):
                addr = "0x" + addr[:-1]
                
            try:
                if addr.isdigit() or addr.startswith('0x'):
                    addr_value = int(addr, 0)
                    return 1, reg, f"{addr_value & 0xFFFF:04X}"
                elif addr in labels:
                    return 1, reg, f"{labels[addr] & 0xFFFF:04X}"
                else:
                    print(f"Unknown address/label: {addr}")
                    return -1, -1, "????"
            except ValueError:
                print(f"Invalid address format: {addr}")
                return -1, -1, "????"
            
        # Label reference - Process as immediate (#constant) - 11
        elif operand in labels:
            value = labels[operand]
            return 3, 0, f"{value & 0xFFFF:04X}"
            
        # Absolute address (non PC-relative) - 01
        elif operand.startswith('$'):
            address_str = operand[1:]
            if address_str.endswith('h'):
                address_str = "0x" + address_str[:-1]
            address = int(address_str, 0)
            return 1, 2, f"{address:04X}"
                
        else:
            print(f"Unknown operand type: {operand}")
            return -1, -1, "????"
            
    except Exception as e:
        print(f"get_addressing_mode error: {str(e)} - operand: {operand}")
        return -1, -1, "????"

def get_bw_bit(mnemonic):
    return 1 if mnemonic.endswith(".B") else 0

def first_pass(assembly_code):
    """First pass to collect labels and calculate addresses"""
    global symtab, labels, start_address
    
    # Sembol tablosunu başlat
    symtab = {
        "equ": {},
        "littab": {},
        "blocktab": {}
    }
    
    # Initialize dictionaries
    labels = {}
    equ_dict = {}
    data_values = {}
    byte_values = {}
    string_values = {}
    space_values = {}
    
    # Initialize symbol table with all required sections
    symtab = {
        "labels": {},      # Labels
        "equ": {},         # EQU definitions
        "data": {},        # Data values
        "byte": {},        # Byte values
        "string": {},      # String values
        "space": {},       # Space values
        "sections": {},    # Section information
        "debug": {},       # Debug information
        "registers": register_table.copy(),  # Register information
        "opcodes": opcode_table.copy(),      # Opcode information
        "emulated": emulated_map.copy(),     # Emulated instructions
        "directives": directives.copy(),     # Directives
        
        # Literal Table (LITTAB)
        "littab": {
            "literals": [],           # List of literals
            "pool_address": None,     # Address of literal pool
            "pool_size": 0,          # Size of literal pool
            "types": {               # Supported literal types
                "IMM": "IMMEDIATE",  # Immediate values (#)
                "EQU": "EQU",        # EQU constants
                "WORD": "WORD",      # .word values
                "BYTE": "BYTE",      # .byte values
                "CHAR": "CHAR",      # .char values
                "STR": "STRING",     # .string values
                "INT": "INT"         # INT values
            }
        },
        
        # Block Table (BLOCKTAB)
        "blocktab": {
            "blocks": [],            # List of blocks
            "current_block": None,   # Current active block
            "block_stack": [],       # Stack for nested blocks
            "types": {               # Supported block types
                "TEXT": ".TEXT",     # Code section
                "DATA": ".DATA",     # Data section
                "BSS": ".BSS",       # Uninitialized data
                "INTVEC": ".INTVEC", # Interrupt vectors
                "SECT": ".SECT"      # Custom section
            }
        }
    }
    
    # Initialize address
    address = 0
    start_address = 0
    
    # Section tracking
    current_section = ".TEXT"  # Default section
    sections = {
        ".TEXT": {"address": 0, "size": 0},
        ".DATA": {"address": 0, "size": 0},
        ".BSS": {"address": 0, "size": 0},
        ".INTVEC": {"address": 0, "size": 0}
    }
    
    # Helper function for LITTAB
    def add_literal(value, type_str="IMM"):
        """Add a literal to the literal table"""
        literal = {
            "value": value,
            "type": type_str,
            "address": None,  # Will be filled in second pass
            "size": 2 if type_str in ["IMM", "EQU", "WORD"] else 1  # Word or byte size
        }
        symtab["littab"]["literals"].append(literal)
        return len(symtab["littab"]["literals"]) - 1
    
    # Helper function for BLOCKTAB
    def add_block(name, type_str, start_addr):
        """Add a block to the block table"""
        block = {
            "name": name,
            "type": type_str,
            "start_address": start_addr,
            "size": 0,
            "end_address": None
        }
        symtab["blocktab"]["blocks"].append(block)
        symtab["blocktab"]["current_block"] = block
        return len(symtab["blocktab"]["blocks"]) - 1
    
    # Helper function to parse value
    def parse_value(value_str):
        """Parse a value string into its appropriate type"""
        if value_str == "$":  # Special case for current address
            return address
        elif value_str in labels:
            return labels[value_str]
        elif value_str in equ_dict:
            return equ_dict[value_str]
        elif value_str.startswith("0x"):
            return int(value_str, 16)
        else:
            try:
                # Önce doğrudan sayı olarak çevirmeyi dene
                return int(value_str, 0)
            except ValueError:
                # Aritmetik ifade olabilir, güvenli eval ile deneyelim
                try:
                    # Aritmetik operatörleri kontrol et (+, -, *, /, %, <<, >>)
                    if any(op in value_str for op in ['+', '-', '*', '/', '%', '<<', '>>']):
                        # Özel sembolleri değerleriyle değiştir
                        expr = value_str
                        for label, val in labels.items():
                            expr = expr.replace(label, str(val))
                        for const, val in equ_dict.items():
                            expr = expr.replace(const, str(val))
                        
                        # Sadece sayılar, operatörler ve parantezlere izin ver
                        safe_chars = "0123456789+-*/()% \t<>"
                        if all(c in safe_chars for c in expr):
                            return eval(expr)
                except:
                    pass
                
                # İfade değerlendirme başarısız olursa orijinal değeri döndür
                return value_str
    
    # First pass: collect all labels and EQU definitions
    for line in assembly_code.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        parts = line.split(';')[0].strip().replace(',', ' ').split()
        if not parts:
            continue
            
        # Handle EQU definitions
        if len(parts) >= 3 and parts[1].upper() == "EQU":
            const_name = parts[0]
            const_value = parts[2]
            if const_value.endswith('h'):
                const_value = "0x" + const_value[:-1]
            try:
                value = parse_value(const_value)
                equ_dict[const_name] = value
                add_literal(value, "EQU")
            except ValueError:
                print(f"Invalid value in EQU: {const_value}")
            continue
            
        # Handle INT directive
        if len(parts) >= 2 and parts[0].upper() == "INT":
            try:
                value = parse_value(parts[1])
                add_literal(value, "INT")
            except ValueError:
                print(f"Invalid value in INT: {parts[1]}")
            continue
            
        # Handle labels
        if parts[0].endswith(":"):
            label_name = parts[0][:-1].strip()
            labels[label_name] = address
            if len(parts) > 1:
                parts = parts[1:]
            else:
                continue
    
    # Second pass: process instructions and directives
    address = 0
    for line in assembly_code.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        parts = line.split(';')[0].strip().replace(',', ' ').split()
        if not parts:
            continue
            
        # Handle section directives (BLOCKTAB)
        if parts[0].upper() in [".TEXT", ".DATA", ".BSS", ".INTVEC", ".SECT"]:
            section_name = parts[0].upper()
            if section_name == ".SECT" and len(parts) > 1:
                section_name = parts[1]
            current_section = section_name
            add_block(section_name, section_name, address)
            if section_name not in sections:
                sections[section_name] = {"address": address, "size": 0}
            else:
                sections[section_name]["address"] = address
            continue
            
        # Handle immediate values (LITTAB)
        if len(parts) > 1 and parts[1].startswith('#'):
            imm_value = parts[1][1:]  # Remove #
            value = parse_value(imm_value)
            if isinstance(value, (int, str)):
                add_literal(value, "IMM")
            continue
            
        # Handle value initialization directives (LITTAB)
        if parts[0].upper() in [".WORD", ".BYTE", ".CHAR", ".STRING", ".INT", ".DW"]:
            current_value_type = parts[0].upper()
            if len(parts) > 1:
                for value in parts[1:]:
                    if current_value_type in [".WORD", ".INT", ".DW"]:
                        parsed_value = parse_value(value)
                        add_literal(parsed_value, "WORD")
                    elif current_value_type == ".BYTE":
                        parsed_value = parse_value(value)
                        add_literal(parsed_value, "BYTE")
                    elif current_value_type == ".CHAR":
                        if value.startswith("'"):
                            value = ord(value[1:-1])
                        else:
                            value = parse_value(value)
                        add_literal(value, "CHAR")
                    elif current_value_type == ".STRING":
                        if value.startswith('"'):
                            value = value[1:-1]
                        add_literal(value, "STR")
            continue
            
        # Handle instructions
        if parts[0].upper() not in ["ORG", "EQU", ".EQU", ".SET", ".DEFINE"]:
            address += 2
            for operand in parts[1:]:
                if operand.startswith('#') and not operand.startswith('#R'):
                    address += 2
                    
    # Update symbol table
    symtab["labels"] = labels.copy()
    symtab["equ"] = equ_dict.copy()
    symtab["data"] = data_values.copy()
    symtab["byte"] = byte_values.copy()
    symtab["string"] = string_values.copy()
    symtab["space"] = space_values.copy()
    symtab["sections"] = sections.copy()
    
    # Update block sizes
    for block in symtab["blocktab"]["blocks"]:
        if block["name"] in sections:
            block["size"] = sections[block["name"]]["size"]
            block["end_address"] = block["start_address"] + block["size"]
    
    return assembly_code

def build_double_operand(opcode, src_mode, src_reg, dst_mode, dst_reg, bw):
    try:
        op_bin = opcode_table[opcode]
        as_bits = format(src_mode, '02b')
        ad_bit = format(dst_mode, '01b')
        bw_bit = str(bw)
        
        as_bits = as_bits.replace("-", "")
        ad_bit = ad_bit.replace("-", "")
        
        instr = f"{op_bin}{format(src_reg, '04b')}{ad_bit}{bw_bit}{as_bits}{format(dst_reg, '04b')}"
        instr = instr.replace("-", "")
        
        print(f"Double Operand Binary: {instr}, Hex: {int(instr, 2):04X}")
        
        return f"{int(instr, 2):04X}"
    except Exception as e:
        print(f"build_double_operand error: {str(e)}")
        return "????"

def build_single_operand(opcode, dst_mode, dst_reg, bw):
    try:
        op_bin = opcode_table[opcode]  # check opcode
        ad_bit = format(dst_mode, '02b')  # get as 2 bits
        bw_bit = str(bw)

        full_bin = f"000100{op_bin}{ad_bit}{bw_bit}{format(dst_reg, '04b')}"
        
        print(f"Single Operand Binary: {full_bin}, Hex: {int(full_bin, 2):04X}")
        
        return f"{int(full_bin, 2):04X}"
    except Exception as e:
        print(f"build_single_operand error: {str(e)}")
        return "????"


def build_jump(opcode, offset):
    try:
        op_bin = opcode_table[opcode]
        
        # Offset değerini işle - negatif offset için 2's complement
        if isinstance(offset, int) and offset < 0:
            # 10-bit için 2's complement hesapla
            offset = 1024 + offset
            
        # 10-bit ile sınırla
        offset_bin = format(offset & 0x3FF, '010b')
        instr = f"{op_bin}{offset_bin}"
        
        print(f"Jump Instruction: {opcode} to offset {offset}, Binary: {instr}, Hex: {int(instr, 2):04X}")
        
        # Label kullanımı için modifikasyon kaydı ekle
        if isinstance(offset, str) and offset in labels:
            add_modification_record(
                int(instr, 2),     # Instruction as address
                10,                # 10-bit offset
                offset,           # Label name
                '+'               # Addition operation
            )
            
        return f"{int(instr, 2):04X}"
    except Exception as e:
        print(f"build_jump error: {str(e)}")
        return "????"


# Global tag configurations
def configure_tags():
    input_text.tag_config("keyword", foreground="#007ACC")  # Blue
    input_text.tag_config("register", foreground="#FF8C00")  # Orange
    input_text.tag_config("number", foreground="#56DB40")   # Green
    input_text.tag_config("comment", foreground="#898989")  # Gray
    input_text.tag_config("addressing", foreground="#DB70DB")  # Pink
    input_text.tag_config("label", foreground="#00B7C3")   # Turquoise
    input_text.tag_config("constant", foreground="#4FC1FF") # Light blue
    input_text.tag_config("comma", foreground="#D4D4D4")   # Light grey
    input_text.tag_config("branch_label", foreground="#E74C3C")  # Red
    input_text.tag_config("error", foreground="#FF1493", underline=True)  # Pink-red
    input_text.tag_config("suggestion", background="#404040")  # Dark grey background
    input_text.tag_config("directive", foreground="#007ACC", font=("Courier", 10, "bold"))  # Blue, bold
    input_text.tag_config("string", foreground="#FFA500")  # Orange
    input_text.tag_config("char", foreground="#FFA500")  # Orange
    input_text.tag_config("delimiter", foreground="#FFD700")  # Gold
    input_text.tag_config("operand", foreground="#98FB98")  # Pale green
    input_text.tag_config("equ", foreground="#56DB40")  # Green for EQU

def highlight_syntax(event=None):
    # Remove all existing tags
    input_text.tag_remove("keyword", "1.0", "end")
    input_text.tag_remove("register", "1.0", "end")
    input_text.tag_remove("number", "1.0", "end")
    input_text.tag_remove("comment", "1.0", "end")
    input_text.tag_remove("addressing", "1.0", "end")
    input_text.tag_remove("label", "1.0", "end")
    input_text.tag_remove("comma", "1.0", "end")
    input_text.tag_remove("branch_label", "1.0", "end")
    input_text.tag_remove("error", "1.0", "end")
    input_text.tag_remove("suggestion", "1.0", "end")
    input_text.tag_remove("constant", "1.0", "end")
    input_text.tag_remove("directive", "1.0", "end")
    input_text.tag_remove("string", "1.0", "end")
    input_text.tag_remove("char", "1.0", "end")
    input_text.tag_remove("delimiter", "1.0", "end")
    input_text.tag_remove("operand", "1.0", "end")
    input_text.tag_remove("equ", "1.0", "end")

    # Define all opcodes and directives
    all_opcodes = set(opcode_table.keys()).union(set(emulated_map.keys()))
    all_directives = set(directives)

    # Get all text
    all_text = input_text.get("1.0", tk.END)
    
    # Find all comments
    comment_ranges = []
    for match in re.finditer(r";.*", all_text):
        input_text.tag_add("comment", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        comment_ranges.append((match.start(), match.end()))

    # Helper to check if position is inside a comment
    def is_in_comment(pos):
        return any(start <= pos < end for start, end in comment_ranges)
    
    # Collect constants and labels
    constants = set()
    labels = set()
    
    # First pass to collect labels and constants
    for line in all_text.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        # Check for EQU definitions
        equ_match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s+EQU\s+', line, re.IGNORECASE)
        if equ_match:
            constant_name = equ_match.group(1)
            constants.add(constant_name)
            
        # Also collect standard labels
        label_match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*):(?:\s+|$)', line)
        if label_match:
            label_name = label_match.group(1)
            labels.add(label_name)

    # 1.4 version syntax highlighting
    # Keyword renklendirme
    for keyword in all_opcodes:
        pattern = r"\b" + re.escape(keyword) + r"(\.(W|B))?\b"
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            if not is_in_comment(match.start()):
                input_text.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Register renklendirme
    registers = [f"R{i}" for i in range(16)] + ["PC", "SP", "SR", "CG"]
    for register in registers:
        pattern = r"\b" + re.escape(register) + r"\b"
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            if not is_in_comment(match.start()):
                input_text.tag_add("register", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Sayılar için renklendirme
    number_pattern = r"\b(0x[0-9a-fA-F]+|\d+h|\d+)\b"
    for match in re.finditer(number_pattern, all_text):
        if not is_in_comment(match.start()):
            input_text.tag_add("number", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Adresleme sembolleri ve operandları için renklendirme - geliştirilmiş versiyon
    addressing_pattern = r"[#@&]([A-Za-z0-9_]+)"
    for match in re.finditer(addressing_pattern, all_text):
        if not is_in_comment(match.start()):
            # Adresleme sembolünü renklendir
            input_text.tag_add("addressing", f"1.0+{match.start()}c", f"1.0+{match.start()+1}c")
            # Operandı renklendir
            input_text.tag_add("operand", f"1.0+{match.start()+1}c", f"1.0+{match.end()}c")

    # Etiketler için renklendirme
    label_pattern = r"\b[A-Za-z_][A-Za-z0-9_]*:"
    for match in re.finditer(label_pattern, all_text):
        if not is_in_comment(match.start()):
            input_text.tag_add("label", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Virgül için renklendirme
    for match in re.finditer(r",", all_text):
        if not is_in_comment(match.start()):
            input_text.tag_add("comma", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Branch talimatları için hedef etiketler
    branch_instructions = ["JNE", "JNZ", "JEQ", "JNC", "JC", "JN", "JGE", "JL", "CALL", "JNZ", 
                         "JZ", "JLO", "JHS", "BR", "RET"]
    for branch in branch_instructions:
        pattern = rf"\b{branch}\s+([A-Za-z_][A-Za-z0-9_]*)\b"
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            if not is_in_comment(match.start(1)):
                input_text.tag_add("branch_label", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")
    
    # EQU tanımları için renklendirme
    equ_pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s+EQU\b"
    for match in re.finditer(equ_pattern, all_text, re.IGNORECASE):
        if not is_in_comment(match.start(1)):
            input_text.tag_add("equ", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")

    # String ve char literalleri için renklendirme
    string_pattern = r'"[^"]*"'
    for match in re.finditer(string_pattern, all_text):
        if not is_in_comment(match.start()):
            input_text.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            input_text.tag_add("delimiter", f"1.0+{match.start()}c", f"1.0+{match.start()+1}c")
            input_text.tag_add("delimiter", f"1.0+{match.end()-1}c", f"1.0+{match.end()}c")

    char_pattern = r"'[^']*'"
    for match in re.finditer(char_pattern, all_text):
        if not is_in_comment(match.start()):
            input_text.tag_add("char", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            input_text.tag_add("delimiter", f"1.0+{match.start()}c", f"1.0+{match.start()+1}c")
            input_text.tag_add("delimiter", f"1.0+{match.end()-1}c", f"1.0+{match.end()}c")

    # Direktifler için özel renklendirme
    for directive in directives:
        pattern = r"\." + re.escape(directive) + r"\b"
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            if not is_in_comment(match.start()):
                input_text.tag_add("directive", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Noktasız direktifler için (sadece EQU ve ORG)
    for directive in non_dot_directives:
        pattern = r"\b" + re.escape(directive) + r"\b"
        for match in re.finditer(pattern, all_text, re.IGNORECASE):
            if not is_in_comment(match.start()):
                input_text.tag_add("directive", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    # Operandlar için renklendirme - geliştirilmiş versiyon
    for line_num, line in enumerate(all_text.splitlines(), 1):
        if not line.strip() or line.strip().startswith(';'):
            continue
            
        # Skip if it's a directive line
        parts = line.split()
        if not parts:
            continue
            
        if parts[0].startswith('.') and parts[0][1:].upper() in all_directives:
            continue
            
        # Skip if it's just a label
        if len(parts) == 1 and parts[0].endswith(':'):
            continue
            
        # Process operands - handle spaces better
        line_content = line.strip()
        if ';' in line_content:
            line_content = line_content.split(';')[0].strip()
            
        # Split by commas first to handle comma-separated operands
        operand_parts = line_content.split(',')
        for i, part in enumerate(operand_parts):
            # Skip the first part if it's the instruction
            if i == 0:
                instruction_parts = part.split()
                if len(instruction_parts) > 1:
                    # Process remaining parts as operands
                    for operand in instruction_parts[1:]:
                        pos = line.find(operand)
                        if pos != -1 and not is_in_comment(pos):
                            input_text.tag_add("operand", f"{line_num}.{pos}", f"{line_num}.{pos+len(operand)}")
            else:
                # Process comma-separated operands
                operand = part.strip()
                if operand:
                    pos = line.find(operand)
                    if pos != -1 and not is_in_comment(pos):
                        input_text.tag_add("operand", f"{line_num}.{pos}", f"{line_num}.{pos+len(operand)}")

    # Hata tespiti - bilinmeyen komutlar için
    invalid_opcodes = []
    suggestions = {}
    
    for i, line in enumerate(all_text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        if ";" in line:
            line = line.split(";")[0].strip()
            
        if not line:
            continue
            
        if line.endswith(":") or ":" in line and line.split(":")[1].strip() == "":
            continue
            
        parts = line.replace(",", " ").split()
        if not parts:
            continue
            
        # Skip if it's a directive line
        if parts[0].startswith('.') and parts[0][1:].upper() in all_directives:
            continue
        
        if parts[0].upper() in non_dot_directives:
            continue
        
        if len(parts) >= 3 and parts[1].upper() == "EQU":
            continue
            
        if ":" in parts[0]:
            if len(parts) == 1 or (len(parts) > 1 and parts[1].startswith(";")):
                continue
            else:
                parts = parts[1:]
        
        command = parts[0].upper().split(".")[0]
        
        if command not in all_opcodes:
            position = all_text.find(line)
            if position != -1:  # Safeguard against not finding the line
                cmd_pos = position + line.find(parts[0])
                cmd_end = cmd_pos + len(parts[0])
                
                if not is_in_comment(cmd_pos):
                    input_text.tag_add("error", f"1.0+{cmd_pos}c", f"1.0+{cmd_end}c")
                    invalid_opcodes.append(parts[0])
                    
                    closest_command = find_closest_command(command, all_opcodes)
                    if closest_command:
                        suffix = ""
                        if "." in parts[0]:
                            suffix = parts[0].split(".", 1)[1]
                            suggestions[parts[0]] = f"{closest_command}.{suffix}"
                        else:
                            suggestions[parts[0]] = closest_command
                            
    # Öneriler göster
    if invalid_opcodes:
        for cmd in invalid_opcodes:
            if cmd in suggestions:
                show_suggestion(cmd, suggestions[cmd])
                                
    # Apply tag configurations
    input_text.tag_config("keyword", foreground="#007ACC")  # Blue
    input_text.tag_config("register", foreground="#FF8C00")  # Orange
    input_text.tag_config("number", foreground="#56DB40")   # Green
    input_text.tag_config("comment", foreground="#898989")  # Gray
    input_text.tag_config("addressing", foreground="#DB70DB")  # Pink
    input_text.tag_config("label", foreground="#00B7C3")   # Turquoise
    input_text.tag_config("constant", foreground="#4FC1FF") # Light blue
    input_text.tag_config("comma", foreground="#D4D4D4")   # Light grey
    input_text.tag_config("branch_label", foreground="#E74C3C")  # Red
    input_text.tag_config("error", foreground="#FF1493", underline=True)  # Pink-red
    input_text.tag_config("suggestion", background="#404040")  # Dark grey background
    input_text.tag_config("directive", foreground="#007ACC", font=("Courier", 10, "bold"))  # Blue, bold
    input_text.tag_config("string", foreground="#FFA500")  # Orange
    input_text.tag_config("char", foreground="#FFA500")  # Orange
    input_text.tag_config("delimiter", foreground="#FFD700")  # Gold
    input_text.tag_config("operand", foreground="#98FB98")  # Pale green
    input_text.tag_config("equ", foreground="#56DB40")  # Green for EQU

def show_suggestion(invalid_cmd, suggestion):
    """Show suggestion for invalid command"""
    # Get current line
    current_line = input_text.get("insert linestart", "insert lineend")
    parts = current_line.split(';')[0].strip().replace(',', ' ').split()
    
    if not parts:
        return
        
    # Skip if it's a directive (either dot-prefixed or non-dot)
    if parts[0].startswith('.') or parts[0].upper() in non_dot_directives:
        return
    
    # Remove existing suggestion tags for this line
    line_start = input_text.index("insert linestart")
    line_end = input_text.index("insert lineend")
    input_text.tag_remove("suggestion", line_start, line_end)
    
    # Find the position of the invalid command in the line
    cmd_start = current_line.find(invalid_cmd)
    if cmd_start == -1:
        return
        
    # Calculate the absolute position
    start_pos = f"{line_start}+{cmd_start}c"
    end_pos = f"{line_start}+{cmd_start + len(invalid_cmd)}c"
    
    # Add suggestion tag
    input_text.tag_add("suggestion", start_pos, end_pos)
    
    # Create tooltip with suggestion
    create_tooltip(input_text, end_pos, f"Did you mean: {suggestion}?")

def create_tooltip(widget, pos, text):
    pass

def find_closest_command(command, valid_commands, threshold=0.6):
    best_match = None
    best_score = 0
    
    command = command.upper()
    
    for valid in valid_commands:
        score = calculate_similarity(command, valid)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = valid
            
    return best_match

def calculate_similarity(str1, str2):
    if not str1 or not str2:
        return 0
        
    if str1[0] != str2[0]:
        return 0.1
        
    distance = levenshtein_distance(str1, str2)
    max_len = max(len(str1), len(str2))
    
    similarity = 1 - (distance / max_len)
    
    return similarity

def levenshtein_distance(str1, str2):
    m, n = len(str1), len(str2)
    
    dp = [[0 for _ in range(n+1)] for _ in range(m+1)]
    
    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j
        
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if str1[i-1] == str2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
            
    return dp[m][n]

def on_text_change(event=None):
    """Handle text changes and update syntax highlighting"""
    highlight_syntax()
    
    # Get current line
    current_line = input_text.get("insert linestart", "insert lineend")
    parts = current_line.split(';')[0].strip().replace(',', ' ').split()
    
    if not parts:
        return
        
    # Initialize all_opcodes set with directives
    all_opcodes = set(opcode_table.keys()).union(set(emulated_map.keys()))
    
    # Add both dot-prefixed directives and non-dot directives (EQU and ORG)
    for directive in directives:
        all_opcodes.add('.' + directive)
    for directive in non_dot_directives:
        all_opcodes.add(directive)
    
    # Remove any existing suggestion tags for this line
    line_start = input_text.index("insert linestart")
    line_end = input_text.index("insert lineend")
    input_text.tag_remove("suggestion", line_start, line_end)
    
    # Check if it's a directive (either dot-prefixed or non-dot)
    if parts[0].startswith('.') or parts[0].upper() in non_dot_directives:
        return
        
    # Check if it's a valid command
    if parts[0].upper() not in all_opcodes:
        # Show suggestion if command is invalid
        suggestion = find_closest_command(parts[0], all_opcodes)
        if suggestion:
            show_suggestion(parts[0], suggestion)

def convert_all():
    global input_text, hex_text, binary_text, status_var, memory_values, section_output_data
    
    print("convert_all function called")
    
    try:
        # Clear outputs
        hex_output = ""
        binary_output = ""
        
        # Section tracking için daha kapsamlı sözlükler
        section_data = {
            ".TEXT": [],
            ".DATA": [],
            ".BSS": [],
            ".INTVEC": [],
            # Özel bölümler dinamik olarak eklenecek
        }
        
        # Get input text
        assembly_code = input_text.get("1.0", tk.END)
        
        # First pass to get labels
        global start_address, labels, symtab
        first_pass(assembly_code)
        
        # Second pass to generate machine code
        lines = assembly_code.splitlines()
        address = start_address
        instruction_count = 0
        processed_lines = 0
        
        # Bellekteki değerleri sıfırla
        if 'memory_values' not in globals():
            memory_values = {}
        
        # Aktif section takibi
        current_section = ".TEXT"  # Default section
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
                
            processed_lines += 1
                
            # Split by semicolon to ignore comments
            line = line.split(';')[0].strip()
            
            # Skip label-only lines
            if line.endswith(':'):
                continue
                
            # Handle directives
            if line.startswith('.'):
                directive_parts = line.split(None, 1)
                directive = directive_parts[0].upper()
                
                # Section değişikliğini takip et
                if directive == '.TEXT':
                    current_section = ".TEXT"
                    continue
                elif directive == '.DATA':
                    current_section = ".DATA"
                    continue
                elif directive == '.BSS':
                    current_section = ".BSS"
                    continue
                elif directive == '.INTVEC':
                    current_section = ".INTVEC"
                    if ".INTVEC" not in section_data:
                        section_data[".INTVEC"] = []
                    continue
                elif directive == '.SECT':
                    # İsteğe bağlı bölüm adı parametresi
                    if len(directive_parts) > 1:
                        # Tırnak işaretlerini temizle
                        section_name = directive_parts[1].strip('"\'')
                        current_section = f".SECT_{section_name}"
                        # Eğer bu bölüm daha önce tanımlanmadıysa, ekle
                        if current_section not in section_data:
                            section_data[current_section] = []
                    else:
                        # Parametre yoksa varsayılan olarak TEXT'e yönlendir
                        current_section = ".TEXT"
                    continue
                
                # Handle .ALIGN directive
                # Handle .SPACE directive
                if directive == '.SPACE':
                    if len(directive_parts) > 1:
                        try:
                            space_size = int(directive_parts[1])
                            for _ in range(space_size):
                                hex_value = "00"
                                binary_value = "00000000"
                                section_data[current_section].append((address, hex_value, binary_value))
                                address += 2
                                instruction_count += 1
                        except ValueError:
                            print(f"Error: Invalid space size in {line}")
                    continue
                
                # Handle .BES directive (not supported)
                if directive == '.BES':
                    print(f"Error: .BES directive is not supported in MSP430")
                    continue
                
                if directive == '.WORD' or directive == '.DW' or directive == '.INT' or directive == '.SHORT':
                    # Handle multiple values
                    if len(directive_parts) > 1:
                        values_str = directive_parts[1]
                        # Split by commas
                        for value_str in values_str.split(','):
                            value_str = value_str.strip()
                            
                            # Handle labels
                            symbol_ref = None
                            if value_str in labels:
                                value = labels[value_str]
                                symbol_ref = value_str
                            elif value_str in symtab["equ"]:
                                value = symtab["equ"][value_str]
                                symbol_ref = value_str
                            else:
                                try:
                                    if value_str.startswith('0x'):
                                        value = int(value_str, 16)
                                    elif value_str.endswith('h'):
                                        value = int(value_str[:-1], 16)
                                    else:
                                        value = int(value_str)
                                except ValueError:
                                    print(f"Invalid number format: {value_str}")
                                    continue
                            
                            hex_value = format(value & 0xFFFF, '04X')
                            binary_value = format(value & 0xFFFF, '016b')
                            section_data[current_section].append((address, hex_value, binary_value))
                            
                            # Add modification record for symbol references in data section
                            if symbol_ref:
                                add_modification_record(
                                    address,         # Address where the symbol is referenced
                                    16,              # Length of 16 bits (word)
                                    symbol_ref,      # Symbol name
                                    '+'              # Addition operation
                                )
                            
                            address += 2
                            instruction_count += 1
                    continue
                
                if directive == '.LONG':
                    # Handle multiple values
                    if len(directive_parts) > 1:
                        values_str = directive_parts[1]
                        # Split by commas
                        for value_str in values_str.split(','):
                            value_str = value_str.strip()
                            
                            # Handle labels
                            symbol_ref = None
                            if value_str in labels:
                                value = labels[value_str]
                                symbol_ref = value_str
                            elif value_str in symtab["equ"]:
                                value = symtab["equ"][value_str]
                                symbol_ref = value_str
                            else:
                                try:
                                    if value_str.startswith('0x'):
                                        value = int(value_str, 16)
                                    elif value_str.endswith('h'):
                                        value = int(value_str[:-1], 16)
                                    else:
                                        value = int(value_str)
                                except ValueError:
                                    print(f"Invalid number format: {value_str}")
                                    continue
                            
                            # Write both words of the long value
                            hex_value_low = format(value & 0xFFFF, '04X')
                            hex_value_high = format((value >> 16) & 0xFFFF, '04X')
                            binary_value_low = format(value & 0xFFFF, '016b')
                            binary_value_high = format((value >> 16) & 0xFFFF, '016b')
                            
                            # Write low word first (little endian)
                            section_data[current_section].append((address, hex_value_low, binary_value_low))
                            address += 2
                            
                            # Write high word
                            section_data[current_section].append((address, hex_value_high, binary_value_high))
                            
                            # Add modification record for symbol references in data section
                            if symbol_ref:
                                add_modification_record(
                                    address - 2,         # Address where the symbol is referenced (low word)
                                    32,                  # Length of 32 bits (long)
                                    symbol_ref,          # Symbol name
                                    '+'                  # Addition operation
                                )
                            
                            address += 2
                            instruction_count += 2
                    continue
                    
                if directive == '.BYTE' or directive == '.DB':
                    # Handle multiple values
                    if len(directive_parts) > 1:
                        values_str = directive_parts[1]
                        # Split by commas
                        for value_str in values_str.split(','):
                            value_str = value_str.strip()
                            
                            try:
                                if value_str.startswith('0x'):
                                    value = int(value_str, 16)
                                elif value_str.endswith('h'):
                                    value = int(value_str[:-1], 16)
                                else:
                                    value = int(value_str)
                            except ValueError:
                                print(f"Invalid number format: {value_str}")
                                continue
                            
                            hex_value = format(value & 0xFF, '02X')
                            binary_value = format(value & 0xFF, '08b')
                            section_data[current_section].append((address, hex_value, binary_value))
                            address += 21
                            instruction_count += 1
                    continue
                    
                if directive == '.STRING' or directive == '.CSTRING':
                    if len(directive_parts) > 1:
                        string_value = directive_parts[1].strip()
                        
                        # Check if it's a valid string (enclosed in quotes)
                        if string_value.startswith('"') and string_value.endswith('"'):
                            # Strip quotes
                            string_value = string_value[1:-1]
                            
                            # Add each character as a byte
                            for char in string_value:
                                hex_value = format(ord(char) & 0xFF, '02X')
                                binary_value = format(ord(char) & 0xFF, '08b')
                                section_data[current_section].append((address, hex_value, binary_value))
                                address += 1
                                instruction_count += 1
                            
                            # Add null terminator for CSTRING
                            if directive == '.CSTRING':
                                section_data[current_section].append((address, "00", "00000000"))
                                address += 1
                                instruction_count += 1
                    continue
                
                if directive == '.UBYTE' or directive == '.UCHAR':
                    if len(directive_parts) > 1:
                        values_str = directive_parts[1]
                        for value_str in values_str.split(','):
                            value_str = value_str.strip()
                            try:
                                if value_str.startswith('0x'):
                                    value = int(value_str, 16)
                                elif value_str.endswith('h'):
                                    value = int(value_str[:-1], 16)
                                else:
                                    value = int(value_str)
                                # 8-bit unsigned sınırı
                                value = value & 0xFF
                                hex_value = format(value, '02X')
                                binary_value = format(value, '08b')
                                section_data[current_section].append((address, hex_value, binary_value))
                                address += 1
                                instruction_count += 1
                            except ValueError:
                                print(f"Error: Invalid value format in {line}")
                    continue
                
                continue
            
            # Parse the instruction
            parts = line.replace(',', ' ').split()
            parts = [p for p in parts if p]  # Remove empty elements
            
            if not parts:
                continue
                
            # Handle ORG directive
            if parts[0].upper() == 'ORG':
                if len(parts) > 1:
                    try:
                        # EQU sembol kontrolü
                        if parts[1] in labels:
                            address = labels[parts[1]]
                        elif parts[1] in symtab["equ"]:
                            address = symtab["equ"][parts[1]]
                        # Sayısal değer kontrolü
                        elif parts[1].startswith('0x'):
                            address = int(parts[1], 16)
                        elif parts[1].endswith('h'):
                            address = int(parts[1][:-1], 16)
                        else:
                            address = int(parts[1])
                    except ValueError:
                        print(f"Invalid address format in ORG: {parts[1]}")
                continue
                
            # Handle EQU directive
            if parts[0].upper() == 'EQU':
                continue
                
            # Handle label:instruction format
            if ':' in parts[0]:
                label, instr = parts[0].split(':', 1)
                if instr:
                    parts[0] = instr
                else:
                    parts = parts[1:]
                    
            # Apply emulated instructions
            parts = apply_emulated_instructions(parts)
            if not parts:
                continue
                
            # Handle instructions
            if parts[0] in hardcoded_commands:
                # Direct hex mapping
                hex_instr = hardcoded_commands[parts[0]]
                hex_value = format(int(hex_instr, 16), '04X')
                binary_value = format(int(hex_instr, 16), '016b')
                section_data[current_section].append((address, hex_value, binary_value))
                address += 2
                instruction_count += 1
                continue
                
            if parts[0] in opcode_table:
                mnemonic = parts[0]
                instr_format = 0  # 0 = double operand, 1 = single operand, 2 = jump
                
                if mnemonic in ["MOV", "ADD", "ADDC", "SUBC", "SUB", "CMP", "DADD", "BIT", "BIC", "BIS", "XOR", "AND"]:
                    instr_format = 0  # Double operand
                elif mnemonic in ["RRC", "SWPB", "RRA", "SXT", "PUSH", "CALL", "RETI"]:
                    instr_format = 1  # Single operand
                elif mnemonic in ["JNE", "JEQ", "JNC", "JC", "JN", "JGE", "JL", "JMP", "JNZ", "JZ", "JLO", "JHS"]:
                    instr_format = 2  # Jump
                
                bw = get_bw_bit(mnemonic)
                
                if instr_format == 0:  # Double operand
                    if len(parts) < 3:
                        print(f"Error: Invalid number of operands for {mnemonic}")
                        continue
                        
                    src_operand = parts[1]
                    dst_operand = parts[2]
                    
                    src_mode, src_reg, src_value = get_addressing_mode(src_operand)
                    dst_mode, dst_reg, dst_value = get_addressing_mode(dst_operand)
                    
                    if src_mode == -1 or dst_mode == -1:
                        print(f"Error: Invalid addressing mode in {line}")
                        continue
                        
                    hex_instr = build_double_operand(mnemonic, src_mode, src_reg, dst_mode, dst_reg, bw)
                    hex_value = format(int(hex_instr, 16), '04X')
                    binary_value = format(int(hex_instr, 16), '016b')
                    section_data[current_section].append((address, hex_value, binary_value))
                    
                    address += 2
                    instruction_count += 1
                    
                    # Add additional words if needed
                    if src_mode == 1 and src_reg == 0:  # Indexed/symbolic src
                        symbol_ref = None
                        # Check if it's a symbol reference
                        if isinstance(src_value, str) and src_value in labels:
                            src_value = labels[src_value]
                            symbol_ref = src_value
                        elif isinstance(src_value, str) and src_value in symtab["equ"]:
                            src_value = symtab["equ"][src_value]
                            symbol_ref = src_value
                            
                        hex_value = format(src_value & 0xFFFF, '04X')
                        binary_value = format(src_value & 0xFFFF, '016b')
                        section_data[current_section].append((address, hex_value, binary_value))
                        
                        # Add modification record for symbol references
                        if symbol_ref:
                            add_modification_record(
                                address,         # Address where the symbol is referenced
                                16,              # Length of 16 bits (word)
                                symbol_ref,      # Symbol name
                                '+'              # Addition operation
                            )
                            
                        address += 2
                    
                    if dst_mode == 1 and dst_reg == 0:  # Indexed/symbolic dst
                        symbol_ref = None
                        # Check if it's a symbol reference
                        if isinstance(dst_value, str) and dst_value in labels:
                            dst_value = labels[dst_value]
                            symbol_ref = dst_value
                        elif isinstance(dst_value, str) and dst_value in symtab["equ"]:
                            dst_value = symtab["equ"][dst_value]
                            symbol_ref = dst_value
                            
                        hex_value = format(dst_value & 0xFFFF, '04X')
                        binary_value = format(dst_value & 0xFFFF, '016b')
                        section_data[current_section].append((address, hex_value, binary_value))
                        
                        # Add modification record for symbol references
                        if symbol_ref:
                            add_modification_record(
                                address,         # Address where the symbol is referenced
                                16,              # Length of 16 bits (word)
                                symbol_ref,      # Symbol name
                                '+'              # Addition operation
                            )
                            
                        address += 2
                    
                elif instr_format == 1:  # Single operand
                    if len(parts) < 2:
                        print(f"Error: Invalid number of operands for {mnemonic}")
                        continue
                        
                    dst_operand = parts[1]
                    dst_mode, dst_reg, dst_value = get_addressing_mode(dst_operand)
                    
                    if dst_mode == -1:
                        print(f"Error: Invalid addressing mode in {line}")
                        continue
                        
                    hex_instr = build_single_operand(mnemonic, dst_mode, dst_reg, bw)
                    hex_value = format(int(hex_instr, 16), '04X')
                    binary_value = format(int(hex_instr, 16), '016b')
                    section_data[current_section].append((address, hex_value, binary_value))
                    
                    address += 2
                    instruction_count += 1
                    
                    # Add additional word if needed
                    if dst_mode == 1 and dst_reg == 0:  # Indexed/symbolic
                        symbol_ref = None
                        # Check if it's a symbol reference
                        if isinstance(dst_value, str) and dst_value in labels:
                            dst_value = labels[dst_value]
                            symbol_ref = dst_value
                        elif isinstance(dst_value, str) and dst_value in symtab["equ"]:
                            dst_value = symtab["equ"][dst_value]
                            symbol_ref = dst_value
                            
                        hex_value = format(dst_value & 0xFFFF, '04X')
                        binary_value = format(dst_value & 0xFFFF, '016b')
                        section_data[current_section].append((address, hex_value, binary_value))
                        
                        # Add modification record for symbol references
                        if symbol_ref:
                            add_modification_record(
                                address,         # Address where the symbol is referenced
                                16,              # Length of 16 bits (word)
                                symbol_ref,      # Symbol name
                                '+'              # Addition operation
                            )
                            
                        address += 2
                    
                    # Add modification record for CALL instructions since they're position-independent
                    if mnemonic == "CALL":
                        add_modification_record(
                            address - 2,     # Address of the instruction
                            16,              # Length of 16 bits (word)
                            "PROGADDR",      # Program address symbol
                            '+'              # Addition operation
                        )
                    
                elif instr_format == 2:  # Jump
                    if len(parts) < 2:
                        print(f"Error: Invalid number of operands for {mnemonic}")
                        continue
                        
                    target_label = parts[1]
                    
                    # Farklı atlama hedef formatlarını işle
                    if target_label.startswith('#'):
                        # Doğrudan değer formatı (#1234)
                        try:
                            if target_label[1:].startswith('0x'):
                                target_addr = int(target_label[1:], 16)
                            elif target_label[1:].endswith('h'):
                                target_addr = int(target_label[1:-1], 16)
                            else:
                                target_addr = int(target_label[1:])
                                
                            # PC-relative offset hesapla
                            offset = (target_addr - (address + 2)) // 2
                        except ValueError:
                            print(f"Error: Invalid jump target format in {line}")
                            continue
                    elif target_label.startswith('+') or target_label.startswith('-'):
                        # Doğrudan offset formatı (+4, -6 gibi)
                        try:
                            offset = int(target_label) // 2  # Word cinsinden offset
                        except ValueError:
                            print(f"Error: Invalid jump offset in {line}")
                            continue
                    elif target_label in labels:
                        # Etiket (label) formatı
                        target_addr = labels[target_label]
                        
                        # PC-relative offset hesapla (word cinsinden)
                        offset = (target_addr - (address + 2)) // 2
                    elif target_label in symtab["equ"]:
                        # EQU sembolü formatı
                        target_addr = symtab["equ"][target_label]
                        
                        # PC-relative offset hesapla (word cinsinden)
                        offset = (target_addr - (address + 2)) // 2
                    else:
                        print(f"Error: Unknown jump target '{target_label}' in {line}")
                        continue
                    
                    # Offset sınırlarını kontrol et (10-bit signed: -512 to 511)
                    if offset < -512 or offset > 511:
                        print(f"Error: Jump offset {offset} is out of range (-512 to 511) in {line}")
                        continue
                    
                    # Makine kodunu oluştur
                    hex_instr = build_jump(mnemonic, offset)
                    hex_value = format(int(hex_instr, 16), '04X')
                    binary_value = format(int(hex_instr, 16), '016b')
                    section_data[current_section].append((address, hex_value, binary_value))
                    
                    # Binary çıktı için dönüştürme
                    address += 2
                    instruction_count += 1
                        
                    target_label = parts[1]
                    
                    # Farklı atlama hedef formatlarını işle
                    if target_label.startswith('#'):
                        # Doğrudan değer formatı (#1234)
                        try:
                            if target_label[1:].startswith('0x'):
                                target_addr = int(target_label[1:], 16)
                            elif target_label[1:].endswith('h'):
                                target_addr = int(target_label[1:-1], 16)
                            else:
                                target_addr = int(target_label[1:])
                                
                            # PC-relative offset hesapla
                            offset = (target_addr - (address + 2)) // 2
                        except ValueError:
                            print(f"Error: Invalid jump target format in {line}")
                            continue
                    elif target_label.startswith('+') or target_label.startswith('-'):
                        # Doğrudan offset formatı (+4, -6 gibi)
                        try:
                            offset = int(target_label) // 2  # Word cinsinden offset
                        except ValueError:
                            print(f"Error: Invalid jump offset in {line}")
                            continue
                    elif target_label in labels:
                        # Etiket (label) formatı
                        target_addr = labels[target_label]
                        
                        # PC-relative offset hesapla (word cinsinden)
                        offset = (target_addr - (address + 2)) // 2
                    elif target_label in symtab["equ"]:
                        # EQU sembolü formatı
                        target_addr = symtab["equ"][target_label]
                        
                        # PC-relative offset hesapla (word cinsinden)
                        offset = (target_addr - (address + 2)) // 2
                    else:
                        print(f"Error: Unknown jump target '{target_label}' in {line}")
                        continue
                    
                    # Offset sınırlarını kontrol et (10-bit signed: -512 to 511)
                    if offset < -512 or offset > 511:
                        print(f"Error: Jump offset {offset} is out of range (-512 to 511) in {line}")
                        continue
                    
                    # Makine kodunu oluştur
                    hex_instr = build_jump(mnemonic, offset)
                    hex_value = format(int(hex_instr, 16), '04X')
                    binary_value = format(int(hex_instr, 16), '016b')
                    section_data[current_section].append((address, hex_value, binary_value))
                    
                    # Binary çıktı için dönüştürme
                    address += 2
                    instruction_count += 1
                        
                    target_label = parts[1]
                    
                    if target_label in labels:
                        target_addr = labels[target_label]
                        # Calculate offset for jumps (PC relative)
                        offset = (target_addr - (address + 2)) // 2
                        if offset > 511 or offset < -512:
                            print(f"Error: Jump offset too large in {line}")
                            continue
                            
                        hex_instr = build_jump(mnemonic, offset & 0x3FF)
                        hex_value = format(int(hex_instr, 16), '04X')
                        binary_value = format(int(hex_instr, 16), '016b')
                        section_data[current_section].append((address, hex_value, binary_value))
                        
                        # Add modification record for jump instructions
                        # These need to be adjusted when program is relocated
                        add_modification_record(
                            address,         # Address of the jump instruction
                            16,              # Length of 16 bits
                            target_label,    # Target label name
                            '+'              # Addition operation
                        )
                        
                    else:
                        print(f"Error: Unknown label {target_label} in {line}")
                        continue
                        
                    address += 2
                    instruction_count += 1
                    
            else:
                print(f"Error: Unknown instruction {parts[0]} in {line}")
                continue
                
        # Sort output by address
        section_data[current_section].sort(key=lambda x: x[0])
        
        # Her section için ayrı çıktılar
        for section_name, data_list in section_data.items():
            if not data_list:  # Boş sectionları atla
                continue
                
            # Sıralama
            data_list.sort(key=lambda x: x[0])  # Adrese göre sırala
            
            # Hex ve binary output için satırlar oluştur
            for addr, hex_val, bin_val in data_list:
                                # Her word için iki ayrı byte belleğe kaydet (low byte, high byte)
                hex_val_int = int(hex_val, 16)
                memory_values[addr] = hex_val_int & 0xFF       # Düşük byte
                memory_values[addr+1] = (hex_val_int >> 8) & 0xFF  # Yüksek byte
                
                # Çıktıları birleştir
                hex_output += f"{addr:04X}: {hex_val}\n"
                binary_output += f"{addr:04X}: {bin_val}\n"
        
        # Update outputs
        hex_text.config(state=tk.NORMAL)
        hex_text.delete("1.0", tk.END)
        hex_text.insert(tk.END, hex_output)
        hex_text.config(state=tk.DISABLED)
        
        binary_text.config(state=tk.NORMAL)
        binary_text.delete("1.0", tk.END)
        binary_text.insert(tk.END, binary_output)
        binary_text.config(state=tk.DISABLED)
        
        # Log conversion in modification record
        if instruction_count > 0:
            add_modification_record_history(
                "Code Conversion",
                f"Successfully converted {processed_lines} lines of assembly code to machine code. "
                f"Generated {instruction_count} instructions with a code size of {address - start_address} bytes."
            )
        
        # Update status
        status_var.set(f"Converted {instruction_count} instructions | Code size: {address - start_address} bytes")
        
        # Store the section data for object code view
        global section_output_data
        section_output_data = section_data
        
        return True
        
    except Exception as e:
        print(f"Error in convert_all: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Conversion Error", f"Error during conversion: {str(e)}")
        return False

def save_to_file():
    """Saves the converted code to a file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Converted Code"
    )
    
    if not file_path:
        return
    
    try:
        # Get content from text widget
        hex_content = hex_text.get("1.0", tk.END)
        
        with open(file_path, "w") as file:
            file.write(hex_content)
        
        status_var.set(f"File saved successfully: {file_path}")
        
        # Add modification record
        add_modification_record(
            "Save File",
            f"Saved converted code to file: {file_path}"
        )
    except Exception as e:
        status_var.set(f"Error saving file: {str(e)}")
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        
        # Add modification record for error
        add_modification_record(
            "File Save Error",
            f"Error saving file to {file_path}: {str(e)}"
        )

def save_object_file():
    """Saves converted code as an object file"""
    # Get content for object file
    title = "MSP430 Assembly Object File"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = f"{title}\nGenerated: {timestamp}\n\n"
    
    hex_content = hex_text.get("1.0", tk.END)
    
    # Prepare object file content
    obj_content = header + "MEMORY MAP:\n"
    obj_content += "======================\n"
    obj_content += "ADDRESS  : HEX VALUE\n"
    obj_content += "----------------------\n"
    obj_content += hex_content
    
    # Information section
    obj_content += "\nSYMBOL TABLE:\n"
    obj_content += "======================\n"
    
    # Add labels
    obj_content += "Labels:\n"
    for label, addr in labels.items():
        obj_content += f"{label:<20}: 0x{addr:04X}\n"
    
    # Add EQU constants
    obj_content += "\nConstants (EQU):\n"
    for const, value in symtab["equ"].items():
        obj_content += f"{const:<20}: {value}\n"
    
    # Call save dialog
    save_to_file_from_dialog(obj_content)
    
    # Add modification record
    add_modification_record(
        "Save Object File",
        "Saved assembly code as an object file with memory map and symbol table"
    )

def save_to_file_from_dialog(content):
    """Generic function to save content to file via dialog"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".obj",
        filetypes=[("Object files", "*.obj"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Save as Object File"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, "w") as file:
            file.write(content)
        
        status_var.set(f"File saved successfully: {file_path}")
    except Exception as e:
        status_var.set(f"Error saving file: {str(e)}")
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        
        # Add modification record for error
        add_modification_record(
            "File Save Error",
            f"Error saving file to {file_path}: {str(e)}"
        )

def on_hover(event):
    event.widget.config(bg="#ff7043")

def on_leave(event):
    event.widget.config(bg=BUTTON_COLOR)

def save_text_file():
    """Saves the input assembly code to a file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".asm",
        filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Assembly Code"
    )
    
    if not file_path:
        return
    
    try:
        # Get content from text widget
        assembly_content = input_text.get("1.0", tk.END)
        
        with open(file_path, "w") as file:
            file.write(assembly_content)
        
        status_var.set(f"Assembly file saved: {file_path}")
        
        # Add modification record
        add_modification_record(
            "Save Assembly File",
            f"Saved assembly source code to file: {file_path}"
        )
    except Exception as e:
        status_var.set(f"Error saving file: {str(e)}")
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        
        # Add modification record for error
        add_modification_record(
            "File Save Error",
            f"Error saving assembly file to {file_path}: {str(e)}"
        )

def open_file():
    """Opens a file for editing"""
    file_path = filedialog.askopenfilename(
        filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Open Assembly File"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, "r") as file:
            file_content = file.read()
        
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, file_content)
        
        # Trigger syntax highlighting
        highlight_syntax()
        
        status_var.set(f"File opened: {file_path}")
        
        # Add modification record
        add_modification_record(
            "Open File",
            f"Opened assembly file: {file_path}"
        )
    except Exception as e:
        status_var.set(f"Error opening file: {str(e)}")
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")
        
        # Add modification record for error
        add_modification_record(
            "File Open Error",
            f"Error opening file {file_path}: {str(e)}"
        )

def add_test_code():
    """Add a test code to the input text box"""
    test_code = """
; MSP430 Kapsamlı Test Kodu
; Bu örnek kod çeşitli komutları ve adres modlarını test eder

; Sabitler tanımlanırken doğru format "SYMBOL EQU VALUE" şeklinde olmalı
DATA_START   EQU 0x0200     ; Veri bölümü başlangıç adresi
RESULT_ADDR  EQU 0x0210     ; Sonuç adresi
RESULT_ADDR2 EQU 0x0212     ; İkinci sonuç adresi

        ORG 0xF800         ; Program başlangıç adresi

RESET:
        ; Stack Pointer ayarları
        MOV     #0x0400, SP        ; Stack pointer'ı ayarla
        
        ; Register temizleme
        MOV     #0, R4             ; R4 = 0
        MOV     #0, R5             ; R5 = 0
        MOV     #0, R6             ; R6 = 0
        MOV     #0, R7             ; R7 = 0
        
        ; Register yükleme ve transfer testleri
        MOV     #1234, R5          ; R5 = 1234 (decimal)
        MOV     #0x5A5A, R6        ; R6 = 5A5A (hex)
        MOV     R5, R7             ; R7 = R5
        MOV     R6, R8             ; R8 = R6
        
        ; Bellek erişim testleri
        MOV     #0xAAAA, &DATA_START     ; DATA_START adresine 0xAAAA yaz
        MOV     &DATA_START, R9          ; R9'a DATA_START adresinden oku
        
        ; İndeksli adres modu testi
        MOV     #DATA_START, R10         ; R10 = DATA_START
        MOV     #0x1111, 2(R10)          ; DATA_START+2 adresine 0x1111 yaz
        MOV     4(R10), R11              ; R11'e DATA_START+4 adresinden oku
        
        ; Aritmetik işlem testleri
        ADD     #10, R5            ; R5 += 10
        SUB     #5, R5             ; R5 -= 5
        INC     R4                 ; R4 += 1
        INCD    R5                 ; R5 += 2
        DEC     R6                 ; R6 -= 1
        DECD    R7                 ; R7 -= 2
        
        ; Mantıksal işlem testleri
        AND     #0x00FF, R6        ; R6 = R6 & 0x00FF (alt byte'ı koru)
        BIS     #0xFF00, R7        ; R7 = R7 | 0xFF00 (üst byte'ı 1 yap)
        BIC     #0x00FF, R8        ; R8 = R8 & ~0x00FF (alt byte'ı temizle)
        XOR     #0xFFFF, R9        ; R9 = R9 ^ 0xFFFF (tüm bitleri tersle)
        
        ; Döngü testi
LOOP:   
        CMP     #10, R4            ; R4 ile 10'u karşılaştır
        JGE     LOOP_END           ; R4 >= 10 ise LOOP_END'e git
        INC     R4                 ; R4 += 1
        JMP     LOOP               ; LOOP'a geri dön
        
LOOP_END:
        ; Karşılaştırma ve dallanma testleri
        CMP     #0x5A5A, R6        ; R6 ile 0x5A5A karşılaştır
        JEQ     IS_EQUAL           ; Eşitse IS_EQUAL'e git
        JMP     NOT_EQUAL          ; Eşit değilse NOT_EQUAL'e git
        
IS_EQUAL:
        MOV     #1, R12            ; R12 = 1 (eşit durumu)
        JMP     AFTER_CMP
        
NOT_EQUAL:
        MOV     #0, R12            ; R12 = 0 (eşit değil durumu)
        
AFTER_CMP:
        ; Alt rutin çağrı testi
        CALL    #SUBROUTINE        ; Alt rutini çağır
        
        ; İşlemlerin sonucunu kaydet
        MOV     R5, &RESULT_ADDR   ; Sonuç R5'i RESULT_ADDR adresine kaydet
        MOV     R6, &RESULT_ADDR2  ; Sonuç R6'yı RESULT_ADDR2 adresine kaydet
        
        ; Sonsuz döngü
FOREVER:
        JMP     FOREVER            ; Sonsuz döngü

; Alt rutin
SUBROUTINE:
        PUSH    R5                 ; R5'i stack'e kaydet
        PUSH    R6                 ; R6'yı stack'e kaydet
        
        MOV     #0xBEEF, R5        ; Test değeri
        MOV     #0xDEAD, R6        ; Test değeri
        
        ; İşlemler...
        ADD     R5, R6             ; R6 += R5
        MOV     R6, &RESULT_ADDR   ; Sonucu RESULT_ADDR adresine kaydet
        
        POP     R6                 ; R6'yı stack'ten geri al
        POP     R5                 ; R5'i stack'ten geri al
        RET                        ; Alt rutinden dön
"""
    
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, test_code)
    highlight_syntax()
    status_var.set("Test code added.")

def add_counter_code():
    """Add a counter code example to the input text box"""
    test_code = """
; MSP430 Register Örneği - Sayaç
; Bu örnek R5 registerında bir sayaç tutar ve her döngüde arttırır

    MOV #0, R5      ; R5 sayacını sıfırla
    
loop:
    INC R5          ; R5'i bir arttır
    MOV R5, R6      ; R5 değerini R6'ya kopyala  
    JMP loop        ; Sonsuz döngü
"""
    
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, test_code)
    highlight_syntax()
    status_var.set("Counter code added.")

def show_object_code():
    # ÖZEL SEKME SİSTEMİ - BUTONLAR İLE YAPILMIŞ
    hex_text.config(state=tk.NORMAL)
    hex_content = hex_text.get("1.0", tk.END).strip()
    hex_text.config(state=tk.DISABLED)

    if not hex_content:
        messagebox.showwarning("Warning", "You need to convert your code first!")
        return

    object_window = tk.Toplevel()
    object_window.title("MSP430 Object Code")
    object_window.geometry("800x600")
    object_window.configure(bg="#1e1e1e")
    
    title_label = tk.Label(object_window, text="MSP430 Object Code Output", font=("Impact", 16), bg="#1e1e1e", fg="#ffffff")
    title_label.pack(pady=10)
    
    info_label = tk.Label(object_window, text="MSP430 code sections in TI format", font=("Arial", 10), bg="#1e1e1e", fg="#aaaaaa")
    info_label.pack(pady=5)
    
    # Section colors
    section_colors = {
        ".TEXT": "#4a86e8",  # Blue for code
        ".DATA": "#6aa84f",  # Green for data 
        ".BSS": "#e69138",   # Orange for BSS
        ".INTVEC": "#9c27b0",    # Purple for interrupt vectors
    }
    
    # Default colors for custom sections
    custom_section_colors = [
        "#e91e63",    # Pink
        "#f44336",    # Red
        "#ff9800",    # Amber
        "#cddc39",    # Lime
        "#009688",    # Teal
        "#00bcd4",    # Cyan
    ]
    
    # Get section data or use backup approach
    if 'section_output_data' in globals():
        section_data = section_output_data
    else:
        # Fallback - parse hex content if section data not available
        section_data = {
            ".TEXT": [],
            ".DATA": [],
            ".BSS": []
        }
        # Default all to TEXT section
        for line in hex_content.splitlines():
            if ":" in line:
                addr_str, value = line.split(":", 1)
                addr = int(addr_str.strip(), 16)
                value = value.strip()
                section_data[".TEXT"].append((addr, value, ""))

    # Assign colors to custom sections
    custom_color_index = 0
    for section_name in section_data.keys():
        if section_name not in section_colors:
            section_colors[section_name] = custom_section_colors[custom_color_index % len(custom_section_colors)]
            custom_color_index += 1
    
    # Sekme butonları için çerçeve
    tab_buttons_frame = tk.Frame(object_window, bg="#1e1e1e")
    tab_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # İçerik gösterme alanı
    content_frame = tk.Frame(object_window, bg="#121212")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Tüm bölüm içeriklerini tutacak sözlük
    section_frames = {}
    
    # Tüm verileri toplama ve sıralama
    all_data = []
    for section_name, data_list in section_data.items():
        for item in data_list:
            all_data.append((section_name, item))
    
    all_data.sort(key=lambda x: x[1][0])
    
    # Aktif sekme takibi için değişken
    active_tab = tk.StringVar(value="Combined View")
    
    # Combined View içeriği oluştur
    combined_frame = tk.Frame(content_frame, bg="#121212")
    section_frames["Combined View"] = combined_frame
    
    combined_content = scrolledtext.ScrolledText(
        combined_frame, 
        wrap=tk.WORD, 
        font=("Courier New", 11), 
        bg="#121212", 
        fg="#ffffff", 
        height=20, 
        borderwidth=0, 
        relief=tk.FLAT
    )
    combined_content.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Combined View içeriği oluştur
    if all_data:
        first_addr = all_data[0][1][0]
        combined_txt = []
        
        # Başlangıç adresini @ ile belirt
        combined_txt.append(f"@{first_addr:04X}")
        
        # Her değeri yeni satırda göster
        for _, (_, value, _) in all_data:
            combined_txt.append(value)
        
        # Dosya sonunu "q" ile işaretle
        combined_txt.append("q")
        
        combined_content.insert(tk.END, "\n".join(combined_txt))
        combined_content.config(state=tk.DISABLED)
    
    # Diğer bölüm içeriklerini oluştur
    for section_name, data_list in section_data.items():
        if not data_list:
            continue
            
        # Özel bölüm adlarını düzenle (.SECT_ önekini kaldır)
        display_name = section_name
        if section_name.startswith(".SECT_"):
            display_name = section_name[6:]  # .SECT_ önekini kaldır
            
        # Bölüm çerçevesi
        section_frame = tk.Frame(content_frame, bg="#121212")
        section_frames[display_name] = section_frame
        
        # Bölüm başlığı
        section_header = tk.Label(
            section_frame, 
            text=f"{display_name} SECTION", 
            font=("Arial", 12, "bold"), 
            bg="#121212", 
            fg=section_colors.get(section_name, "#ffffff")
        )
        section_header.pack(anchor="w", pady=(10, 10), padx=10)
        
        # Bölüm içeriği
        content = scrolledtext.ScrolledText(
            section_frame, 
            wrap=tk.WORD, 
            font=("Courier New", 11), 
            bg="#121212", 
            fg="#ffffff", 
            height=18, 
            borderwidth=0, 
            relief=tk.FLAT
        )
        content.pack(fill="both", expand=True, padx=10)
        
        # Verileri adrese göre sırala
        data_list.sort(key=lambda x: x[0])
        
        # İçeriği oluştur
        ti_txt_content = []
        ti_txt_content.append(f"===== {display_name} SECTION =====")
        ti_txt_content.append("")
        
        for addr, hex_val, _ in data_list:
            ti_txt_content.append(f"{addr:04X}: {hex_val}")
        
        content.insert(tk.END, "\n".join(ti_txt_content))
        content.config(state=tk.DISABLED)
        
        # Bölüm özeti
        if data_list:
            section_summary = tk.Label(
                section_frame, 
                text=f"Total bytes: {len(data_list) * 2 if section_name != '.BSS' else len(data_list)} | Addresses: {data_list[0][0]:04X}-{data_list[-1][0]:04X}", 
                font=("Arial", 10), 
                bg="#121212", 
                fg="#aaaaaa"
            )
            section_summary.pack(anchor="w", pady=(5, 10), padx=10)
    
    # Sekme değiştirme fonksiyonu
    def change_tab(tab_name):
        # Mevcut aktif sekmeyi gizle
        for frame in section_frames.values():
            frame.pack_forget()
        
        # Yeni sekmeyi göster
        if tab_name in section_frames:
            section_frames[tab_name].pack(fill=tk.BOTH, expand=True)
            active_tab.set(tab_name)
            
            # Aktif butonun stilini güncelle
            for btn in tab_buttons:
                if btn["text"] == tab_name:
                    btn.config(bg="#3a3a3a", fg="#ffffff", relief=tk.SUNKEN)
                else:
                    btn.config(bg="#2d2d2d", fg="#cccccc", relief=tk.RAISED)
    
    # Sekme butonlarını oluştur
    tab_buttons = []
    
    # Önce Combined View butonu
    combined_btn = tk.Button(
        tab_buttons_frame, 
        text="Combined View", 
        bg="#3a3a3a",  # Başlangıçta aktif
        fg="#ffffff", 
        font=("Arial", 10, "bold"), 
        padx=15, 
        pady=5, 
        relief=tk.SUNKEN,
        command=lambda: change_tab("Combined View")
    )
    combined_btn.pack(side=tk.LEFT, padx=2)
    tab_buttons.append(combined_btn)
    
    # Diğer bölüm butonları
    for section_name in section_data.keys():
        if not section_data[section_name]:
            continue
            
        display_name = section_name
        if section_name.startswith(".SECT_"):
            display_name = section_name[6:]
                
        section_btn = tk.Button(
            tab_buttons_frame, 
            text=display_name, 
            bg="#2d2d2d", 
            fg="#cccccc", 
            font=("Arial", 10), 
            padx=15, 
            pady=5,
            relief=tk.RAISED,
            command=lambda name=display_name: change_tab(name)
        )
        section_btn.pack(side=tk.LEFT, padx=2)
        tab_buttons.append(section_btn)
    
    # İlk sekmeyi göster
    change_tab("Combined View")
    
    # Alt kısımdaki butonlar
    button_frame = tk.Frame(object_window, bg="#1e1e1e")
    button_frame.pack(fill=tk.X, padx=15, pady=10)
    
    save_button = tk.Button(
        button_frame, 
        text="Save to File", 
        font=("Arial", 10), 
        bg="#ff5722", 
        fg="#ffffff", 
        padx=10, 
        pady=5, 
        command=lambda: save_to_file_from_dialog(combined_content.get("1.0", tk.END))
    )
    save_button.pack(side=tk.LEFT, padx=5)
    
    close_button = tk.Button(
        button_frame, 
        text="Close", 
        font=("Arial", 10), 
        bg="#2d2d2d", 
        fg="#ffffff", 
        padx=10, 
        pady=5, 
        command=object_window.destroy
    )
    close_button.pack(side=tk.LEFT, padx=5)

def show_memory_viewer():
    """Show memory viewer window"""
    global memory_viewer_window, memory_text
    
    memory_viewer_window = tk.Toplevel()
    memory_viewer_window.title("Memory Viewer")
    memory_viewer_window.geometry("800x600")
    memory_viewer_window.configure(bg=BG_COLOR)
    
    # Title
    title_label = tk.Label(memory_viewer_window,
                          text="Memory Viewer",
                          font=("Impact", 16),
                          bg=BG_COLOR,
                          fg=HEADER_COLOR)
    title_label.pack(pady=10)
    
    # Top menu frame
    top_frame = tk.Frame(memory_viewer_window, bg=BG_COLOR)
    top_frame.pack(fill=tk.X, padx=15, pady=5)
    
    # Address label and entry
    addr_label = tk.Label(top_frame, text="Address:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 11))
    addr_label.pack(side=tk.LEFT, padx=(0, 5))
    
    addr_entry = tk.Entry(top_frame, width=10, bg=TEXTBOX_BG, fg=TEXT_COLOR, font=("Courier New", 11))
    addr_entry.pack(side=tk.LEFT, padx=(0, 10))
    addr_entry.insert(0, "0000")
    
    # Go button
    go_button = tk.Button(top_frame, text="Go", bg=BUTTON_COLOR, fg=BUTTON_TEXT, font=("Arial", 10),
                         command=lambda: show_memory_at_address(addr_entry.get(), memory_text))
    go_button.pack(side=tk.LEFT, padx=5)
    
    # Refresh button
    refresh_button = tk.Button(top_frame, text="Refresh", bg=BUTTON_COLOR, fg=BUTTON_TEXT, font=("Arial", 10),
                              command=lambda: refresh_memory(memory_text))
    refresh_button.pack(side=tk.LEFT, padx=5)
    
    # Address format
    format_label = tk.Label(top_frame, text="Format:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 11))
    format_label.pack(side=tk.LEFT, padx=(20, 5))
    
    format_var = tk.StringVar(value="HEX")
    hex_radio = tk.Radiobutton(top_frame, text="Hex", variable=format_var, value="HEX", 
                              bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INFO_BG,
                              command=lambda: change_format(format_var.get(), memory_text))
    hex_radio.pack(side=tk.LEFT)
    
    dec_radio = tk.Radiobutton(top_frame, text="Decimal", variable=format_var, value="DEC", 
                              bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INFO_BG,
                              command=lambda: change_format(format_var.get(), memory_text))
    dec_radio.pack(side=tk.LEFT)
    
    bin_radio = tk.Radiobutton(top_frame, text="Binary", variable=format_var, value="BIN", 
                              bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INFO_BG,
                              command=lambda: change_format(format_var.get(), memory_text))
    bin_radio.pack(side=tk.LEFT)
    
    # Memory status
    status_frame = tk.Frame(memory_viewer_window, bg=INFO_BG)
    status_frame.pack(fill=tk.X, padx=15, pady=5)
    
    status_label = tk.Label(status_frame, text="Memory Status: Simulation Mode", 
                           bg=INFO_BG, fg=TEXT_COLOR, font=("Arial", 10))
    status_label.pack(side=tk.LEFT, padx=10)
    
    # Memory content - editable text area
    memory_text = scrolledtext.ScrolledText(memory_viewer_window,
                                          wrap=tk.WORD,
                                          font=("Courier New", 11),
                                          bg=TEXTBOX_BG,
                                          fg=TEXT_COLOR,
                                          height=25)
    memory_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Create memory content - starting at 0x0000
    for addr in range(0, 0x1000):
        if addr not in memory_values:
            memory_values[addr] = 0x00
    
    # Show initial values
    update_memory_display(memory_text, 0x0000, memory_values, "HEX")
    
    # Capture edit event
    memory_text.bind("<KeyRelease>", lambda e: parse_memory_edits(memory_text, memory_values))
    
    # Bottom frame - buttons
    bottom_frame = tk.Frame(memory_viewer_window, bg=BG_COLOR)
    bottom_frame.pack(fill=tk.X, padx=15, pady=10)
    
    # Load button
    load_button = tk.Button(bottom_frame, text="Load Memory File", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                           font=("Arial", 10), command=lambda: load_memory_file(memory_text, memory_values))
    load_button.pack(side=tk.LEFT, padx=5)
    
    # Save button
    save_button = tk.Button(bottom_frame, text="Save Memory File", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                           font=("Arial", 10), command=lambda: save_memory_file(memory_values))
    save_button.pack(side=tk.LEFT, padx=5)
    
    # Fill memory button
    fill_button = tk.Button(bottom_frame, text="Fill Address Range", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                           font=("Arial", 10), command=lambda: show_fill_dialog(memory_text, memory_values))
    fill_button.pack(side=tk.LEFT, padx=5)

def update_memory_display(text_widget, start_addr, memory_values, format_type="HEX"):
    """Display memory contents"""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    lines = []
    for base_addr in range(start_addr, start_addr + 0x100, 16):
        if format_type == "HEX":
            line = f"{base_addr:04X}: "
            ascii_chars = ""
            
            for offset in range(16):
                addr = base_addr + offset
                value = memory_values.get(addr, 0)
                line += f"{value:02X} "
                
                # Add ASCII character (for printable ones)
                if 32 <= value <= 126:
                    ascii_chars += chr(value)
                else:
                    ascii_chars += "."
            
            line += "  |" + ascii_chars + "|"
            lines.append(line)
            
        elif format_type == "DEC":
            line = f"{base_addr:04d}: "
            for offset in range(16):
                addr = base_addr + offset
                value = memory_values.get(addr, 0)
                line += f"{value:3d} "
            lines.append(line)
            
        elif format_type == "BIN":
            for offset in range(0, 16, 4):  # 4 values per line (due to line length)
                addr = base_addr + offset
                line = f"{addr:04X}: "
                for i in range(4):
                    value = memory_values.get(addr + i, 0)
                    line += f"{value:08b} "
                lines.append(line)
    
    text_widget.insert(tk.END, "\n".join(lines))
    text_widget.config(state=tk.NORMAL)  # Editing enabled
def show_memory_at_address(addr_str, text_widget):
    """Show memory content from the specified address"""
    try:
        # Process hex or decimal address
        if addr_str.lower().startswith("0x"):
            addr = int(addr_str, 16)
        else:
            addr = int(addr_str, 0)
        
        # Ensure address is a multiple of 16 (for line start)
        addr = addr & 0xFFF0
        
        # Update address and refresh display
        update_memory_display(text_widget, addr, memory_values, current_format)
    except ValueError:
        messagebox.showerror("Error", f"Invalid address format: {addr_str}")

def refresh_memory(text_widget):
    """Refresh the memory display"""
    global current_format, addr_entry, start_label, status_label, memory_values
    
    # Get start address from entry - yorumla decimal olarak
    try:
        start_addr = int(addr_entry.get(), 10)  # 16 yerine 10 kullanarak decimal olarak yorumla
    except ValueError:
        start_addr = 0
        addr_entry.delete(0, tk.END)
        addr_entry.insert(0, "0000")
    
    # Update memory display with current format
    update_memory_display(text_widget, start_addr, memory_values, current_format)
    
    # Update status message
    if start_label:
        start_label.config(text=f"Start: 0x{start_addr:04X}")
    if status_label:
        status_label.config(text=f"Memory view refreshed. Format: {current_format}")

def change_format(format_type, text_widget):
    """Change display format"""
    global current_format
    current_format = format_type
    
    # Get the current top address
    first_line = text_widget.get("1.0", "1.end")
    addr_str = first_line.split(":")[0]
    
    try:
        if current_format == "HEX":
            addr = int(addr_str, 16)
        else:
            addr = int(addr_str, 0)
        
        update_memory_display(text_widget, addr, memory_values, current_format)
    except:
        update_memory_display(text_widget, 0, memory_values, current_format)

def parse_memory_edits(text_widget, memory_values):
    """Parse and apply memory edits from the text widget"""
    try:
        content = text_widget.get("1.0", tk.END)
        lines = content.strip().split('\n')
        edited_values = []
        
        for line in lines:
            if ":" not in line:
                continue
                
            addr_str, value_str = line.split(":", 1)
            addr = int(addr_str.strip(), 16)
            
            if current_format == "HEX":
                # Format: ADDR: XX XX or ADDR: XXXX
                hex_values = value_str.strip().split()
                if len(hex_values) == 1:
                    # Word format (XXXX)
                    value = int(hex_values[0], 16)
                    memory_values[addr] = value
                    edited_values.append((addr, value))
                else:
                    # Byte format (XX XX)
                    for i, hex_val in enumerate(hex_values):
                        byte_addr = addr + i
                        byte_val = int(hex_val, 16) & 0xFF
                        memory_values[byte_addr] = byte_val
                        edited_values.append((byte_addr, byte_val))
            
            elif current_format == "BIN":
                # Format: ADDR: XXXXXXXX or ADDR: XXXXXXXXXXXXXXXX
                bin_values = value_str.strip().split()
                if len(bin_values) == 1:
                    if len(bin_values[0]) <= 8:
                        # Byte format
                        value = int(bin_values[0], 2) & 0xFF
                        memory_values[addr] = value
                        edited_values.append((addr, value))
                    else:
                        # Word format
                        value = int(bin_values[0], 2) & 0xFFFF
                        memory_values[addr] = value
                        edited_values.append((addr, value))
        
        # Log memory edits in modification record
        if edited_values:
            edit_details = f"Modified {len(edited_values)} memory locations:\n"
            for addr, value in edited_values[:5]:  # Show first 5 edits max
                edit_details += f"- 0x{addr:04X}: 0x{value:04X}\n"
            
            if len(edited_values) > 5:
                edit_details += f"...and {len(edited_values) - 5} more locations"
            
            add_modification_record(
                "Memory Edit",
                edit_details
            )
            
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse memory edits: {str(e)}")
        print(f"Error parsing memory edits: {str(e)}")
        
        # Log error
        add_modification_record(
            "Memory Edit Error",
            f"Error while editing memory: {str(e)}"
        )
        
        return False

def load_memory_file(text_widget, memory_values):
    """Load memory values from a file"""
    file_path = filedialog.askopenfilename(
        filetypes=[("Memory files", "*.mem"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Load Memory File"
    )
    
    if not file_path:
        return
    
    try:
        loaded_values = []
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):  # Skip comments and empty lines
                    continue
                
                if ":" in line:
                    addr_str, value_str = line.split(":", 1)
                    addr = int(addr_str.strip(), 16)
                    
                    # Try to parse hex values
                    try:
                        for i, hex_val in enumerate(value_str.strip().split()):
                            byte_addr = addr + i
                            byte_val = int(hex_val, 16) & 0xFF
                            memory_values[byte_addr] = byte_val
                            loaded_values.append((byte_addr, byte_val))
                    except ValueError:
                        # If hex parsing fails, try binary
                        for i, bin_val in enumerate(value_str.strip().split()):
                            byte_addr = addr + i
                            byte_val = int(bin_val, 2) & 0xFF
                            memory_values[byte_addr] = byte_val
                            loaded_values.append((byte_addr, byte_val))
        
        # Refresh the memory display
        refresh_memory(text_widget)
        
        # Log memory load in modification record
        add_modification_record(
            "Memory Load",
            f"Loaded memory file: {file_path}\nLoaded {len(loaded_values)} values"
        )
        
        messagebox.showinfo("Success", f"Memory file loaded: {len(loaded_values)} values")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load memory file: {str(e)}")
        
        # Log error
        add_modification_record(
            "Memory Load Error",
            f"Error loading memory file {file_path}: {str(e)}"
        )

def save_memory_file(memory_values):
    """Save memory values to a file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".mem",
        filetypes=[("Memory files", "*.mem"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Memory File"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, "w") as file:
            file.write("# MSP430 Memory Values\n")
            file.write("# Format: ADDRESS: VALUE\n")
            file.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Sort addresses for clean output
            addresses = sorted(memory_values.keys())
            saved_count = 0
            
            for addr in addresses:
                value = memory_values[addr]
                
                # Only write non-zero values to keep file size reasonable
                if value != 0:
                    file.write(f"{addr:04X}: {value:02X}\n")
                    saved_count += 1
            
        # Log memory save in modification record
        add_modification_record(
            "Memory Save",
            f"Saved memory to file: {file_path}\nSaved {saved_count} values"
        )
        
        messagebox.showinfo("Success", f"Memory saved to: {file_path}\n{saved_count} values written")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save memory file: {str(e)}")
        
        # Log error
        add_modification_record(
            "Memory Save Error",
            f"Error saving memory to {file_path}: {str(e)}"
        )

def show_fill_dialog(text_widget, memory_values):
    """Memory range fill dialog"""
    fill_window = tk.Toplevel()
    fill_window.title("Fill Memory Range")
    fill_window.geometry("400x200")
    fill_window.configure(bg=BG_COLOR)
    
    # Frame
    frame = tk.Frame(fill_window, bg=BG_COLOR, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Start address
    start_label = tk.Label(frame, text="Start Address (Hex):", bg=BG_COLOR, fg=TEXT_COLOR)
    start_label.grid(row=0, column=0, sticky="w", pady=5)
    
    start_entry = tk.Entry(frame, bg=TEXTBOX_BG, fg=TEXT_COLOR)
    start_entry.grid(row=0, column=1, sticky="ew", pady=5)
    start_entry.insert(0, "0000")
    
    # End address
    end_label = tk.Label(frame, text="End Address (Hex):", bg=BG_COLOR, fg=TEXT_COLOR)
    end_label.grid(row=1, column=0, sticky="w", pady=5)
    
    end_entry = tk.Entry(frame, bg=TEXTBOX_BG, fg=TEXT_COLOR)
    end_entry.grid(row=1, column=1, sticky="ew", pady=5)
    end_entry.insert(0, "000F")
    
    # Value
    value_label = tk.Label(frame, text="Value (Hex):", bg=BG_COLOR, fg=TEXT_COLOR)
    value_label.grid(row=2, column=0, sticky="w", pady=5)
    
    value_entry = tk.Entry(frame, bg=TEXTBOX_BG, fg=TEXT_COLOR)
    value_entry.grid(row=2, column=1, sticky="ew", pady=5)
    value_entry.insert(0, "00")
    
    # Buttons
    button_frame = tk.Frame(frame, bg=BG_COLOR)
    button_frame.grid(row=3, column=0, columnspan=2, pady=15)
    
    cancel_button = tk.Button(button_frame, text="Cancel", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                             command=fill_window.destroy)
    cancel_button.grid(row=0, column=0, padx=5)
    
    ok_button = tk.Button(button_frame, text="OK", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                         command=lambda: fill_memory_range(
                             start_entry.get(), end_entry.get(), value_entry.get(), 
                             text_widget, memory_values, fill_window))
    ok_button.grid(row=0, column=1, padx=5)

def fill_memory_range(start_str, end_str, value_str, text_widget, memory_values, dialog):
    """Fill a range of memory with a specific value"""
    try:
        start_addr = int(start_str, 16)
        end_addr = int(end_str, 16)
        
        if start_addr > end_addr:
            messagebox.showerror("Error", "Start address must be less than or equal to end address")
            return
        
        value = int(value_str, 16) & 0xFF  # Limit to byte value
        
        # Fill memory range
        for addr in range(start_addr, end_addr + 1):
            memory_values[addr] = value
        
        # Log memory fill in modification record
        add_modification_record(
            "Memory Fill",
            f"Filled memory range 0x{start_addr:04X} to 0x{end_addr:04X} with value 0x{value:02X}"
        )
        
        # Close dialog and refresh display
        dialog.destroy()
        refresh_memory(text_widget)
        
    except ValueError:
        messagebox.showerror("Error", "Invalid hexadecimal value")
    except Exception as e:
        messagebox.showerror("Error", f"Error filling memory: {str(e)}")
        
        # Log error
        add_modification_record(
            "Memory Fill Error",
            f"Error filling memory range: {str(e)}"
        )

def show_register_viewer():
    """Opens the register status viewer window"""
    register_window = tk.Toplevel()
    register_window.title("Register State")
    register_window.geometry("400x500")
    register_window.configure(bg=BG_COLOR)
    
    # Title
    title_label = tk.Label(register_window,
                          text="Register State",
                          font=("Impact", 16),
                          bg=BG_COLOR,
                          fg=HEADER_COLOR)
    title_label.pack(pady=10)
    
    # Top menu frame
    top_frame = tk.Frame(register_window, bg=BG_COLOR)
    top_frame.pack(fill=tk.X, padx=15, pady=5)
    
    # Save/Load buttons
    save_regs_button = tk.Button(top_frame, text="Save", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                               font=("Arial", 10), command=lambda: save_registers(reg_entries))
    save_regs_button.pack(side=tk.LEFT, padx=5)
    
    load_regs_button = tk.Button(top_frame, text="Load", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                               font=("Arial", 10), command=lambda: load_registers(reg_entries))
    load_regs_button.pack(side=tk.LEFT, padx=5)
    
    reset_regs_button = tk.Button(top_frame, text="Reset", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                                font=("Arial", 10), command=lambda: reset_registers(reg_entries))
    reset_regs_button.pack(side=tk.LEFT, padx=5)
    
    # Format selection
    format_label = tk.Label(top_frame, text="Format:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 11))
    format_label.pack(side=tk.LEFT, padx=(20, 5))
    
    format_var = tk.StringVar(value="HEX")
    hex_radio = tk.Radiobutton(top_frame, text="Hex", variable=format_var, value="HEX", 
                              bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INFO_BG,
                              command=lambda: update_register_format(format_var.get(), reg_entries))
    hex_radio.pack(side=tk.LEFT)
    
    dec_radio = tk.Radiobutton(top_frame, text="Decimal", variable=format_var, value="DEC", 
                              bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INFO_BG,
                              command=lambda: update_register_format(format_var.get(), reg_entries))
    dec_radio.pack(side=tk.LEFT)
    
    # Register frame
    register_frame = tk.Frame(register_window, bg=BG_COLOR)
    register_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Register values and entry fields
    registers = [
        ("R0 (PC)", "Program Counter"),
        ("R1 (SP)", "Stack Pointer"),
        ("R2 (SR)", "Status Register"),
        ("R3 (CG)", "Constant Generator"),
        ("R4", "General Purpose"),
        ("R5", "General Purpose"),
        ("R6", "General Purpose"),
        ("R7", "General Purpose"),
        ("R8", "General Purpose"),
        ("R9", "General Purpose"),
        ("R10", "General Purpose"),
        ("R11", "General Purpose"),
        ("R12", "General Purpose"),
        ("R13", "General Purpose"),
        ("R14", "General Purpose"),
        ("R15", "General Purpose")
    ]
    
    reg_entries = {}
    
    # Header row
    header_frame = tk.Frame(register_frame, bg=INFO_BG)
    header_frame.pack(fill=tk.X, pady=5)
    
    header_name = tk.Label(header_frame, text="Register", font=("Arial", 11, "bold"), 
                         bg=INFO_BG, fg=TEXT_COLOR, width=10, anchor="w")
    header_name.pack(side=tk.LEFT, padx=5)
    
    header_value = tk.Label(header_frame, text="Value", font=("Arial", 11, "bold"), 
                          bg=INFO_BG, fg=TEXT_COLOR, width=8, anchor="w")
    header_value.pack(side=tk.LEFT, padx=5)
    
    header_desc = tk.Label(header_frame, text="Description", font=("Arial", 11, "bold"), 
                         bg=INFO_BG, fg=TEXT_COLOR, anchor="w")
    header_desc.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    # Register rows
    for i, (reg_name, desc) in enumerate(registers):
        frame = tk.Frame(register_frame, bg=BG_COLOR)
        frame.pack(fill=tk.X, pady=2)
        
        # Register name
        name_label = tk.Label(frame,
                            text=reg_name,
                            font=("Arial", 11),
                            bg=BG_COLOR,
                            fg=TEXT_COLOR,
                            width=10,
                            anchor="w")
        name_label.pack(side=tk.LEFT, padx=5)
        
        # Register value (editable)
        value_entry = tk.Entry(frame,
                             font=("Courier New", 11),
                             bg=TEXTBOX_BG,
                             fg=TEXT_COLOR,
                             width=8)
        value_entry.pack(side=tk.LEFT, padx=5)
        
        # Register değerini göster
        # R5 gibi register adını çıkar
        reg_num = reg_name.split()[0][1:] if "(" in reg_name else reg_name[1:]
        try:
            # Sadece sayısal register numaralarını işle
            if reg_num.isdigit():
                value = register_values.get(reg_num, 0)
                value_entry.delete(0, tk.END)
                if format_var.get() == "HEX":
                    value_entry.insert(0, f"{value:04X}")
                else:
                    value_entry.insert(0, str(value))
            else:
                value_entry.insert(0, "0000")
        except:
            value_entry.insert(0, "0000")
            
        value_entry.bind("<FocusOut>", lambda e, name=reg_name, entry=value_entry: validate_register_value(name, entry, format_var.get(), status_label))
        
        # Register description
        desc_label = tk.Label(frame,
                            text=desc,
                            font=("Arial", 10),
                            bg=BG_COLOR,
                            fg=TEXT_COLOR)
        desc_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Add to register list
        reg_entries[reg_name] = value_entry
    
    # Status bar
    status_frame = tk.Frame(register_window, bg=INFO_BG)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_label = tk.Label(status_frame, text="SR(R2) Flags: [ ] C [ ] Z [ ] N [ ] V", 
                           bg=INFO_BG, fg=TEXT_COLOR, font=("Arial", 10))
    status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    # Update flags when SR value changes
    reg_entries["R2 (SR)"].bind("<KeyRelease>", lambda e: update_status_flags(status_label, reg_entries["R2 (SR)"].get()))
    
    # Info panel
    info_frame = tk.Frame(register_window, bg=INFO_BG)
    info_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    info_text = tk.Label(info_frame, 
                        text="Click to edit values. You can enter Hex (0xNNNN, NNNN, NNNNh) or decimal (NNN) format.",
                        bg=INFO_BG, fg=TEXT_COLOR, font=("Arial", 9), wraplength=380, justify=tk.LEFT)
    info_text.pack(padx=10, pady=5)
    
    # SR bayraklarını güncelle - SR değerini R2 registerından al
    sr_value = register_values.get("2", 0)
    update_status_flags(status_label, f"{sr_value:04X}")

def validate_register_value(reg_name, entry, format_type, status_label):
    """Validate and update register value"""
    global register_values
    
    try:
        value_str = entry.get()
        
        if not value_str:
            status_label.config(text="Error: Value cannot be empty")
            return False
        
        # Register numarasını al
        reg_num = reg_name.split()[0][1:] if "(" in reg_name else reg_name[1:]
        
        if format_type == "HEX":
            # Remove 0x prefix if present
            if value_str.startswith("0x"):
                value_str = value_str[2:]
            # Remove 'h' suffix if present
            if value_str.lower().endswith("h"):
                value_str = value_str[:-1]
            value = int(value_str, 16)
        else:  # DEC
            value = int(value_str)
        
        # Ensure value fits in register (16-bit)
        value = value & 0xFFFF
        
        # Update the display with formatted value
        entry.delete(0, tk.END)
        if format_type == "HEX":
            entry.insert(0, f"{value:04X}")
        else:
            entry.insert(0, str(value))
            
        # Update the register value in our global dictionary
        if reg_num.isdigit():
            register_values[reg_num] = value
            
        # Update status
        status_label.config(text=f"Updated {reg_name} to {value:04X}h")
        
        # Special handling for SR register (R2)
        if reg_num == "2":
            update_status_flags(status_label, f"{value:04X}")
        
        return True
        
    except ValueError:
        status_label.config(text=f"Error: Invalid {format_type} value")
        return False
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")
        return False

def update_register_format(format_type, entries):
    """Convert register values to specified format"""
    for reg_name, entry in entries.items():
        try:
            # Register numarasını al
            reg_num = reg_name.split()[0][1:] if "(" in reg_name else reg_name[1:]
            
            if not reg_num.isdigit():
                continue
                
            # Register değerini al
            value = register_values.get(reg_num, 0)
            
            # Değeri belirtilen formatta göster
            entry.delete(0, tk.END)
            if format_type == "HEX":
                entry.insert(0, f"{value:04X}")
            else:  # DEC
                entry.insert(0, str(value))
                
        except Exception as e:
            print(f"Format update error: {str(e)}")

def update_status_flags(label, sr_value):
    """Update status register flags display"""
    try:
        # Convert the SR value to integer
        if isinstance(sr_value, str):
            if sr_value.startswith("0x"):
                sr_value = int(sr_value[2:], 16)
            elif sr_value.lower().endswith("h"):
                sr_value = int(sr_value[:-1], 16)
            else:
                try:
                    sr_value = int(sr_value, 16)  # First try as hex
                except ValueError:
                    sr_value = int(sr_value)  # Then as decimal
        
        # Extract flag bits
        c_flag = (sr_value & 0x0001) != 0  # Carry flag (bit 0)
        z_flag = (sr_value & 0x0002) != 0  # Zero flag (bit 1)
        n_flag = (sr_value & 0x0004) != 0  # Negative flag (bit 2)
        v_flag = (sr_value & 0x0100) != 0  # Overflow flag (bit 8)
        
        # Update the status label
        flags_text = f"SR(R2) Flags: {'[X]' if c_flag else '[ ]'} C {'[X]' if z_flag else '[ ]'} Z {'[X]' if n_flag else '[ ]'} N {'[X]' if v_flag else '[ ]'} V"
        label.config(text=flags_text)
    except Exception as e:
        label.config(text=f"SR(R2) Flags: [ ] C [ ] Z [ ] N [ ] V - Error: {str(e)}")

def save_registers(entries):
    """Save register values to a file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".reg",
        filetypes=[("Register files", "*.reg"), ("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not file_path:
        return
        
    try:
        with open(file_path, 'w') as file:
            for reg_name, entry in entries.items():
                # Register numarasını al
                reg_num = reg_name.split()[0][1:] if "(" in reg_name else reg_name[1:]
                
                if not reg_num.isdigit():
                    continue
                    
                # Değeri al
                value = register_values.get(reg_num, 0)
                
                # Dosyaya yaz
                file.write(f"{reg_name}={value:04X}\n")
        
        messagebox.showinfo("Info", f"Register values saved to: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def load_registers(entries):
    """Load register values from a file"""
    file_path = filedialog.askopenfilename(
        filetypes=[("Register files", "*.reg"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Load Register Values"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):  # Skip comments and empty lines
                    continue
                
                if "=" in line:
                    reg_str, value_str = line.split("=", 1)
                    reg_str = reg_str.strip()
                    value_str = value_str.strip()
                    
                    # Register değerini çıkar (R5 -> 5)
                    reg_name = reg_str
                    if reg_str.startswith("R") and "(" not in reg_str:
                        reg_num = reg_str[1:]
                    elif "(" in reg_str:
                        reg_num = reg_str.split()[0][1:]
                    else:
                        continue
                        
                    if not reg_num.isdigit():
                        continue
                        
                    # Değeri hex olarak oku
                    try:
                        if value_str.startswith("0x"):
                            value = int(value_str[2:], 16)
                        elif value_str.lower().endswith("h"):
                            value = int(value_str[:-1], 16)
                        else:
                            try:
                                value = int(value_str, 16)  # İlk hex olarak dene
                            except ValueError:
                                value = int(value_str)  # Sonra decimal olarak
                                
                        # Register değerini güncelle
                        register_values[reg_num] = value & 0xFFFF
                        
                        # Görüntülenen değeri güncelle
                        if reg_name in entries:
                            entries[reg_name].delete(0, tk.END)
                            entries[reg_name].insert(0, f"{value:04X}")
                    except ValueError:
                        continue
                        
        messagebox.showinfo("Info", f"Register values loaded from: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {str(e)}")

def reset_registers(entries):
    """Reset all register values to zero"""
    global register_values
    
    # Tüm register değerlerini sıfırla
    register_values = {f"{i}": 0 for i in range(16)}
    
    # Görüntülenen değerleri güncelle
    for entry in entries.values():
        entry.delete(0, tk.END)
        entry.insert(0, "0000")
        
    messagebox.showinfo("Info", "All register values have been reset to zero.")

def create_gui():
    """Create the main GUI window"""
    global root, input_text, output_text, status_label, examples_menu
    
    """Creates GUI components"""
    global root, input_text, hex_text, binary_text
    global convert_button, clear_button, load_button, save_button
    global status_var, status_bar, title_label, input_label
    global info_panel, info_label, hex_label, binary_label
    
    # Main window
    root = tk.Tk()
    root.title("MSP430 Assembly Converter")
    root.geometry("1200x800")
    root.configure(bg=BG_COLOR)
    
    # Status bar variable
    status_var = tk.StringVar()
    status_var.set("Ready")
    
    # Menu bar
    menu_bar = tk.Menu(root)
    
    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_text_file)
    file_menu.add_command(label="Save as Object File", command=save_object_file)
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # View menu
    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(label="Memory Viewer", command=show_memory_viewer)
    view_menu.add_command(label="Register State", command=show_register_viewer)
    view_menu.add_command(label="Command Reference Guide", command=show_command_reference)
    
    view_menu.add_command(label="SIC/XE Modification Records", command=show_modification_records_window)
    view_menu.add_command(label="Sensor Interface", command=show_sensor_interface)
    view_menu.add_command(label="Symbol Table", command=show_symtab_window)
    menu_bar.add_cascade(label="View", menu=view_menu)
    
    # Yardım menüsü (Help Menu)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Command Reference", command=show_command_reference)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "MSP430 Assembly Converter v2\nCopyright © 2025"))
    menu_bar.add_cascade(label="Help", menu=help_menu)
    
    # Donanım Menüsü Entegrasyonu (Hardware Menu Integration)
    try:
        msp430_integration.integrate_hardware_interface(root, menu_bar)
    except Exception as e:
        print(f"Donanım entegrasyonu yüklenirken hata: {str(e)}")
    
    # Enable menu
    root.config(menu=menu_bar)

    # Eye-catching fonts
    title_font = ("Impact", 20)             # Title font
    heading_font = ("Verdana", 11)          # Sub-headings
    button_font = ("Arial", 11)             # Button text
    code_font = ("Courier New", 11)         # Monospace code font

# Title
    title_label = tk.Label(root, 
                          text="MSP430 Assembly Converter",
                          font=title_font,
                          bg=BG_COLOR,
                          fg=HEADER_COLOR)
    title_label.pack(pady=(20, 30))
    
    # Assembly Input area label
    input_label = tk.Label(root, 
                          text="Assembly Code Input:",
                          font=heading_font,
                          bg=BG_COLOR,
                          fg=TEXT_COLOR,
                          anchor="w")
    input_label.pack(fill=tk.X, padx=15)
    
    # Info panel
    info_panel = tk.Frame(root, bg=INFO_BG, padx=10, pady=5, relief=tk.FLAT, borderwidth=1)
    info_panel.pack(fill=tk.X, padx=15, pady=(0, 5))
    
    # Color code labels
    info_label = tk.Label(info_panel, text="Color Codes:", bg=INFO_BG, fg=TEXT_COLOR, font=("Arial", 11, "bold"))
    info_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
    
    # Color coding labels
    colors = [
        ("Commands", KEYWORD_COLOR),
        ("Registers", REGISTER_COLOR),
        ("Numbers", NUMBER_COLOR),
        ("Comments", COMMENT_COLOR),
        ("Addressing (#,@)", ADDRESSING_COLOR),
        ("Byte/Word (.B/.W)", BYTE_WORD_COLOR),
        ("Labels", LABEL_COLOR),
        ("Branch Targets", BRANCH_LABEL_COLOR),
        ("Errors", ERROR_COLOR),
        ("Suggestions", SUGGESTION_COLOR)
    ]
    
    # Color boxes and descriptions
    for i, (label_text, color) in enumerate(colors):
        # Color square
        color_box = tk.Frame(info_panel, bg=color, width=20, height=20, relief=tk.RAISED, borderwidth=1)
        col = i
        if i >= 5:  # Move to next row after 5th element
            col = i - 5
        color_box.grid(row=i//5, column=col*2+1, padx=(5, 0), pady=(3 if i >= 5 else 0))
        
        # Fixed size
        color_box.grid_propagate(False)
        
        # Description
        label = tk.Label(info_panel, text=label_text, bg=INFO_BG, fg=TEXT_COLOR, font=("Arial", 10))
        label.grid(row=i//5, column=col*2+2, sticky="w", padx=(2, 10), pady=(3 if i >= 5 else 0))
    
    # Input text box
    input_text = scrolledtext.ScrolledText(root,
                                          wrap=tk.WORD,
                                          font=code_font,
                                          bg=TEXTBOX_BG,
                                          fg=TEXT_COLOR,
                                          insertbackground=TEXT_COLOR,
                                          height=12,
                                          borderwidth=0,
                                          relief=tk.FLAT)
    input_text.pack(fill=tk.X, padx=15, pady=5)
    input_text.bind("<KeyRelease>", on_text_change)
    
    # Syntax highlighting tags
    input_text.tag_configure("keyword", foreground=KEYWORD_COLOR)
    input_text.tag_configure("register", foreground=REGISTER_COLOR)
    input_text.tag_configure("number", foreground=NUMBER_COLOR)
    input_text.tag_configure("comment", foreground=COMMENT_COLOR)
    input_text.tag_configure("addressing", foreground=ADDRESSING_COLOR)
    input_text.tag_configure("byte_word", foreground=BYTE_WORD_COLOR)
    input_text.tag_configure("label", foreground=LABEL_COLOR)
    input_text.tag_configure("comma", foreground="white")
    input_text.tag_configure("branch_label", foreground=BRANCH_LABEL_COLOR)
    input_text.tag_configure("error", foreground=ERROR_COLOR, background=ERROR_BG)
    input_text.tag_configure("suggestion", foreground=SUGGESTION_COLOR)
    
    # Button frame
    button_frame = tk.Frame(root, bg=BG_COLOR)
    button_frame.pack(pady=15)
    
    # Buttons
    convert_button = tk.Button(button_frame, 
                               text="Convert",
                               font=button_font,
                               bg=BUTTON_COLOR,
                               fg=BUTTON_TEXT,
                               width=20,
                               relief=tk.RAISED,
                               padx=15,
                               pady=8,
                               command=convert_all)
    convert_button.pack(side=tk.LEFT, padx=10)
    convert_button.bind("<Enter>", on_hover)
    convert_button.bind("<Leave>", on_leave)
    
    save_obj_button = tk.Button(button_frame, 
                            text="View Object Code",
                            font=button_font,
                            bg=BUTTON_COLOR,
                            fg=BUTTON_TEXT,
                            width=20,
                            relief=tk.RAISED,
                            padx=15,
                            pady=8,
                            command=show_object_code)
    save_obj_button.pack(side=tk.LEFT, padx=10)
    save_obj_button.bind("<Enter>", on_hover)
    save_obj_button.bind("<Leave>", on_leave)
    
    # Output frame
    output_frame = tk.Frame(root, bg=BG_COLOR)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Left side - Hex output
    hex_frame = tk.Frame(output_frame, bg=BG_COLOR)
    hex_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    hex_label = tk.Label(hex_frame, 
                        text="Hex Output:",
                        font=heading_font,
                        bg=BG_COLOR,
                        fg=TEXT_COLOR,
                        anchor="w")
    hex_label.pack(fill=tk.X, pady=(15, 0))
    
    hex_text = scrolledtext.ScrolledText(hex_frame,
                                        wrap=tk.WORD,
                                        font=code_font,
                                        bg=TEXTBOX_BG,
                                        fg=TEXT_COLOR,
                                        height=10,
                                        borderwidth=0,
                                        relief=tk.FLAT)
    hex_text.pack(fill=tk.BOTH, expand=True, pady=5)
    hex_text.config(state=tk.DISABLED)
    
    # Right side - Binary output
    binary_frame = tk.Frame(output_frame, bg=BG_COLOR)
    binary_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    binary_label = tk.Label(binary_frame, 
                          text="Binary Output:",
                          font=heading_font,
                          bg=BG_COLOR,
                          fg=TEXT_COLOR,
                          anchor="w")
    binary_label.pack(fill=tk.X, pady=(15, 0))
    
    binary_text = scrolledtext.ScrolledText(binary_frame,
                                          wrap=tk.WORD,
                                          font=code_font,
                                          bg=TEXTBOX_BG,
                                          fg=TEXT_COLOR,
                                          height=10,
                                          borderwidth=0,
                                          relief=tk.FLAT)
    binary_text.pack(fill=tk.BOTH, expand=True, pady=5)
    binary_text.config(state=tk.DISABLED)
    
    # Status bar
    status_bar = tk.Label(root, 
                         textvariable=status_var, 
                         bd=1, 
                         relief=tk.SUNKEN, 
                         anchor=tk.W,
                         bg=INFO_BG,
                         fg=TEXT_COLOR,
                         font=("Arial", 11))
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Add Symbol Table button
    symtab_button = tk.Button(button_frame, 
                            text="Symbol Table",
                            font=button_font,
                            bg=BUTTON_COLOR,
                            fg=BUTTON_TEXT,
                            width=20,
                            relief=tk.RAISED,
                            padx=15,
                            pady=8,
                            command=show_symtab_window)
    symtab_button.pack(side=tk.LEFT, padx=10)
    symtab_button.bind("<Enter>", on_hover)
    symtab_button.bind("<Leave>", on_leave)
    
    
    
    return root

def show_command_reference():
    """Opens the command reference guide window"""
    reference_window = tk.Toplevel()
    reference_window.title("Command Reference Guide")
    reference_window.geometry("1000x600")
    reference_window.configure(bg=BG_COLOR)
    
    # Title
    title_label = tk.Label(reference_window,
                          text="MSP430 Command Reference Guide",
                          font=("Impact", 16),
                          bg=BG_COLOR,
                          fg=HEADER_COLOR)
    title_label.pack(pady=10)
    
    # Main frame
    main_frame = tk.Frame(reference_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Left panel (categories)
    left_frame = tk.Frame(main_frame, bg=INFO_BG, width=200)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)
    left_frame.pack_propagate(False)  # Fix size
    
    # Category title
    category_title = tk.Label(left_frame, text="Command Categories", 
                             font=("Arial", 11, "bold"), bg=INFO_BG, fg=TEXT_COLOR)
    category_title.pack(pady=10, padx=5, anchor=tk.W)
    
    # Search box
    search_frame = tk.Frame(left_frame, bg=INFO_BG)
    search_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
    
    search_entry = tk.Entry(search_frame, bg=TEXTBOX_BG, fg=TEXT_COLOR)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    search_button = tk.Button(search_frame, text="Search", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                             command=lambda: search_commands(search_entry.get(), command_text))
    search_button.pack(side=tk.LEFT, padx=(5, 0))
    
    # Categories
    categories = [
        "Double Operand Commands",
        "Branch Commands",
        "Single Operand Commands",
        "Emulated Commands",
        "Addressing Modes",
        "Assembly Directives",  # New category
        "Show All"
    ]
    
    buttons_frame = tk.Frame(left_frame, bg=INFO_BG)
    buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5)
    
    # Category buttons
    for category in categories:
        button = tk.Button(buttons_frame, text=category, bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                          width=22, anchor="w", command=lambda c=category: show_category(c, command_text))
        button.pack(pady=2, anchor=tk.W)
    
    # Right panel (command content)
    right_frame = tk.Frame(main_frame, bg=BG_COLOR)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Command detail title
    command_title = tk.Label(right_frame, text="Command Details", 
                            font=("Arial", 11, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
    command_title.pack(pady=(0, 5), anchor=tk.W)
    
    # Command detail content
    command_text = scrolledtext.ScrolledText(right_frame,
                                           wrap=tk.WORD,
                                           font=("Courier New", 11),
                                           bg=TEXTBOX_BG,
                                           fg=TEXT_COLOR,
                                           height=30)
    command_text.pack(fill=tk.BOTH, expand=True)
    
    # Show all commands by default
    show_category("Show All", command_text)
    
    # Bottom panel: status and extra buttons
    bottom_frame = tk.Frame(reference_window, bg=INFO_BG)
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_label = tk.Label(bottom_frame, text="MSP430 Assembly Reference Guide", bg=INFO_BG, fg=TEXT_COLOR)
    status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    example_button = tk.Button(bottom_frame, text="Command Examples", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                             command=lambda: show_examples(command_text))
    example_button.pack(side=tk.RIGHT, padx=10, pady=5)

def show_category(category, text_widget):
    """Show commands in the selected category"""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    header = f"MSP430 {category}\n"
    text_widget.insert(tk.END, header, "header")
    text_widget.insert(tk.END, "="*len(header) + "\n\n", "header")
    
    if category == "Double Operand Commands" or category == "Show All":
        text_widget.insert(tk.END, "Double Operand Commands (Format I):\n", "subheader")
        text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
        
        commands = [
            ("MOV", "dst = src", "Destination operand value is replaced with source operand value."),
            ("ADD", "dst = dst + src", "Destination operand is added with source operand value."),
            ("ADDC", "dst = dst + src + C", "Destination operand is added with source operand value and carry bit."),
            ("SUBC", "dst = dst - src - ~C", "Source operand value and inverted carry are subtracted from destination operand."),
            ("SUB", "dst = dst - src", "Source operand value is subtracted from destination operand."),
            ("CMP", "dst - src", "Destination and source operands are compared, result is not stored, only flags are affected."),
            ("DADD", "dst = dst + src + C (BCD)", "Decimal addition in BCD format. Carry is included."),
            ("BIT", "dst & src", "Destination and source operands undergo AND operation, result is not stored, only flags are affected."),
            ("BIC", "dst = dst & ~src", "Bits in destination operand are masked (cleared) with source operand value."),
            ("BIS", "dst = dst | src", "Source operand value is added to destination operand with OR operation."),
            ("XOR", "dst = dst ^ src", "Destination operand undergoes XOR operation with source operand value."),
            ("AND", "dst = dst & src", "Destination operand undergoes AND operation with source operand value.")
        ]
        
        for cmd, syntax, desc in commands:
            text_widget.insert(tk.END, f"{cmd:<6} {syntax:<18} : {desc}\n", "command")
        
        text_widget.insert(tk.END, "\n")
    
    if category == "Branch Commands" or category == "Show All":
        text_widget.insert(tk.END, "Branch Commands (Format II):\n", "subheader")
        text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
        
        commands = [
            ("JNE/JNZ", "Branch if Z=0", "Branches if Zero flag is 0 (not equal/not zero)."),
            ("JEQ/JZ", "Branch if Z=1", "Branches if Zero flag is 1 (equal/zero)."),
            ("JNC/JLO", "Branch if C=0", "Branches if Carry flag is 0 (no carry/unsigned lower)."),
            ("JC/JHS", "Branch if C=1", "Branches if Carry flag is 1 (carry/unsigned higher or same)."),
            ("JN", "Branch if N=1", "Branches if Negative flag is 1 (negative)."),
            ("JGE", "Branch if N=V", "Branches if Negative and overflow flags have same value (signed greater or equal)."),
            ("JL", "Branch if N!=V", "Branches if Negative and overflow flags have different values (signed lower)."),
            ("JMP", "Unconditional branch", "Performs unconditional branch.")
        ]
        
        for cmd, syntax, desc in commands:
            text_widget.insert(tk.END, f"{cmd:<8} {syntax:<15} : {desc}\n", "command")
        
        text_widget.insert(tk.END, "\n")
    
    if category == "Single Operand Commands" or category == "Show All":
        text_widget.insert(tk.END, "Single Operand Commands (Format III):\n", "subheader")
        text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
        
        commands = [
            ("RRC", "Right shift with C", "Destination operand is shifted right, carry bit goes to MSB and LSB goes to carry bit."),
            ("SWPB", "Swap bytes", "Swaps high and low bytes of destination operand."),
            ("RRA", "Arithmetic right shift", "Destination operand is shifted right arithmetically, MSB is preserved."),
            ("SXT", "Sign extend byte to word", "Extends signed byte value of destination operand to word."),
            ("PUSH", "Push to stack", "Places destination operand on stack and decrements SP by 2."),
            ("CALL", "Call subroutine", "Calls subroutine at destination address, saves return address on stack."),
            ("RETI", "Return from interrupt", "Returns from interrupt handler, restores SR and PC values from stack.")
        ]
        
        for cmd, syntax, desc in commands:
            text_widget.insert(tk.END, f"{cmd:<6} {syntax:<22} : {desc}\n", "command")
        
        text_widget.insert(tk.END, "\n")
    
    if category == "Emulated Commands" or category == "Show All":
        text_widget.insert(tk.END, "Emulated Commands:\n", "subheader")
        text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
        
        commands = [
            ("ADC", "ADDC #0,dst", "Adds carry value to operand."),
            ("BR", "MOV dst,PC", "Branches to address in operand."),
            ("CLR", "MOV #0,dst", "Clears operand."),
            ("CLRC", "BIC #1,SR", "Clears carry flag."),
            ("CLRN", "BIC #4,SR", "Clears negative flag."),
            ("CLRZ", "BIC #2,SR", "Clears zero flag."),
            ("DADC", "DADD #0,dst", "Adds carry value to operand in BCD format."),
            ("DEC", "SUB #1,dst", "Decrements operand by one."),
            ("DECD", "SUB #2,dst", "Decrements operand by two."),
            ("DINT", "BIC #8,SR", "Disables interrupts."),
            ("EINT", "BIS #8,SR", "Enables interrupts."),
            ("INC", "ADD #1,dst", "Increments operand by one."),
            ("INCD", "ADD #2,dst", "Increments operand by two."),
            ("INV", "XOR #-1,dst", "Inverts bits of operand."),
            ("NOP", "MOV #0,R3", "No operation."),
            ("POP", "MOV @SP+,dst", "Pops value from stack to operand."),
            ("RET", "MOV @SP+,PC", "Returns from subroutine."),
            ("RLA", "ADD dst,dst", "Shifts operand left, LSB is zeroed. (carry not affected)"),
            ("RLC", "ADDC dst,dst", "Shifts operand left, LSB is filled with carry value."),
            ("SBC", "SUBC #0,dst", "Subtracts inverted carry from operand."),
            ("SETC", "BIS #1,SR", "Sets carry flag."),
            ("SETN", "BIS #4,SR", "Sets negative flag."),
            ("SETZ", "BIS #2,SR", "Sets zero flag."),
            ("TST", "CMP #0,dst", "Compares operand with zero.")
        ]
        
        for cmd, syntax, desc in commands:
            text_widget.insert(tk.END, f"{cmd:<6} {syntax:<14} : {desc}\n", "command")
        
        text_widget.insert(tk.END, "\n")
    
    if category == "Addressing Modes" or category == "Show All":
        text_widget.insert(tk.END, "Addressing Modes:\n", "subheader")
        text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
        
        text_widget.insert(tk.END, "Register Direct (Rn)        : Register value is used\n", "command")
        text_widget.insert(tk.END, "Indexed (X(Rn))               : Memory content is fetched from address X+Rn\n", "command")
        text_widget.insert(tk.END, "Register Indirect (@Rn)       : Memory content is fetched from address Rn\n", "command")
        text_widget.insert(tk.END, "Indirect Autoincrement (@Rn+) : Memory content is fetched from address Rn, then Rn is incremented by 1 or 2\n", "command")
        text_widget.insert(tk.END, "Immediate (#X)                : Value X is used\n", "command")
        text_widget.insert(tk.END, "Absolute (&X)                 : Memory content is fetched from address X\n", "command")
        text_widget.insert(tk.END, "Symbolic (LABEL)              : Memory content is fetched from address LABEL\n", "command")
        
        text_widget.insert(tk.END, "\n")
    
    if category == "Assembly Directives" or category == "Show All":
        text_widget.insert(tk.END, "Assembly Directives:\n", "subheader")
        text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
        
        commands = [
            (".TEXT", "Code section starts here", "Defines the start of the code section."),
            (".DATA", "Data section starts here", "Defines the start of the data section."),
            (".BSS", "Uninitialized data section", "Defines the start of the uninitialized data section."),
            (".SECT", "Define section", "Defines a new section with a specified name and size."),
            (".ALIGN", "Align to boundary", "Aligns the current address to the specified boundary."),
            ("ORG", "Set origin", "Sets the origin address for the program."),
            ("EQU", "Define constant", "Defines a constant with a specified name and value."),
            ("DW", "Define word", "Defines a word (16-bit) data item."),
            (".WORD", "Define word", "Defines a word (16-bit) data item."),
            ("DB", "Define byte", "Defines a byte (8-bit) data item."),
            (".BYTE", "Define byte", "Defines a byte (8-bit) data item."),
            (".STRING", "Define string", "Defines a string with a null terminator."),
            (".CSTRING", "Define C-string", "Defines a C-string with a null terminator."),
            (".SPACE", "Reserve space", "Reserves a specified number of bytes of space.")
        ]
        
        for cmd, syntax, desc in commands:
            text_widget.insert(tk.END, f"{cmd:<10} {syntax:<20} : {desc}\n", "command")
        
        text_widget.insert(tk.END, "\n")
    
    # Apply styles
    text_widget.tag_configure("header", foreground=HEADER_COLOR, font=("Courier New", 13, "bold"))
    text_widget.tag_configure("subheader", foreground=KEYWORD_COLOR, font=("Courier New", 12, "bold"))
    text_widget.tag_configure("command", foreground=TEXT_COLOR, font=("Courier New", 11))
    
    text_widget.config(state=tk.DISABLED)

def search_commands(query, text_widget):
    """Search for commands"""
    if not query:
        show_category("Show All", text_widget)
        return
    
    query = query.upper()
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    header = f"Search Results: '{query}'\n"
    text_widget.insert(tk.END, header, "header")
    text_widget.insert(tk.END, "="*len(header) + "\n\n", "header")
    
    found = False
    
    # Search in double operand commands
    double_op_commands = [
        "MOV", "ADD", "ADDC", "SUBC", "SUB", "CMP", "DADD", 
        "BIT", "BIC", "BIS", "XOR", "AND"
    ]
    for cmd in double_op_commands:
        if query in cmd:
            found = True
            text_widget.insert(tk.END, f"{cmd}: Double Operand Command (Format I)\n", "subheader")
            text_widget.insert(tk.END, f"Usage: {cmd}(.B/.W) src, dst\n\n", "command")
    
    # Search in branch commands
    branch_commands = [
        "JNE", "JNZ", "JEQ", "JZ", "JNC", "JLO", "JC", "JHS", 
        "JN", "JGE", "JL", "JMP"
    ]
    for cmd in branch_commands:
        if query in cmd:
            found = True
            text_widget.insert(tk.END, f"{cmd}: Branch Command (Format II)\n", "subheader")
            text_widget.insert(tk.END, f"Usage: {cmd} label\n\n", "command")
    
    # Search in single operand commands
    single_op_commands = [
        "RRC", "SWPB", "RRA", "SXT", "PUSH", "CALL", "RETI"
    ]
    for cmd in single_op_commands:
        if query in cmd:
            found = True
            text_widget.insert(tk.END, f"{cmd}: Single Operand Command (Format III)\n", "subheader")
            text_widget.insert(tk.END, f"Usage: {cmd}(.B/.W) dst\n\n", "command")
    
    # Search in emulated commands
    emulated_commands = list(emulated_map.keys())
    for cmd in emulated_commands:
        clean_cmd = cmd.split(".")[0]  # Remove .B/.W part
        if query in clean_cmd:
            found = True
            text_widget.insert(tk.END, f"{clean_cmd}: Emulated Command\n", "subheader")
            text_widget.insert(tk.END, f"Implementation: {emulated_map[cmd]}\n\n", "command")
    
    # Search addressing modes
    if "REGISTER" in query or "RN" in query or "ADDRESS" in query:
        found = True
        text_widget.insert(tk.END, "Addressing Modes:\n", "subheader")
        text_widget.insert(tk.END, "- Register Direct (Rn)\n", "command")
        text_widget.insert(tk.END, "- Indexed (X(Rn))\n", "command")
        text_widget.insert(tk.END, "- Register Indirect (@Rn)\n", "command")
        text_widget.insert(tk.END, "- Indirect Autoincrement (@Rn+)\n", "command")
        text_widget.insert(tk.END, "- Immediate (#X)\n", "command")
        text_widget.insert(tk.END, "- Absolute (&X)\n", "command")
        text_widget.insert(tk.END, "- Symbolic (LABEL)\n\n", "command")
    
    if not found:
        text_widget.insert(tk.END, "No search results found.\n", "command")
    
    # Apply styles
    text_widget.tag_configure("header", foreground=HEADER_COLOR, font=("Courier New", 13, "bold"))
    text_widget.tag_configure("subheader", foreground=KEYWORD_COLOR, font=("Courier New", 12, "bold"))
    text_widget.tag_configure("command", foreground=TEXT_COLOR, font=("Courier New", 11))
    
    text_widget.config(state=tk.DISABLED)

def show_examples(text_widget):
    """Show command examples"""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    header = "MSP430 Command Examples\n"
    text_widget.insert(tk.END, header, "header")
    text_widget.insert(tk.END, "="*len(header) + "\n\n", "header")
    
    # Data Movement Examples
    text_widget.insert(tk.END, "Data Movement Examples:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Loading constant value to register\n", "comment")
    text_widget.insert(tk.END, "MOV.W   #0x1234, R5     ; R5 = 0x1234\n\n", "command")
    
    text_widget.insert(tk.END, "; Moving from register to register\n", "comment")
    text_widget.insert(tk.END, "MOV.W   R5, R6          ; R6 = R5\n\n", "command")
    
    text_widget.insert(tk.END, "; Writing register value to memory address\n", "comment")
    text_widget.insert(tk.END, "MOV.W   R5, &0x0200     ; Memory[0x0200] = R5\n\n", "command")
    
    text_widget.insert(tk.END, "; Reading from memory to register\n", "comment")
    text_widget.insert(tk.END, "MOV.B   &0x0200, R7     ; R7 = Memory[0x0200] (as byte)\n\n", "command")
    
    # Arithmetic Operation Examples
    text_widget.insert(tk.END, "Arithmetic Operation Examples:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Addition\n", "comment")
    text_widget.insert(tk.END, "ADD.W   #0x1234, R5     ; R5 += 0x1234\n\n", "command")
    
    text_widget.insert(tk.END, "; Subtraction\n", "comment")
    text_widget.insert(tk.END, "SUB.W   #1, R6          ; R6 -= 1\n\n", "command")
    
    text_widget.insert(tk.END, "; Increment and Decrement\n", "comment")
    text_widget.insert(tk.END, "INC     R7              ; R7 += 1\n", "command")
    text_widget.insert(tk.END, "DEC     R8              ; R8 -= 1\n", "command")
    text_widget.insert(tk.END, "INCD    R9              ; R9 += 2\n", "command")
    text_widget.insert(tk.END, "DECD    R10             ; R10 -= 2\n\n", "command")
    
    # Branch Examples
    text_widget.insert(tk.END, "Branch Examples:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Unconditional branch\n", "comment")
    text_widget.insert(tk.END, "JMP     LABEL           ; Jump to LABEL address\n\n", "command")
    
    text_widget.insert(tk.END, "; Compare and conditional branch\n", "comment")
    text_widget.insert(tk.END, "CMP.W   #0, R5          ; Compare R5 with 0\n", "command")
    text_widget.insert(tk.END, "JEQ     ZERO_FOUND      ; Jump to ZERO_FOUND if R5 = 0\n", "command")
    text_widget.insert(tk.END, "JNE     NON_ZERO        ; Jump to NON_ZERO if R5 != 0\n\n", "command")
    
    text_widget.insert(tk.END, "; Compare and branch (signed)\n", "comment")
    text_widget.insert(tk.END, "CMP.W   R5, R6          ; Comparison R6 - R5\n", "command")
    text_widget.insert(tk.END, "JGE     GREATER_EQ      ; Jump if R6 >= R5\n", "command")
    text_widget.insert(tk.END, "JL      LESS            ; Jump if R6 < R5\n\n", "command")
    
    # Subroutine Examples
    text_widget.insert(tk.END, "Subroutine Examples:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Calling subroutine\n", "comment")
    text_widget.insert(tk.END, "CALL    SUB_ROUTINE     ; Call SUB_ROUTINE subroutine\n\n", "command")
    
    text_widget.insert(tk.END, "; Return from subroutine\n", "comment")
    text_widget.insert(tk.END, "RET                     ; Return to caller address\n\n", "command")
    
    text_widget.insert(tk.END, "; Subroutine with parameter\n", "comment")
    text_widget.insert(tk.END, "MOV.W   #0x1234, R12    ; Load parameter to R12\n", "command")
    text_widget.insert(tk.END, "CALL    CALCULATE       ; Call subroutine with parameter\n\n", "command")
    
    # Logical Operation Examples
    text_widget.insert(tk.END, "Logical Operation Examples:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; AND operation\n", "comment")
    text_widget.insert(tk.END, "AND.W   #0x00FF, R5     ; R5 = R5 & 0x00FF (preserve lower byte)\n\n", "command")
    
    text_widget.insert(tk.END, "; Bit clearing\n", "comment")
    text_widget.insert(tk.END, "BIC.W   #0x8000, R6     ; Clear highest bit of R6\n\n", "command")
    
    text_widget.insert(tk.END, "; Bit setting\n", "comment")
    text_widget.insert(tk.END, "BIS.W   #0x0001, R7     ; Set lowest bit of R7\n\n", "command")
    
    text_widget.insert(tk.END, "; XOR operation\n", "comment")
    text_widget.insert(tk.END, "XOR.W   #0xFFFF, R8     ; Invert all bits of R8\n\n", "command")
    
    # Stack Operations
    text_widget.insert(tk.END, "Stack Operations:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Setting stack pointer\n", "comment")
    text_widget.insert(tk.END, "MOV.W   #0x0400, SP     ; SP = 0x0400 (stack start)\n\n", "command")
    
    text_widget.insert(tk.END, "; Pushing data to stack\n", "comment")
    text_widget.insert(tk.END, "PUSH    R5              ; Push R5 value to stack\n\n", "command")
    
    text_widget.insert(tk.END, "; Popping data from stack\n", "comment")
    text_widget.insert(tk.END, "POP     R6              ; Pop value from stack to R6\n\n", "command")
    
    # Complete Program Example
    text_widget.insert(tk.END, "Complete Program Example:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Program to sum numbers in an array starting at 0x0200\n", "comment")
    text_widget.insert(tk.END, "ORG     0xF800          ; Program start address\n\n", "command")
    
    text_widget.insert(tk.END, "; Constants and variables\n", "comment")
    text_widget.insert(tk.END, "ARR_ADDR    EQU 0x0200  ; Array start address\n", "command")
    text_widget.insert(tk.END, "RESULT      EQU 0x0210  ; Result address\n\n", "command")
    
    text_widget.insert(tk.END, "RESET:  ; Reset vector\n", "comment")
    text_widget.insert(tk.END, "        MOV.W   #0x0400, SP     ; Set stack pointer\n", "command")
    text_widget.insert(tk.END, "        MOV.W   #5, R5          ; Number of array elements\n", "command")
    text_widget.insert(tk.END, "        MOV.W   #ARR_ADDR, R6   ; Array start address\n", "command")
    text_widget.insert(tk.END, "        MOV.W   #0, R7          ; Sum value (start with 0)\n\n", "command")
    
    text_widget.insert(tk.END, "LOOP:   ; Main loop\n", "comment")
    text_widget.insert(tk.END, "        ADD.W   @R6+, R7        ; Add array element and increment pointer\n", "command")
    text_widget.insert(tk.END, "        DEC     R5              ; Decrement counter\n", "command")
    text_widget.insert(tk.END, "        JNZ     LOOP            ; Continue loop if counter not zero\n\n", "command")
    
    text_widget.insert(tk.END, "DONE:   ; Addition complete\n", "comment")
    text_widget.insert(tk.END, "        MOV.W   R7, &RESULT     ; Save result to memory\n", "command")
    text_widget.insert(tk.END, "        JMP     $               ; Infinite loop\n\n", "command")
    
    # Special Example
    text_widget.insert(tk.END, "Interrupt Usage Example:\n", "subheader")
    text_widget.insert(tk.END, "-"*35 + "\n\n", "subheader")
    
    text_widget.insert(tk.END, "; Timer interrupt handling example\n", "comment")
    text_widget.insert(tk.END, "        MOV.W   #WDTPW+WDTHOLD, &WDTCTL  ; Stop watchdog timer\n", "command")
    text_widget.insert(tk.END, "        MOV.W   #CCIE, &CCTL0            ; Enable CCR0 interrupt\n", "command")
    text_widget.insert(tk.END, "        MOV.W   #1000, &CCR0             ; Load value to CCR0\n", "command")
    text_widget.insert(tk.END, "        MOV.W   #TASSEL_2+MC_1, &TACTL   ; SMCLK, upmode\n", "command")
    text_widget.insert(tk.END, "        EINT                              ; Enable interrupts\n\n", "command")
    
    text_widget.insert(tk.END, "LOOP:   ; Main loop\n", "comment")
    text_widget.insert(tk.END, "        NOP                      ; Do nothing\n", "command")
    text_widget.insert(tk.END, "        JMP     LOOP            ; Continue loop\n\n", "command")
    
    text_widget.insert(tk.END, "; Timer_A0 interrupt vector\n", "comment")
    text_widget.insert(tk.END, "ORG     0xFFF2\n", "command")
    text_widget.insert(tk.END, "        DW      TIMER_ISR\n\n", "command")
    
    text_widget.insert(tk.END, "; Timer interrupt handler\n", "comment")
    text_widget.insert(tk.END, "TIMER_ISR:\n", "command")
    text_widget.insert(tk.END, "        XOR.W   #0x0001, &P1OUT  ; Toggle P1.0 LED\n", "command")
    text_widget.insert(tk.END, "        RETI                      ; Return from interrupt\n", "command")
    
    # Apply styles
    text_widget.tag_configure("header", foreground=HEADER_COLOR, font=("Courier New", 13, "bold"))
    text_widget.tag_configure("subheader", foreground=KEYWORD_COLOR, font=("Courier New", 12, "bold"))
    text_widget.tag_configure("command", foreground=TEXT_COLOR, font=("Courier New", 11))
    text_widget.tag_configure("comment", foreground=COMMENT_COLOR, font=("Courier New", 11))
    
    text_widget.config(state=tk.DISABLED)

# Global variables for modification record tracking
modification_records = []

def add_modification_record(action_type, details, timestamp=None):
    """Add a new modification record with timestamp"""
    if timestamp is None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    record = {
        "timestamp": timestamp,
        "action": action_type,
        "details": details
    }
    
    modification_records.append(record)

def show_modification_records():
    """Shows the modification records window"""
    window = Toplevel()
    window.title("MSP430 Modification Records")
    window.geometry("800x600")
    window.configure(bg=BG_COLOR)
    
    # Title
    title = tk.Label(window, text="MSP430 Modification Records", font=("Impact", 16), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=10)
    
    # Main frame
    main_frame = tk.Frame(window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(fill=tk.X, pady=(0, 10))

    # Add new record button
    add_record_button = tk.Button(button_frame, text="Add New Record", 
                                bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                                command=lambda: show_add_record_dialog(records_text))
    add_record_button.pack(side=tk.LEFT, padx=5)

    # Export records button
    export_button = tk.Button(button_frame, text="Export Records", 
                            bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=lambda: export_modification_records(records_text))
    export_button.pack(side=tk.LEFT, padx=5)

    # Clear records button
    clear_button = tk.Button(button_frame, text="Clear All Records", 
                            bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=lambda: clear_modification_records(records_text))
    clear_button.pack(side=tk.LEFT, padx=5)

    # Records text area
    records_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                          font=("Courier New", 11),
                                          bg=TEXTBOX_BG, fg=TEXT_COLOR)
    records_text.pack(fill=tk.BOTH, expand=True)

    # Display existing records
    update_records_display(records_text)

def update_records_display(text_widget):
    """Update the records display with current records"""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    if not modification_records:
        text_widget.insert(tk.END, "No modification records found.\n")
    else:
        for i, record in enumerate(modification_records, 1):
            text_widget.insert(tk.END, f"#{i} - {record['timestamp']}\n", "header")
            text_widget.insert(tk.END, f"Action: {record['action']}\n", "action")
            text_widget.insert(tk.END, f"Details: {record['details']}\n\n", "details")
    
    # Apply tags
    text_widget.tag_configure("header", foreground=KEYWORD_COLOR, font=("Courier New", 11, "bold"))
    text_widget.tag_configure("action", foreground=REGISTER_COLOR, font=("Courier New", 11))
    text_widget.tag_configure("details", foreground=TEXT_COLOR, font=("Courier New", 11))
    
    text_widget.config(state=tk.DISABLED)

def show_add_record_dialog(parent_text_widget):
    """Show dialog to add a new modification record"""
    dialog = Toplevel()
    dialog.title("Add Modification Record")
    dialog.geometry("500x350")
    dialog.configure(bg=BG_COLOR)
    dialog.transient(root)  # Set to be on top of the main window
    dialog.grab_set()  # Make dialog modal
    
    # Title
    title = tk.Label(dialog, text="Add New Modification Record", 
                   font=("Arial", 12, "bold"), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=10)
    
    # Form frame
    form_frame = tk.Frame(dialog, bg=BG_COLOR)
    form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    
    # Action type
    action_label = tk.Label(form_frame, text="Action Type:", bg=BG_COLOR, fg=TEXT_COLOR)
    action_label.grid(row=0, column=0, sticky="w", pady=5)
    
    action_var = tk.StringVar(value="Code Modification")
    action_combobox = ttk.Combobox(form_frame, textvariable=action_var, width=30)
    action_combobox['values'] = (
        "Code Modification", 
        "Bug Fix", 
        "Feature Addition", 
        "Optimization", 
        "Refactoring",
        "Testing",
        "Documentation",
        "Other"
    )
    action_combobox.grid(row=0, column=1, sticky="w", pady=5)
    
    # Details
    details_label = tk.Label(form_frame, text="Details:", bg=BG_COLOR, fg=TEXT_COLOR)
    details_label.grid(row=1, column=0, sticky="nw", pady=5)
    
    details_text = scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, 
                                          height=10, width=40,
                                          bg=TEXTBOX_BG, fg=TEXT_COLOR)
    details_text.grid(row=1, column=1, sticky="w", pady=5)
    
    # Buttons frame
    buttons_frame = tk.Frame(dialog, bg=BG_COLOR)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    # Save button
    save_button = tk.Button(buttons_frame, text="Save Record", 
                          bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                          command=lambda: save_new_record(
                              action_var.get(), 
                              details_text.get("1.0", tk.END).strip(),
                              dialog,
                              parent_text_widget))
    save_button.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_button = tk.Button(buttons_frame, text="Cancel", 
                            bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=dialog.destroy)
    cancel_button.pack(side=tk.LEFT, padx=10)

def save_new_record(action, details, dialog, text_widget):
    """Save a new modification record"""
    if not details:
        messagebox.showwarning("Warning", "Please enter details for the modification record.")
        return
    
    add_modification_record(action, details)
    update_records_display(text_widget)
    dialog.destroy()

def export_modification_records(text_widget):
    """Export modification records to a file"""
    if not modification_records:
        messagebox.showinfo("Info", "No records to export.")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Export Modification Records"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, "w") as file:
            file.write("MSP430 MODIFICATION RECORDS\n")
            file.write("=========================\n\n")
            
            for i, record in enumerate(modification_records, 1):
                file.write(f"Record #{i}\n")
                file.write(f"Timestamp: {record['timestamp']}\n")
                file.write(f"Action: {record['action']}\n")
                file.write(f"Details: {record['details']}\n")
                file.write("-------------------------\n\n")
        
        messagebox.showinfo("Success", f"Records exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export records: {str(e)}")

def clear_modification_records(text_widget):
    """Clear all modification records"""
    if not modification_records:
        messagebox.showinfo("Info", "No records to clear.")
        return
    
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all modification records?"):
        modification_records.clear()
        update_records_display(text_widget)
        messagebox.showinfo("Success", "All records have been cleared.")

# Global variables for modification records
modification_records = []
program_relocation_address = 0x0000

# Add modification record class
class ModificationRecord:
    """SIC/XE style modification record"""
    
    def __init__(self, address=0, length=0, symbol_name=None, operation='+'):
        self.address = address if isinstance(address, int) else 0
        self.length = length if isinstance(length, int) else 0
        self.symbol_name = symbol_name
        self.operation = operation
    
    def __str__(self):
        return f"M {self.address:06X} {self.length:02d} {self.operation}{self.symbol_name or ''}"
    
    def get_details(self):
        """Get details as a dictionary for display"""
        return {
            "address": f"0x{self.address:06X}" if isinstance(self.address, int) else str(self.address),
            "length": str(self.length),
            "symbol": self.symbol_name or "PROGADDR",
            "operation": self.operation,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def add_modification_record(address, length, symbol_name=None, operation='+'):
    """Add a new SIC/XE style modification record"""
    global modification_records
    
    # Convert address to int if it's a string
    if isinstance(address, str):
        try:
            address = int(address, 0)
        except ValueError:
            address = 0
    
    # Ensure length is an integer
    if isinstance(length, str):
        try:
            length = int(length, 0)
        except ValueError:
            length = 0
    
    record = ModificationRecord(address, length, symbol_name, operation)
    modification_records.append(record)
    
    print(f"Added modification record: address=0x{record.address:06X}, length={record.length} bits, {record.operation}{record.symbol_name or ''}")
    
    return record

def show_modification_records_window():
    """Shows a window with SIC/XE style modification records"""
    window = Toplevel()
    window.title("MSP430 Modification Records (SIC/XE Style)")
    window.geometry("900x600")
    window.configure(bg=BG_COLOR)
    
    # Title
    title = tk.Label(window, text="MSP430 Modification Records (SIC/XE Style)", font=("Impact", 16), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=10)
    
    # Info label
    info_label = tk.Label(window, 
                        text="Modification records are used during program loading to adjust addresses based on actual load location.",
                        font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR, 
                        justify=tk.LEFT, wraplength=850)
    info_label.pack(pady=(0, 10), padx=15, anchor=tk.W)
    
    # Top frame for relocation base
    top_frame = tk.Frame(window, bg=BG_COLOR)
    top_frame.pack(fill=tk.X, padx=15, pady=5)
    
    # Relocation base entry
    reloc_label = tk.Label(top_frame, text="Program Relocation Base Address:", bg=BG_COLOR, fg=TEXT_COLOR)
    reloc_label.pack(side=tk.LEFT, padx=(0, 5))
    
    reloc_entry = tk.Entry(top_frame, width=10, font=("Courier New", 11))
    reloc_entry.insert(0, f"{program_relocation_address:04X}")
    reloc_entry.pack(side=tk.LEFT)
    
    # Set relocation button
    set_reloc_btn = tk.Button(top_frame, text="Set Base Address", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=lambda: set_relocation_base(reloc_entry.get(), records_text))
    set_reloc_btn.pack(side=tk.LEFT, padx=10)
    
    # Button frame
    button_frame = tk.Frame(window, bg=BG_COLOR)
    button_frame.pack(fill=tk.X, padx=15, pady=5)
    
    # Add record button
    add_record_btn = tk.Button(button_frame, text="Add Modification Record", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                             command=lambda: show_add_mod_record_dialog(records_text))
    add_record_btn.pack(side=tk.LEFT, padx=5)
    
    # Export button
    export_btn = tk.Button(button_frame, text="Export Records", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                          command=lambda: export_mod_records(records_text))
    export_btn.pack(side=tk.LEFT, padx=5)
    
    # Clear button
    clear_btn = tk.Button(button_frame, text="Clear All Records", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                         command=lambda: clear_mod_records(records_text))
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    # Apply modifications button
    apply_btn = tk.Button(button_frame, text="Apply Modifications", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                         command=lambda: apply_modifications(records_text))
    apply_btn.pack(side=tk.LEFT, padx=5)
    
    # Main text area
    records_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, 
                                           font=("Courier New", 11),
                                          bg=TEXTBOX_BG, fg=TEXT_COLOR)
    records_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # Update records display
    update_mod_records_display(records_text)
    
    # Add modification record
    add_modification_record_history(
        "Feature Usage",
        "Opened SIC/XE style Modification Records window"
    )

def update_mod_records_display(text_widget):
    """Update the records text widget with current modification records"""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    if not modification_records:
        text_widget.insert(tk.END, "No modification records exist. Use 'Add Modification Record' to create records.\n")
        text_widget.insert(tk.END, "\nProgram Relocation Base: " + f"0x{program_relocation_address:04X}\n", "bold")
    else:
        text_widget.insert(tk.END, "CURRENT MODIFICATION RECORDS:\n", "header")
        text_widget.insert(tk.END, "===============================\n\n", "header")
        text_widget.insert(tk.END, "Program Relocation Base: " + f"0x{program_relocation_address:04X}\n\n", "bold")
        
        # Format record information
        text_widget.insert(tk.END, f"{'Record':<8}{'Address':<12}{'Length':<10}{'Operation':<10}{'Symbol':<15}{'Added'}\n", "bold")
        text_widget.insert(tk.END, "-" * 70 + "\n", "normal")
        
        for i, record in enumerate(modification_records, 1):
            details = record.get_details()
            text_widget.insert(tk.END, f"{i:<8}{details['address']:<12}{details['length']:<10}{record.operation:<10}{details['symbol']:<15}{details['timestamp']}\n", "normal")
        
        text_widget.insert(tk.END, "\n\nSIC/XE FORMAT RECORDS:\n", "header")
        text_widget.insert(tk.END, "=====================\n\n", "header")
        
        for i, record in enumerate(modification_records, 1):
            text_widget.insert(tk.END, f"{str(record)}\n", "code")
    
    # Apply tag styles
    text_widget.tag_configure("header", foreground=HEADER_COLOR, font=("Courier New", 12, "bold"))
    text_widget.tag_configure("bold", foreground=TEXT_COLOR, font=("Courier New", 11, "bold"))
    text_widget.tag_configure("normal", foreground=TEXT_COLOR, font=("Courier New", 11))
    text_widget.tag_configure("code", foreground=NUMBER_COLOR, font=("Courier New", 11))
    
    text_widget.config(state=tk.DISABLED)

def show_add_mod_record_dialog(parent_text_widget):
    """Show dialog to add a new modification record"""
    dialog = Toplevel()
    dialog.title("Add Modification Record")
    dialog.geometry("450x300")
    dialog.configure(bg=BG_COLOR)
    dialog.transient()  # Set to be on top
    dialog.grab_set()   # Make dialog modal
    
    # Title
    title = tk.Label(dialog, text="Add New Modification Record", 
                    font=("Arial", 12, "bold"), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=10)
    
    # Form frame
    form_frame = tk.Frame(dialog, bg=BG_COLOR)
    form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    
    # Address
    addr_label = tk.Label(form_frame, text="Address (hex):", bg=BG_COLOR, fg=TEXT_COLOR)
    addr_label.grid(row=0, column=0, sticky="w", pady=5)
    
    addr_entry = tk.Entry(form_frame, width=20)
    addr_entry.grid(row=0, column=1, sticky="w", pady=5)
    
    # Length
    length_label = tk.Label(form_frame, text="Length (bits):", bg=BG_COLOR, fg=TEXT_COLOR)
    length_label.grid(row=1, column=0, sticky="w", pady=5)
    
    length_entry = tk.Entry(form_frame, width=20)
    length_entry.grid(row=1, column=1, sticky="w", pady=5)
    
    # Symbol
    symbol_label = tk.Label(form_frame, text="Symbol (optional):", bg=BG_COLOR, fg=TEXT_COLOR)
    symbol_label.grid(row=2, column=0, sticky="w", pady=5)
    
    symbol_entry = tk.Entry(form_frame, width=20)
    symbol_entry.grid(row=2, column=1, sticky="w", pady=5)
    
    # Operation
    op_label = tk.Label(form_frame, text="Operation:", bg=BG_COLOR, fg=TEXT_COLOR)
    op_label.grid(row=3, column=0, sticky="w", pady=5)
    
    op_var = tk.StringVar(value="+")
    op_frame = tk.Frame(form_frame, bg=BG_COLOR)
    op_frame.grid(row=3, column=1, sticky="w", pady=5)
    
    add_radio = tk.Radiobutton(op_frame, text="Add (+)", variable=op_var, value="+", bg=BG_COLOR, fg=TEXT_COLOR)
    add_radio.pack(side=tk.LEFT)
    
    sub_radio = tk.Radiobutton(op_frame, text="Subtract (-)", variable=op_var, value="-", bg=BG_COLOR, fg=TEXT_COLOR)
    sub_radio.pack(side=tk.LEFT)
    
    # Info text
    info_text = tk.Label(form_frame, 
                       text="Modification records in SIC/XE format are used during\nprogram loading to adjust addresses based on\nactual memory location.",
                       bg=BG_COLOR, fg=COMMENT_COLOR, justify=tk.LEFT)
    info_text.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)
    
    # Buttons frame
    buttons_frame = tk.Frame(dialog, bg=BG_COLOR)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    # Save button
    save_button = tk.Button(buttons_frame, text="Save Record", 
                          bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                          command=lambda: save_mod_record(
                              addr_entry.get(), 
                              length_entry.get(),
                              symbol_entry.get(),
                              op_var.get(),
                              dialog,
                              parent_text_widget))
    save_button.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_button = tk.Button(buttons_frame, text="Cancel", 
                            bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=dialog.destroy)
    cancel_button.pack(side=tk.LEFT, padx=10)

def save_mod_record(addr_str, length_str, symbol_str, operation, dialog, text_widget):
    """Save a new modification record"""
    try:
        # Parse address as hex
        if addr_str.startswith("0x"):
            addr_str = addr_str[2:]
        address = int(addr_str, 16)
        
        # Parse length as decimal
        length = int(length_str)
        
        # Check symbol
        symbol = symbol_str.strip() if symbol_str.strip() else None
        
        # Create the record
        add_modification_record(address, length, symbol, operation)
        
        # Update display and close dialog
        update_mod_records_display(text_widget)
        dialog.destroy()
        
    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Please enter valid values: {str(e)}")

def export_mod_records(text_widget):
    """Export modification records to a file"""
    if not modification_records:
        messagebox.showinfo("Info", "No records to export.")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".mod",
        filetypes=[("Modification records", "*.mod"), ("Text files", "*.txt"), ("All files", "*.*")],
        title="Export Modification Records"
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, "w") as file:
            file.write("MSP430 MODIFICATION RECORDS (SIC/XE STYLE)\n")
            file.write("=======================================\n\n")
            file.write(f"Program Relocation Base: 0x{program_relocation_address:04X}\n\n")
            
            # Write records in SIC/XE format
            file.write("SIC/XE Format Records:\n")
            file.write("=====================\n")
            for record in modification_records:
                file.write(f"{str(record)}\n")
            
            # Write detailed records
            file.write("\n\nDetailed Records:\n")
            file.write("================\n\n")
            file.write(f"{'Record':<8}{'Address':<12}{'Length':<10}{'Operation':<10}{'Symbol':<15}{'Added'}\n")
            file.write("-" * 70 + "\n")
            
            for i, record in enumerate(modification_records, 1):
                details = record.get_details()
                file.write(f"{i:<8}{details['address']:<12}{details['length']:<10}{record.operation:<10}{details['symbol']:<15}{details['timestamp']}\n")
        
        messagebox.showinfo("Success", f"Records exported to {file_path}")
        
        # Add history record
        add_modification_record_history(
            "Export Records",
            f"Exported {len(modification_records)} modification records to file: {file_path}"
        )
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export records: {str(e)}")

def clear_mod_records(text_widget):
    """Clear all modification records"""
    if not modification_records:
        messagebox.showinfo("Info", "No records to clear.")
        return
    
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all modification records?"):
        modification_records.clear()
        update_mod_records_display(text_widget)
        
        # Add history record
        add_modification_record_history(
            "Clear Records",
            "Cleared all modification records"
        )
        
        messagebox.showinfo("Success", "All records have been cleared.")

def set_relocation_base(addr_str, text_widget):
    """Set the program relocation base address"""
    global program_relocation_address
    
    try:
        # Parse address as hex
        if addr_str.startswith("0x"):
            addr_str = addr_str[2:]
        
        address = int(addr_str, 16)
        program_relocation_address = address
        
        # Update display
        update_mod_records_display(text_widget)
        
        # Add history record
        add_modification_record_history(
            "Relocation Base",
            f"Set program relocation base address to 0x{address:04X}"
        )
        
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid hexadecimal address.")

def apply_modifications(text_widget):
    """Apply modification records to the memory values"""
    global memory_values
    
    if not modification_records:
        messagebox.showinfo("Info", "No modification records to apply.")
        return
    
    try:
        modified_addresses = []
        
        for record in modification_records:
            # Calculate byte addresses affected and bit positions
            start_byte = record.address
            num_bytes = (record.length + 7) // 8  # Round up to nearest byte
            
            # Process each affected byte
            for i in range(num_bytes):
                addr = start_byte + i
                
                # Get current value at this address
                current_value = memory_values.get(addr, 0)
                
                # Calculate how many bits to modify in this byte
                bits_in_this_byte = min(8, record.length - (i * 8))
                if bits_in_this_byte <= 0:
                    break
                
                # Calculate bit position and mask
                start_bit = 0 if i > 0 else (8 - (record.length % 8)) % 8
                mask = ((1 << bits_in_this_byte) - 1) << start_bit
                
                # Calculate relocation value
                reloc_value = program_relocation_address
                if record.symbol_name:
                    # If symbol is provided, look it up
                    if record.symbol_name in labels:
                        symbol_value = labels[record.symbol_name]
                    elif record.symbol_name in symtab["equ"]:
                        symbol_value = symtab["equ"][record.symbol_name]
                    else:
                        messagebox.showerror("Symbol Error", f"Symbol '{record.symbol_name}' not found.")
                        continue
                    reloc_value = symbol_value
                
                # Apply the operation (+ or -)
                if record.operation == '+':
                    new_value = current_value + ((reloc_value >> (i * 8)) & 0xFF)
                else:
                    new_value = current_value - ((reloc_value >> (i * 8)) & 0xFF)
                
                # Update memory
                memory_values[addr] = new_value & 0xFF
                modified_addresses.append(addr)
        
        # Add history record
        add_modification_record_history(
            "Apply Modifications",
            f"Applied {len(modification_records)} modification records, affecting {len(set(modified_addresses))} memory locations"
        )
        
        messagebox.showinfo("Success", f"Applied {len(modification_records)} modification records to memory.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to apply modifications: {str(e)}")

# Update GUI with SIC/XE Modification Records in View menu
def update_gui():
    """Updates GUI with new components after initialization"""
    global root
    
    try:
        # Get the menu bar from root
        menu_bar = root.nametowidget(root.cget("menu"))
        
        # Simülasyon menüsü ekle
        simulation_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Simulation", menu=simulation_menu)
        
        # Simülasyon menü öğelerini ekle
        simulation_menu.add_command(label="Simulate Code", command=simulate_code)
        simulation_menu.add_command(label="Simulate Step By Step", command=lambda: simulate_code(step_by_step=True))
        simulation_menu.add_command(label="Register Viewer", command=show_register_viewer)
        
        # Örnekler menüsü ekle
        examples_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Example Test Codes", menu=examples_menu)
        
        # Örnek kodlar
        examples_menu.add_command(label="Simple Test Code", command=add_test_code)
        examples_menu.add_command(label="Counter Code (Infinite Loop)", command=add_counter_code)
        examples_menu.add_command(label="Add Modification Test Code", command=add_modification_test_code)
        examples_menu.add_command(label="Add Directive Test Code", command=add_directive_test_code)
        examples_menu.add_command(label="LITTAB and BLOCKTAB Test", command=add_littab_blocktab_test_code)
     
    except Exception as e:
        print(f"Error updating GUI: {str(e)}")

# Add this function to connect our two modification systems
def add_modification_record_history(action_type, details, timestamp=None):
    """Add a new modification record to the general history"""
    # Sadece bir mesaj yazdır, ikinci bir add_modification_record çağrısı yapmaya çalışma
    try:
        print(f"Modification history: {action_type} - {details}")
    except:
        pass
    # Önceki implementasyon çakışmaya neden oluyordu:
    # add_modification_record(action_type, details, timestamp)

def show_sensor_interface():
    """Show sensor interface guide and examples"""
    window = Toplevel(root)
    window.title("MSP430 Sensor Interface Guide")
    window.geometry("900x700")
    window.configure(bg=BG_COLOR)
    
    # Title
    title_font = ("Arial", 16, "bold")
    title = tk.Label(window, text="MSP430 Sensor Interface Guide", font=title_font, bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=15)
    
    # Create notebook (tabs)
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # Overview tab
    overview_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(overview_frame, text="Overview")
    
    overview_text = scrolledtext.ScrolledText(overview_frame, wrap=tk.WORD, font=("Courier New", 11), 
                                              bg=TEXTBOX_BG, fg=TEXT_COLOR, borderwidth=0, relief=tk.FLAT)
    overview_text.pack(fill=tk.BOTH, expand=True, pady=10)
    overview_text.insert(tk.END, """MSP430 SENSOR INTERFACE GUIDE
============================

The MSP430 microcontroller can interface with a wide variety of sensors through its GPIO pins,
ADC inputs, and communication interfaces like I2C, SPI, and UART.

SENSOR CONNECTIONS:
------------------
1. Digital Sensors: Connect to GPIO pins (P1.x, P2.x, etc.)
2. Analog Sensors: Connect to ADC input pins (typically P1.0-P1.7 on many MSP430 variants)
3. I2C Sensors: Connect to UCB0SDA and UCB0SCL pins (typically P1.6 and P1.7)
4. SPI Sensors: Connect to UCB0SIMO, UCB0SOMI, UCB0CLK, and a GPIO pin for chip select

Common Sensor Types:
------------------
1. Temperature sensors (DS18B20, TMP36, LM35)
2. Humidity sensors (DHT11, DHT22, SHT21)
3. Pressure sensors (BMP180, BMP280)
4. Light sensors (LDR, TSL2561)
5. Motion sensors (PIR, ultrasonic)
6. Accelerometers and gyroscopes (MPU6050, ADXL345)

BASIC CONNECTION GUIDELINES:
--------------------------
1. Always connect sensor VCC to MSP430 VCC (3.3V or 5V depending on sensor)
2. Connect sensor GND to MSP430 GND
3. For digital sensors, connect to GPIO pins
4. For analog sensors, connect to ADC input pins
5. Use pull-up or pull-down resistors as needed

See the other tabs for specific examples and code.
""")
    overview_text.config(state=tk.DISABLED)
    
    # DHT11 Temperature/Humidity sensor tab
    dht11_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(dht11_frame, text="DHT11 Sensor")
    
    dht11_text = scrolledtext.ScrolledText(dht11_frame, wrap=tk.WORD, font=("Courier New", 11), 
                                          bg=TEXTBOX_BG, fg=TEXT_COLOR, borderwidth=0, relief=tk.FLAT)
    dht11_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    dht11_code = """#include <msp430.h>
#include <stdint.h>

// DHT11 Temperature and Humidity Sensor Example
// Connect DHT11 data pin to P1.4

// Define DHT11 data pin
#define DHT11_PIN BIT4
#define DHT11_PORT P1OUT
#define DHT11_DIR P1DIR
#define DHT11_IN P1IN

// Variables for storing sensor data
uint8_t humidity = 0;
uint8_t temperature = 0;
uint8_t checksum = 0;

// Function prototypes
void initMSP430(void);
uint8_t readDHT11(void);
void delay_ms(unsigned int ms);
void delay_us(unsigned int us);

void main(void)
{
    initMSP430();
    
    while(1)
    {
        if(readDHT11() == 0) // 0 means success
        {
            // Data is available in humidity and temperature variables
            // Process data or send to display/UART
            
            // Example: Toggle LED on successful read
            P1OUT ^= BIT0;
        }
        
        // Wait about 2 seconds between readings
        delay_ms(2000);
    }
}

void initMSP430(void)
{
    WDTCTL = WDTPW | WDTHOLD;   // Stop watchdog timer
    
    // Setup LED on P1.0 for status
    P1DIR |= BIT0;
    P1OUT &= ~BIT0;
    
    // Initial DHT11 pin setup (output high)
    DHT11_DIR |= DHT11_PIN;
    DHT11_PORT |= DHT11_PIN;
    
    // Wait for DHT11 to stabilize
    delay_ms(1000);
}

uint8_t readDHT11(void)
{
    uint8_t bits[5] = {0}; // Data array: [humidity_int, humidity_dec, temp_int, temp_dec, checksum]
    uint8_t i, j;
    
    // Start signal: pull low for at least 18ms
    DHT11_DIR |= DHT11_PIN;   // Set as output
    DHT11_PORT &= ~DHT11_PIN; // Pull low
    delay_ms(20);             // Hold low for 20ms
    
    // End start signal and wait for response
    DHT11_PORT |= DHT11_PIN;  // Pull high
    delay_us(30);             // Wait 30us
    
    // Set pin as input to read response
    DHT11_DIR &= ~DHT11_PIN;
    
    // Check for DHT11 presence pulse
    if((DHT11_IN & DHT11_PIN) == 0) {
        // Wait for DHT11 to pull low (80us)
        delay_us(80);
        
        // Check if DHT11 pulled high
        if((DHT11_IN & DHT11_PIN) != 0) {
            // Wait for DHT11 to pull low again
            delay_us(80);
            
            // Now read 40 bits (5 bytes)
            for(i = 0; i < 5; i++) {
                for(j = 0; j < 8; j++) {
                    // Wait for rising edge
                    while((DHT11_IN & DHT11_PIN) == 0);
                    
                    // Delay ~30us and check if bit is 1 or 0
                    delay_us(30);
                    
                    // If pin is high after 30us, bit is 1
                    if((DHT11_IN & DHT11_PIN) != 0) {
                        bits[i] |= (1 << (7-j));
                        
                        // Wait for pin to go low for next bit
                        while((DHT11_IN & DHT11_PIN) != 0);
                    }
                }
            }
            
            // Store values
            humidity = bits[0];
            temperature = bits[2];
            checksum = bits[4];
            
            // Verify checksum
            if(bits[0] + bits[1] + bits[2] + bits[3] == bits[4]) {
                return 0; // Success
            }
        }
    }
    
    return 1; // Error
}

void delay_ms(unsigned int ms)
{
    while(ms--)
    {
        __delay_cycles(1000); // Adjust based on your CPU frequency
    }
}

void delay_us(unsigned int us)
{
    while(us--)
    {
        __delay_cycles(1); // Adjust based on your CPU frequency
    }
}"""
    
    dht11_text.insert(tk.END, "DHT11 TEMPERATURE/HUMIDITY SENSOR\n")
    dht11_text.insert(tk.END, "===============================\n\n")
    dht11_text.insert(tk.END, "Connection:\n")
    dht11_text.insert(tk.END, "- VCC: Connect to 3.3V or 5V\n")
    dht11_text.insert(tk.END, "- GND: Connect to GND\n")
    dht11_text.insert(tk.END, "- DATA: Connect to P1.4 with a 4.7K pull-up resistor\n\n")
    dht11_text.insert(tk.END, "Example Code:\n\n")
    dht11_text.insert(tk.END, dht11_code)
    
    # Add a button to load this example code
    button_frame = tk.Frame(dht11_frame, bg=BG_COLOR)
    button_frame.pack(pady=10)
    
    load_button = tk.Button(button_frame, text="Load This Example", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=lambda: load_example_to_editor(dht11_code))
    load_button.pack()
    
    # Analog Sensors tab
    analog_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(analog_frame, text="Analog Sensors")
    
    analog_text = scrolledtext.ScrolledText(analog_frame, wrap=tk.WORD, font=("Courier New", 11), 
                                           bg=TEXTBOX_BG, fg=TEXT_COLOR, borderwidth=0, relief=tk.FLAT)
    analog_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    analog_code = """#include <msp430.h>
#include <stdint.h>

// Analog Sensor Example (LDR Light Sensor)
// Connect analog sensor to P1.3 (A3)

// Variables for storing sensor data
uint16_t adc_value = 0;

// Function prototypes
void initMSP430(void);
void initADC(void);
uint16_t readADC(void);

void main(void)
{
    initMSP430();
    initADC();
    
    while(1)
    {
        // Read ADC value
        adc_value = readADC();
        
        // Simple threshold detection
        if(adc_value > 512) {
            // High light level detected
            P1OUT |= BIT0;  // Turn on LED
        } else {
            // Low light level detected
            P1OUT &= ~BIT0; // Turn off LED
        }
        
        // Wait before next reading
        __delay_cycles(100000);
    }
}

void initMSP430(void)
{
    WDTCTL = WDTPW | WDTHOLD;   // Stop watchdog timer
    
    // Setup LED on P1.0 for status
    P1DIR |= BIT0;
    P1OUT &= ~BIT0;
}

void initADC(void)
{
    // Configure ADC
    ADC10CTL0 = SREF_0 + ADC10SHT_2 + ADC10ON;  // Ref=VCC, 16 clock cycles, ADC on
    ADC10CTL1 = INCH_3;                         // Input channel A3 (P1.3)
    ADC10AE0 |= BIT3;                           // Enable analog input on P1.3
}

uint16_t readADC(void)
{
    // Start conversion
    ADC10CTL0 |= ENC + ADC10SC;
    
    // Wait for conversion to complete
    while(ADC10CTL1 & ADC10BUSY);
    
    // Return result
    return ADC10MEM;
}"""
    
    analog_text.insert(tk.END, "ANALOG SENSORS\n")
    analog_text.insert(tk.END, "==============\n\n")
    analog_text.insert(tk.END, "Common Analog Sensors:\n")
    analog_text.insert(tk.END, "- Light sensors (LDR, photoresistors)\n")
    analog_text.insert(tk.END, "- Temperature sensors (TMP36, LM35)\n")
    analog_text.insert(tk.END, "- Force sensitive resistors (FSR)\n")
    analog_text.insert(tk.END, "- Gas sensors (MQ series)\n\n")
    analog_text.insert(tk.END, "Connection:\n")
    analog_text.insert(tk.END, "- VCC: Connect to 3.3V\n")
    analog_text.insert(tk.END, "- GND: Connect to GND\n")
    analog_text.insert(tk.END, "- Signal: Connect to analog input pin (P1.0-P1.7)\n\n")
    analog_text.insert(tk.END, "For resistive sensors like LDR, use a voltage divider:\n")
    analog_text.insert(tk.END, "- Connect a 10K resistor between VCC and sensor\n")
    analog_text.insert(tk.END, "- Connect the junction of resistor and sensor to analog pin\n")
    analog_text.insert(tk.END, "- Connect other end of sensor to GND\n\n")
    analog_text.insert(tk.END, "Example Code (Light Sensor):\n\n")
    analog_text.insert(tk.END, analog_code)
    
    # Add a button to load this example code
    button_frame = tk.Frame(analog_frame, bg=BG_COLOR)
    button_frame.pack(pady=10)
    
    load_button = tk.Button(button_frame, text="Load This Example", bg=BUTTON_COLOR, fg=BUTTON_TEXT,
                            command=lambda: load_example_to_editor(analog_code))
    load_button.pack()
    
    # Helper function to load example code to editor
    def load_example_to_editor(code):
        if messagebox.askyesno("Load Example", "This will replace your current code. Continue?"):
            input_text.delete(1.0, tk.END)
            input_text.insert(tk.END, code)
            highlight_syntax()
            window.destroy()

# Registerlara ait değerleri tutacak global değişkenler
register_values = {f"{i}": 0 for i in range(16)}  # R0 - R15 değerleri
cycles_count = 0  # Döngü sayısı
loop_detection = {}  # Sonsuz döngü tespiti için
memory_values = {}  # Bellek değerleri

def simulate_code(step_by_step=False, max_cycles_limit=1000):
    """Simulate assembly code and update register values"""
    global cycles_count, register_values, loop_detection
    
    # Input textinden kodu al
    code = input_text.get("1.0", tk.END)
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    
    # Loop detection için değişkenler
    cycles_count = 0
    loop_detection = {}
    max_cycles = max_cycles_limit  # Maksimum döngü sayısı
    
    # Program counter başlangıç değeri
    pc = 0
    
    # Etiketleri topla
    labels = {}
    for i, line in enumerate(lines):
        if ":" in line:
            label = line.split(":")[0].strip()
            labels[label] = i
    
    # Adım adım izleme
    if step_by_step:
        sim_window = tk.Toplevel()
        sim_window.title("Simulation Viewver")
        sim_window.geometry("600x500")
        sim_window.configure(bg=BG_COLOR)
        
        # Başlık
        title_label = tk.Label(sim_window,
                              text="MSP430 Simulation Viewer",
                          font=("Impact", 16),
                          bg=BG_COLOR,
                              fg=HEADER_COLOR)
        title_label.pack(pady=10)
        
        # Kod görüntüsü
        code_frame = tk.Frame(sim_window, bg=BG_COLOR)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        code_text = scrolledtext.ScrolledText(code_frame,
                                            wrap=tk.WORD,
                                            font=("Courier New", 11),
                                            bg=TEXTBOX_BG,
                                            fg=TEXT_COLOR,
                                            height=15)
        code_text.pack(fill=tk.BOTH, expand=True)
        
        # Registerleri göster
        register_frame = tk.Frame(sim_window, bg=BG_COLOR)
        register_frame.pack(fill=tk.X, padx=15, pady=5)
        
        reg_text = tk.Text(register_frame,
                          wrap=tk.WORD,
                          font=("Courier New", 11),
                          bg=TEXTBOX_BG,
                          fg=TEXT_COLOR,
                          height=4)
        reg_text.pack(fill=tk.X, pady=5)
        
        # Butonlar
        button_frame = tk.Frame(sim_window, bg=BG_COLOR)
        button_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # PC ve cycles_count için wrapper
        class SimState:
            def __init__(self):
                self.pc = pc
                self.cycles = cycles_count
        
        sim_state = SimState()
                
        def update_display():
            # Kodu göster, mevcut satırı vurgula
            code_text.delete("1.0", tk.END)
            for i, line in enumerate(lines):
                code_text.insert(tk.END, line + "\n")
                if i == sim_state.pc:
                    code_text.tag_add("current", f"{i+1}.0", f"{i+1}.end")
            
            code_text.tag_config("current", background="#3a3a3a", foreground="#ffffff")
            code_text.see(f"{sim_state.pc+1}.0")
            
            # Register değerlerini göster
            reg_text.delete("1.0", tk.END)
            reg_text.insert(tk.END, "PC: {}\tCycles: {}\n".format(sim_state.pc, sim_state.cycles))
            
            reg_values = []
            for i in range(16):
                if i % 4 == 0 and i > 0:
                    reg_values.append("\n")
                reg_values.append("R{}: {:04X}".format(i, register_values.get(str(i), 0)))
                if i % 4 != 3:
                    reg_values.append("\t")
            
            reg_text.insert(tk.END, "".join(reg_values))
        
        # İlk görüntüleme
        update_display()
        
        # Simülasyon işlemleri
        def step_simulation():
            if run_one_instruction():
                update_display()
            else:
                messagebox.showinfo("Info", "Simulation completed.")
                
        def run_simulation():
            run_flag = [True]  # Durma sinyali için
            
            def run_loop():
                if not run_flag[0]:
                    return
                    
                if run_one_instruction():
                    update_display()
                    sim_window.after(200, run_loop)  # Her 200ms'de bir tekrar
                else:
                    messagebox.showinfo("Info", "Simulation completed.")
            
            # Çalıştırma ve durdurma için buton
            def stop_simulation():
                run_flag[0] = False
                
            # Stop butonu güncelle
            stop_button.config(command=stop_simulation)
            
            # Simülasyonu başlat
            run_loop()
        
        # Butonlar
        step_button = tk.Button(button_frame, text="Step", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                               font=("Arial", 10), command=step_simulation)
        step_button.pack(side=tk.LEFT, padx=5)
        
        run_button = tk.Button(button_frame, text="Run", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                              font=("Arial", 10), command=run_simulation)
        run_button.pack(side=tk.LEFT, padx=5)
        
        stop_button = tk.Button(button_frame, text="Stop", bg=BUTTON_COLOR, fg=BUTTON_TEXT, 
                               font=("Arial", 10), command=lambda: show_register_viewer())
        stop_button.pack(side=tk.LEFT, padx=5)
        
        # Tek adım çalıştırma fonksiyonu - simülasyon adımı
        def run_one_instruction():
            global register_values
            
            if sim_state.pc < 0 or sim_state.pc >= len(lines) or sim_state.cycles >= max_cycles:
                return False
                
            current_line = lines[sim_state.pc].strip()
            
            # Sonsuz döngü tespiti
            if sim_state.pc in loop_detection:
                loop_detection[sim_state.pc] += 1
                if loop_detection[sim_state.pc] > 50:  # 50 defadan fazla aynı satır çalıştırılırsa
                    messagebox.showwarning("Uyarı", f"Possible infinite loop detected: {current_line}")
                    return False
            else:
                loop_detection[sim_state.pc] = 1
            
            # Etiketleri atla
            if ":" in current_line:
                parts = current_line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    current_line = parts[1].strip()
                else:
                    sim_state.pc += 1
                    sim_state.cycles += 1
                    return True
            
            # Boş satırları veya yorum satırlarını atla
            if not current_line or current_line.startswith(";"):
                sim_state.pc += 1
                sim_state.cycles += 1
                return True
            
            # Komutu çözümle
            parts = current_line.replace(",", " ").split()
            if not parts:
                sim_state.pc += 1
                sim_state.cycles += 1
                return True
            
            # Komut ve operandları al
            command = parts[0].upper()
            
            # Komutu işle
            if command == "MOV":
                if len(parts) >= 3:
                    src = parts[1]
                    dst = parts[2]
                    
                    # Kaynak değerini al
                    src_value = 0
                    if src.startswith("#"):
                        # Immediate değer
                        try:
                            if src[1:].startswith("0x"):
                                src_value = int(src[1:], 16)
                            elif src[1:].isdigit():
                                src_value = int(src[1:])
                            else:
                                src_value = int(src[1:])
                        except:
                            pass
                    elif src.startswith("R"):
                        # Register değeri
                        reg_num = src[1:]
                        src_value = register_values.get(reg_num, 0)
                    
                    # Hedef registera değeri yaz
                    if dst.startswith("R"):
                        reg_num = dst[1:]
                        register_values[reg_num] = src_value
            
            elif command == "ADD":
                if len(parts) >= 3:
                    src = parts[1]
                    dst = parts[2]
                    
                    # Kaynak değerini al
                    src_value = 0
                    if src.startswith("#"):
                        # Immediate değer
                        try:
                            if src[1:].startswith("0x"):
                                src_value = int(src[1:], 16)
                            elif src[1:].isdigit():
                                src_value = int(src[1:])
                            else:
                                src_value = int(src[1:])
                        except:
                            pass
                    elif src.startswith("R"):
                        # Register değeri
                        reg_num = src[1:]
                        src_value = register_values.get(reg_num, 0)
                    
                    # Hedef registera değeri ekle
                    if dst.startswith("R"):
                        reg_num = dst[1:]
                        register_values[reg_num] = (register_values.get(reg_num, 0) + src_value) & 0xFFFF  # 16-bit sınırı
                        
            elif command == "SUB":
                if len(parts) >= 3:
                    src = parts[1]
                    dst = parts[2]
                    
                    # Kaynak değerini al
                    src_value = 0
                    if src.startswith("#"):
                        # Immediate değer
                        try:
                            if src[1:].startswith("0x"):
                                src_value = int(src[1:], 16)
                            elif src[1:].isdigit():
                                src_value = int(src[1:])
                            else:
                                src_value = int(src[1:])
                        except:
                            pass
                    elif src.startswith("R"):
                        # Register değeri
                        reg_num = src[1:]
                        src_value = register_values.get(reg_num, 0)
                    
                    # Hedef registerdan değeri çıkar
                    if dst.startswith("R"):
                        reg_num = dst[1:]
                        register_values[reg_num] = (register_values.get(reg_num, 0) - src_value) & 0xFFFF  # 16-bit sınırı
            
            elif command == "INC":
                if len(parts) >= 2:
                    dst = parts[1]
                    if dst.startswith("R"):
                        reg_num = dst[1:]
                        register_values[reg_num] = (register_values.get(reg_num, 0) + 1) & 0xFFFF  # 16-bit sınırı
            
            elif command == "DEC":
                if len(parts) >= 2:
                    dst = parts[1]
                    if dst.startswith("R"):
                        reg_num = dst[1:]
                        register_values[reg_num] = (register_values.get(reg_num, 0) - 1) & 0xFFFF  # 16-bit sınırı
                        
            elif command == "RRC":
                if len(parts) >= 2:
                    dst = parts[1]
                    if dst.startswith("R"):
                        reg_num = dst[1:]
                        value = register_values.get(reg_num, 0)
                        c = value & 1  # LSB kaydır
                        value = (value >> 1) & 0x7FFF  # 15-bit sağa kaydır
                        
                        # Carry değerini SR(R2) registerına yaz
                        sr_value = register_values.get("2", 0)
                        if c:
                            sr_value |= 1  # Carry bit 0
                        else:
                            sr_value &= ~1  # Carry bit 0
                        register_values["2"] = sr_value
                        
                        # Sonucu yaz
                        register_values[reg_num] = value
                        
            elif command == "JMP":
                if len(parts) >= 2:
                    label = parts[1]
                    if label in labels:
                        sim_state.pc = labels[label]
                        sim_state.cycles += 1
                        return True  # PC değişti, döngü başına dön
            
            # Sonraki satıra geç
            sim_state.pc += 1
            sim_state.cycles += 1
            return True
        
        return  # step_by_step modunda return, simülasyon penceresi üzerinden işleme devam edilecek
    
    # Normal simülasyon (adım adım değil)
    while 0 <= pc < len(lines) and cycles_count < max_cycles:
        current_line = lines[pc].strip()
        
        # Sonsuz döngü tespiti
        if pc in loop_detection:
            loop_detection[pc] += 1
            if loop_detection[pc] > 50:  # 50 defadan fazla aynı satır çalıştırılırsa
                messagebox.showwarning("Uyarı", f"Possible infinite loop detected: {current_line}")
                break
        else:
            loop_detection[pc] = 1
        
        # Etiketleri atla
        if ":" in current_line:
            parts = current_line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                current_line = parts[1].strip()
            else:
                pc += 1
                continue
        
        # Boş satırları veya yorum satırlarını atla
        if not current_line or current_line.startswith(";"):
            pc += 1
            continue
        
        # Komutu çözümle
        parts = current_line.replace(",", " ").split()
        if not parts:
            pc += 1
            continue
        
        # Komut ve operandları al
        command = parts[0].upper()
        
        # Komutu işle
        if command == "MOV":
            if len(parts) >= 3:
                src = parts[1]
                dst = parts[2]
                
                # Kaynak değerini al
                src_value = 0
                if src.startswith("#"):
                    # Immediate değer
                    try:
                        if src[1:].startswith("0x"):
                            src_value = int(src[1:], 16)
                        elif src[1:].isdigit():
                            src_value = int(src[1:])
                        else:
                            src_value = int(src[1:])
                    except:
                        pass
                elif src.startswith("R"):
                    # Register değeri
                    reg_num = src[1:]
                    src_value = register_values.get(reg_num, 0)
                
                # Hedef registera değeri yaz
                if dst.startswith("R"):
                    reg_num = dst[1:]
                    register_values[reg_num] = src_value
        
        elif command == "ADD":
            if len(parts) >= 3:
                src = parts[1]
                dst = parts[2]
                
                # Kaynak değerini al
                src_value = 0
                if src.startswith("#"):
                    # Immediate değer
                    try:
                        if src[1:].startswith("0x"):
                            src_value = int(src[1:], 16)
                        elif src[1:].isdigit():
                            src_value = int(src[1:])
                        else:
                            src_value = int(src[1:])
                    except:
                        pass
                elif src.startswith("R"):
                    # Register değeri
                    reg_num = src[1:]
                    src_value = register_values.get(reg_num, 0)
                
                # Hedef registera değeri ekle
                if dst.startswith("R"):
                    reg_num = dst[1:]
                    register_values[reg_num] = (register_values.get(reg_num, 0) + src_value) & 0xFFFF  # 16-bit sınırı
                    
        elif command == "SUB":
            if len(parts) >= 3:
                src = parts[1]
                dst = parts[2]
                
                # Kaynak değerini al
                src_value = 0
                if src.startswith("#"):
                    # Immediate değer
                    try:
                        if src[1:].startswith("0x"):
                            src_value = int(src[1:], 16)
                        elif src[1:].isdigit():
                            src_value = int(src[1:])
                        else:
                            src_value = int(src[1:])
                    except:
                        pass
                elif src.startswith("R"):
                    # Register değeri
                    reg_num = src[1:]
                    src_value = register_values.get(reg_num, 0)
                
                # Hedef registerdan değeri çıkar
                if dst.startswith("R"):
                    reg_num = dst[1:]
                    register_values[reg_num] = (register_values.get(reg_num, 0) - src_value) & 0xFFFF  # 16-bit sınırı
        
        elif command == "INC":
            if len(parts) >= 2:
                dst = parts[1]
                if dst.startswith("R"):
                    reg_num = dst[1:]
                    register_values[reg_num] = (register_values.get(reg_num, 0) + 1) & 0xFFFF  # 16-bit sınırı
        
        elif command == "DEC":
            if len(parts) >= 2:
                dst = parts[1]
                if dst.startswith("R"):
                    reg_num = dst[1:]
                    register_values[reg_num] = (register_values.get(reg_num, 0) - 1) & 0xFFFF  # 16-bit sınırı
                    
        elif command == "RRC":
            if len(parts) >= 2:
                dst = parts[1]
                if dst.startswith("R"):
                    reg_num = dst[1:]
                    value = register_values.get(reg_num, 0)
                    c = value & 1  # LSB kaydır
                    value = (value >> 1) & 0x7FFF  # 15-bit sağa kaydır
                    
                    # Carry değerini SR(R2) registerına yaz
                    sr_value = register_values.get("2", 0)
                    if c:
                        sr_value |= 1  # Carry bit 0
                    else:
                        sr_value &= ~1  # Carry bit 0
                    register_values["2"] = sr_value
                    
                    # Sonucu yaz
                    register_values[reg_num] = value
                    
        elif command == "JMP":
            if len(parts) >= 2:
                label = parts[1]
                if label in labels:
                    pc = labels[label]
                    continue  # PC değişti, döngü başına dön
        
        # Sonraki satıra geç
        pc += 1
        cycles_count += 1
    
    if cycles_count >= max_cycles:
        messagebox.showwarning("Warning", "Reached maximum loop limit.Simulation stopped.")
    
    # Register değerlerini göster
    show_register_viewer()

def add_modification_test_code():
    """Add a test code for modification records and relocation"""
    test_code = """
; MSP430 Modification Records Test Code
; Bu örnek kod relocation ve modification records'u test eder

; Sabitler
PROGADDR    EQU 0x1000     ; Program başlangıç adresi
DATA_START  EQU 0x0200     ; Veri bölümü başlangıç adresi
RESULT_ADDR EQU 0x0210     ; Sonuç adresi

        ORG PROGADDR       ; Program başlangıç adresi

RESET:
        ; Stack Pointer ayarları
        MOV     #0x0400, SP        ; Stack pointer'ı ayarla
        
        ; Register temizleme
        MOV     #0, R4             ; R4 = 0
        MOV     #0, R5             ; R5 = 0
        
        ; Relocation testi için değerler
        MOV     #DATA_START, R6    ; R6 = DATA_START (relocation gerektirir)
        MOV     #RESULT_ADDR, R7   ; R7 = RESULT_ADDR (relocation gerektirir)
        
        ; Modification testi için değerler
        MOV     #0x1234, R8        ; R8 = 0x1234
        MOV     #0x5678, R9        ; R9 = 0x5678
        
        ; Relocation gerektiren bellek erişimleri
        MOV     R8, 0(R6)          ; DATA_START adresine R8'i yaz
        MOV     R9, 0(R7)          ; RESULT_ADDR adresine R9'u yaz
        
        ; Modification gerektiren işlemler
        ADD     #0x1000, R8        ; R8 += 0x1000 (modification gerektirir)
        SUB     #0x2000, R9        ; R9 -= 0x2000 (modification gerektirir)
        
        ; Sonuçları kaydet
        MOV     R8, 2(R6)          ; DATA_START+2 adresine R8'i yaz
        MOV     R9, 2(R7)          ; RESULT_ADDR+2 adresine R9'u yaz
        
        ; Sonsuz döngü
FOREVER:
        JMP     FOREVER            ; Sonsuz döngü
"""
    
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, test_code)
    highlight_syntax()
    status_var.set("Modification test code added.")

def add_directive_test_code():
    test_code = """; Advanced MSP430 Assembly Code Example
; Demonstrates usage of various literal types, loops, interrupts, and macros

; Text section (BLOCKTAB)
.TEXT
    ; Initialize constants (LITTAB)
    MOV     #0x2000, R4    ; Hex immediate
    MOV     #500, R5       ; Decimal immediate
    MOV     #0xAA, R6      ; Another hex immediate
    
    ; EQU constants (LITTAB)
MAX_VALUE   EQU     0x8000
DELAY_CNT   EQU     0x1000
    
    ; Using EQU constants for calculation
    ADD     #MAX_VALUE, R7 ; Add constant to register
    MOV     #DELAY_CNT, R8 ; Set delay constant
    
    ; Setting up Stack Pointer (SP)
    MOV     #0x3000, SP    ; Stack pointer initialization
    
    ; Loop to create a delay (Basic for-loop simulation)
LOOP_DELAY:
    DEC     R8             ; Decrease delay counter
    JNE     LOOP_DELAY     ; Jump if not equal (R8 != 0)
    
    ; Set up a flag for a loop (setting bits to indicate loop finished)
    BIS     #0x01, R6      ; Bit set to flag completion
    
    ; Enable interrupts globally
    EINT                    ; Enable global interrupt flag
    
    ; Data section (BLOCKTAB)
.DATA
    .WORD   0x1234         ; Word data (16-bit value)
    .BYTE   0x56           ; Byte data (8-bit value)
    .CHAR   'M'            ; Single character
    .STRING "Assembly Demo" ; String data
    
    ; Load data into registers (showing addressing modes)
    MOV     &0x0100, R9    ; Load word from address 0x0100
    MOV.B   &0x0102, R10   ; Load byte from address 0x0102
    
    ; Initialize interrupt vector section
.INTVEC
    .WORD   RESET_VECTOR    ; Reset vector
    .WORD   INT_VECTOR_1    ; Interrupt vector 1
    .WORD   INT_VECTOR_2    ; Interrupt vector 2
    
; BSS section (BLOCKTAB)
.BSS
    .SPACE  20             ; Allocate 20 bytes of space for uninitialized data
    .RESERVE 4             ; Reserve space for another 4 bytes
    
    ; Allocate space for a flag variable
    .BYTE   0             ; Reserved byte for a flag (initial value 0)
    
; Custom section (BLOCKTAB)
.SECT "CUSTOM"
    ; Complex mathematical operation (LITTAB)
    MOV     #100, R11     ; Decimal immediate
    MUL     R11, R12      ; Multiply R11 by R12 (result in R12)
    
    ; String manipulation
    .STRING "Advanced MSP430"   ; A longer string in data section
    .CHAR   '?'                   ; Character for testing
    
    ; Conditional branch with flag checking
    TST     &0x0200        ; Test value at address 0x0200
    JZ      FLAG_ZERO      ; Jump if zero flag is set
    
    ; Set some flags
FLAG_ZERO:
    BIS     #0x02, R6      ; Set another flag bit in R6
    
    ; Custom delay routine with loop
CUSTOM_DELAY:
    MOV     #0x10, R8      ; Load delay count
    DEC_LOOP:
        DEC     R8         ; Decrement delay counter
        JNE     DEC_LOOP   ; Loop until counter reaches 0
    
    ; Back to text section (BLOCKTAB)
.TEXT
    JMP     $             ; Infinite loop (end of program)

; Interrupt vector definitions
RESET_VECTOR:
    NOP                     ; No operation (for simplicity)

INT_VECTOR_1:
    NOP                     ; Placeholder for interrupt vector 1

INT_VECTOR_2:
    NOP                     ; Placeholder for interrupt vector 2
"""
    input_text.delete("1.0", tk.END)
    input_text.insert("1.0", test_code)
    highlight_syntax()

def add_littab_blocktab_test_code():
    """Add test code for LITTAB and BLOCKTAB demonstration"""
    test_code = """
; LITTAB and BLOCKTAB Test Code
; Demonstrates various literal types and sections in MSP430 assembly

; Text section (BLOCKTAB)
.TEXT
    ; Immediate values (LITTAB)
    MOV     #0x1234, R4    ; Hex immediate
    MOV     #100, R5       ; Decimal immediate
    
    ; EQU constants (LITTAB)
MAX_COUNT   EQU     0x100
DELAY_TIME  EQU     0x5000
    
    ; Using EQU constants
    MOV     #MAX_COUNT, R7
    MOV     #DELAY_TIME, R8
    
    ; Data section (BLOCKTAB)
.DATA
    ; Value initialization directives (LITTAB)
    .WORD   0x5678     ; 16-bit value
    .BYTE   0x9A       ; 8-bit value
    .CHAR   'B'        ; Character
    .STRING "Hello"    ; String
    
    ; Using initialized values
    MOV     &0x0200, R9    ; Load word value
    MOV.B   &0x0202, R10   ; Load byte value
    
; BSS section (BLOCKTAB)
.BSS
    ; Uninitialized data
    .SPACE  10         ; 10 bytes of space
    
; Interrupt vector section (BLOCKTAB)
.INTVEC
    .WORD   START      ; Reset vector
    .WORD   INT1       ; Interrupt 1
    .WORD   INT2       ; Interrupt 2
    
; Custom section (BLOCKTAB)
.SECT "CUSTOM"
    ; More immediate values (LITTAB)
    ADD     #0xFFFF, R11   ; Hex immediate
    SUB     #-1, R12       ; Decimal immediate
    
    ; String and character data (LITTAB)
    .STRING "MSP430"   ; String in data section
    .CHAR   '!'        ; Character in data section
    
; Back to text section (BLOCKTAB)
.TEXT
    ; End of program
    JMP     $
"""
    input_text.delete("1.0", tk.END)
    input_text.insert("1.0", test_code)
    highlight_syntax()

# BLOCKTAB ve LITTAB için pencere fonksiyonları
def show_blocktab_window():
    """BLOCKTAB penceresini göster"""
    blocktab_window = tk.Toplevel()
    blocktab_window.title("BLOCKTAB")
    blocktab_window.geometry("600x400")
    blocktab_window.configure(bg=BG_COLOR)
    
    # Pencereyi ekranın ortasına konumlandır
    screen_width = blocktab_window.winfo_screenwidth()
    screen_height = blocktab_window.winfo_screenheight()
    x = (screen_width - 600) // 2
    y = (screen_height - 400) // 2
    blocktab_window.geometry(f"600x400+{x}+{y}")
    
    # Başlık etiketi
    title_label = tk.Label(blocktab_window, text="BLOCK TABLE", 
                          font=("Courier New", 12, "bold"),
                          bg=BG_COLOR, fg=KEYWORD_COLOR)
    title_label.pack(pady=10)
    
    # BLOCKTAB içeriği için kaydırılabilir metin kutusu
    blocktab_text = scrolledtext.ScrolledText(blocktab_window, wrap=tk.WORD,
                                           font=("Courier New", 11),
                                           bg=TEXTBOX_BG, fg=TEXT_COLOR)
    blocktab_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # BLOCKTAB içeriğini doldur
    blocktab_text.config(state=tk.NORMAL)
    blocktab_text.delete("1.0", tk.END)
    
    # Mevcut blok bilgisi
    if "current_block" in symtab:
        blocktab_text.insert(tk.END, "CURRENT BLOCK:\n", "header")
        blocktab_text.insert(tk.END, f"  Name: {symtab['current_block']}\n\n", "content")
    
    # Tüm bloklar
    if "blocktab" in symtab and symtab["blocktab"]:
        blocktab_text.insert(tk.END, "ALL BLOCKS:\n", "header")
        for block_name, block_info in symtab["blocktab"].items():
            blocktab_text.insert(tk.END, f"  Block: {block_name}\n", "subheader")
            blocktab_text.insert(tk.END, f"    Type: {block_info.get('type', 'N/A')}\n", "content")
            blocktab_text.insert(tk.END, f"    Address: {block_info.get('address', 0):04X}h\n\n", "content")
    else:
        blocktab_text.insert(tk.END, "No blocks defined.\n", "content")
    
    # Etiketlerin stilini yapılandır
    blocktab_text.tag_configure("header", foreground=KEYWORD_COLOR, font=("Courier New", 11, "bold"))
    blocktab_text.tag_configure("subheader", foreground=REGISTER_COLOR, font=("Courier New", 11, "bold"))
    blocktab_text.tag_configure("content", foreground=TEXT_COLOR, font=("Courier New", 11))
    
    blocktab_text.config(state=tk.DISABLED)

def show_littab_window():
    """LITTAB penceresini göster"""
    littab_window = tk.Toplevel()
    littab_window.title("LITTAB")
    littab_window.geometry("600x400")
    littab_window.configure(bg=BG_COLOR)
    
    # Pencereyi ekranın ortasına konumlandır
    screen_width = littab_window.winfo_screenwidth()
    screen_height = littab_window.winfo_screenheight()
    x = (screen_width - 600) // 2
    y = (screen_height - 400) // 2
    littab_window.geometry(f"600x400+{x}+{y}")
    
    # Başlık etiketi
    title_label = tk.Label(littab_window, text="LITERAL TABLE", 
                          font=("Courier New", 12, "bold"),
                          bg=BG_COLOR, fg=KEYWORD_COLOR)
    title_label.pack(pady=10)
    
    # LITTAB içeriği için kaydırılabilir metin kutusu
    littab_text = scrolledtext.ScrolledText(littab_window, wrap=tk.WORD,
                                         font=("Courier New", 11),
                                         bg=TEXTBOX_BG, fg=TEXT_COLOR)
    littab_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # LITTAB içeriğini doldur
    littab_text.config(state=tk.NORMAL)
    littab_text.delete("1.0", tk.END)
    
    # Havuz bilgisi
    littab_text.insert(tk.END, "LITERAL POOL INFORMATION:\n", "header")
    
    # Tüm sabitler
    if "littab" in symtab and symtab["littab"]:
        littab_text.insert(tk.END, "\nLITERALS:\n", "header")
        for lit_id, lit_info in symtab["littab"].items():
            littab_text.insert(tk.END, f"  Literal: {lit_id}\n", "subheader")
            littab_text.insert(tk.END, f"    Value: {lit_info.get('value', 0)}\n", "content")
            littab_text.insert(tk.END, f"    Type: {lit_info.get('type', 'N/A')}\n", "content")
            littab_text.insert(tk.END, f"    Address: {lit_info.get('address', 0):04X}h\n\n", "content")
    else:
        littab_text.insert(tk.END, "No literals defined.\n", "content")
    
    # Etiketlerin stilini yapılandır
    littab_text.tag_configure("header", foreground=KEYWORD_COLOR, font=("Courier New", 11, "bold"))
    littab_text.tag_configure("subheader", foreground=REGISTER_COLOR, font=("Courier New", 11, "bold"))
    littab_text.tag_configure("content", foreground=TEXT_COLOR, font=("Courier New", 11))
    
    littab_text.config(state=tk.DISABLED)

def show_simulator(parent=None):
    """MSP430 simülatörünü gösterir - basitleştirilmiş sürüm"""
    global memory_values
    
    try:
        # Önce derleme/dönüştürme işlemini yap
        if not memory_values:
            convert_all()  # Kodları önce dönüştür
            
        # Hala bellek değerleri yoksa basit bir örnek ekle
        if not memory_values:
            # Basit LED yakıp söndüren test kodu
            memory_values = {
                0x0200: 0x40B2,  # MOV #FF, &0x0022 (P1DIR)
                0x0202: 0x00FF,
                0x0204: 0x0022,
                0x0206: 0x40B2,  # MOV #FF, &0x0021 (P1OUT) - LED'leri yak
                0x0208: 0x00FF,
                0x020A: 0x0021
            }
        
        # Yeni bir toplevel pencere oluştur
        sim_window = tk.Toplevel(root)
        sim_window.title("MSP430 Simülatör")
        sim_window.geometry("1000x800")
        sim_window.configure(bg="#0a0a0a")
        
        # Simülatörü doğrudan bu pencereye oluştur
        simulator = msp430_simulator.MSP430Simulator(sim_window)
        
        # Bellek değerlerini simülatöre yükle
        simulator.memory = memory_values.copy()
            
        # Bilgi mesajları
        simulator.write_to_terminal("MSP430 Simülatörü başarıyla başlatıldı.")
        simulator.write_to_terminal(f"Toplam {len(memory_values)} bellek adresi yüklendi.")
        simulator.write_to_terminal("'Simülasyonu Başlat' butonuna tıklayarak LED kontrol simülasyonunu başlatabilirsiniz.")
        
        return simulator
        
    except Exception as e:
        messagebox.showerror("Simülatör Hatası", f"Simülatör açılırken bir hata oluştu: {str(e)}")
        traceback.print_exc()
        return None

# Ana başlangıç noktası
if __name__ == "__main__":
    root = create_gui()
    
    # Call highlight_syntax function after GUI is created
    highlight_syntax()
    
    # Update GUI with new menu items
    update_gui()
    
    # Donanım entegrasyonu menüsünü ekle
    if 'HARDWARE_AVAILABLE' in globals() and HARDWARE_AVAILABLE:
        try:
            msp430_integration.integrate_hardware_interface(root)
            print("MSP430 donanım entegrasyonu başarıyla eklendi.")
        except Exception as e:
            print(f"Donanım entegrasyonu hatası: {str(e)}")
    
    # Simülatör butonu ekle
    simulate_frame = tk.Frame(root, bg=BG_COLOR)
    simulate_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
    
    simulate_button = tk.Button(simulate_frame, 
                             text="Open Simulator", 
                             font=("Arial", 12, "bold"),
                             bg="#4CAF50", 
                             fg="#ffffff", 
                             padx=20, 
                             pady=10,
                             command=lambda: show_simulator(root))
    simulate_button.pack(pady=10)
    
    # Kullanıcıya simülatör hakkında bilgi
    simulate_label = tk.Label(simulate_frame,
                           text="you can open simulator after converting code.",
                           font=("Arial", 10),
                           bg=BG_COLOR,
                           fg="#dddddd")
    simulate_label.pack(pady=5)
    
    # Örnek kod yükle
    example_code = """; MSP430 LED Kontrol Kodu
; Bu kod 8 LED'i sırayla yakıp söndürür

    ORG     0x0200          ; Programı 0x0200 adresinden başlat
    
    MOV     #0, R5          ; R5 = LED sayacı
    MOV     #8, R6          ; R6 = Toplam LED sayısı
    MOV     #0xFFFF, R7     ; R7 = Gecikme değeri
    
LOOP:
    MOV     #1, R4          ; R4 = LED durumu (1 = açık)
    
    ; LED durumunu port çıkışına yaz (gerçek donanımda P1OUT olurdu)
    ADD     R5, R5          ; LED pozisyonunu hesapla (2^R5)
    MOV     R4, &0x0210     ; LED'i yak
    
    ; Gecikme rutini
    MOV     R7, R8          ; Gecikme sayacını yükle
DELAY:
    DEC     R8              ; Sayacı azalt
    JNZ     DELAY           ; Sıfır değilse döngüye devam et
    
    MOV     #0, &0x0210     ; LED'i söndür
    
    INC     R5              ; Sonraki LED'e geç
    CMP     R6, R5          ; Son LED'e ulaştık mı?
    JL      LOOP            ; Hayır, döngüye devam et
    
    MOV     #0, R5          ; LED sayacını sıfırla
    JMP     LOOP            ; Döngüyü baştan başlat
"""
    if input_text:
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, example_code)
        highlight_syntax()
    
    status_var.set("Hazır - Örnek LED kontrol kodu yüklendi")
    
    # Başlat
    root.mainloop()