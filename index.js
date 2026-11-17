/**
 * DeepSeek Harness Host plugin: serves the bundled self-psychology supervision skill
 * (`SKILL.md` at the package root) through the skill registry.
 *
 * The catalog carries only the frontmatter description; the instruction body, and the
 * `assets/prompts/` templates it names, are read on demand from this package.
 */
import { readFile } from 'node:fs/promises'
import { dirname, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

/** Cordis plugin identity. */
export const name = 'skill-self-psychology-supervision'

/** The plugin contributes to `ctx.skills` and must mount after the registry. */
export const inject = ['skills']

const SKILL_NAME = 'self-psychology-supervision'
const PROVIDER_NAME = 'self-psychology-supervision'
/** Precedence of a packaged skill provider; an equal-named workspace copy still wins. */
const RANK = 600

const SKILL_PATH = fileURLToPath(new URL('./SKILL.md', import.meta.url))
const RESOURCE_BASE = Object.freeze({
  kind: 'directory',
  path: dirname(SKILL_PATH).split(sep).join('/'),
})

/** Strip one matching pair of YAML quotes. */
function unquote(value) {
  if (value.length < 2) return value
  const first = value[0]
  const last = value[value.length - 1]
  return (first === '"' && last === '"') || (first === "'" && last === "'") ? value.slice(1, -1) : value
}

/**
 * Split a `SKILL.md` into its frontmatter fields and its Markdown body.
 * Reads `key: value`, quoted values, and `|` / `>` block scalars; ignores other YAML.
 * @param raw - Whole file text.
 * @param path - File path used in error messages.
 * @returns The routing description, optional routing guidance, and the body.
 * @throws When the frontmatter is missing or carries no description.
 */
function parseSkill(raw, path) {
  const frontmatter = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/u.exec(raw)
  if (frontmatter?.[1] === undefined) throw new Error(`${path} has no YAML frontmatter`)
  const fields = {}
  const lines = frontmatter[1].split(/\r?\n/)
  for (let index = 0; index < lines.length; index += 1) {
    const entry = /^([A-Za-z][A-Za-z0-9_-]*):[ \t]*(.*)$/u.exec(lines[index])
    if (entry === null) continue
    const key = entry[1]
    const value = entry[2].trim()
    if (/^[|>][-+]?$/u.test(value)) {
      const block = []
      while (index + 1 < lines.length && (/^[ \t]+\S/u.test(lines[index + 1]) || lines[index + 1].trim() === '')) {
        block.push(lines[index + 1].trim())
        index += 1
      }
      fields[key] = value.startsWith('|')
        ? block.join('\n').trim()
        : block.filter(Boolean).join(' ').trim()
      continue
    }
    fields[key] = unquote(value)
  }
  const description = typeof fields.description === 'string' ? fields.description.trim() : ''
  if (description === '') throw new Error(`${path} has no description`)
  const whenToUse = typeof fields.whenToUse === 'string' ? fields.whenToUse.trim() : ''
  return {
    description,
    whenToUse: whenToUse === '' ? undefined : whenToUse,
    content: raw.slice(frontmatter[0].length).trim(),
  }
}

/**
 * Register the packaged skill as a provider, reading `SKILL.md` during discovery and on every load.
 * A missing or malformed file is reported once and leaves the catalog without this skill; its
 * failure is not treated as an empty catalog, so a later fix is picked up on the next lookup.
 * @param ctx - Context carrying the skill registry.
 */
export function apply(ctx) {
  let reported = ''
  function warn(error) {
    const message = String(error)
    if (message === reported) return
    reported = message
    ctx.logger.warn(`skill-self-psychology-supervision: ${message}`)
  }
  async function readSkill(signal) {
    const raw = await readFile(SKILL_PATH, { encoding: 'utf8', signal })
    return parseSkill(raw, SKILL_PATH)
  }
  ctx.skills.registerProvider(control => ({
    name: PROVIDER_NAME,
    async list(options) {
      let skill
      try {
        skill = await readSkill(options.signal)
      } catch (error) {
        if (options.signal?.aborted === true) throw error
        warn(error)
        return { candidates: [], complete: false }
      }
      return {
        complete: true,
        candidates: [{
          name: SKILL_NAME,
          description: skill.description,
          ...(skill.whenToUse === undefined ? {} : { whenToUse: skill.whenToUse }),
          invocation: { modelInvocable: true, userInvocable: true },
          provider: PROVIDER_NAME,
          source: 'bundled',
          rank: RANK,
          path: SKILL_PATH,
          resourceBase: RESOURCE_BASE,
          locator: SKILL_PATH,
        }],
      }
    },
    async get(candidate, options) {
      let skill
      try {
        skill = await readSkill(options.signal)
      } catch (error) {
        if (options.signal?.aborted === true) throw error
        warn(error)
        control.invalidate()
        return undefined
      }
      return {
        name: candidate.name,
        description: skill.description,
        ...(skill.whenToUse === undefined ? {} : { whenToUse: skill.whenToUse }),
        invocation: candidate.invocation,
        source: candidate.source,
        provider: PROVIDER_NAME,
        path: SKILL_PATH,
        resourceBase: RESOURCE_BASE,
        content: skill.content,
      }
    },
  }))
}
