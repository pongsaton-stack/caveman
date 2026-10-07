# tools/blender/bl.py — ส่งสคริปต์ bpy ให้ Blender ที่เปิดอยู่ (พอร์ต MCP 9876 · tools/blender/start_blender_mcp.sh ที่ราก repo)
#   python3 tools/blender/bl.py <script.py> [KEY=VALUE ...]     ค่าหลังชื่อไฟล์ส่งเข้าเป็นตัวแปร ARGS (dict) ในสคริปต์
import json, socket, sys

def run(code, port=9876, timeout=600):
	s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
	s.sendall(json.dumps({"type": "execute_code", "params": {"code": code}}).encode())
	buf = b""
	while True:
		c = s.recv(1 << 16)
		if not c:
			break
		buf += c
		try:
			r = json.loads(buf)
			break
		except ValueError:
			pass
	s.close()
	return r

if __name__ == "__main__":
	args = dict(a.split("=", 1) for a in sys.argv[2:])
	code = "ARGS = %r\n" % args + open(sys.argv[1], encoding="utf-8").read()
	r = run(code)
	if r.get("status") != "success":
		sys.exit("Blender ตอบ error: %s" % r.get("message"))
	print(r["result"].get("result", "").strip())
