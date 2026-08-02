import { assets } from "../assets";

export function Footer() {
  return (
    <footer className="site-footer section-dark">
      <div className="container footer-grid">
        <img src={assets.logo} alt="Abíádé" width="302" height="84" loading="lazy" />
        <p>Experience Yoruba Culture, Creativity, and Community.</p>
        <p>
          <small>
            &copy; <time dateTime="2026">2026</time> Abíádé.
          </small>
        </p>
      </div>
    </footer>
  );
}
