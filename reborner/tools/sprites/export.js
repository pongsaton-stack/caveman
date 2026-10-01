// วาดสไปรต์มอนใหม่ทั้งชุด: node tools/sprites/export.js (แก้ทรง/สีที่ monsters.js)
const M = require('./monsters');
const fs = require('fs');
const out = require('path').join(__dirname, '../../assets/sprites/monsters');
fs.mkdirSync(out, { recursive: true });
const map = { M01: M.slime(), M03: M.grub(false), M06: M.bat(false), M15: M.wolf(), 'COMP-M03': M.grub(true), 'COMP-M06': M.bat(true), B1: M.grubKing() };
