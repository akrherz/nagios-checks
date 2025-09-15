# Run every script in scripts and ensure an exit status of 0, 1, or 2
set -x

finalexit = 0

for script in scripts/*.py; do
    echo "Running $script"
    # Run the script and capture the STDERR to a variable called se
    se=$(python "$script" 2>&1)
    # If "Traceback" is found in se, we have a problem
    if echo "$se" | grep -q "Traceback"; then
        echo "Script $script produced a traceback:"
        finalexit = 1
    fi
    status=$?
    if [[ $status -ne 0 && $status -ne 1 && $status -ne 2 ]]; then
        echo "Script $script exited with unexpected status $status"
        exit 1
    fi
done

exit $finalexit
