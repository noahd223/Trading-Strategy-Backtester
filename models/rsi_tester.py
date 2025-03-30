# used for testing the rsi model run from parent directory of project using python .\models\rsi_tester.py
# after configuring the rsi_model.py
import subprocess
import re
import numpy as np

# Number of times to run the optimizer
num_runs = 10
return_differences = []

for i in range(num_runs):
    print(f"Running iteration {i+1}/{num_runs}...")
    
    # Run the optimizer module and capture output
    result = subprocess.run(["python", "-m", "models.rsi_model"], capture_output=True, text=True)
    print(result)
    # Extract return difference from output using regex
    match = re.search(r"Return Difference:\s*([-\d.]+)%", result.stdout)
    
    if match:
        return_diff = float(match.group(1))
        return_differences.append(return_diff)
    else:
        print("Warning: Could not extract return difference from output.")

# Compute statistics
max_return_diff = max(return_differences)
min_return_diff = min(return_differences)
avg_return_diff = np.mean(return_differences)

# Print results
print("\n===== Summary of 30 Runs =====")
print(f"Max Return Difference: {max_return_diff:.2f}%")
print(f"Min Return Difference: {min_return_diff:.2f}%")
print(f"Avg Return Difference: {avg_return_diff:.2f}%")
