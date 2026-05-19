// lib/knowledge.js — Đọc tất cả .md trong zalo-knowledge/ thành 1 knowledge string

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Load tất cả file .md trong zalo-knowledge/ folder.
 * Mỗi file thành 1 section với header tên file.
 * @returns {string} Knowledge string ready to inject vào system prompt
 */
export function loadKnowledge() {
  const dir = path.join(__dirname, '..', 'zalo-knowledge');

  if (!fs.existsSync(dir)) {
    console.warn(`[knowledge] Folder not found: ${dir}`);
    return '(Chưa có knowledge base — tạo file .md trong zalo-knowledge/ để bot có thông tin trả lời)';
  }

  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.md') && !f.startsWith('_'))
    .sort();

  if (files.length === 0) {
    console.warn('[knowledge] No .md files in zalo-knowledge/');
    return '(Chưa có knowledge base)';
  }

  const sections = files.map(filename => {
    const content = fs.readFileSync(path.join(dir, filename), 'utf-8').trim();
    const sectionName = filename.replace(/\.md$/, '').toUpperCase().replaceAll('-', ' ');
    return `### ${sectionName}\n\n${content}`;
  });

  console.log(`[knowledge] Loaded files: ${files.join(', ')}`);
  return sections.join('\n\n---\n\n');
}
