import subprocess


def run_prolog(file_path, query):
    result = subprocess.run(
        [
            "swipl",
            "-q",
            "-s", file_path,
            "-g", query,
            "-t", "halt"
        ],
        capture_output=True,
        text=True
    )

    return result


result = run_prolog(
    "src/prolog/pro-test.pl",
    "animal(tom)"
)

print("Return code:", result.returncode)
print("Output:", result.stdout)
print("Errors:", result.stderr)