#!/usr/bin/env node

import { readdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const ROOT_DIR = path.resolve(__dirname, '..')
const SKILLS_DIR = path.join(ROOT_DIR, 'skills')
const README_PATH = path.join(ROOT_DIR, 'README.md')

const START_MARKER = '<!-- skills-index:start -->'
const END_MARKER = '<!-- skills-index:end -->'

function extractFrontmatterValue(frontmatter, key) {
  const match = frontmatter.match(
    new RegExp(`^${key}:\\s*(?:"([^"]+)"|(.+))\\s*$`, 'm'),
  )

  if (!match) {
    throw new Error(`Missing ${key} in frontmatter`)
  }

  return (match[1] ?? match[2]).trim()
}

async function getSkills() {
  const entries = await readdir(SKILLS_DIR, { withFileTypes: true })
  const skills = []

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue
    }

    const skillPath = path.join(SKILLS_DIR, entry.name, 'SKILL.md')
    const content = await readFile(skillPath, 'utf8')
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/)

    if (!frontmatterMatch) {
      throw new Error(`Missing frontmatter in ${skillPath}`)
    }

    const frontmatter = frontmatterMatch[1]
    const name = extractFrontmatterValue(frontmatter, 'name')
    const description = extractFrontmatterValue(frontmatter, 'description')

    skills.push({
      directoryName: entry.name,
      name,
      description,
    })
  }

  return skills.sort((a, b) => a.name.localeCompare(b.name))
}

function buildIndex(skills) {
  return skills
    .map(
      (skill) =>
        `- [\`${skill.name}\`](skills/${skill.directoryName}/SKILL.md) — ${skill.description}`,
    )
    .join('\n')
}

async function main() {
  const skills = await getSkills()
  const readme = await readFile(README_PATH, 'utf8')

  if (!readme.includes(START_MARKER) || !readme.includes(END_MARKER)) {
    throw new Error('README.md is missing skills index markers')
  }

  const updatedReadme = readme.replace(
    new RegExp(`${START_MARKER}[\\s\\S]*?${END_MARKER}`),
    `${START_MARKER}\n${buildIndex(skills)}\n${END_MARKER}`,
  )

  await writeFile(README_PATH, updatedReadme)

  process.stdout.write(`Updated README index with ${skills.length} skills.\n`)
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`)
  process.exitCode = 1
})
