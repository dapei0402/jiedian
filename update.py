# update.py
import requests
import random
import string
import urllib.parse
import base64
import os

# ========== 配置 ==========
V2_FILE = "sub/v2ray.txt"
CLASH_FILE = "sub/clash.txt"
API_NODE_URL = "https://api.tianmiao.icu/api/nodeListV2"  # 节点接口

# ========== 工具函数 ==========
def generate_random_email():
    s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{s}@qq.com"

def get_nodes():
    """获取节点信息"""
    # 这里假设你已经有 token，如果需要注册账号可以在此扩展
    headers = {"User-Agent": "Mozilla/5.0"}
    data = {"protocol": "all", "include_ss": "1", "include_shadowsocks": "1", "include_trojan": "1"}
    
    try:
        resp = requests.post(API_NODE_URL, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        nodes = []
        for group in result.get("data", []):
            if group.get("type") == "vip" and "node" in group:
                nodes.extend(group["node"])
        return nodes
    except Exception as e:
        print("获取节点失败:", e)
        return []

def generate_v2ray_sub(nodes):
    """生成 V2Ray 订阅"""
    links = []
    for node in nodes:
        url = node.get("url")
        if url:
            links.append(url)
    return "\n".join(links)

def generate_clash_sub(nodes):
    """生成 Clash 订阅"""
    clash_lines = []
    for node in nodes:
        url = node.get("url")
        if not url:
            continue
        # 简单转换 ss://base64 -> Clash 格式
        try:
            url_parts = url.split("#")
            name = urllib.parse.unquote(url_parts[1]) if len(url_parts) > 1 else "节点"
            auth_part, server_port = url_parts[0].split("@")
            cipher_password = base64.b64decode(auth_part.split("://")[1]+"==").decode()
            cipher, password = cipher_password.split(":")
            server, port = server_port.split(":")
            clash_lines.append(
                f"- name: {name}\n  type: ss\n  server: {server}\n  port: {port}\n  cipher: {cipher}\n  password: {password}\n  udp: true"
            )
        except:
            continue
    return "\n".join(clash_lines)

# ========== 主程序 ==========
def main():
    if not os.path.exists("sub"):
        os.makedirs("sub")
    
    nodes = get_nodes()
    if not nodes:
        print("没有获取到节点，退出")
        return
    
    v2_text = generate_v2ray_sub(nodes)
    clash_text = generate_clash_sub(nodes)
    
    with open(V2_FILE, "w", encoding="utf-8") as f:
        f.write(v2_text)
    with open(CLASH_FILE, "w", encoding="utf-8") as f:
        f.write(clash_text)
    
    print(f"V2Ray 订阅已生成: {V2_FILE}")
    print(f"Clash 订阅已生成: {CLASH_FILE}")

if __name__ == "__main__":
    main()
