import { heroSlideItems } from "../content";
import { HeroTextilePanel } from "../patterns/AdirePattern";

export function Hero() {
  return (
    <section className="hero section-dark motion-section" id="top" aria-labelledby="hero-title" data-motion-section>
      <div className="hero-slideshow" aria-hidden="true">
        {heroSlideItems.map(function renderHeroSlide(item, index) {
          return <img key={item.id} src={item.src} alt="" loading={index === 0 ? "eager" : "lazy"} />;
        })}
      </div>
      <div className="container hero-grid">
        <div className="hero-panel scroll-reveal">
          <p className="eyebrow">THEME · THE SOURCE WITHIN (OMI) · NOVEMBER 15</p>
          <h1 id="hero-title">ABÍÁDÉ ADIRE FESTIVAL 2026</h1>
          <p className="hero-intro">Join us for a celebration of Yoruba culture, craft, and community.</p>
          <div className="hero-actions" aria-label="Primary actions">
            <a className="button button--light" href="#patterns" title="Explore the Abíádé Adire Festival program">
              Experience the Magic
            </a>
            <a className="button button--outline" href="#orders" title="View Abíádé Adire Festival tickets">
              Buy Tickets
            </a>
          </div>
        </div>
        <aside className="hero-textile" aria-label="Animated Adire repeat pattern panel">
          <HeroTextilePanel />
        </aside>
      </div>

    </section>
  );
}
