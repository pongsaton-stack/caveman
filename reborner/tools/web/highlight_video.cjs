// คลิปไฮไลต์ 20 วิ จากหน้าฉากต่อสู้: เสียงอัดแบบออฟไลน์ (เสียงชุดเดียวกับหน้า) + ภาพทีละเฟรม 30 fps
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = process.argv[2], MODE = process.argv[3] || 'all', FPS = 30;
const INTRO = 1.2, OUTRO = 1.3;
const SEGS = [
	{ clip: 'blc_bl0', foe: 'M15', bg: 'bg:frost_volcano', a: 14, b: 62, title: 'bl0' },
	{ clip: 'mon_M01_guard', foe: 'M01', bg: 'bg:ash_village', a: 16, b: 72, title: 'guard' },
	{ clip: 'blc_bl1', foe: 'B1', bg: 'bg:flooded_ruins', a: 16, b: 60, title: 'bl1' },
	{ clip: 'blc_glim', foe: 'M01', bg: 'bg:frost_volcano', a: 18, b: 110, title: 'glim' },
	{ clip: 'aot_bl7', foe: 'B1', bg: 'bg:ash_village', a: 18, b: 76, title: 'bl7' },
];
let t = INTRO; for (const s of SEGS) { s.T0 = t; t += (s.b - s.a) * 0.06; s.T1 = t; }
const TOTAL = t + OUTRO;

(async () => {
	fs.mkdirSync(OUT, { recursive: true });
	const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
	const errs = [];
	const open = async () => { const p = await b.newPage({ viewport: { width: 1200, height: 900 } }); p.on('pageerror', e => errs.push(String(e)));
		await p.goto('http://127.0.0.1:8765/combat.html'); await p.waitForTimeout(4000); return p; };

	if (MODE !== 'video') {   // ── เสียง
		const p = await open();
		const wav = await p.evaluate(async ([SEGS, TOTAL, INTRO]) => {
			const SR = 48000, off = new OfflineAudioContext(2, Math.ceil(SR * (TOTAL + 0.5)), SR), VT = { t: 0 };
			const fake = new Proxy(off, { get(o, k) { if (k === 'currentTime') return VT.t; if (k === 'state') return 'running'; const v = o[k]; return typeof v === 'function' ? v.bind(o) : v; } });
			window.AudioContext = function () { return fake; }; AU = null; auInit(); S.sound = true; S.music = true;
			bgmStep = 0; bgmNext = 0; bgmTimer = 1;
			const ev = [];
			for (const s of SEGS) for (let F = s.a; F < s.b; F++) ev.push([s.T0 + (F - s.a) * 0.06, s, F]);
			let cur = null, k = 0;
			for (let tt = 0; tt < TOTAL; tt += 0.02) {
				VT.t = tt; bgmTick();
				while (k < ev.length && ev[k][0] <= tt + 1e-6) { const [, s, F] = ev[k++]; VT.t = ev[k - 1][0];
					if (cur !== s) { S.pkFoe = s.foe; S.bg = s.bg; pickClip(s.clip); S.playing = false; cur = s; }
					const c = CLIPS[s.clip]; S.frame = F;
					if (c.blc) blcSound(F); else if (c.aot) aotSound(F); else if (c.mon) monAtkSound(F, c); VT.t = tt; }
			}
			const g = AU.music.gain; g.setValueAtTime(0.28, TOTAL - OUTRO_FADE()); g.linearRampToValueAtTime(0.0001, TOTAL);
			function OUTRO_FADE() { return 1.1; }
			const buf = await off.startRendering(), n = buf.length, L = buf.getChannelData(0), R = buf.getChannelData(1);
			const dv = new DataView(new ArrayBuffer(44 + n * 4)), w = (o, s) => { for (let i = 0; i < s.length; i++) dv.setUint8(o + i, s.charCodeAt(i)); };
			w(0, 'RIFF'); dv.setUint32(4, 36 + n * 4, true); w(8, 'WAVE'); w(12, 'fmt '); dv.setUint32(16, 16, true); dv.setUint16(20, 1, true); dv.setUint16(22, 2, true);
			dv.setUint32(24, SR, true); dv.setUint32(28, SR * 4, true); dv.setUint16(32, 4, true); dv.setUint16(34, 16, true); w(36, 'data'); dv.setUint32(40, n * 4, true);
			let peak = 0; for (let i = 0; i < n; i++) { const l = Math.max(-1, Math.min(1, L[i] * 0.6)), r = Math.max(-1, Math.min(1, R[i] * 0.6)); peak = Math.max(peak, Math.abs(l), Math.abs(r)); dv.setInt16(44 + i * 4, l * 32767, true); dv.setInt16(46 + i * 4, r * 32767, true); }
			const u = new Uint8Array(dv.buffer); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000));
			return { b64: btoa(s), peak, events: ev.length };
		}, [SEGS, TOTAL, INTRO]);
		fs.writeFileSync(path.join(OUT, 'audio.wav'), Buffer.from(wav.b64, 'base64'));
		console.log('audio', TOTAL.toFixed(2), 's · peak', wav.peak.toFixed(3), '· sound events', wav.events);
		await p.close();
	}

	if (MODE !== 'audio') {   // ── ภาพ
		const p = await open();
		await p.evaluate(([SEGS]) => {
			sceneCaption = () => {};   // แถบคำอธิบายแบบหน้าเทสไม่ใส่ในคลิปโชว์
			const V = document.createElement('canvas'); V.width = 1080; V.height = 1080; window.__V = V;
			const big = document.createElement('canvas'); window.__big = big;
			const mons = {}; for (const m of (DATA.monsters_px || [])) mons[m.id] = m.name;
			const nm = id => (glimRow(id) || {}).name_th || id;
			window.__lab = { bl0: [nm('bl0'), 'Rion  vs  ' + mons.M15], guard: ['ตั้งรับ!', mons.M01 + ' โจมตีกลับ'], bl1: [nm('bl1'), 'Rion  vs  ' + mons.B1],
				glim: ['★ ประกาย', 'ได้ท่าใหม่กลางการต่อสู้ · ' + nm('bl1')], bl7: [nm('bl7'), 'Rion  vs  ' + mons.B1] };
		}, [SEGS]);
		let cur = -1;
		const N = Math.round(TOTAL * FPS);
		for (let i = 0; i < N; i++) {
			const tt = i / FPS, si = SEGS.findIndex(s => tt >= s.T0 && tt < s.T1);
			const url = await p.evaluate(([tt, si, SEGS, INTRO, TOTAL, OUTRO, cur]) => {
				const V = window.__V, g = V.getContext('2d'), big = window.__big;
				const last = SEGS[SEGS.length - 1], s = si >= 0 ? SEGS[si] : tt < INTRO ? SEGS[0] : last;
				const F = si >= 0 ? s.a + Math.floor((tt - s.T0) / 0.06 + 1e-6) : tt < INTRO ? s.a : s.b - 1;
				if (si !== cur || window.__clip !== s.clip) { S.pkFoe = s.foe; S.bg = s.bg; pickClip(s.clip); window.__clip = s.clip; }
				S.playing = false; S.frame = F; S.bgT = tt; LOGICAL_H = 0; clipView();
				// พื้นหลัง
				const gr = g.createLinearGradient(0, 0, 0, 1080); gr.addColorStop(0, '#0b1020'); gr.addColorStop(1, '#1b0f2a'); g.fillStyle = gr; g.fillRect(0, 0, 1080, 1080);
				for (let k = 0; k < 40; k++) { const x = (k * 263 + 71) % 1080, y = (k * 151 + 37) % 1080, a = 0.15 + 0.15 * Math.sin(tt * 2 + k); g.fillStyle = `rgba(255,230,160,${a})`; g.fillRect(x, y, 3, 3); }
				// เวที: ขยาย 4 เท่าแบบพิกเซลคม แล้วย่อนุ่มลงกว้าง 1080
				const sw = cv.width, sh = cv.height; big.width = sw * 4; big.height = sh * 4; const bx = big.getContext('2d'); bx.imageSmoothingEnabled = false; bx.drawImage(cv, 0, 0, big.width, big.height);
				const SH = Math.round(1080 * sh / sw), SY = 236;
				g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; g.drawImage(big, 0, SY, 1080, SH);
				g.fillStyle = '#e8b84a'; g.fillRect(0, SY - 4, 1080, 4); g.fillRect(0, SY + SH, 1080, 4);
				const txt = (str, x, y, size, fill, al = 1, stroke = '#1a0f0a', align = 'center') => { g.save(); g.globalAlpha = al; g.textAlign = align; g.textBaseline = 'middle'; g.font = `900 ${size}px "Noto Sans Thai", "Sarabun", sans-serif`; g.lineJoin = 'round'; g.lineWidth = Math.max(4, size / 7); g.strokeStyle = stroke; g.strokeText(str, x, y); g.fillStyle = fill; g.fillText(str, x, y); g.restore(); };
				// หัว
				txt('REBORNER', 540, 96, 104, '#ffd75e'); txt('ไฮไลต์ฉากต่อสู้', 540, 178, 38, '#f4e6c8');
				// ป้ายท่า (เลื่อนเข้า)
				if (si >= 0) { const u = Math.min(1, (tt - s.T0) / 0.25), e = 1 - Math.pow(1 - u, 3), [a, b] = window.__lab[s.title];
					txt(a, 540 - (1 - e) * 300, SY + SH + 92, 78, s.title === 'glim' ? '#ffd75e' : '#ffffff', e); txt(b, 540 + (1 - e) * 300, SY + SH + 162, 34, '#bcd4ff', e);
					const w = (tt - s.T0) * 30; if (w < 5 && si > 0) { g.fillStyle = `rgba(255,255,255,${0.85 * (1 - w / 5)})`; g.fillRect(0, SY, 1080, SH); } }   // ตัดฉาก = วาบขาว
				// เปิด: มืด → เวทีค่อยสว่าง + ชื่อเกมตัวใหญ่
				if (tt < INTRO) { const u = tt / INTRO; g.fillStyle = `rgba(5,6,12,${0.92 - 0.5 * u})`; g.fillRect(0, 0, 1080, 1080);
					const z = 1 + 0.25 * Math.pow(1 - Math.min(1, u * 1.6), 3); g.save(); g.translate(540, 520); g.scale(z, z); txt('REBORNER', 0, 0, 150, '#ffd75e', Math.min(1, u * 3)); g.restore();
					txt('ประกาย + ท่าต่อสู้', 540, 640, 46, '#f4e6c8', Math.max(0, Math.min(1, u * 3 - 0.8))); }
				// ปิด
				if (tt >= TOTAL - OUTRO) { const u = Math.min(1, (tt - (TOTAL - OUTRO)) / 0.4); g.fillStyle = `rgba(5,6,12,${0.85 * u})`; g.fillRect(0, 0, 1080, 1080);
					txt('REBORNER', 540, 470, 150, '#ffd75e', u); txt('ประกาย · ท่าต่อสู้ · มอนโจมตีกลับ', 540, 590, 42, '#f4e6c8', u); txt('เกมอยู่ระหว่างพัฒนา', 540, 660, 32, '#bcd4ff', u); }
				return V.toDataURL('image/png');
			}, [tt, si, SEGS, INTRO, TOTAL, OUTRO, cur]);
			cur = si;
			fs.writeFileSync(path.join(OUT, `f${String(i).padStart(4, '0')}.png`), Buffer.from(url.split(',')[1], 'base64'));
		}
		console.log('frames', N);
		await p.close();
	}
	console.log('errs', errs.slice(0, 5)); await b.close();
})();
