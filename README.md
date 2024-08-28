Below is a sample `README.md` file for the script you provided:

```markdown
# UDP/RTP Link Testing Script

## Overview

This script is designed to test UDP and RTP links provided in M3U playlist files. It supports testing individual links or entire playlists, logging results, generating CSV reports, and optionally sending those reports via email.

## Features

- **Link Testing**: Test UDP and RTP links to determine their status.
- **Logging**: Logs test results to both console and log files.
- **Reporting**: Generates CSV reports of the test results.
- **Email Notification**: Sends the generated report via email (optional).
- **Repeat Testing**: Option to repeat the test at specified intervals.

## Requirements

- Python 3.x
- Required libraries: `socket`, `argparse`, `csv`, `logging`, `datetime`, `time`, `smtplib`, `email`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/udp-rtp-link-tester.git
   ```
2. Navigate to the project directory:
   ```bash
   cd udp-rtp-link-tester
   ```

3. Ensure you have Python 3.x installed on your system.

## Usage

You can run the script using the command line with various options depending on what you want to achieve.

### Command Line Options

- `--udp-playlist` : Path to a UDP M3U playlist file.
- `--udp-link` : A single UDP link to test.
- `--rtp-link` : A single RTP link to test.
- `--rtp-playlist` : Path to an RTP M3U playlist file.
- `--all` : Test all URLs in the specified M3U playlist file.
- `--report` : Generate a CSV report and save it to a specified file.
- `--email` : Email address to send the report.
- `--smtp-server` : SMTP server address (default: `smtp.gmail.com`).
- `--smtp-port` : SMTP server port (default: `587`).
- `--sender-email` : Sender email address.
- `--sender-password` : Sender email password.
- `--time` : Time interval (in seconds) to repeat the test.

### Example Commands

1. **Test a Single UDP Link**:
   ```bash
   python test_links.py --udp-link udp://224.0.0.1:5000 --report udp_report.csv
   ```

2. **Test an RTP Playlist**:
   ```bash
   python test_links.py --rtp-playlist rtp_playlist.m3u --report rtp_report.csv
   ```

3. **Test All URLs in a Playlist and Send Email Report**:
   ```bash
   python test_links.py --all playlist.m3u --report all_report.csv --email recipient@example.com --sender-email youremail@gmail.com --sender-password yourpassword
   ```

4. **Repeat Test Every 60 Seconds**:
   ```bash
   python test_links.py --udp-playlist udp_playlist.m3u --time 60
   ```

## Logging

Log files are created for each channel tested and are named after the channel with spaces replaced by underscores. The log files contain detailed debug information about each test.

## Reporting

If you use the `--report` option, a CSV file will be generated containing the following fields:
- `timestamp`: The time when the test was conducted.
- `channel_name`: The name of the channel tested.
- `link`: The URL of the tested link.
- `protocol`: The protocol used (`UDP` or `RTP`).
- `status`: The result of the test (`Working` or `Failed`).
- `error_message`: Any error messages encountered during the test.
- `packet_count`: The number of packets received.
- `packet_loss`: The number of packets lost.
- `debug_info`: Additional debug information.

## Email Notification

The script can send the report as an email attachment. You'll need to provide your SMTP server details and email credentials. It's recommended to use an app-specific password if you're using Gmail.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License.

## Contact

For any issues or questions, please contact [yourname@example.com](mailto:yourname@example.com).
```

This `README.md` should give users a clear understanding of how to use your script, including setup, usage, and additional features like logging and email reporting.
