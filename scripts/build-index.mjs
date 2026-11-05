import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS_DIR = join(root, "skills");
const REPO_URL = "https://github.com/SHRIJANAGAIN/RAW-SKILLS";
const UPDATED = new Date().toISOString().slice(0, 10);

// skills/<bucket>/<skill-name>/SKILL.md
function skillFolders() {
  if (!existsSync(SKILLS_DIR)) return [];
  const found = [];
  for (const bucket of readdirSync(SKILLS_DIR, { withFileTypes: true })) {
    if (!bucket.isDirectory()) continue;
    for (const skill of readdirSync(join(SKILLS_DIR, bucket.name), { withFileTypes: true })) {
      if (skill.isDirectory()) found.push({ bucket: bucket.name, name: skill.name });
    }
  }
  return found.sort((a, b) => a.name.localeCompare(b.name));
}

function frontmatterDescription(file) {
  if (!existsSync(file)) return "";
  const text = readFileSync(file, "utf8");
  const fm = /^---\r?\n([\s\S]*?)\r?\n---/.exec(text);
  const lines = (fm ? fm[1] : text).split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const match = /^description:\s*(.*)$/i.exec(lines[i]);
    if (!match) continue;
    const inline = match[1].trim();
    const continuation = [];
    for (let j = i + 1; j < lines.length; j++) {
      if (/^\S/.test(lines[j])) break;
      if (lines[j].trim()) continuation.push(lines[j].trim());
    }
    return [inline, ...continuation].filter(Boolean).join(" ").replace(/^["']|["']$/g, "");
  }
  const firstLine = lines.find((line) => line.trim() && !line.startsWith("#") && line.trim() !== "---");
  return (firstLine || "").trim();
}

function countFiles(dir) {
  let total = 0;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === ".git") continue;
    total += entry.isDirectory() ? countFiles(join(dir, entry.name)) : 1;
  }
  return total;
}

const skills = skillFolders();
const out = [
  "# Skill Index",
  "",
  `All ${skills.length.toLocaleString("en-US")} skills in this repository, grouped by the bucket folder that holds them. Each entry links to its \`SKILL.md\`.`,
  "",
  `- Repository: <${REPO_URL}>`,
  `- Last updated: ${UPDATED}`,
  `- Content: ${countFiles(root).toLocaleString("en-US")} files`,
  "",
  "| # | Skill | Path | Description |",
  "| --- | --- | --- | --- |",
];

skills.forEach(({ bucket, name }, i) => {
  const description = frontmatterDescription(join(SKILLS_DIR, bucket, name, "SKILL.md"))
    .replace(/\s+/g, " ")
    .trim();
  const short = description.length > 160 ? `${description.slice(0, 157)}...` : description || "-";
  out.push(
    `| ${i + 1} | ${name} | [skills/${bucket}/${name}](${encodeURI(`skills/${bucket}/${name}`)}/SKILL.md) | ${short.replace(/\|/g, "\\|")} |`
  );
});

out.push("");
writeFileSync(join(root, "SKILLS.md"), out.join("\n"), "utf8");
console.log(`Wrote SKILLS.md with ${skills.length} skills.`);
