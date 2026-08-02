import { patternItems } from "../content";
import { PatternBand } from "../patterns/AdirePattern";

export function PatternSection() {
  return (
    <section className="pattern-section section-dark motion-section" id="patterns" aria-labelledby="patterns-title" data-motion-section>
      <div className="container pattern-grid">
        <div className="pattern-copy scroll-reveal">
          <p className="eyebrow">FESTIVAL PROGRAM</p>
          <h2 id="patterns-title">CELEBRATING YORUBA CULTURE & CREATIVITY</h2>
          <p>
            Abíádé Adire Festival brings fashion, performance, craft, and knowledge into one cultural experience. The current page keeps the textile-led identity, but now frames it as a public celebration.
          </p>
        </div>
        <ul className="pattern-cards" aria-label="Abíádé pattern principles">
          {patternItems.map(function renderPatternItem(item) {
            return (
              <li key={item.id} className={`pattern-card pattern-card--${item.id}`}>
                <item.Icon aria-hidden="true" />
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </li>
            );
          })}
        </ul>
      </div>
      <PatternBand />
    </section>
  );
}
