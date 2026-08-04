export function PromoBanner() {
  return (
    <aside className="promo-banner" aria-label="Abíádé Adire Festival announcement">
      <div className="container promo-banner__grid">
        <time className="promo-banner__date" dateTime="2026-11-15" aria-label="November 15, 2026">
          <span>NOV</span>
          <strong>15</strong>
        </time>
        <div className="promo-banner__copy">
          <p className="eyebrow">ABÍÁDÉ ADIRE FESTIVAL 2026</p>
          <p className="promo-banner__title">The Source Within (Omi)</p>
          <p>
            Join us on <time dateTime="2026-11-15">November 15</time> for a celebration of Yoruba culture, craft, and community.
          </p>
        </div>
        <a className="promo-banner__link" href="#orders" title="View Abíádé Adire Festival tickets">
          Get Tickets
        </a>
      </div>
    </aside>
  );
}
