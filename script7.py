import socket
import argparse
import csv
import logging
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BUFFER_SIZE = 65535  # Maximum UDP packet size

def setup_logger(log_file, channel_name):
    logger = logging.getLogger(channel_name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def parse_link(link):
    try:
        protocol, address = link.split("://")
        if "@" in address:
            _, address = address.split("@")
        ip, port = address.split(":")
        return ip, int(port)
    except Exception as e:
        raise ValueError(f"Invalid link format: {link} - {str(e)}")

def test_link(channel_name, link, logger, protocol):
    status = "Failed"
    error_message = ""
    packet_count = 0
    packet_loss = 0
    debug_info = ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        ip, port = parse_link(link)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.settimeout(20)
            sock.bind(('0.0.0.0', port))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(ip) + socket.inet_aton('0.0.0.0'))
            start_time = datetime.now()
            while (datetime.now() - start_time).seconds < 20:  # Test for 20 seconds
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    packet_count += 1
                    debug_info = f"Received {len(data)} bytes from {addr}"
                    logger.debug(debug_info)
                except socket.timeout:
                    packet_loss += 1
                    logger.warning(f"Packet loss encountered.")

            if packet_count > 0:
                status = "Working"
                logger.info(f"Channel: {channel_name} - {protocol} link {link} is working with {packet_count} packets received and {packet_loss} packets lost.")
            else:
                error_message = "No packets received."
                logger.error(f"Channel: {channel_name} - {protocol} link {link} failed: {error_message}")

        except socket.timeout:
            error_message = "Timeout. Make sure the server is running and reachable."
            logger.error(f"Channel: {channel_name} - {protocol} link {link} failed: {error_message}")
        except socket.error as e:
            error_message = str(e)
            logger.error(f"Channel: {channel_name} - {protocol} link {link} failed: {error_message}")
        except Exception as e:
            error_message = str(e)
            logger.error(f"Channel: {channel_name} - {protocol} link {link} failed: {error_message}")
        finally:
            sock.close()
    except ValueError as ve:
        error_message = str(ve)
        logger.error(error_message)
    except Exception as e:
        error_message = str(e)
        logger.error(error_message)

    return {
        "timestamp": timestamp,
        "channel_name": channel_name,
        "link": link,
        "protocol": protocol,
        "status": status,
        "error_message": error_message,
        "packet_count": packet_count,
        "packet_loss": packet_loss,
        "debug_info": debug_info
    }

def test_playlist(playlist_file, report_file=None):
    results = []
    try:
        with open(playlist_file, 'r') as f:
            lines = f.readlines()
            channel_name = None
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    channel_name = line.split(",")[1]
                elif line.startswith("udp://") or line.startswith("rtp://"):
                    protocol = "UDP" if line.startswith("udp://") else "RTP"
                    if channel_name:
                        log_file = f"{channel_name.replace(' ', '_')}.log"
                        logger = setup_logger(log_file, channel_name)
                        result = test_link(channel_name, line, logger, protocol)
                        results.append(result)
                    channel_name = None
    except Exception as e:
        print(f"Error testing playlist: {e}")

    if report_file:
        generate_report(results, report_file)

    return results

def generate_report(results, report_file):
    try:
        with open(report_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'channel_name', 'link', 'protocol', 'status', 'error_message', 'packet_count', 'packet_loss', 'debug_info']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        print(f"Report generated: {report_file}")
    except Exception as e:
        print(f"Error generating report: {e}")

def send_email(report_file, recipient_email, smtp_server, smtp_port, sender_email, sender_password):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "UDP/RTP Link Test Report"

        body = "Please find the attached report for the UDP/RTP link tests."
        msg.attach(MIMEText(body, 'plain'))

        with open(report_file, 'r') as f:
            attachment = MIMEText(f.read(), 'csv')
            attachment.add_header('Content-Disposition', 'attachment', filename=report_file)
            msg.attach(attachment)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main(args):
    while True:
        if args.udp_playlist:
            results = test_playlist(args.udp_playlist, report_file=args.report)
        elif args.udp_link:
            log_file = "udp_test.log"
            logger = setup_logger(log_file, "Single UDP Link")
            result = test_link("Single UDP Link", args.udp_link, logger, "UDP")
            if args.report:
                generate_report([result], args.report)
        elif args.rtp_link:
            log_file = "rtp_test.log"
            logger = setup_logger(log_file, "Single RTP Link")
            result = test_link("Single RTP Link", args.rtp_link, logger, "RTP")
            if args.report:
                generate_report([result], args.report)
        elif args.rtp_playlist:
            results = test_playlist(args.rtp_playlist, report_file=args.report)
        elif args.all:
            results = test_playlist(args.all, report_file=args.report)
        else:
            print("Please provide either a playlist file with --udp-playlist, a single UDP link with --udp-link, a single RTP link with --rtp-link, an RTP playlist file with --rtp_playlist, or use --all with a specified M3U playlist file to test all URLs.")
            return

        if args.email and args.report:
            send_email(
                report_file=args.report,
                recipient_email=args.email,
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                sender_email="khaleeqmalik190190@gmail.com",
                sender_password="robj keoe hokk dnoa"
            )

        if args.time:
            print(f"Repeating test in {args.time} seconds.")
            time.sleep(args.time)
        else:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test UDP and RTP links in an M3U playlist.")
    parser.add_argument("--udp-playlist", help="Path to UDP M3U playlist file", required=False)
    parser.add_argument("--udp-link", help="Single UDP link to test", required=False)
    parser.add_argument("--rtp-link", help="Single RTP link to test", required=False)
    parser.add_argument("--rtp-playlist", help="Path to RTP M3U playlist file", required=False)
    parser.add_argument("--all", help="Test all URLs in the specified M3U playlist file", required=False)
    parser.add_argument("--report", help="Generate a CSV report", required=False)
    parser.add_argument("--email", help="Email address to send the report", required=False)
    parser.add_argument("--smtp-server", help="SMTP server address", required=False)
    parser.add_argument("--smtp-port", help="SMTP server port", type=int, required=False, default=587)
    parser.add_argument("--sender-email", help="Sender email address", required=False)
    parser.add_argument("--sender-password", help="Sender email password", required=False)
    parser.add_argument("--time", help="Time interval (in seconds) to repeat the test", type=int, required=False)
    args = parser.parse_args()

    main(args)
