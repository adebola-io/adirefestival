import { professionalImageItems } from "../content";

export function ProfessionalSeries() {
  return (
    <section className="professional section-light motion-section" id="professional" aria-labelledby="professional-title" data-motion-section>
      <div className="container section-heading section-heading--split scroll-reveal">
        <div>
          <p className="eyebrow">GALLERY</p>
          <h2 id="professional-title">ADIRE IN MOTION</h2>
        </div>
        <p>
          Festival moments, Adire looks, and the people carrying the cloth into motion.
        </p>
      </div>

      <ul className="container professional-carousel" aria-label="Professional Abiade Adire image series">
        {professionalImageItems.map(function renderProfessionalImage(item) {
          return (
            <li className="professional-slide" key={item.id}>
              <figure className="professional-card">
                <img src={item.src} alt={item.alt} width={item.width} height={item.height} loading="lazy" />
              </figure>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
