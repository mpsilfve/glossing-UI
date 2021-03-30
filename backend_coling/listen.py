# file watch 
dynet_seed = 42  # Load that from the JSON
run_command([
    "python", "run_transducer.py",
    "--dynet-seed", dynet_seed,
    "--dynet-mem", "1000"
])