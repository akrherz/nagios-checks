# Run every script in scripts and ensure an exit status of 0, 1, or 2

for script in scripts/*; do
    echo "Running $script"
    python $script
    status=$?
    if [[ $status -ne 0 && $status -ne 1 && $status -ne 2 ]]; then
        echo "Script $script exited with unexpected status $status"
        exit 1
    fi
done
