import { craftItems } from "../content";

export function Craft() {
  return (
    <section className="craft section-dark motion-section" id="craft" aria-labelledby="craft-title" data-motion-section>
      <div className="container craft-heading scroll-reveal">
        <p className="eyebrow">THE EXPERIENCE</p>
        <h2 id="craft-title">WHAT AWAITS YOU</h2>
        <p>Three headline experiences bring the festival to life through fashion, performance, and Symposium.</p>
      </div>

      <ol className="container craft-feature-grid" aria-label="Three main Abiade Adire Festival events">
        {craftItems.map(function renderCraftItem(item, index) {
          return (
            <li className="craft-feature-card scroll-reveal" key={item.term}>
              <div className="craft-feature-card__top">
                <span className="craft-feature-card__icon" aria-hidden="true">
                  <item.Icon />
                </span>
                <span className="craft-feature-card__number" aria-hidden="true">
                  0{index + 1}
                </span>
              </div>
              <h3 title={item.term}>{item.term}</h3>
              <p title={item.description}>{item.description}</p>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
