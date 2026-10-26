const { Sprite, darken } = require('./lib');

const ASH = ['#3d3936', '#5f5a55', '#857e76', '#aaa298', '#cdc5b8'];
const EMBER = { deep: '#b8401c', mid: '#ff8a2a', hot: '#ffd166', core: '#fff1c2' };
const STONE = ['#3e342a', '#5d5043', '#7e7060', '#a1927b', '#c3b598'];
const FLESH = ['#7d3a42', '#b25a5e', '#d9877e', '#f2b39f'];
const BAT = ['#1f1729', '#352745', '#4f3b65', '#6b5585'];
const WING = ['#3a2d52', '#584573', '#7a6898', '#9e8dbb'];
const WOLF = ['#2e2b2b', '#4d4846', '#736c66', '#998f86', '#beb4a8'];
const GOLD = '#f2c94c', RED = '#e0362a', INK = '#16120f', WHITE = '#fffbe9';
const SCARF = ['#5c1f24', '#8f2f31', '#c2463d', '#e46e55'];

function eye(s, x, y, iris, big) {
	if (big) {
		s.px([[x, y], [x + 1, y], [x, y + 1], [x + 1, y + 1], [x, y + 2], [x + 1, y + 2], [x - 1, y + 1], [x + 2, y + 1]], INK);
		s.px([[x, y], [x + 1, y + 1]], WHITE);
		if (iris) s.px([[x, y + 2], [x + 1, y + 2]], iris);
	} else {
		s.px([[x, y], [x, y + 1]], iris || INK);
		s.px([[x, y]], WHITE);
	}
}

// ── M01 สไลม์เถ้า ──────────────────────────────────────────
function slime() {
	const s = new Sprite(48, 48);
	s.ell(24, 41, 19, 4.5, ASH, { bias: -0.15 });
	s.ell(24, 31, 17, 14, ASH, { clip: (x, y) => y <= 42 });
	s.ell(27, 17.5, 4, 4, ASH);
	// glowing cracks (fire weakness)
	const crack = [[11, 33], [14, 31], [16, 34], [19, 32], [21, 36], [23, 35]];
	const crack2 = [[30, 22], [32, 26], [30, 29], [33, 33], [35, 32], [37, 36]];
	const crack3 = [[16, 23], [19, 25], [18, 27]];
	for (const c of [crack, crack2, crack3]) for (let i = 0; i < c.length - 1; i++) {
		s.line(c[i][0], c[i][1] + 1, c[i + 1][0], c[i + 1][1] + 1, EMBER.deep, { onlyOver: true });
		s.line(c[i][0], c[i][1], c[i + 1][0], c[i + 1][1], EMBER.mid, { onlyOver: true });
	}
	s.px([[14, 31], [19, 32], [32, 26], [33, 33], [19, 25]], EMBER.hot);
	s.px([[19, 32], [33, 33]], EMBER.core);
	// face
	s.px([[19, 26], [20, 26], [19, 27], [20, 27], [19, 28], [20, 28], [27, 26], [28, 26], [27, 27], [28, 27], [27, 28], [28, 28]], INK);
	s.px([[19, 26], [27, 26]], WHITE);
	s.px([[22, 31], [23, 32], [24, 32], [25, 31]], darken(ASH[0], 0.7));
	// shine
	s.px([[14, 22], [15, 21], [16, 20], [15, 22]], ASH[4]);
	s.px([[15, 21]], WHITE);
	s.outline();
	return s;
}

// ── M03 หนอนหิน ────────────────────────────────────────────
function grub(friendly) {
	const s = new Sprite(48, 48);
	// curled body: segments from tail (back-right) to head (front-left)
	const seg = [[38, 38, 6, 5], [33, 33, 8, 7], [25, 30, 10, 9], [17, 33, 9, 8.5], [12, 38, 7.5, 6.5]];
	for (const [x, y, rx, ry] of seg) s.ell(x, y + 2, rx, ry * 0.75, FLESH, { bias: -0.05 });
	for (const [x, y, rx, ry] of seg.slice(0, 4)) s.ell(x, y - 1, rx, ry * 0.85, STONE, { edge: true, clip: (px, py) => py < y + ry * 0.5 });
	// head
	s.ell(12, 38, 7.5, 6.5, FLESH, { edge: true });
	s.ell(13, 33.5, 6.5, 3.6, STONE, { edge: true, clip: (px, py) => py < 35 });
	// cracks on shell (blunt weakness)
	s.line(24, 22, 26, 25, STONE[0], { onlyOver: true }); s.line(26, 25, 24, 28, STONE[0], { onlyOver: true });
	s.line(26, 25, 29, 26, STONE[0], { onlyOver: true });
	s.line(16, 27, 18, 30, STONE[0], { onlyOver: true });
	s.line(33, 28, 35, 30, STONE[0], { onlyOver: true });
	// pink flesh seen through cracks
	s.px([[25, 26], [17, 29], [34, 29]], FLESH[2]);
	// pebbles
	s.px([[21, 24], [30, 27], [14, 30]], STONE[4]);
	// belly ridges
	for (const x of [20, 24, 28, 32]) s.px([[x, 39], [x, 40]], FLESH[0], { onlyOver: true });
	if (friendly) {
		eye(s, 8, 36, '#3b2a20', true); eye(s, 13, 36, '#3b2a20', true);
		s.px([[10, 41], [11, 42], [12, 41]], FLESH[0]);
		s.px([[7, 40], [15, 40]], '#f08f8a');
		// scarf around the neck segment
		s.poly([[17, 33], [23, 31], [24, 37], [18, 40]], SCARF, { xs: 0.3 });
		s.poly([[21, 38], [25, 39], [27, 45], [23, 44]], SCARF, { flat: 0.45 });
		s.line(19, 34, 23, 33, SCARF[3], { onlyOver: true });
	} else {
		eye(s, 8, 37, null, false); eye(s, 12, 37, null, false);
		s.px([[9, 41], [10, 41], [11, 41]], FLESH[0]);
		s.px([[8, 42], [11, 42]], WHITE);
	}
	s.outline();
	return s;
}

// ── M06 ค้างคาวเงา ─────────────────────────────────────────
function bat(friendly) {
	const s = new Sprite(48, 48);
	const wingL = [[22, 22], [12, 13], [4, 15], [1, 22], [4, 27], [7, 25], [10, 30], [14, 27], [17, 31], [22, 28]];
	const wingR = wingL.map(([x, y]) => [48 - x, y]);
	s.poly(wingL, WING, { xs: -0.3 });
	s.poly(wingR, WING, { xs: 0.3 });
	// wing bones
	for (const w of [[[22, 22], [12, 14], [4, 16]], [[12, 14], [7, 25]], [[12, 14], [14, 27]]]) for (let i = 0; i < w.length - 1; i++) {
		s.line(w[i][0], w[i][1], w[i + 1][0], w[i + 1][1], BAT[1], { onlyOver: true });
		s.line(48 - w[i][0], w[i][1], 48 - w[i + 1][0], w[i + 1][1], BAT[1], { onlyOver: true });
	}
	// light-corroded patches (light weakness)
	if (!friendly) s.px([[6, 20], [7, 20], [6, 21], [40, 22], [41, 22], [41, 23], [9, 26]], '#c9c0d8');
	// body + head
	s.ell(24, 28, 6.5, 7.5, BAT, { bias: 0.05 });
	s.ell(24, 20, 6, 5.2, BAT, { edge: true, bias: 0.1 });
	s.poly([[19, 17], [18, 10], [22, 15]], BAT, { flat: 0.5 });
	s.poly([[29, 17], [30, 10], [26, 15]], BAT, { flat: 0.4 });
	s.px([[19, 13], [19, 14]], '#a07a9a'); s.px([[29, 13], [29, 14]], '#a07a9a');
	// feet
	s.px([[22, 36], [22, 37], [26, 36], [26, 37]], BAT[1]);
	if (friendly) {
		eye(s, 20, 18, '#4a2f12', true); eye(s, 26, 18, '#4a2f12', true);
		s.px([[23, 23], [24, 24], [25, 23]], '#d07a8a');
		s.poly([[18, 24], [30, 24], [30, 27], [18, 27]], SCARF, { xs: 0.2 });
		s.line(18, 24, 30, 24, SCARF[3], { onlyOver: true });
		s.poly([[29, 25], [33, 26], [36, 31], [33, 32], [31, 28]], SCARF, { flat: 0.4 });
	} else {
		s.px([[21, 19], [22, 19], [22, 20], [26, 19], [27, 19], [26, 20]], GOLD);
		s.px([[21, 19], [27, 19]], '#fff3b0');
		s.px([[23, 23], [25, 23]], WHITE);
	}
	s.outline();
	return s;
}

// ── M15 หมาป่าคู่ (หนึ่งตัว หันซ้าย) ─────────────────────────
function wolf() {
	const s = new Sprite(48, 48);
	// tail (scorched tip — fire weakness)
	s.poly([[36, 26], [44, 18], [47, 20], [44, 27], [38, 31]], WOLF, { xs: 0.1 });
	s.px([[44, 18], [45, 18], [46, 19], [45, 19], [46, 20], [44, 19]], '#2a1a12');
	s.px([[45, 19], [46, 20]], EMBER.mid);
	// back legs
	s.poly([[33, 34], [38, 33], [38, 44], [35, 44], [34, 39]], WOLF, { bias: -0.15 });
	s.poly([[13, 34], [18, 34], [17, 44], [14, 44]], WOLF, { bias: -0.15 });
	// body
	s.ell(26, 30, 13, 7, WOLF, { edge: true });
	// near legs
	s.poly([[28, 32], [35, 32], [33, 39], [33, 45], [30, 45], [30, 39]], WOLF);
	s.poly([[15, 32], [21, 32], [20, 39], [19, 45], [16, 45], [17, 39]], WOLF);
	// bristling mane
	s.poly([[10, 22], [13, 17], [15, 21], [18, 16], [20, 21], [23, 17], [24, 24], [18, 32], [11, 30]], WOLF, { xs: 0.2 });
	// head
	s.ell(11, 21, 6.5, 5.5, WOLF, { edge: true });
	s.poly([[1, 22], [6, 19], [9, 22], [7, 26], [2, 25]], WOLF, { bias: 0.05 });
	s.poly([[9, 17], [10, 10], [14, 16]], WOLF, { flat: 0.45 });
	s.poly([[13, 17], [16, 11], [17, 18]], WOLF, { flat: 0.6 });
	s.px([[11, 13], [11, 14], [15, 14]], '#5a3c38');
	s.px([[1, 22], [2, 22]], INK);
	// red eye
	s.px([[8, 20], [9, 20], [8, 19]], RED); s.px([[8, 19]], '#ffb0a0');
	// mouth + fang
	s.line(2, 25, 7, 25, darken(WOLF[0], 0.6));
	s.px([[4, 26]], WHITE);
	// paws
	s.px([[29, 45], [16, 45], [15, 45], [29, 44]], WOLF[2]);
	// fur ticks
	s.px([[24, 26], [28, 25], [32, 27], [30, 30]], WOLF[1], { onlyOver: true });
	s.outline();
	return s;
}

// ── B1 ราชาหนอนเถ้า (80x80) ─────────────────────────────────
function grubKing() {
	const s = new Sprite(80, 80);
	const KING = ['#3a2d26', '#5a463a', '#7c6450', '#a08468', '#c2a888'];
	const BELLY = ['#6e3a35', '#9a5548', '#c47b62', '#e0a283'];
	// cracked ground
	s.ell(40, 73, 34, 5, ['#2c2520', '#40362e', '#54483c'], { bias: -0.1 });
	s.line(14, 73, 22, 75, '#1a1410', { onlyOver: true }); s.line(22, 75, 28, 73, '#1a1410', { onlyOver: true });
	s.line(52, 72, 60, 75, '#1a1410', { onlyOver: true }); s.line(60, 75, 66, 73, '#1a1410', { onlyOver: true });
	s.px([[22, 74], [60, 74]], EMBER.mid);
	// rearing body: tail coils at base → upright
	const seg = [[63, 67, 11, 6.5], [50, 64, 15, 9.5], [39, 56, 16, 11], [35, 45, 16, 11], [37, 34, 15, 10.5], [40, 25, 14, 10]];
	for (const [x, y, rx, ry] of seg) s.ell(x, y, rx, ry, KING, { edge: true });
	// belly plates facing viewer (left side)
	for (const [x, y, rx, ry] of seg.slice(2)) s.ell(x - rx * 0.45, y + 1, rx * 0.5, ry * 0.75, BELLY, { edge: true });
	// head
	s.ell(36, 18, 13, 10, KING, { edge: true });
	s.ell(29, 23, 7, 5, BELLY, { edge: true });
	// mouth with fangs
	s.line(24, 24, 33, 24, '#2a1410');
	s.px([[25, 25], [28, 25], [31, 25]], WHITE);
	// mandibles
	s.poly([[23, 21], [17, 24], [18, 27], [24, 25]], ['#3a2c24', '#5c4638', '#80624c']);
	s.poly([[33, 25], [36, 30], [38, 29], [36, 24]], ['#3a2c24', '#5c4638', '#80624c']);
	// blood-red eyes, angry brow
	s.px([[26, 15], [27, 15], [28, 15], [26, 16], [27, 16], [28, 16], [34, 14], [35, 14], [36, 14], [34, 15], [35, 15], [36, 15]], RED);
	s.px([[26, 15], [34, 14]], '#ffd2b8');
	s.px([[25, 13], [26, 13], [27, 14], [28, 14], [37, 12], [36, 12], [35, 13], [34, 13]], INK);
	// ember crown
	const crown = [[27, 10], [28, 3], [32, 7], [35, 0], [38, 6], [42, 2], [44, 9], [45, 11], [27, 12]];
	s.poly(crown, ['#7a2a14', EMBER.deep, EMBER.mid, EMBER.hot], { xs: 0.1 });
	s.px([[28, 4], [35, 1], [42, 3]], EMBER.core);
	s.px([[33, 9], [37, 9], [40, 9]], '#3a1a10');
	s.px([[35, 9]], '#ff4f3a');
	// smoldering motes
	s.px([[23, 4], [48, 5], [47, 0], [25, 0]], EMBER.mid);
	// ash cracks with ember glow along the body
	for (const [a, b, c, d] of [[40, 44, 44, 48], [44, 48, 42, 52], [38, 30, 42, 33], [50, 62, 55, 66], [40, 22, 44, 25]]) {
		s.line(a, b + 1, c, d + 1, '#2a1a12', { onlyOver: true }); s.line(a, b, c, d, EMBER.mid, { onlyOver: true });
	}
	s.outline();
	return s;
}

module.exports = { slime, grub, bat, wolf, grubKing };
