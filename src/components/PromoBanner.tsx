export function PromoBanner() {
  return (
    <aside className="promo-banner" aria-label="Abiade Adire Festival announcement">
      <div className="container promo-banner__grid">
        <time className="promo-banner__date" dateTime="2026-12-26" aria-label="December 26, 2026">
          <span>DEC</span>
          <strong>26</strong>
        </time>
        <div className="promo-banner__copy">
          <p className="eyebrow">ABIÁDÉ ADIRE FESTIVAL 2026</p>
          <p className="promo-banner__title">The Source Within (Omi)</p>
          <p>
            Join us on <time dateTime="2026-12-26">December 26</time> for a celebration of Yoruba culture, craft, and community.
          </p>
        </div>
        <a className="promo-banner__link" href="#orders" title="View Abiade Adire Festival tickets">
          Get Tickets
        </a>
      </div>
    </aside>
  );
}
