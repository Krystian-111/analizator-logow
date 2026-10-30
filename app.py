
from flask import Flask, render_template
from collections import Counter
from pathlib import Path
import re

app = Flask(__name__)

# Lokalizacja pliku z logami
LOG_FILE = Path(__file__).with_name("access.log")

# Wzorzec rozpoznający rekord Apache
PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<date>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)


def analyze_logs():
    logs = []

    if not LOG_FILE.exists():
        return logs, {}, {}, 0, 0

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            match = PATTERN.search(line)

            if match:
                data = match.groupdict()

                size = data["size"]
                data["size"] = 0 if size == "-" else int(size)
                data["status"] = int(data["status"])

                logs.append(data)

    total_requests = len(logs)
    total_bytes = sum(log["size"] for log in logs)

    status_stats = Counter(
        log["status"] for log in logs
    )

    ip_stats = Counter(
        log["ip"] for log in logs
    )

    return (
        logs,
        status_stats,
        ip_stats,
        total_requests,
        total_bytes
    )


@app.route("/")
def index():
    logs, statuses, ips, total, total_bytes = analyze_logs()

    return render_template(
        "index.html",
        logs=logs,
        statuses=statuses,
        ips=ips,
        total=total,
        total_bytes=total_bytes,
        unique_ips=len(ips)
    )


if __name__ == "__main__":
    app.run(debug=True)
