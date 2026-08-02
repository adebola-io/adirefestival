import type { MouseEvent } from "react";
import { lookbookItems } from "../content";
import type { PreviewHandler } from "../types";

interface LookbookProps {
  onPreview: PreviewHandler;
}

export function Lookbook({ onPreview }: LookbookProps) {
  return (
    <section className="lookbook section-light motion-section" id="lookbook" aria-labelledby="lookbook-title" data-motion-section>
      <div className="container section-heading scroll-reveal">
        <p className="eyebrow">LOOKBOOK</p>
        <h2 id="lookbook-title">CELEBRATING ADIRE, CELEBRATING STORIES.</h2>
        <p>
          Every piece reflects our core values: creativity, heritage, and impact. Whether it’s a customized design for your special event or a project that uplifts our community, each work is a testament to the beauty and resilience of Yoruba culture.
        </p>
      </div>

      <ul className="container lookbook-grid" aria-label="Abíádé lookbook images">
        {lookbookItems.map(function renderLookbookItem(item) {
          function handlePreviewClick(event: MouseEvent<HTMLButtonElement>) {
            onPreview(item, event);
          }

          return (
            <li className={item.className} key={item.id}>
              <button className="image-button" type="button" onClick={handlePreviewClick} title={item.title}>
                <img src={item.src} alt={item.alt} width={item.width} height={item.height} loading="lazy" />
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
