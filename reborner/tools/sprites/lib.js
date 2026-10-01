// pixel sprite toolkit: shaded primitives + auto outline + PNG writer
const zlib = require('zlib');
const fs = require('fs');

function hex(c) { c = c.replace('#', ''); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function toHex(r) { return '#' + r.map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join(''); }
function darken(c, k) { const [r, g, b] = hex(c); return toHex([r * k, g * k, b * k * 1.08]); }

const L = (() => { const v = [-0.55, -0.7, 0.62]; const n = Math.hypot(...v); return v.map(x => x / n); })();

class Sprite {
	constructor(w, h) { this.w = w; this.h = h; this.c = new Array(w * h).fill(null); this.o = new Array(w * h).fill(null); }
	in(x, y) { return x >= 0 && y >= 0 && x < this.w && y < this.h; }
	get(x, y) { return this.in(x, y) ? this.c[y * this.w + x] : null; }
	set(x, y, col, outline) {
		x = Math.round(x); y = Math.round(y);
		if (!this.in(x, y) || col == null) return;
		this.c[y * this.w + x] = col;
		this.o[y * this.w + x] = outline || darken(col, 0.45);
	}
	// shaded ellipse. ramp dark→light. opts: edge (inner line), bias, light override, clip(x,y)->bool
	ell(cx, cy, rx, ry, ramp, opts = {}) {
		const pts = [];
		for (let y = Math.floor(cy - ry - 1); y <= Math.ceil(cy + ry + 1); y++)
			for (let x = Math.floor(cx - rx - 1); x <= Math.ceil(cx + rx + 1); x++) {
				const nx = (x + 0.5 - cx) / rx, ny = (y + 0.5 - cy) / ry, r2 = nx * nx + ny * ny;
				if (r2 > 1) continue;
				if (opts.clip && !opts.clip(x, y)) continue;
				pts.push([x, y, nx, ny, r2]);
			}
		const inside = new Set(pts.map(p => p[0] + ',' + p[1]));
		for (const [x, y, nx, ny, r2] of pts) {
			const nz = Math.sqrt(Math.max(0, 1 - r2));
			let d = nx * L[0] + ny * L[1] + nz * L[2];
			let t = (d * 0.5 + 0.5) + (opts.bias || 0);
			let i = Math.max(0, Math.min(ramp.length - 1, Math.floor(t * ramp.length)));
			const isEdge = !inside.has((x + 1) + ',' + y) || !inside.has((x - 1) + ',' + y) || !inside.has(x + ',' + (y + 1)) || !inside.has(x + ',' + (y - 1));
			if (opts.edge && isEdge && this.get(x, y) != null) i = 0;
			this.set(x, y, ramp[i], opts.outline || darken(ramp[0], 0.55));
		}
	}
	// polygon with vertical gradient (top light)
	poly(pts, ramp, opts = {}) {
		const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
		const y0 = Math.floor(Math.min(...ys)), y1 = Math.ceil(Math.max(...ys));
		const x0 = Math.floor(Math.min(...xs)), x1 = Math.ceil(Math.max(...xs));
		for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
			const px = x + 0.5, py = y + 0.5;
			let c = false;
			for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
				const [xi, yi] = pts[i], [xj, yj] = pts[j];
				if ((yi > py) !== (yj > py) && px < (xj - xi) * (py - yi) / (yj - yi) + xi) c = !c;
			}
			if (!c) continue;
			let t = opts.flat != null ? opts.flat : 1 - (py - y0) / Math.max(1, y1 - y0) * 0.9 - (px - x0) / Math.max(1, x1 - x0) * (opts.xs || 0.25);
			t += opts.bias || 0;
			const i = Math.max(0, Math.min(ramp.length - 1, Math.floor(t * ramp.length)));
			this.set(x, y, ramp[i], opts.outline || darken(ramp[0], 0.55));
		}
	}
	line(x0, y0, x1, y1, col, opts = {}) {
		x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
		const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
		let e = dx + dy;
		for (;;) {
			if (!opts.onlyOver || this.get(x0, y0) != null) this.set(x0, y0, col, opts.outline);
			if (x0 === x1 && y0 === y1) break;
			const e2 = 2 * e;
			if (e2 >= dy) { e += dy; x0 += sx; }
			if (e2 <= dx) { e += dx; y0 += sy; }
		}
	}
	px(list, col, opts = {}) { for (const [x, y] of list) if (!opts.onlyOver || this.get(x, y) != null) this.set(x, y, col, opts.outline); }
	// outline every transparent pixel touching an opaque one (4-neighbour), colour from neighbour
	outline() {
		const add = [];
		for (let y = 0; y < this.h; y++) for (let x = 0; x < this.w; x++) {
			if (this.get(x, y) != null) continue;
			for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
				const nx = x + dx, ny = y + dy;
				if (this.get(nx, ny) != null) { add.push([x, y, this.o[ny * this.w + nx]]); break; }
			}
		}
		for (const [x, y, c] of add) { this.c[y * this.w + x] = c; this.o[y * this.w + x] = c; }
	}
	flipX() { const n = new Sprite(this.w, this.h); for (let y = 0; y < this.h; y++) for (let x = 0; x < this.w; x++) { n.c[y * this.w + x] = this.c[y * this.w + (this.w - 1 - x)]; n.o[y * this.w + x] = this.o[y * this.w + (this.w - 1 - x)]; } return n; }
	png(file, scale = 1) {
		const W = this.w * scale, H = this.h * scale;
		const raw = Buffer.alloc((W * 4 + 1) * H);
		for (let y = 0; y < H; y++) {
			raw[y * (W * 4 + 1)] = 0;
			for (let x = 0; x < W; x++) {
				const c = this.c[Math.floor(y / scale) * this.w + Math.floor(x / scale)];
				const o = y * (W * 4 + 1) + 1 + x * 4;
				if (c) { const [r, g, b] = hex(c); raw[o] = r; raw[o + 1] = g; raw[o + 2] = b; raw[o + 3] = 255; }
			}
		}
		fs.writeFileSync(file, encodePng(W, H, raw));
	}
}

const CRC = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
function crc32(b) { let c = 0xffffffff; for (const x of b) c = CRC[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }
function chunk(type, data) { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td)); return Buffer.concat([len, td, crc]); }
function encodePng(w, h, raw) {
	const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 6;
	return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}

// sheet: compose sprites onto a preview background
function sheet(file, items, scale, bg = '#2b2620') {
	const pad = 4;
	const W = items.reduce((a, s) => a + s.w + pad, pad), H = Math.max(...items.map(s => s.h)) + pad * 2;
	const out = new Sprite(W, H);
	for (let i = 0; i < out.c.length; i++) out.c[i] = bg;
	let x = pad;
	for (const s of items) { const oy = H - pad - s.h; for (let y = 0; y < s.h; y++) for (let xx = 0; xx < s.w; xx++) { const c = s.c[y * s.w + xx]; if (c) out.c[(oy + y) * W + x + xx] = c; } x += s.w + pad; }
	out.png(file, scale);
}

module.exports = { Sprite, darken, sheet, hex, toHex };
