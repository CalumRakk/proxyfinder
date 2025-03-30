# ProxyFinder

A Python script to find, check, and manage HTTP proxies with a command-line interface (CLI).

## Features

- **Find Proxies:** Scrapes proxies from multiple online sources.
- **Check Proxies:** Verifies the functionality of the proxies.
- **Store Proxies:** Stores proxies and their status in a SQLite database.
- **Manage Proxies:** Provides commands to filter, display, and export proxies.

## Installation

Install the package and its dependencies using `pip`:

```bash
pip install git+https://github.com/CalumRakk/proxyfinder
```

## Usage

The script is executed from the command line using the `proxyfinder` command followed by the action you want to perform and any relevant options.

### Command Overview

The general structure of the commands is:

```bash
proxyfinder <command> [options]
```

### Available Commands:

1.  **`find`:** Finds and adds new proxies to the database.

    ```bash
    proxyfinder find [--concurrency <num>]
    ```

    - `--concurrency <num>` (optional): Number of threads to use for searching. Defaults to 10.

    This command searches for new proxies in the configured sources and adds them to the database. It doesn't verify proxy servers, so you must use the check command.

    **Example:**

    ```bash
    proxyfinder find
    ```

    This command finds new proxies

2.  **`check`:** Checks the status of proxies.

    ```bash
    proxyfinder check [--status <status>] [--concurrency <num>] [--older-than <days>]
    ```

    - `--status <status>` (optional): Filters the proxies to check based on their status. Possible values: `working`, `broken`, `unchecked`, or `all`. Defaults to `working`.
    - `--concurrency <num>` (optional): Number of threads to use for checking. Defaults to 10.
    - `--older-than <days>` (optional): Only check proxies that haven't been checked in the last N days. Defaults to 0 (checks all proxies).

    This command verifies the functionality of the proxies in the database and updates their status (working/broken).

    **Examples:**

    ```bash
    proxyfinder check --status unchecked
    proxyfinder check --older-than 7
    ```

    The first command checks all unchecked proxies. The second command checks proxies that haven't been checked in the last 7 days.

3.  **`show`:** Displays proxies from the database in a paginated format on the terminal.

    ```bash
    proxyfinder show [--status <status>] [--limit <num>] [--count] [--sort-by <field>] [--reverse] [--older-than <days>]
    ```

    - `--status <status>` (optional): Filters proxies by status. Possible values: `working`, `broken`, `unchecked`, or `all`. Defaults to `working`.
    - `--limit <num>` (optional): Limits the number of proxies to display.
    - `--count` (optional): Displays only the number of proxies instead of showing the full list.
    - `--sort-by <field>` (optional): Sorts proxies by the specified field. Possible values: `latency`, `created_at`, `updated_at`. Defaults to `latency`.
    - `--reverse` (optional): Reverses the sorting order.

    - `--older-than <days>` (optional): Show only the proxies that has passed that days.

    **Examples:**

    ```bash
    proxyfinder show --status working --limit 20 --sort-by latency --reverse
    proxyfinder show --status all --count
    ```

    The first command displays the 20 best working proxies ordered by latency in reverse. The second command shows the total number of proxies in the database.

4.  **`export`:** Exports proxies to a CSV file.

    ```bash
    proxyfinder export <output_file> [--all]
    ```

    - `<output_file>` (required): The path to the output CSV file.
    - `--all` (optional): Exports all proxies, not just working ones.

    This command exports the selected proxies to a CSV file.

    **Examples:**

    ```bash
    proxyfinder export working_proxies.csv
    proxyfinder export all_proxies.csv --all
    ```

    The first command exports only working proxies to `working_proxies.csv`. The second command exports all proxies to `all_proxies.csv`.

5.  **`update`:** Finds new proxies and checks the found proxies.

    ```bash
    proxyfinder update [--concurrency <num>]
    ```

    - `--concurrency <num>` (optional): Number of threads to use for searching and checking. Defaults to 10.

    This command combines the `find` and `check` commands. First, it finds the new proxies and then checks these proxies.

    **Example:**

    ```bash
    proxyfinder update --concurrency 15
    ```

    This command finds and checks new proxies, using 15 threads for both operations.

**Tips for using the CLI:**

- Use `proxyfinder help <command>` to get detailed help for a specific command.
- Be mindful of the `--concurrency` parameter. Although the thread count is adjusted based on system resources, using too many threads may still lead to overload.
- Regularly run `proxyfinder check` to keep your proxy list up-to-date.
