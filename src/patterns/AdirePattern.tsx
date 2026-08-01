import type { CSSProperties } from "react";
import type { PatternTone, PatternType } from "../types";

const DEFAULT_PATTERN_CELLS: readonly PatternType[] = ["agbole", "waala", "ododo", "waya", "orogbo", "gangan"];
const HERO_PATTERN_ROWS: readonly (readonly PatternType[])[] = [
  ["agbole", "waala", "ododo", "waya", "orogbo", "gangan"],
  ["gangan", "orogbo", "waya", "ododo", "waala", "agbole"],
  ["waala", "ododo", "gangan", "agbole", "waya", "orogbo"],
  ["orogbo", "waya", "agbole", "gangan", "ododo", "waala"],
  ["ododo", "agbole", "orogbo", "waala", "gangan", "waya"],
  ["waya", "gangan", "waala", "orogbo", "agbole", "ododo"],
  ["agbole", "gangan", "ododo", "orogbo", "waala", "waya"],
  ["waala", "waya", "orogbo", "ododo", "gangan", "agbole"],
  ["ododo", "orogbo", "agbole", "waya", "waala", "gangan"],
  ["gangan", "agbole", "waya", "waala", "orogbo", "ododo"]
];
const DEFAULT_REPEAT_COUNT = 4;
const HERO_REPEAT_COUNT = 6;

const PATTERN_MASKS = {
  agbole: new URL("../../assets/patterns/agbole.svg", import.meta.url).href,
  waala: new URL("../../assets/patterns/waala.svg", import.meta.url).href,
  ododo: new URL("../../assets/patterns/ododo.svg", import.meta.url).href,
  waya: new URL("../../assets/patterns/waya.svg", import.meta.url).href,
  orogbo: new URL("../../assets/patterns/orogbo.svg", import.meta.url).href,
  gangan: new URL("../../assets/patterns/gangan.svg", import.meta.url).href
} satisfies Record<PatternType, string>;

interface AdirePatternProps {
  className: string;
  tone: PatternTone;
  cells?: readonly PatternType[];
  repeatCount?: number;
}

interface PatternCellProps {
  type: PatternType;
}

interface PatternCellStyle extends CSSProperties {
  "--pattern-mask": string;
}

export function HeroTextilePanel() {
  return (
    <div className="hero-textile__bands" aria-hidden="true">
      {HERO_PATTERN_ROWS.map(function renderHeroPatternRow(rowCells, rowIndex) {
        const direction = rowIndex % 2 === 0 ? "left" : "right";

        return (
          <div className={`hero-textile__row hero-textile__row--${direction}`} key={`${rowCells.join("-")}-${rowIndex}`}>
            <AdirePattern className="hero-textile__pattern" tone="cream" cells={rowCells} repeatCount={HERO_REPEAT_COUNT} />
          </div>
        );
      })}
    </div>
  );
}

export function PatternBand() {
  return (
    <div className="pattern-band" aria-hidden="true">
      <AdirePattern className="pattern-band__inner" tone="indigo" />
    </div>
  );
}

function AdirePattern({ className, tone, cells = DEFAULT_PATTERN_CELLS, repeatCount = DEFAULT_REPEAT_COUNT }: AdirePatternProps) {
  return (
    <div className={`${className} adire-pattern adire-pattern--${tone}`} aria-hidden="true">
      <div className="adire-pattern__track">
        {Array.from({ length: repeatCount }).map(function renderRepeat(_, repeatIndex) {
          return (
            <div className="adire-repeat" key={repeatIndex}>
              {cells.map(function renderCell(type, cellIndex) {
                return <PatternCell key={`${repeatIndex}-${type}-${cellIndex}`} type={type} />;
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PatternCell({ type }: PatternCellProps) {
  const style: PatternCellStyle = {
    "--pattern-mask": `url("${PATTERN_MASKS[type]}")`
  };

  return <span className={`pattern-cell pattern-cell--${type}`} style={style} aria-hidden="true" />;
}
