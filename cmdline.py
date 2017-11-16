from pyTIS.cpu import CPU

if __name__ == "__main__":
    program = [
        "MOV 100 ACC",
        "LOOP:",
        "SUB 1",
        "JNZ LOOP"
    ]

    program = [
        "MOV 100 ACC",
        "LOOP:",
        "SWP",
        "ADD 1",
        "SWP",
        "SUB 1",
        "JNZ LOOP"
    ]

    cpu = CPU()
    cpu.setprogram(program)
    cpu.run()
    sys.exit()
