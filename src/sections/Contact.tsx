import { ExternalLink } from "lucide-react";
import { assets } from "../assets";
import { links } from "../content";

export function Contact() {
  return (
    <section className="contact section-dark motion-section" id="contact" aria-labelledby="contact-title" data-motion-section>
      <div className="container contact-grid">
        <div className="contact-copy scroll-reveal">
          <p className="eyebrow">CONTACT</p>
          <h2 id="contact-title">REGISTER OR JOIN THE ACADEMY</h2>
          <p>Register for the Abiádé Adire Festival 2026 or submit your details for an Abiade Adire Academy course, workshop, or training session.</p>
          <div className="contact-actions">
            <a className="button button--accent" href={links.festivalForm} target="_blank" rel="noopener noreferrer" title="Open the Abiádé Adire Festival 2026 registration form">
              <ExternalLink aria-hidden="true" />
              Festival Registration
            </a>
            <a className="button button--outline" href={links.academyForm} target="_blank" rel="noopener noreferrer" title="Open the updated Abiade Adire Academy form">
              <ExternalLink aria-hidden="true" />
              Academy Application
            </a>
          </div>
        </div>

        <aside className="contact-panel scroll-reveal" id="whatsapp-qr" aria-labelledby="qr-title">
          <p className="eyebrow">SCAN TO ENQUIRE</p>
          <h3 id="qr-title">WhatsApp Business</h3>
          <img src={assets.whatsappQr} alt="Abiade WhatsApp Business QR code" width="180" height="180" loading="lazy" />
          <p>Scan to ask about courses, workshops, training dates, and Adire learning sessions in one message.</p>
        </aside>
      </div>
    </section>
  );
}
