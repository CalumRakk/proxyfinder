# ProxyFinder

A Python script to find and verify HTTP proxies.

## Installation

Install the package and its dependencies using `pip`:

```bash
pip install git+https://github.com/CalumRakk/proxyfinder
```

## Usage

The script can be executed from the command line using the `proxyfinder` command followed by the action you want to perform and the corresponding options.

### **`check`:** Finds and verifies proxies

```bash
proxyfinder check
```

This command does not require additional arguments.

### **`export`:** Exports the proxies to a CSV file.

```bash
proxyfinder export <location> [--all]
```

- `<location>` (optional): The location of the CSV file to which the proxies will be exported (e.g., `proxies.csv` or `my_directory/proxies.csv`). If not specified, the default filename `proxies.csv` will be used and saved in the current working directory.

- `--all` (optional): A flag to export _all_ proxies from the database, regardless of whether they are working or not. If not specified, only proxies that have been verified and are considered to be working will be exported.

## Usage examples:

- **Verify proxies:**

  ```bash
  proxyfinder check
  ```

  This command will start the process of finding and verifying proxies, updating the database with the results.

- **Export functional proxies to a specific location (`my_file.csv`):**

  ```bash
  proxyfinder export my_file.csv
  ```

  This command will export the functional proxies to the `my_file.csv` file in the current directory.

- **Export _all_ proxies to a specific location (`all_proxies.csv`):**

  ```bash
  proxyfinder export all_proxies.csv --all
  ```

  This command will export _all_ proxies from the database (including non-working ones) to the `all_proxies.csv` file in the current directory.
