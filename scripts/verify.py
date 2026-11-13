#!/usr/bin/env python3
"""Load every generated rule in a real Mihomo process and check provider counts."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

import yaml


def verify(output, binary):
    output = output.resolve()
    manifest = json.loads((output / "manifest.json").read_text())
    fragment = yaml.safe_load((output / "rules-config.yaml").read_text())
    with tempfile.TemporaryDirectory(prefix="proxy-rules-check-") as directory:
        home = Path(directory)
        for name, provider in fragment["rule-providers"].items():
            filename = name.removeprefix("pr-") + ".yaml"
            (home / filename).write_bytes((output / filename).read_bytes())
            provider.update(type="file", path="./" + filename)
            provider.pop("url")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        config = {**fragment, "mode": "rule", "log-level": "warning", "external-controller": f"127.0.0.1:{port}", "secret": "local-validation", "proxy-groups": [{"name": "自定义分流", "type": "select", "proxies": ["DIRECT"]}]}
        config_path = home / "config.yaml"
        config_path.write_text(yaml.safe_dump(config, allow_unicode=True))
        subprocess.run([binary, "-t", "-d", directory, "-f", str(config_path)], check=True)
        # -t alone does not prove all provider entries parsed successfully.
        with (home / "core.log").open("w+") as log:
            process = subprocess.Popen([binary, "-d", directory, "-f", str(config_path)], stdout=log, stderr=log)
            try:
                expected = {"pr-" + name: count for name, count in manifest["counts"].items()}
                actual = {}
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                for _ in range(150):
                    if process.poll() is not None:
                        break
                    try:
                        request = urllib.request.Request(f"http://127.0.0.1:{port}/providers/rules", headers={"Authorization": "Bearer local-validation"})
                        with opener.open(request, timeout=1) as response:
                            data = json.load(response)
                        actual = {name: item["ruleCount"] for name, item in data["providers"].items()}
                        if actual == expected:
                            print("Mihomo loaded all providers:", actual)
                            return
                    except (urllib.error.URLError, TimeoutError):
                        pass
                    time.sleep(0.2)
                log.seek(0)
                raise RuntimeError(f"Provider counts differ: expected={expected}, actual={actual}\n{log.read()}")
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--mihomo", required=True)
    args = parser.parse_args()
    verify(args.output, args.mihomo)
